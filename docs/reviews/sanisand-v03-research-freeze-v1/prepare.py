"""Validate frozen inputs and stage normal sources; never build or integrate."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
from atlas.compiler import generate
from atlas.initialization import initialize_state
from atlas.model import load, state_role
from atlas.dsl import ValidationError


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_pins():
    for receipt in ('prospective-freeze.json', 'source-pins.json'):
        for name, expected in json.loads((HERE / receipt).read_text())['files'].items():
            if digest(ROOT / name) != expected:
                raise ValueError('pinned input mismatch: ' + name)


def named_state(model, flat):
    result = {}; offset = 0
    for field in model['state']:
        size = 6 if field['shape'] == 'sym' else 1
        values = flat[offset:offset + size]
        if len(values) != size:
            raise ValueError('incomplete state')
        if state_role(field) == 'persistent':
            result[field['name']] = values if size == 6 else values[0]
        offset += size
    if offset != len(flat):
        raise ValueError('extra state')
    return result


def validate_inputs():
    check_pins()
    from verify_wire import validate_wire
    assert validate_wire(ROOT, HERE) == 81
    model = load(HERE / 'model.json')
    legacy = json.loads((ROOT / 'models/research/sanisand-2004-fixed-memory-be.json').read_text())
    bridge = json.loads((HERE / 'bridge.json').read_text())
    for field in bridge['identical_fields']:
        assert model[field] == legacy[field], field
    for old, new in zip(legacy['state'], model['state']):
        for key in bridge['state_numeric_fields_unchanged']:
            assert old.get(key) == new.get(key), key
    assert len(model['state']) == len(legacy['state']) == 6
    assert sum(6 if f['shape'] == 'sym' else 1 for f in model['state']) == 26
    assert [f['name'] for f in model['state'] if state_role(f) == 'persistent'] == ['sigma', 'e', 'alpha', 'fabric', 'alpha_in']
    requests = json.loads(gzip.decompress((HERE / 'trajectory-requests.json.gz').read_bytes()))
    assert len(requests) == 81 and len({r['id'] for r in requests}) == 81
    cases = {}; total_knots = 0
    expected_controls = [x for i in range(6) for x in [0.0] + [float(i == j) for j in range(6)]]
    accepted = []
    for r in requests:
        args = r['args']; n = r['plastic_steps']
        assert n in (256, 512, 1024)
        assert r['function'] == 'atlas_replay_recorded_scope' and r['types'] == ['string'] * 9
        assert len(args) == 9 and args[0] == model['id'] and args[8] == 'effective'
        numeric = [[float(v) for v in arg.split(',')] for arg in args[1:8]]
        assert all(math.isfinite(x) for values in numeric for x in values)
        params, state, strain, controls, flat_knots, material, recorded = numeric
        assert len(params) == 16 and len(state) == 26 and strain == [0.0] * 6
        assert controls == expected_controls
        assert args[6] == '2e-10,1e-6,45,14,20000,11'
        assert args[7] == '1e-10,30,10,20000,1e-7'
        assert len(flat_knots) == 7 * (n + 2) and r['knots_count'] == n + 2
        knots = [flat_knots[i:i+7] for i in range(0, len(flat_knots), 7)]
        assert knots[0] == [0.0] * 7 and knots[-1][0] == 0.02
        assert all(a[0] < b[0] for a, b in zip(knots, knots[1:]))
        assert r['sample_indices'] == [0, 1] + [1 + j * n // 16 for j in range(1, 17)]
        total_knots += len(knots)
        cases.setdefault(r['case'], []).append(n)
        initial = initialize_state(model, named_state(model, state), dict(zip(model['parameters'], params)))
        assert initial['initial'] == state
        if n == 256:
            accepted.append(r['case'])
    assert len(cases) == 27 and all(sorted(v) == [256, 512, 1024] for v in cases.values())
    assert total_knots == 48546
    probes = json.loads((HERE / 'negative-probes.json').read_text())['probes']
    rejected = []
    for probe in probes:
        if probe['id'] in ('incomplete-state', 'forced-plastic-failure'):
            continue  # API layout / nonlinear solve checks belong to backend qualification.
        args = probe['args']
        try:
            initialize_state(model, named_state(model, [float(x) for x in args[2].split(',')]),
                             dict(zip(model['parameters'], [float(x) for x in args[1].split(',')])))
        except (ValidationError, ArithmeticError, ValueError) as exc:
            rejected.append({'id': probe['id'], 'reason': str(exc)})
        else:
            raise AssertionError('initializer unexpectedly accepted: ' + probe['id'])
    assert len(rejected) == 10
    return {'model': model['id'], 'schema': model['schema_version'],
            'math_bridge': 'unchanged parameters/derived/domain/equations and numeric state layout',
            'requests_checked': len(requests), 'total_knots': total_knots,
            'material_intervals': total_knots - len(requests),
            'distinct_initial_states_accepted': accepted,
            'initialization_calls_accepted': len(requests), 'initializer_rejections': rejected,
            'candidate_integrations': 0, 'compiled_builds': 0,
            'deferred': ['backend execution', 'accuracy/refinement assessment', 'rollback/recovery/transaction probes', 'native/Wasm parity', 'scientific admission']}


def prepare(destination):
    report = validate_inputs()
    destination.mkdir(parents=True, exist_ok=False)
    pins = json.loads((HERE / 'source-pins.json').read_text())['files']
    for name in pins:
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    candidate = destination / 'models' / (report['model'] + '.json')
    candidate.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(HERE / 'model.json', candidate)
    generate(destination / 'generated', [candidate])
    generated = {str(f.relative_to(destination)): digest(f) for f in sorted((destination / 'generated').rglob('*')) if f.is_file()}
    assert generated
    report['generated'] = generated
    report['staged_source_files'] = len(pins)
    report['catalogue_models'] = [report['model']]
    (destination / 'preflight.json').write_text(json.dumps(report, indent=2) + '\n')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('destination', type=Path, help='new exclusive directory; no build or integration')
    options = parser.parse_args()
    print(json.dumps(prepare(options.destination.resolve()), indent=2))
