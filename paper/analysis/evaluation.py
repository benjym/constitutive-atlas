"""Explicit development evaluation protocols, separate from calibration objectives."""
import math

from .metrics import compare, compare_acquisition
from .pilot import prepare_experiment, score_prediction
from .reservations import assert_development_ids


def prepare_evaluation(experiment, config):
    if 'evaluation_protocol' not in config:
        return prepare_experiment(experiment, config)
    assert_development_ids([experiment['id']])
    if experiment['protocol'] != 'drained-triaxial':
        raise ValueError('replay evaluation requires drained triaxial tests')
    initial = experiment['initial']
    if ('void_ratio' not in initial or not math.isfinite(initial['void_ratio']) or
            initial['void_ratio'] <= 0 or len(initial['effective_stress']) != 6 or
            any(not math.isfinite(v) for v in initial['effective_stress'])):
        raise ValueError('finite measured void ratio and six initial stresses required')
    rows = []
    for row in experiment['rows']:
        x = row['axial_strain']
        if not math.isfinite(x) or x < 0:
            raise ValueError('finite nonnegative compression coordinate required')
        # Stop at the first crossing, never select later returning portions.
        if x > config['maximum_axial_strain']:
            break
        if any(not math.isfinite(row[c]) for c in config['objective']['channels']):
            raise ValueError('finite evaluation observables required')
        rows.append(row)
    if len(rows) < 2 or rows[0]['axial_strain'] != 0:
        raise ValueError('at least two acquisition rows beginning at zero required')
    if sum(abs(b['axial_strain']-a['axial_strain']) for a,b in zip(rows,rows[1:])) <= 0:
        raise ValueError('positive acquisition strain travel required')
    pressure = sum(initial['effective_stress'][:3])/3
    if pressure <= 0:
        raise ValueError('positive initial effective pressure required')
    return {'experiment': experiment, 'rows': rows,
            'scales': {'q': pressure, 'volumetric_strain': config['objective']['volumetric_strain_scale']}}


def resolutions(config):
    if 'evaluation_protocol' in config:
        protocol = config['evaluation_protocol']
        return [{'maximum_increment': step} for step in
                [protocol['maximum_increment'], *protocol['refinement_maximum_increments']]]
    return [{'steps': steps} for steps in [config['steps'], *config['refinement_steps']]]


def score_evaluation(prepared, prediction, config):
    if 'evaluation_protocol' not in config:
        return score_prediction(prepared, prediction, config['samples'])
    if prediction['status'] != 'success':
        return None
    try:
        return {channel: compare_acquisition(prepared['rows'], prediction, channel, prepared['scales'][channel])
                for channel in config['objective']['channels']}
    except (ValueError, KeyError) as exc:
        prediction['status'] = 'invalid_prediction'
        prediction['message'] = str(exc)
        return None


def predict_evaluation(prepared, mid, parameters, adapter, config, resolution=None):
    resolution = resolutions(config)[0] if resolution is None else resolution
    if 'evaluation_protocol' in config:
        prediction = adapter.replay(mid, parameters, prepared['experiment'],
            [r['axial_strain'] for r in prepared['rows']], resolution['maximum_increment'], config['timeout_seconds'])
    else:
        prediction = adapter.simulate(mid, parameters, prepared['experiment'], prepared['target'],
                                      resolution['steps'], config['timeout_seconds'])
    return prediction, score_evaluation(prepared, prediction, config)


def refinement_changes(prepared, previous, refined, config):
    if previous['status'] != 'success' or refined['status'] != 'success':
        return None
    if 'evaluation_protocol' in config:
        return {channel: compare_acquisition(previous['points'], refined, channel, prepared['scales'][channel])
                for channel in config['objective']['channels']}
    return {channel: compare([(p['axial_strain'], p[channel]) for p in previous['points']],
                             [(p['axial_strain'], p[channel]) for p in refined['points']],
                             prepared['scales'][channel], config['samples'])
            for channel in config['objective']['channels']}
