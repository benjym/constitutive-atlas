"""Development calibration, keeping evaluation observations out of optimization."""
import math
import random

from .metrics import compare, monotonic_pairs
from .reservations import assert_development_ids


def validate_config(config):
    if config.get('paper_record_version') != 1 or config.get('phase') != 'development_only':
        raise ValueError('this runner only implements the development pilot contract')
    known = set(config['experiment_paths'])
    assert_development_ids(known)
    evaluation = config['evaluation_ids']
    if not evaluation or len(evaluation) != len(set(evaluation)) or not set(evaluation) <= known:
        raise ValueError('invalid evaluation IDs')
    for package, ids in config['packages'].items():
        if not ids or len(ids) != len(set(ids)) or not set(ids) <= known:
            raise ValueError(f'{package}: invalid calibration IDs')
        if set(ids) & set(evaluation):
            raise ValueError(f'{package}: calibration/evaluation leakage')
    contrast = config.get('calibration_design_contrast')
    if contrast is not None:
        packages = [contrast['reference_package'], contrast['alternative_package']]
        if contrast['kind'] != 'matched_test_count' or len(set(packages)) != 2:
            raise ValueError('two distinct matched-count packages required')
        if any(len(config['packages'][p]) != contrast['tests_per_package'] for p in packages):
            raise ValueError('matched-count packages must have the declared equal test count')
        grouped = [eid for group in contrast['evaluation_groups'].values() for eid in group]
        if (any(not group for group in contrast['evaluation_groups'].values()) or
                len(grouped) != len(set(grouped)) or set(grouped) != set(evaluation)):
            raise ValueError('contrast evaluation groups must partition all evaluation IDs')
        weights = contrast['evaluation_stress_weight_sensitivity']
        if (contrast['primary_stress_weight'] != .5 or .5 not in weights or
                len(weights) != len(set(weights)) or any(not 0 <= w <= 1 for w in weights)):
            raise ValueError('invalid declared evaluation-weight sensitivity')
    if config['objective']['channels'] != ['q', 'volumetric_strain']:
        raise ValueError('unsupported objective channels')
    if config['objective']['q_scale'] != 'initial_mean_effective_stress':
        raise ValueError('unsupported stress scaling')
    if config['objective']['volumetric_strain_scale'] <= 0:
        raise ValueError('invalid volumetric scale')
    if config['objective']['aggregation'] != 'equal channel MSE within test, equal tests':
        raise ValueError('unsupported aggregation')
    optimizer = config['optimizer']
    if optimizer['method'] != 'bounded_coordinate_pattern_search':
        raise ValueError('unsupported optimizer')
    if optimizer['max_evaluations'] < 1 or not optimizer['seeds']:
        raise ValueError('empty calibration budget')
    if len(set(optimizer['seeds'])) != len(optimizer['seeds']):
        raise ValueError('duplicate optimizer seeds')
    if not 0 < optimizer['minimum_step'] < optimizer['initial_step'] <= 1:
        raise ValueError('invalid search step')
    if config['samples'] < 2 or config['steps'] < 1 or config['maximum_axial_strain'] <= 0:
        raise ValueError('invalid evaluation grid')
    if sorted(set(config['refinement_steps'])) != config['refinement_steps'] or any(s <= config['steps'] for s in config['refinement_steps']):
        raise ValueError('refinement steps must increase beyond baseline steps')
    evaluation_protocol = config.get('evaluation_protocol')
    if evaluation_protocol is not None:
        if (evaluation_protocol['kind'] != 'acquisition_order_drained' or
                evaluation_protocol['initial_state_policy'] != 'measured_file_void_ratio_and_effective_stress' or
                evaluation_protocol['metric'] != 'absolute_axial_strain_travel_trapezoidal_endpoint_error'):
            raise ValueError('unsupported evaluation protocol or initial-state policy')
        resolutions = [evaluation_protocol['maximum_increment'], *evaluation_protocol['refinement_maximum_increments']]
        if (len(resolutions) < 2 or any(not math.isfinite(s) or s <= 0 for s in resolutions) or
                any(b >= a for a, b in zip(resolutions, resolutions[1:]))):
            raise ValueError('replay increments must be positive and strictly refine')
    ids = [m['id'] for m in config['models']]
    if len(ids) != len(set(ids)) or not ids:
        raise ValueError('invalid model list')
    for model in config['models']:
        fitted, fixed = set(model['fit']), set(model['fixed_parameters'])
        if fitted & fixed or fitted | fixed != set(model['baseline_parameters']):
            raise ValueError('fitted and fixed parameters must partition all parameters')
        for name, definition in model['fit'].items():
            lo, hi = definition['bounds']
            if not math.isfinite(lo) or not math.isfinite(hi) or hi <= lo:
                raise ValueError('invalid fit bounds')
            if definition['transform'] not in ('log', 'linear') or (definition['transform'] == 'log' and lo <= 0):
                raise ValueError('invalid parameter transform')
            if not lo <= model['baseline_parameters'][name] <= hi:
                raise ValueError('baseline outside fit bounds')
        if any(model['baseline_parameters'][n] != v for n, v in model['fixed_parameters'].items()):
            raise ValueError('fixed parameters disagree with baseline')


