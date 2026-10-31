# Architecture and conventions

`models/*.json` → structural checks → typed/dimensioned expression AST → Python reference evaluation + generated templated C++ → shared integration engine → native CLI / Emscripten Worker. Catalogue pages, SQLite and source displays derive from the definitions. No model ID controls constitutive mathematics inside the engine.

## Representation v0.1

JSON is the canonical JSON-compatible subset of YAML. Arbitrary YAML is not parsed in this first implementation. `schemas/model.schema.json` defines structure; `atlas.model.validate` adds semantic checks. SI dimension vectors use rational mass/length/time exponents, with `1` and `Pa` as the v0.1 declaration units. The separate experimental [physical-time ODE subset](TIME_ODE_API.md) adds v0.2 definitions with time/temperature dimensions and bounded rational SI exponent declarations. State types are scalar or symmetric second-order tensor. General vector/fourth-order types, algebraic observables, timed mixed-control schedules and constitutive events remain outstanding. The [temporal integration design draft](TEMPORAL_INTEGRATION.md) specifies the proposed extension, migration rules and verification gates; its broader schedule/constraint proposal is not yet an accepted runtime capability.

Each model declares parameters, ordered state, ordered derived expressions, one equation per state, domain comparisons, and `residual` or `rate` integration. State scales must be positive parameter-only expressions with matching dimensions. `sigma` must be the first six state components in v0.1; other state is model-declared. Transient plastic multipliers are reset each increment and marked `multiplier` to request the generic elastic predictor before complementarity correction. They are incremental solve variables, not accumulated plastic strain.

The expression language supports finite literals, declared names, `+ - * / **`, `sqrt exp log sin cos abs min max`, `trace dev dot norm cube_trace`, scalar comparisons, and lazy `select(condition, yes, no)`. Tensor products must be explicit. No `eval`, attribute access, indexing, imports or native snippets. Bounds and cross-parameter conditions are checked at runtime; source annotations do not supply executable instructions.

Stress/strain compression is positive. Stress is effective stress, in Pa; strain is dimensionless. Mandel order is `[xx, yy, zz, sqrt(2)xy, sqrt(2)yz, sqrt(2)xz]`. Scalar `q` is nonnegative; laboratory `q_signed = sigma_xx-(sigma_yy+sigma_zz)/2` preserves extension. Angles are radians. Kinematics are infinitesimal and spin is zero. Finite-rotation objectivity is not implemented; fixed-frame rotational covariance is tested.

## Algorithms

Implicit residuals use forward-mode AD, state/residual scaling, pivoted dense linear solves, line search and recursive substepping. A declared multiplier invokes a zero-plastic-increment predictor followed by the full semismooth complementarity equations. The current `rate` equations return state increments for `de` over a normalized strain path, not derivatives per second. They use explicit midpoint with step doubling and an endpoint quadrature defect on each candidate half step; the accepted solution is two half steps. The endpoint check addresses the [IGS hidden-crossing counterexample](models/hypoplastic-sand-igs97.md#endpoint-defect-correction-and-v2-evidence), where both midpoint estimates can agree while missing a loading transition. It supplements the error heuristic without guaranteeing detection of every nonsmooth event. Relative-to-declared-scale local error tolerance is `1e-6`; implicit residual tolerance is `2e-10`. Recursion depth is limited to 14 and accepted substeps to 20,000 per increment. Bounds fail explicitly; values are not silently clipped except the documented IGS mobilisation cap and DP apex direction regularization.

`integrate` is transactional: failure returns the input state. Laboratory mixed-control residuals evaluate each trial from the same committed state. Tangents in the control solver are finite-difference derivatives of the transactional update; constitutive residual Jacobians use AD. The initial implementation does not expose a consistent algorithmic material tangent through its public API. C++ uses the standard library only (a deliberate portability simplification from the plan's initial Eigen choice).

Laboratory protocols: `0` oedometer, `1` drained triaxial fixed radial effective stress, `2` undrained axial strain control, `3` undrained signed-q stress control, `4` isotropic equal normal-strain increments. For protocol 4 the `target` is strain in each normal direction, not volumetric strain. Initial stress must be axisymmetric and shear-free. Stress targets are Pa, other targets dimensionless. Histories are linear ramps or sine cycles. The stress-control initial signed q is retained and the target is its change. Undrained volume is constrained to zero, assuming incompressible constituents; `delta_u` assumes fixed radial total stress. No pore pressure is reported as a defined physical result for drained paths.

## Interfaces

The generated model catalogue describes state and parameter layouts. Native `--list` prints model IDs. The CLI accepts `--mode run|integrate|evaluate`, `--model`, positional-layout numeric CSV for `--parameters`, `--initial`, `--current`, `--strain`, and laboratory controls. `atlas.cli run` accepts a JSON specification and writes a JSON result. `atlas_evaluate`, `atlas_integrate`, and `atlas_run` are C ABI exports; their returned string storage remains valid only until the next call. Each Worker owns an engine instance.

Run output includes status, last-committed samples, diagnostics, effective stress, signed and unsigned q, pore-pressure change where defined, all state, inputs and catalogue hash. Python compiler output order is deterministic. Browser imports require the matching catalogue hash, use complete input arrays, and enforce the same basic limits. Cancellation terminates the Worker; a new run creates a fresh instance.

## Data and evidence

Raw archives are ignored and immutable. `atlas.data` recognizes only reviewed TMD/TMU layouts, reads zip members without extracting paths, records hashes/headers and converts units explicitly. TMD void ratio remains dimensionless despite a misleading percent header. TMU initial e is missing and must be supplied with a source. Generic cyclic/kaolin ingestion is not yet implemented.

`benchmarks/kfs-drained.json` is a published-parameter **transfer demonstration**, not calibration or held-out validation. It compares only the early monotonic window, with declared duplicate-strain handling and a uniform interpolation grid. The complete measured path is not replayed. SQLite is a generated read model; definitions remain authoritative.

## Known capability gate: SANISAND

SANISAND-2004 needs source-complete equations and reversal-dependent memory updates. The current DSL cannot safely encode those events. Do not publish a simplified substitute using the SANISAND ID. Extend the general state/event representation, define deterministic event timing/rollback, add source-specific initialisation and independent reference tests, and only then admit it. The six-model proof is incomplete until this gate passes.

## Experimental physical-time update

[The ODE API](TIME_ODE_API.md) documents v0.2 state/second equations, stage-time/rate inputs, adaptive midpoint error control and transactional state/clock rollback. Scalar ODE state need not start with stress. Native/Wasm analytical fixtures are built separately from the five public models. Physical-time residuals, DAEs, stress observables and timed laboratory schedules remain unsupported; Terracotta is still a candidate.
