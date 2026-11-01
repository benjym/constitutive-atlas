# Two-component power creep — approved bounded scope

The exact [v0.3 definition](../../models/research/power-creep/power-creep-itasca900-both-active-ode.json)
is accepted by explicit user instruction after [independent agent review](../ingestion/power-creep-itasca900/review-v1/README.md).
The [approval registry](../../catalogue/approved-models.json) binds its immutable
bytes; embedded historical `draft` metadata remains intact. This is bounded
project acceptance, not experimental validation or a human scientific signature.

The Itasca9.0 manual's both-components-active Norton law adds
`f = b1*(q/p_ref)^n1 + b2*(q/p_ref)^n2`, with deviatoric creep rate
`Dc = 3*f*s/(2*q)` and elastic volume. At `q=0` the vector continuous limit is
used; `n_i>=1` is a declared project restriction. Source Eq2's deviator projection
is retained instead of inconsistent printed Eq7. Compression-positive Mandel
stresses use Pa, physical time uses seconds. The six stress components are the
persistent state. Explicit initial stress and loading/time history are required.
Scope is dry uncoupled zero-pore-pressure, small strain, fixed frame and zero spin.

[Source inventory](../ingestion/power-creep-itasca900/README.md),
[execution evidence](../ingestion/power-creep-itasca900/execution-v1/README.md),
[history verification](../ingestion/power-creep-itasca900/verification-v1/README.md)
and [review clarifications](../ingestion/power-creep-itasca900/review-v1/README.md)
remain distinct. Refined native and Wasm requests pass27/27 each, with nine
independent source-rate checks and29 additional history/invariance/dissipation
checks. Earlier loose-setting failures remain retained. See exact policies and
settings; arbitrary tolerances and full parameter ranges are not qualified.

The website offers a dedicated physical-time creep/relaxation laboratory, linked
from the main navigation and catalogue. It uses a separate generated engine and
exact model identity, outside the strain-path model selector. Illustrative
parameters are not calibrated. Public evidence distinguishes user acceptance,
agent review and numerical qualification from physical validation.

Thresholded mechanisms/equality events, vendor finite-step equivalence, finite
rotation, saturated coupling, arbitrary adaptive restart recovery, FE/MPM hosts
and calibrated predictive behavior are not claimed.
