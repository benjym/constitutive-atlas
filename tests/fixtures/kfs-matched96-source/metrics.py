"""Monotonic development metrics with fixed physical scales and no extrapolation."""
from bisect import bisect_right
import math


def monotonic_pairs(rows, xkey, ykey, maximum):
    pairs = []
    duplicates = 0
    for row in rows:
        x, y = row[xkey], row[ykey]
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError('nonfinite channel')
        if pairs and x < pairs[-1][0]:
            raise ValueError('decreasing loading coordinate requires another path adapter')
        if x < 0:
            raise ValueError('negative loading coordinate unsupported by compression pilot')
        if x > maximum:
            break
        if pairs and x == pairs[-1][0]:
            pairs[-1] = (x, y)
            duplicates += 1
        else:
            pairs.append((x, y))
    if len(pairs) < 2:
        raise ValueError('insufficient monotonic observations')
    return pairs, duplicates


def interpolate(pairs, x):
    if x < pairs[0][0] or x > pairs[-1][0]:
        raise ValueError('extrapolation forbidden')
    index = bisect_right([p[0] for p in pairs], x)
    if index == len(pairs):
        return pairs[-1][1]
    a, b = pairs[max(0, index - 1)], pairs[index]
    return a[1] + (b[1] - a[1]) * (x - a[0]) / (b[0] - a[0])


def compare(measured, predicted, scale, samples=101):
    if scale <= 0 or not math.isfinite(scale) or samples < 2:
        raise ValueError('positive scale and at least two samples required')
    for pairs in (measured, predicted):
        if len(pairs) < 2 or any(not math.isfinite(v) for pair in pairs for v in pair):
            raise ValueError('at least two finite curve points required')
        if any(b[0] <= a[0] for a, b in zip(pairs, pairs[1:])):
            raise ValueError('curve coordinate must increase strictly')
    # The prediction must cover the entire declared measured window.
    # Truncation cannot improve a failed or incomplete model's score.
    lo, hi = measured[0][0], measured[-1][0]
    if hi <= lo or predicted[0][0] > lo or predicted[-1][0] < hi:
        raise ValueError('prediction does not cover evaluation window')
    grid = [lo + (hi - lo) * i / (samples - 1) for i in range(samples)]
    grid[-1] = hi
    residual = [interpolate(predicted, x) - interpolate(measured, x) for x in grid]
    mse = sum(r*r for r in residual) / samples
    return {'rmse': math.sqrt(mse), 'mae': sum(abs(r) for r in residual)/samples,
            'scaled_mse': mse / scale**2, 'scale': scale,
            'grid': {'kind': 'uniform_axial_strain', 'start': lo, 'end': hi, 'samples': samples}}


def compare_acquisition(rows, prediction, channel, scale):
    """Endpoint-error quadrature over absolute axial-strain travel, in row order.

    Repeated coordinates have zero travel weight. This is not a time-weighted
    metric and is not interchangeable with the monotonic resampling objective.
    """
    if prediction['status'] != 'success' or len(prediction['points']) != len(rows):
        raise ValueError('complete successful acquisition replay required')
    if len(rows) < 2 or not math.isfinite(scale) or scale <= 0:
        raise ValueError('at least two observations and positive finite scale required')
    coordinates, errors = [], []
    for index, (row, point) in enumerate(zip(rows, prediction['points'])):
        if point['observation_index'] != index or point['axial_strain'] != row['axial_strain']:
            raise ValueError('replay must preserve acquisition coordinates and indices')
        x, observed, predicted = row['axial_strain'], row[channel], point[channel]
        if not all(math.isfinite(v) for v in (x, observed, predicted)):
            raise ValueError('finite acquisition channels required')
        coordinates.append(x)
        errors.append(predicted-observed)
    weights = [abs(b-a) for a, b in zip(coordinates, coordinates[1:])]
    travel = sum(weights)
    if travel <= 0:
        raise ValueError('positive axial-strain travel required')
    mse = sum(w*(a*a+b*b)/2 for w, a, b in zip(weights, errors, errors[1:]))/travel
    mae = sum(w*(abs(a)+abs(b))/2 for w, a, b in zip(weights, errors, errors[1:]))/travel
    return {'rmse': math.sqrt(mse), 'mae': mae, 'scaled_mse': mse/scale**2,
            'scale': scale, 'weighting': 'trapezoidal endpoint error over absolute axial-strain travel',
            'total_absolute_axial_strain_travel': travel, 'observations': len(rows),
            'zero_travel_segments': sum(w == 0 for w in weights)}
