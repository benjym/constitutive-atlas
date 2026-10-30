# Physical-time ODE support — experimental v0.2 subset

The shared engine now implements the first part of [the temporal design](TEMPORAL_INTEGRATION.md). This is a material-update capability, not a completed timed laboratory driver or an executable Terracotta model.

## Accepted model contract

Use [model-v0.2.schema.json](../schemas/model-v0.2.schema.json), plus `atlas.model.validate` for semantic checks. v0.1 definitions and their strain-path/residual semantics remain supported unchanged.

A v0.2 model declares `formulation: {"time_dependence": "physical_time", "equation_form": "ode"}`. It supplies one `equations` expression per persistent state, with **state units per second**. The expression inputs are current state, parameters, `time` in seconds, and `strain_rate` as a symmetric Mandel tensor in 1/s. Previous-state symbols, `de`, `dt`, incremental multipliers and transient state are rejected. There is no algebraic-constraint or physical-time-residual support in this subset.

State need not start with stress. The generic timed update supports scalar/tensor states up to 24 components. This removes the stress-first restriction for physical ODEs; stress observables and the original Terracotta invariant/control contract are still to implement before connecting a physical-time model to laboratory plots.

Units are `1`, `Pa`, `s`, `K`, or `{"si": [mass, length, time, temperature]}`. Exponents may be numbers or exact rational strings such as `"1/3"`; absolute magnitude is at most 16 and reduced denominator at most 16. Values are in SI; no automatic kPa or other prefix conversion occurs. For example, Pa·s is `{"si": [1,-1,-1,0]}`, 1/s is `[0,0,-1,0]` inside the same object, and K²/Pa is `[-1,1,2,2]`. Temperature units do not assert that a mesoscopic state has the physical meaning of ordinary thermodynamic temperature.

`atlas.model.interpret(..., time=stage_time)` uses the same dimensional contract; its `increment` argument supplies strain rate for a v0.2 model. The legacy argument name remains for compatibility. Previous state is unused and may be `None` for a physical-time ODE.

## Update and numerical contract

`atlas::integrate_time` in [time.hpp](../cpp/include/atlas/time.hpp) accepts committed state, a constant strain-rate tensor, parameters, start time, duration and `TimeSettings`. `integrate_time_history` accepts a pure function mapping physical stage time to prescribed strain rate. The caller must split control discontinuities into separate advances. This callback is a C++ API; arbitrary code is not accepted from a model document or browser input.

The method is explicit midpoint with step doubling, returning the two-half-step state. Rate, time and state are evaluated at matching stages. Error is estimated by the full/two-half difference divided by three, normalized componentwise by:

```text
absolute_tolerance * declared_state_scale
  + relative_tolerance * max(abs(incoming_state), abs(candidate_state))
```

Both tolerances are positive dimensionless fractions. Default values are `1e-9` and `1e-6`, respectively. They control local temporal error, not a guaranteed global trajectory error. State-scale and time-step refinement are required when choosing settings for a scientific comparison. The minimum step limits accepted half-step duration; the maximum step limits each trial full interval, so accepted half steps are no larger. The initial trial is the requested duration, recursively partitioned by the maximum-step limit and error rejection. No dense output is implemented.

Default limits are a `1e-12` s minimum accepted step, `1e6` s maximum trial interval, 20,000 accepted substeps and recursion depth 40. Depth can be configured through the C++ settings (bounded to 50); the current C ABI fixes it to the recorded default. These defaults are engineering choices, not model-specific recommendations. This explicit method is not yet assessed as suitable for Terracotta's stiffness regimes; no BDF/DAE support is implied.

A positive, finite duration and a representably later finite endpoint are required. On success both state and clock advance to the requested endpoint. On failure both roll back to the incoming values, even if an earlier recursive half succeeded. Diagnostics retain work counts and the last accepted temporal error norm. Initial/domain checks can run without evaluating the evolution equations. Admissibility expressions and their required derived values are still evaluated; models must provide a well-defined initial domain test at zero prescribed rate.

## Native and Wasm interfaces

The additive C ABI exports are:

```text
atlas_evaluate_time(id, parameters_csv, current_csv, strain_rate_csv, time)
atlas_integrate_time(id, parameters_csv, initial_csv, strain_rate_csv,
                     start_time, duration, rtol, atol, min_step, max_step,
                     max_substeps)
```

They return JSON strings with the same storage lifetime as existing exports. The timed integration result records model/catalogue identity, inputs, method/settings, committed time/state, diagnostics and rollback message. `temporal_error_norm` is distinct from legacy residual-error diagnostics. Evaluation returns instantaneous rates, not integrated increments. Untimed entry points reject physical-time models; native CLI modes reject incompatible options rather than ignoring them.

Synthetic fixtures are deliberately generated into a separate catalogue/module. After the normal CMake build, an example is:

```sh
./build/atlas_time_solver --mode integrate-time --model test-maxwell \
  --strain-rate 0,0,0,0,0,0 --start-time 7 --duration 4 \
  --rtol 1e-10 --atol 1e-13
```

The expected first stress component is `100000 + 40000 exp(-2)` Pa and the committed time is 11 s. This is an analytical engine test, not an admitted literature model. `atlas_time_solver`, `time-fixtures.js` and its Wasm are not copied to the public website. The public model catalogue still contains five executable definitions.

## Evidence and remaining gates

[Native analytical tests](../tests/test_time.cpp) cover relaxation, the stationary-stress Maxwell creep relation, nonautonomous evolution, varying stage rates, partitioning, refinement, rejected steps, full-update rollback and invalid times/settings. The creep relation uses its analytically known strain rate; it does **not** test a numerical stress-control driver. [Python tests](../tests/test_time.py) cover dimensions, equation/version boundaries, reserved inputs and interpreter/native agreement. [Wasm tests](../tools/test_time_wasm.mjs) compare analytical values and native/Wasm success/failure results.

TIME-01/02/04/05 have an implemented ODE subset, not full milestone acceptance. Outstanding work includes source-complete Terracotta equations and units, independent review, algebraic observables, original invariant kinematics, timed mixed controls/holds, ordered schedule serialization, reference-case stiffness assessment and browser controls. TIME-03 and TIME-06 remain open. The broader roadmap, including the six-model SANISAND gate and the twenty-model research release, remains incomplete.
