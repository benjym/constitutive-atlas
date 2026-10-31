# Symmetric spectral expressions

The generic expression language supports ordered principal values and isolated-extreme projectors of a symmetric tensor in Atlas Mandel order `[xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz]`. Principal values are ordered maximum to minimum algebraically; the functions do not change the model's declared stress sign convention.

| Expression | Result | Derivative requirement |
| --- | --- | --- |
| `principal_max(A)`, `principal_mid(A)`, `principal_min(A)` | Scalar in A's units | Selected eigenvalue isolated from the other two |
| `principal_upper_sum(A)` | Sum of the two largest values, in A's units | Smallest eigenvalue isolated; largest two may repeat |
| `principal_lower_sum(A)` | Sum of the two smallest values, in A's units | Largest eigenvalue isolated; smallest two may repeat |
| `projector_max(A)`, `projector_min(A)` | Dimensionless symmetric rank-one projector | Selected extreme isolated; complementary values may repeat |
| `principal_max_value(A)`, `principal_mid_value(A)`, `principal_min_value(A)` | Value-only scalar in A's units | Repeated values allowed; no derivative supplied |

Isolation is a numerical resolution check: selected gaps must exceed `1024 * epsilon * ||A||F` in scaled arithmetic. It does not smooth a constitutive corner or establish a physical admissibility condition. The scaled cyclic Jacobi implementation uses 24 sweeps and explicit residual, orthogonality, finite-input and output-range diagnostics. Unresolved gaps and unrepresentable outputs fail explicitly.

## Value-only controls

A value-only scalar may participate in arithmetic used to construct a comparison. Its qualifier propagates through numerical functions and aliases. A comparison consumes that qualifier as primal Boolean control; a lazy `select` may then choose ordinary differentiable expressions. For example, `select(principal_max_value(A) > p, B, C)` is allowed when B and C have equal shape and units. Only the executed arm is evaluated.

A value-only number cannot enter a numerical equation, observable, scale, initialization term/state/rate or history write. Both numerical branches of a `select` must meet that rule even if one is never selected. `select(1 > 0, p, principal_max_value(A))` therefore remains qualified and is rejected at a numerical sink. Boolean arithmetic is forbidden, so a comparison cannot be converted into an untracked coefficient through multiplication.

Signed parent-increment reset guards and experimental history event guards have a stricter policy: value-only spectral query dependencies are rejected even if hidden inside an internal comparison/conditional. Located event semantics and derivatives of switching times are not provided by these helpers.

Derived expressions are eager in the existing compiler. Put a restricted projector or principal-value operation inside the appropriate lazy arm; defining it as a global derived term does not make it lazy merely because its name appears in an unselected arm. Checked failures mark a sticky model-evaluation failure or enter the existing history exception/rollback path. Zero Jet storage for value-only queries is transport only, not a mathematical derivative.

## Evidence and remaining integration gate

The [standalone primitive study](../catalogue/investigations/symmetric-spectral-primitive-v1/RESULTS.md) verified double and all 38 Jet directions against independent exact-stored-Mandel references on native and Wasm. This production helper retains those exact numerical source bytes.

The [integration source packet](reviews/spectral-dsl-integration-v1/README.md) retains the reviewed candidate, independent primal comparisons, qualifier/consumer checks, an original event-guard bypass witness and its fix. Permanent source regressions are in `tests/test_spectral_dsl.py`. Source typing and primitive verification do not yet prove generated model/history execution, complete AD propagation, failure rollback or a Mohr–Coulomb return algorithm. A separate prospectively frozen generated-context study is required before claiming those properties. No new model or scientific admission follows from this API installation.
