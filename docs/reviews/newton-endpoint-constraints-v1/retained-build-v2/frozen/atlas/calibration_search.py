"""Serial bounded coordinate search scored on complete whole-test predictions."""
import copy
import hashlib
import json
import math
import re

from .study_allocation import require
from .study_objective import score_objective, validate_objective
from .study_parameters import number

METHOD = 'bounded-coordinate-poll-v1'


class PredictionFailure(ValueError):
    """An expected model/solver failure; reject this entire candidate, without penalty."""


def validate_search(spec):
    """Validate explicit search settings; this is not model-domain admission."""
    keys = {'id', 'method', 'parameters', 'fitted', 'max_evaluations',
            'initial_step', 'minimum_step'}
    require(isinstance(spec, dict) and set(spec) == keys, 'exact search fields required')
    require(isinstance(spec['id'], str) and
            re.fullmatch(r'[a-z][a-z0-9-]*', spec['id']) is not None, 'invalid search ID')
    require(spec['method'] == METHOD, 'unsupported search method')
    base = spec['parameters']
    require(isinstance(base, dict) and bool(base), 'complete parameter vector required')
    for name, value in base.items():
        require(isinstance(name, str) and bool(name), 'parameter names must be strings')
        number(value, name)
    fit = spec['fitted']
    require(isinstance(fit, list) and bool(fit), 'ordered fitted parameters required')
    seen = set()
    axes = []
    for item in fit:
        require(isinstance(item, dict) and set(item) == {'name', 'bounds', 'transform'},
                'exact fitted name/bounds/transform required')
        name = item['name']
        require(isinstance(name, str) and name in base and name not in seen,
                'unknown or duplicate fitted parameter')
        seen.add(name)
        bounds = item['bounds']
        require(isinstance(bounds, list) and len(bounds) == 2, 'two search bounds required')
        lo, hi = [number(v, name + ' bound') for v in bounds]
        require(lo < hi and lo <= base[name] <= hi, 'seed must lie in strict ordered bounds')
        transform = item['transform']
        require(transform in ('linear', 'log'), 'unsupported search transform')
        require(transform != 'log' or lo > 0, 'log bounds must be positive')
        a, b = (math.log(lo), math.log(hi)) if transform == 'log' else (lo, hi)
        span = b - a
        require(math.isfinite(span) and span > 0, 'transformed span is not representable')
        seed = math.log(base[name]) if transform == 'log' else base[name]
        axes.append((name, lo, hi, transform, a, b, (seed-a)/span))
    budget = spec['max_evaluations']
    require(type(budget) is int and 1 <= budget <= 10000,
            'candidate budget must be an integer in 1..10000')
    step = number(spec['initial_step'], 'initial_step')
    minimum = number(spec['minimum_step'], 'minimum_step')
    require(0 < minimum <= step <= 1, 'require 0 < minimum_step <= initial_step <= 1')
    return axes


