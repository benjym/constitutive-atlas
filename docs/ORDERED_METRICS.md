# Ordered curve error over axial-strain travel

The shared Python function `atlas.curve_metrics.compare_acquisition_linear`
implements method **piecewise-linear-residual-axial-travel-v1**. It compares a
completed prediction to observations in their original acquisition order. It
loads no data and invokes no material model. This is a bounded contribution to
[CAL-05](../ROADMAP.md), not a completed calibration study or scientific admission.

## Contract and use

```python
from atlas.curve_metrics import compare_acquisition_linear

rows = [{"axial_strain": 0.0, "q": 0.0},
        {"axial_strain": 0.01, "q": 10.0}]
prediction = {"status": "success", "points": [
    {"observation_index": 0, "axial_strain": 0.0, "q": 0.0},
    {"observation_index": 1, "axial_strain": 0.01, "q": 11.0}]}
result = compare_acquisition_linear(rows, prediction, "q", scale=1.0)
# rmse ≈ sqrt(1/3), mae = 0.5, max_abs = 1; scaled_mse ≈ 1/3.
```

The caller supplies the channel and a positive finite scale in its units. Every
observation must have exactly one prediction, with the original integer index
and matching axial strain. Failed, truncated, reordered or mismatched predictions
raise `ValueError`; there is no successful-prefix score. No sorting, extrapolation
or interpolation between different acquisition indices is performed. Values must
be finite real numbers; booleans are rejected. Inputs are not modified.

## Definition

Let residual `e_i = prediction_i − observation_i`, segment travel
`w_i = |strain_(i+1) − strain_i|`, and total travel `L = sum(w_i) > 0`.
Interpolate the residual linearly within each segment in acquisition order. For
endpoint residuals `a, b`, the exact segment squared-error integral is:

`w * (a² + a*b + b²) / 3`.

The segment absolute-error integral is `w * (|a| + |b|) / 2` when signs agree;
when they cross it is `w * (a² + b²) / (2*(|a| + |b|))`.
RMSE is the square root of the summed squared integrals divided by `L`; MAE is
the summed absolute integrals divided by `L`. `scaled_mse = (rmse / scale)²`.
`max_abs` covers every observed endpoint.

This integrates the **piecewise-linear residual**, not an unknown continuous
physical response. Adding redundant points on that interpolant preserves the
score within rounding. Additional curvature or a different loading path can
change it. Reversals accumulate absolute travel instead of canceling through net
strain. Uniform positive coordinate rescaling preserves the weighted errors.

Zero-travel segments contribute zero integral weight. Their endpoint errors still
contribute to `max_abs`; counts report both repeated-coordinate segments and
those with changed residual. An all-zero-travel record is rejected. This metric
cannot assess the duration of relaxation during a strain hold: it is explicitly
not physical-time weighted. A time-dependent study needs a separately declared
coordinate and metric. It also needs a declared eligible window, initialization,
channel scales, feature errors and aggregation across tests.

The implementation uses two-point Gaussian quadrature for the squared linear
residual and scaled absolute-integral arithmetic to avoid premature squares or
products overflowing. Arithmetic uses binary64; extremely small contributions
may round away. Nonrepresentable travel, residuals or final scores are rejected.
Synthetic large-value checks establish specific witnesses, not a certification
over the entire floating-point range.

## Historical results and verification

Historical development code in `paper/analysis/metrics.py` uses endpoint
trapezoidal quadrature of squared error. For residual 0→1 it gives MSE 0.5;
inserting its linear midpoint changes that to 0.375. The new method gives 1/3 in
both cases. Historical code, scores, objectives and manuscript are unchanged.
No existing calibration or evaluation automatically switches methods. Any future
study must freeze the method identity and scales before observing its results.

Run `python3 -m unittest discover -s tests -p 'test_curve_metrics.py' -v` from
the repository root. Twelve synthetic tests pass: analytic and sign-crossing
integrals, redundant sampling, reversal, holds, unit/coordinate scaling,
large/tiny contributions, failed/incomplete/order mismatch rejection, invalid
numbers and input immutability. No experimental responses, compiled builds or
parameter fits are used. [The board](../IMPLEMENTATION_PLAN.md) tracks this bounded
delivery; physical features, sensitivity and uncertainty under CAL-05 remain open.
