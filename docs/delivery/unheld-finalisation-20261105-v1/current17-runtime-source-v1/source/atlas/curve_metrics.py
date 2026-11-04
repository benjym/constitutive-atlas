"""Ordered curve comparison, independent of model execution and data loading."""
import math
from numbers import Real

METHOD = "piecewise-linear-residual-axial-travel-v1"


def _finite(value, label):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{label} must be a finite real number")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{label} must be representable and finite") from exc
    if not math.isfinite(value):
        raise ValueError(f"{label} must be finite")
    return value


def _weighted_average_term(weight, value, total):
    """Evaluate weight * value / total without premature product overflow."""
    if weight == 0 or value == 0:
        return 0.0
    mw, ew = math.frexp(weight)
    mv, ev = math.frexp(value)
    mt, et = math.frexp(total)
    return math.ldexp(mw * mv / mt, ew + ev - et)


def compare_acquisition_linear(rows, prediction, channel, scale):
    """Integrate a linearly interpolated residual in original acquisition order.

    Coordinates must match exactly and every observation must be predicted.
    Absolute axial-strain travel weights segments; holds have zero weight.
    This is a new metric identity, not a replacement for historical scores.
    Raises ValueError for invalid inputs or nonrepresentable results.
    """
    scale = _finite(scale, "scale")
    if scale <= 0:
        raise ValueError("scale must be positive")
    if not isinstance(channel, str) or not channel or channel in {
        "axial_strain", "observation_index"
    }:
        raise ValueError("channel must name a response quantity")
    if not isinstance(rows, (list, tuple)) or len(rows) < 2:
        raise ValueError("at least two observations are required")
    if not isinstance(prediction, dict) or prediction.get("status") != "success":
        raise ValueError("prediction must have successful completion status")
    points = prediction.get("points")
    if not isinstance(points, (list, tuple)) or len(points) != len(rows):
        raise ValueError("prediction must cover every observation exactly")
    coordinates, errors = [], []
    for index, (row, point) in enumerate(zip(rows, points)):
        if not isinstance(row, dict) or not isinstance(point, dict):
            raise ValueError("observations and predictions must be records")
        oi = point.get("observation_index")
        if type(oi) is not int or oi != index:
            raise ValueError("prediction observation_index must preserve acquisition order")
        x = _finite(row.get("axial_strain"), "measured axial_strain")
        px = _finite(point.get("axial_strain"), "predicted axial_strain")
        if point["axial_strain"] != row["axial_strain"] or px != x:
            raise ValueError("prediction coordinates must match observations exactly")
        observed = _finite(row.get(channel), "observed channel")
        predicted = _finite(point.get(channel), "predicted channel")
        errors.append(_finite(predicted - observed, "residual"))
        coordinates.append(x)
    weights = [abs(b - a) for a, b in zip(coordinates, coordinates[1:])]
    if not all(math.isfinite(w) for w in weights):
        raise ValueError("segment travel must be finite")
    try:
        travel = math.fsum(weights)
        if not math.isfinite(travel) or travel <= 0:
            raise ValueError("total absolute axial-strain travel must be positive and finite")
        # Two-point Gauss quadrature integrates a squared linear residual exactly.
        # Square roots before ratios retain contributions from very short segments.
        t = 0.5 - 1.0 / (2.0 * math.sqrt(3.0))
        rms_terms, absolute_terms = [], []
        for w, a, b in zip(weights, errors, errors[1:]):
            if w == 0:
                continue
            factor = (math.sqrt(w) / math.sqrt(travel)) / math.sqrt(2.0)
            rms_terms.extend((factor * ((1-t)*a + t*b),
                              factor * (t*a + (1-t)*b)))
            aa, bb = abs(a), abs(b)
            if (a < 0 < b) or (b < 0 < a):
                magnitude = max(aa, bb)
                u, v = aa / magnitude, bb / magnitude
                average_absolute = magnitude * ((u*u + v*v) / (2*(u+v)))
            else:
                average_absolute = 0.5*aa + 0.5*bb
            absolute_terms.append(_weighted_average_term(w, average_absolute, travel))
        rmse = math.hypot(*rms_terms)
        mae = math.fsum(absolute_terms)
        scaled_mse = (rmse / scale)**2
        if not all(math.isfinite(v) for v in (rmse, mae, scaled_mse)):
            raise ValueError("metric result is not representable as a finite number")
    except OverflowError as exc:
        raise ValueError("metric result or total travel is not representable") from exc
    return {
        "method": METHOD,
        "coordinate": "axial_strain",
        "physical_time_weighted": False,
        "rmse": rmse,
        "mae": mae,
        "max_abs": max(abs(e) for e in errors),
        "scaled_mse": scaled_mse,
        "scale": scale,
        "observations": len(rows),
        "total_absolute_axial_strain_travel": travel,
        "zero_travel_segments": sum(w == 0 for w in weights),
        "zero_travel_residual_change_segments": sum(
            w == 0 and a != b for w, a, b in zip(weights, errors, errors[1:])
        ),
    }