def calibrate(spec, predict, objective, allocation, reservations, observations, *,
              allocation_sha256, reservation_sha256, on_candidate=None):
    """Poll transformed-box neighbours serially; retain every attempted evaluation.

    predict receives a fresh complete parameter dict and must return predictions
    for exactly the objective's calibration package. It may raise PredictionFailure
    for an expected failure. Other Exceptions are recorded and stop the search.
    on_candidate receives a detached receipt before any next prediction call;
    sink exceptions propagate so durable-recording failure never goes unnoticed.
    No model/data files, processes, clocks, random generators or evaluation data
    are opened by this routine. Digests must describe the caller's decoded bytes.
    """
    spec, objective, allocation, reservations, observations = copy.deepcopy(
        (spec, objective, allocation, reservations, observations))
    axes = validate_search(spec)
    plan = validate_objective(objective, allocation, reservations,
                              allocation_sha256=allocation_sha256,
                              reservation_sha256=reservation_sha256)
    require(callable(predict), 'prediction callback required')
    require(on_candidate is None or callable(on_candidate), 'candidate sink must be callable')
    require(isinstance(observations, dict) and set(observations) == set(plan['test_ids']),
            'observations must cover exactly the calibration package')
    # Reuse the metric contract to preflight observation shape/units/travel before
    # invoking a model. Self-comparison is only data validation, never a prediction.
    identity = {}
    for tid, obs in observations.items():
        require(isinstance(obs, dict) and set(obs) == {'units', 'rows'} and
                isinstance(obs['rows'], list) and all(isinstance(r, dict) for r in obs['rows']),
                'observation bundle must contain units and row records')
        identity[tid] = {'units': obs['units'], 'status': 'success',
                         'points': [dict(r, observation_index=i) for i, r in enumerate(obs['rows'])]}
    kwargs = dict(allocation_sha256=allocation_sha256, reservation_sha256=reservation_sha256)
    score_objective(objective, allocation, reservations, observations, identity, **kwargs)
    observation_json = json.dumps(observations, sort_keys=True, separators=(',', ':'), allow_nan=False)
    receipts, seen = [], set()
    best = None
    center = [axis[6] for axis in axes]
    step = spec['initial_step']
    fatal = False

    def evaluate(parameters):
        nonlocal best, fatal
        key = tuple(parameters[axis[0]] for axis in axes)
        if key in seen:
            return None
        seen.add(key)
        receipt = {'sequence': len(receipts), 'parameters': copy.deepcopy(parameters),
                   'status': 'rejected', 'objective': None, 'error': None, 'score': None}
        try:
            predictions = predict(copy.deepcopy(parameters))
        except PredictionFailure as exc:
            receipt['error'] = str(exc) or type(exc).__name__
        except Exception as exc:
            receipt.update(status='error', error=type(exc).__name__ + ': ' + str(exc))
            fatal = True
        else:
            try:
                score = score_objective(objective, allocation, reservations, observations,
                                        predictions, **kwargs)
            except (ValueError, OverflowError, TypeError, KeyError) as exc:
                receipt['error'] = type(exc).__name__ + ': ' + str(exc)
            else:
                receipt.update(status='success', objective=score['objective'], score=score)
        receipts.append(receipt)
        if on_candidate is not None:
            on_candidate(copy.deepcopy(receipt))
        if receipt['status'] == 'success' and (best is None or receipt['objective'] < best['objective']):
            best = receipt
        return receipt

    def parameters_at(point):
        values = copy.deepcopy(spec['parameters'])
        for z, (name, lo, hi, transform, a, b, _) in zip(point, axes):
            if z <= 0:
                value = lo
            elif z >= 1:
                value = hi
            else:
                v = (1-z)*a + z*b
                value = math.exp(v) if transform == 'log' else v
                value = min(hi, max(lo, value))
            values[name] = value
        return values

    evaluate(spec['parameters'])  # Preserve the seed's original binary64 values.
    stop = 'evaluation_budget'
    while not fatal and len(receipts) < spec['max_evaluations']:
        prior_best = best
        selected = center
        for j in range(len(axes)):
            for sign in (-1, 1):
                if fatal or len(receipts) >= spec['max_evaluations']:
                    break
                point = center.copy()
                point[j] = min(1., max(0., center[j] + sign*step))
                before = best
                evaluate(parameters_at(point))
                if best is not before:
                    selected = point
            if fatal:
                break
        if best is not prior_best:
            center = selected
        elif step <= spec['minimum_step']:
            stop = 'minimum_step'
            break
        else:
            # Halving is fixed by the method identity, with no tolerance tuning.
            step = max(spec['minimum_step'], step / 2)
    if fatal:
        stop = 'evaluator_error'
    elif len(receipts) >= spec['max_evaluations']:
        stop = 'evaluation_budget'
    return {'kind': 'calibration-search-result', 'id': spec['id'], 'method': METHOD,
            'status': 'error' if fatal else ('success' if best is not None else 'no_feasible_candidate'),
            'stop_reason': stop, 'evaluations': len(receipts), 'final_step': step,
            'configuration': spec, 'objective_policy': objective,
            'allocation_sha256': allocation_sha256, 'reservation_sha256': reservation_sha256,
            'observation_values_sha256': hashlib.sha256(observation_json.encode()).hexdigest(),
            'best': copy.deepcopy(best), 'candidates': receipts, 'scientific_admission': False}
