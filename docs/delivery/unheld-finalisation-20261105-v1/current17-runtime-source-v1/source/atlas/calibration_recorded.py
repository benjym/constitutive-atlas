"""Exclusive on-disk calibration runs through the existing native recorded API."""
import copy
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess

from .calibration_search import PredictionFailure, calibrate, validate_search
from .experiment_replay import digest, parse_json, prepare_replay
from .model import validate
from .recorded import CONTROL_DEFAULTS, execute_recorded
from .study_allocation import require
from .study_objective import score_objective, validate_objective
from .study_parameters import number


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write(path, value):
    content = json.dumps(value, indent=2, allow_nan=False) + '\n'
    with Path(path).open('x') as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())


def run_recorded_search(spec, objective, allocation, reservations, model,
                        experiments, configurations, *, allocation_sha256,
                        reservation_sha256, solver, solver_sha256, catalogue,
                        output, timeout=15):
    """Run serially with fixed explicit preparation and immutable candidate receipts.

    Inputs are decoded values; freeze.json records canonical value hashes, not
    original file-byte provenance. Output must be a new directory. Raw native
    stdout/stderr are not captured here: execute_recorded checks process status
    and request/settings identity before returning its parsed response.
    """
    (spec, objective, allocation, reservations, model, experiments,
     configurations, catalogue) = copy.deepcopy((spec, objective, allocation,
        reservations, model, experiments, configurations, catalogue))
    axes = validate_search(spec)
    plan = validate_objective(objective, allocation, reservations,
        allocation_sha256=allocation_sha256, reservation_sha256=reservation_sha256)
    validate(model)
    require(set(spec['parameters']) == set(model['parameters']), 'complete model parameter vector required')
    for name, field in model['parameters'].items():
        require(field['min'] <= spec['parameters'][name] <= field['max'], 'seed outside model bounds')
    for name, lo, hi, *_ in axes:
        field = model['parameters'][name]
        require(field['min'] <= lo < hi <= field['max'], 'search bounds exceed model bounds')
    ids = plan['test_ids']
    require(isinstance(experiments, dict) and set(experiments) == set(ids) and
            isinstance(configurations, dict) and set(configurations) == set(ids),
            'experiments/configurations must cover exactly the calibration package')
    observations = {}
    channels = objective['channels']
    units = {name: value['unit'] for name, value in channels.items()}
    for tid in ids:
        experiment, config = experiments[tid], configurations[tid]
        require(experiment.get('id') == tid, 'experiment ID does not match allocation')
        require(config.get('parameters') == spec['parameters'], 'configuration must explicitly use the search seed')
        prepare_replay(experiment, config, model=model)
        if 'volumetric_strain' in channels:
            require(experiment['rows'][0].get('volumetric_strain') == 0,
                    'volumetric observations must be referenced to zero at the first observation')
        observations[tid] = {'units': copy.deepcopy(units), 'rows': copy.deepcopy(experiment['rows'])}
    identity = {tid: {'units': units, 'status': 'success', 'points':
        [dict(row, observation_index=i) for i, row in enumerate(observations[tid]['rows'])]} for tid in ids}
    score_objective(objective, allocation, reservations, observations, identity,
        allocation_sha256=allocation_sha256, reservation_sha256=reservation_sha256)
    require(isinstance(catalogue, dict) and catalogue.get('schema_version') == '0.1' and
            isinstance(catalogue.get('models'), list), 'compiled catalogue required')
    require(catalogue.get('sha256') == digest(catalogue['models']), 'compiled catalogue hash mismatch')
    selected = [m for m in catalogue['models'] if m.get('id') == model['id']]
    require(len(selected) == 1 and selected[0] == model and
            list(selected[0]['parameters']) == list(model['parameters']),
            'compiled catalogue model or parameter order differs from supplied definition')
    solver = Path(solver).resolve()
    require(isinstance(solver_sha256, str) and len(solver_sha256) == 64 and
            _sha(solver) == solver_sha256, 'native executable identity mismatch')
    require(0 < number(timeout, 'timeout') <= 60, 'timeout must lie in (0,60] seconds')
    output = Path(output)
    require(not output.exists(), 'output directory already exists; no overwrite or resume')
    metadata = subprocess.run([str(solver), '--describe'], capture_output=True, text=True, timeout=timeout)
    require(metadata.returncode == 0 and parse_json(metadata.stdout) == catalogue,
            'native descriptor does not match frozen catalogue')
    # Dict equality ignores order; native parameter order is independently bound.
    described = next(m for m in parse_json(metadata.stdout)['models'] if m['id'] == model['id'])
    require(list(described['parameters']) == list(model['parameters']), 'native parameter order mismatch')
    require(_sha(solver) == solver_sha256, 'executable changed during metadata check')
    output.mkdir()
    freeze = dict(kind='recorded-calibration-freeze-v1', search=spec, objective=objective,
        allocation=allocation, reservations=reservations, model=model,
        experiments=experiments, configurations=configurations, catalogue=catalogue,
        allocation_sha256=allocation_sha256, reservation_sha256=reservation_sha256,
        solver_sha256=solver_sha256, timeout=timeout,
        value_sha256={name: digest(value) for name, value in
            [('model', model), ('experiments', experiments), ('configurations', configurations),
             ('search', spec), ('objective', objective), ('catalogue', catalogue)]},
        source_files_sha256={str(p.relative_to(Path(__file__).parent.parent)): _sha(p)
            for p in [Path(__file__), Path(__file__).with_name('calibration_search.py'),
                      Path(__file__).with_name('study_objective.py'),
                      Path(__file__).with_name('experiment_replay.py'),
                      Path(__file__).with_name('recorded.py')]},
        scientific_admission=False)
    _write(output/'freeze.json', freeze)
    _write(output/'metadata.json', dict(returncode=metadata.returncode,
        stdout=metadata.stdout, stderr=metadata.stderr))
    attempt = 0

    def predict(parameters):
        nonlocal attempt
        directory = output/f'candidate-{attempt:05d}'
        attempt += 1
        directory.mkdir()
        predictions = {}
        for i, tid in enumerate(ids):
            config = copy.deepcopy(configurations[tid])
            config['parameters'] = copy.deepcopy(parameters)
            try:
                prepared = prepare_replay(experiments[tid], config, model=model)
            except ValueError as exc:
                _write(directory/f'{i:03d}-preparation-error.json', {'test_id': tid, 'error': str(exc)})
                raise PredictionFailure(tid + ': ' + str(exc)) from exc
            request = prepared['request']
            _write(directory/f'{i:03d}-request.json', {'test_id': tid, **prepared})
            require(_sha(solver) == solver_sha256, 'executable changed before material call')
            try:
                response = execute_recorded(copy.deepcopy(request), solver, timeout=timeout)
            except Exception as exc:
                _write(directory/f'{i:03d}-execution-error.json',
                       {'test_id': tid, 'type': type(exc).__name__, 'error': str(exc)})
                if isinstance(exc, subprocess.TimeoutExpired):
                    raise PredictionFailure(tid + ': solver timeout') from exc
                raise
            _write(directory/f'{i:03d}-response.json', response)
            if response.get('ok') is True or 'api_version' in response:
                require(response.get('catalogue_hash') == catalogue['sha256'] and
                        response.get('model') == model['id'] and
                        response.get('parameters') == request['parameters'] and
                        response.get('initial') == request['initial'],
                        'response model/catalogue/parameters/preparation mismatch')
            if response.get('ok') is not True:
                raise PredictionFailure(tid + ': ' + str(response.get('message', 'recorded update failed')))
            points = response.get('points')
            require(isinstance(points, list) and len(points) == len(experiments[tid]['rows']),
                    'successful response does not cover every observation')
            require(response.get('state') == points[-1]['state'] and
                    response.get('strain') == points[-1]['strain'], 'final response state mismatch')
            tolerance = (CONTROL_DEFAULTS | request.get('control_settings', {}))['control_tolerance']
            mapped = []
            for j, (point, row) in enumerate(zip(points, experiments[tid]['rows'])):
                require(point['coordinate'] == j, 'response observation order mismatch')
                require(0 <= number(point['control_error'], 'control_error') <= tolerance,
                        'response exceeds declared control tolerance')
                state, strain = point['state'], point['strain']
                require(len(state) == len(request['initial']) and len(strain) == 6,
                        'response point state/strain layout mismatch')
                for value in state + strain: number(value, 'response component')
                radial = (state[1]+state[2])/2
                values = {'q': state[0]-radial, 'p': sum(state[:3])/3,
                          'volumetric_strain': math.fsum(strain[:3])-math.fsum(request['path']['initial_strain'][:3])}
                mapped.append(dict(observation_index=j, axial_strain=row['axial_strain'],
                                   **{name: values[name] for name in channels}))
            predictions[tid] = {'units': copy.deepcopy(units), 'status': 'success', 'points': mapped}
        return predictions

    def record(receipt):
        directory = output/f"candidate-{receipt['sequence']:05d}"
        _write(directory/'assessment.json', receipt)

    result = calibrate(spec, predict, objective, allocation, reservations, observations,
        allocation_sha256=allocation_sha256, reservation_sha256=reservation_sha256,
        on_candidate=record)
    require(_sha(solver) == solver_sha256, 'executable changed during calibration')
    _write(output/'result.json', result)
    _write(output/'manifest.json', {'kind': 'recorded-calibration-files-v1',
        'files': {str(p.relative_to(output)): _sha(p) for p in sorted(output.rglob('*.json'))},
        'scientific_admission': False})
    return result
