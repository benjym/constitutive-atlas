"""Complete whole-test calibration objective; no data loading or model execution."""
import math
import re
from .curve_metrics import METHOD, compare_acquisition_linear
from .study_allocation import require, validate_allocation
from .study_parameters import number

UNITS = {"q": "Pa", "p": "Pa", "volumetric_strain": "1"}


def validate_objective(policy, allocation, reservations, *, allocation_sha256,
                       reservation_sha256):
    """Callers compute digests from the exact bytes decoded, before response access."""
    validate_allocation(allocation, reservations, policy_sha256=reservation_sha256)
    keys = {"schema_version", "kind", "id", "allocation_sha256", "package",
            "method", "test_aggregation", "failure_policy", "channels"}
    require(isinstance(policy, dict) and set(policy) == keys, "unsupported objective fields")
    require(policy['schema_version'] == '0.1' and policy['kind'] == 'study-objective',
            "unsupported objective version/kind")
    require(isinstance(policy['id'], str) and re.fullmatch(r'[a-z][a-z0-9-]*', policy['id']) is not None,
            "invalid objective ID")
    digest = policy['allocation_sha256']
    require(isinstance(digest, str) and re.fullmatch(r'[a-f0-9]{64}', digest) is not None
            and digest == allocation_sha256, "allocation identity mismatch")
    package = policy['package']
    require(isinstance(package, str) and package in allocation['calibration_packages'],
            "objective must select one calibration package")
    require(policy['method'] == METHOD and policy['test_aggregation'] == 'equal_whole_test'
            and policy['failure_policy'] == 'reject_entire_candidate',
            "unsupported metric, aggregation or failure policy")
    channels = policy['channels']
    require(isinstance(channels, dict) and bool(channels), "objective channels required")
    weights = []
    for name, settings in channels.items():
        require(name in UNITS, "unsupported objective channel")
        require(isinstance(settings, dict) and set(settings) == {'unit', 'scale', 'weight'},
                "exact unit, scale and weight required")
        require(settings['unit'] == UNITS[name], "channel unit mismatch; no implicit conversion")
        for key in ('scale', 'weight'):
            require(number(settings[key], name + ' ' + key) > 0, "positive scale/weight required")
        weights.append(settings['weight'])
    try:
        total = math.fsum(weights)
    except OverflowError as exc:
        raise ValueError("channel weight sum must be finite") from exc
    require(math.isfinite(total), "channel weight sum must be finite")
    normalized = [w / total for w in weights]
    require(all(w > 0 for w in normalized), "channel weight underflow")
    return {'test_ids': list(allocation['calibration_packages'][package]),
            'channel_weights': dict(zip(channels, normalized))}


def score_objective(policy, allocation, reservations, observations, predictions, *,
                    allocation_sha256, reservation_sha256):
    """Reject any invalid/failed test; never return a successful-prefix objective.

    Supplied bundles contain explicit units and ordered rows/points. This function
    does not prove that caller data or predictions match a source/model revision.
    """
    plan = validate_objective(policy, allocation, reservations,
                              allocation_sha256=allocation_sha256,
                              reservation_sha256=reservation_sha256)
    ids = plan['test_ids']
    require(isinstance(observations, dict) and set(observations) == set(ids),
            "observations must cover exactly the calibration package")
    require(isinstance(predictions, dict) and set(predictions) == set(ids),
            "predictions must cover exactly the calibration package")
    units = {name: settings['unit'] for name, settings in policy['channels'].items()}
    tests = []
    for tid in ids:
        obs, pred = observations[tid], predictions[tid]
        require(isinstance(obs, dict) and set(obs) == {'units', 'rows'}
                and obs['units'] == units, "observation bundle units/fields mismatch: " + tid)
        require(isinstance(pred, dict) and set(pred) == {'units', 'status', 'points'}
                and pred['units'] == units, "prediction bundle units/fields mismatch: " + tid)
        metrics = {}
        for channel, settings in policy['channels'].items():
            try:
                metrics[channel] = compare_acquisition_linear(obs['rows'], pred, channel, settings['scale'])
            except ValueError as exc:
                raise ValueError(tid + '/' + channel + ': ' + str(exc)) from exc
        value = math.fsum(plan['channel_weights'][c] * m['scaled_mse'] for c, m in metrics.items())
        require(math.isfinite(value), "nonfinite per-test objective")
        tests.append({'id': tid, 'scaled_mse': value, 'channels': metrics})
    objective = math.fsum(test['scaled_mse'] / len(tests) for test in tests)
    require(math.isfinite(objective), "nonfinite aggregate objective")
    return {'kind': 'study-objective-result', 'id': policy['id'], 'status': 'success',
            'allocation_sha256': allocation_sha256, 'package': policy['package'],
            'method': METHOD, 'test_aggregation': policy['test_aggregation'],
            'failure_policy': policy['failure_policy'], 'channel_weights': plan['channel_weights'],
            'objective': objective, 'tests': tests, 'scientific_admission': False}