def prepare_experiment(experiment, config):
    if 'id' in experiment:
        assert_development_ids([experiment['id']])
    if experiment['protocol'] != 'drained-triaxial':
        raise ValueError('pilot requires drained triaxial tests')
    if 'void_ratio' not in experiment['initial']:
        raise ValueError('initial void ratio is required')
    curves = {}
    duplicates = {}
    for channel in config['objective']['channels']:
        curves[channel], duplicates[channel] = monotonic_pairs(
            experiment['rows'], 'axial_strain', channel, config['maximum_axial_strain'])
    if curves['q'][0][0] != 0:
        raise ValueError('pilot requires initial strain zero; explicit offset adapter needed')
    pressure = sum(experiment['initial']['effective_stress'][:3])/3
    if pressure <= 0:
        raise ValueError('positive initial effective pressure required')
    return {'experiment': experiment, 'curves': curves, 'duplicates': duplicates,
            'target': curves['q'][-1][0],
            'scales': {'q': pressure, 'volumetric_strain': config['objective']['volumetric_strain_scale']}}


def score_prediction(prepared, prediction, samples):
    if prediction['status'] != 'success':
        return None
    metrics = {}
    try:
        for channel, measured in prepared['curves'].items():
            predicted = [(p['axial_strain'], p[channel]) for p in prediction['points']]
            metrics[channel] = compare(measured, predicted, prepared['scales'][channel], samples)
    except (ValueError, KeyError) as exc:
        prediction['status'] = 'invalid_prediction'
        prediction['message'] = str(exc)
        return None
    return metrics


def unit_parameter(value, definition, inverse=False):
    lo, hi = definition['bounds']
    logarithmic = definition['transform'] == 'log'
    if logarithmic:
        lo, hi = math.log(lo), math.log(hi)
    if inverse:
        value = lo + value * (hi-lo)
        return math.exp(value) if logarithmic else value
    value = math.log(value) if logarithmic else value
    return (value-lo)/(hi-lo)


def calibrate(model, calibration, config, adapter, seed, checkpoint):
    """The optimizer receives only calibration tests, never evaluation records."""
    names = list(model['fit'])
    options = config['optimizer']
    rng = random.Random(seed)
    current = [unit_parameter(model['baseline_parameters'][n], model['fit'][n]) for n in names]
    if seed != 0:
        current = [rng.random() for _ in names]
    trace = []

    def evaluate(vector):
        parameters = dict(model['fixed_parameters'])
        parameters.update({n: unit_parameter(v, model['fit'][n], inverse=True) for n, v in zip(names, vector)})
        tests = []
        for prepared in calibration:
            prediction = adapter.simulate(model['id'], parameters, prepared['experiment'],
                                          prepared['target'], config['steps'], config['timeout_seconds'])
            metrics = score_prediction(prepared, prediction, config['samples'])
            tests.append({'experiment_id': prepared['experiment']['id'],
                          **{k: v for k, v in prediction.items() if k != 'points'}, 'metrics': metrics})
        completed = all(t['metrics'] is not None for t in tests)
        objective = (sum(sum(c['scaled_mse'] for c in t['metrics'].values())/2 for t in tests)/len(tests)
                     if completed else options['failure_objective'])
        row = {'evaluation': len(trace)+1, 'parameters': parameters, 'objective': objective,
               'completed': completed, 'tests': tests}
        trace.append(row)
        checkpoint(row)
        return objective

    best_value = evaluate(current)
    best_index = 0
    step = options['initial_step']
    while len(trace) < options['max_evaluations'] and step >= options['minimum_step']:
        candidates = []
        # All trials in a sweep originate at the same incumbent.
        for index in range(len(names)):
            for sign in (-1, 1):
                trial = list(current)
                trial[index] = max(0., min(1., trial[index] + sign*step))
                if trial == current:
                    continue
                candidates.append(trial)
        improved = False
        next_vector = current
        for trial in candidates:
            if len(trace) >= options['max_evaluations']:
                break
            value = evaluate(trial)
            if value < best_value:
                best_value, next_vector, best_index = value, trial, len(trace)-1
                improved = True
        current = next_vector
        if not improved:
            step /= 2
    best = trace[best_index]
    return {'seed': seed, 'status': 'success' if best['completed'] else 'calibration_failure',
            'termination': 'step_threshold' if step < options['minimum_step'] else 'budget_limit',
            'final_search_step': step, 'evaluation_count': len(trace),
            'best': best, 'trace': trace}
