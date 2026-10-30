# Experimental ordered incremental replay

`experimental-recorded-path-0.1` adds a [JSON contract](../schemas/recorded-path.schema.json), [Python validation](../atlas/recorded.py) and [C++ driver](../cpp/include/atlas/recorded.hpp) for recorded paths. It advances NUM-04 with ordered reversals, linear mixed constraints and committed-history replay. The typed C++ driver and experimental native C ABI/CLI consume this contract. The Wasm runtime and browser also consume it through the same C entry point; the benchmark importer remains separate. Existing ramp/sinusoid interfaces remain separate.

## Contract and units

A path has six fixed linear control rows and 2–5001 ordered knots. Each row declares `kind: strain|stress` and six dimensionless coefficients acting on orthonormal Mandel components `[xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz]`. Every knot supplies six **absolute projection targets**. A strain row constrains `coefficients:accumulated_strain`; a stress row constrains `coefficients:effective_stress`. Strain targets are dimensionless, stress targets are Pa. No row combines stress and strain into a dimensionally mixed equation.

Rows can specify individual components, volume strain, signed deviatoric stress or oblique normal/shear combinations. For example, a strain row `[1,1,1,0,0,0]` fixes volume strain; a stress row `[1,-.5,-.5,0,0,0]` fixes signed axisymmetric q. Six independent strain rows impose general tensor strain. Prescribing axial strain, two radial stresses and three zero shear strains gives a drained triaxial path. See [the example](../protocols/recorded-drained-reversal.json).

`coordinate` declares a nonempty label, unit `1` and meaning `path_order`. Knot coordinates must be finite and strictly increase **in supplied order**. They may start below zero or have irregular gaps. The driver never sorts by strain, deduplicates targets, fits a sine or infers a physical loading speed. Reparameterizing coordinates leaves the constitutive result unchanged. These are not timestamps: physical-time models must use the separate timed API. Repeated strain/stress targets at different coordinates remain separate output observations; they do not represent elapsed-time creep or relaxation.

`initial_strain` is a six-component accumulated laboratory strain origin, independent of constitutive history. Initial stress and all other model states/parameters are separate C++ arguments. The first knot must match the supplied stress/strain within the declared control tolerance. There is no hidden consolidation or preparation. Source-specific state initialization remains the caller's responsibility.

## Endpoint integration policy

Each subsequent knot defines one **caller increment**. The driver solves for a total strain increment whose accepted material update meets the six endpoint targets. The material integrator follows a straight strain-increment direction through its own substeps. Stress constraints apply at caller endpoints; constant or linearly interpolated stress between those endpoints is not guaranteed. There is no resampling/interpolation between the supplied records in this version. Adding caller knots is an explicit change to the numerical path, and can change parent-reset events as well as accuracy. A continuous-control or experimental claim needs its own path-density/refinement study.

Control rows stay fixed for the path. Mode changes, automatic knot insertion, event location, arbitrary coupled stress/strain equations, finite rotations and physical-time evolution are outside this contract. No full recorded Wichtmann benchmark or controlled calibration result is claimed.

## Root solve and transactions

`atlas::replay_recorded(model, initial, parameters, path, settings)` accepts typed `RecordedPath`/`RecordedSettings` values and returns a `RecordedResult`. The Python validator checks the document and returns it unchanged. The C++ driver repeats numerical/capability validation; the model must be untimed with six leading `sigma` components. All-strain rows must have numerical rank six. Mixed-control solvability depends on the material response, so document validation does not certify it.

Rows and their targets are temporarily divided by the largest coefficient magnitude in that row; inputs stay unchanged. Strain residuals use unit scale. Stress residuals use a **fixed** scale: the maximum of 1 Pa, the six initial stress magnitudes and the six declared stress state scales. Control convergence is the maximum absolute normalized residual. Defaults are `1e-10` control tolerance, 30 Newton iterations, 10 backtracks, 20,000 material trials for the whole path, and `1e-7` finite-difference step. Settings reject nonfinite/out-of-range values. These numerical choices are not source-prescribed material constants.

All-strain paths solve the linear strain constraints and call the material integrator once per changed record. Mixed paths first solve the prescribed strain projections by rectangular pivot elimination. The remaining increments lie in their nullspace. Newton directions, finite-difference probes and line-search candidates use that parameterization, so stress-root iterations preserve the known strain constraints. Numerical rank checks use a `1e-14` pivot threshold after row normalization; they are conditioning guards, not exact symbolic rank decisions.

Stress-root derivatives use the existing complete-update tangent with accepted partition/branches fixed. If unavailable, numerical one-sided probes use the same immutable parent along free directions; a failed positive probe is retried negatively. Free directions have maximum component magnitude one, and probe size is `finite_difference_step*max(1,abs(free_coordinate))`. These probes are numerical root aids and do not establish a unique constitutive derivative at a nonsmooth point. Already-converged endpoints are accepted before requiring derivatives; a valid root need not have a nonsingular tangent. The driver makes no uniqueness claim for redundant/nonlinear mixed constraints. If a Newton correction is needed and its system is singular, the knot fails explicitly.

Every material trial starts from the preceding committed knot. Each trial independently selects any parent-increment resets; rejected guesses never accumulate state. A **bit-preserving observation bypass applies only to identical consecutive target arrays** whose current residual meets tolerance. A distinct tiny prescribed strain still executes a material update. Successful final Newton corrections are accepted even on the last permitted iteration/material trial.

Failure retains the accepted prefix, exact last committed state/strain, failed knot index and reason. Invalid specifications are rejected before execution. Per-point material diagnostics describe only the accepted update. `material_trials`, `attempted_substeps` and `finite_difference_probes` separately account for discarded work across the path; attempted substeps include accepted internal work in failed trials. `last_control_error`/`last_trial_increment` diagnose the latest mixed-root trial and are not committed state. The material integration settings still bound each call; the trial cap is not a wall-clock or total arithmetic-work guarantee.

Restart by passing the saved committed state and accumulated strain, retaining the same controls/parameters and using that saved knot as the first knot of the remaining path. Do not reconstruct the state from plotted stress alone.

## Verification and reproduction

The [evidence manifest](../catalogue/investigations/recorded-path-v1/manifest.json) pins sources, toolchain, outputs and the initial failed IGS investigation. The first full-unknown solve incorrectly attenuated prescribed strain while line searching; it stalled on IGS drained loading. The reduced solve resolves that case at the original tolerance. A separate read-only agent supplied the analytical elasticity cases and reviewed iteration/no-op/derivative semantics; this is bounded AI verification, not independent scientific review.

The public fixture checks analytical elasticity, all three shears, oblique rows, row scaling/permutation, coordinate reparameterization, general prestress/strain origins, ordered reversals, duplicate records, tiny strains, rank/input/budget failures and iteration/trial boundaries. It compares all five public laws with direct material replay and existing drained endpoint controls, and checks restart equality. Shared-integrator comparisons check driver semantics, not model correctness or experimental accuracy.

The separate fixture checks parent-memory reset isolation, exact duplicate history, repeated execution, a domain failure after accepted internal substeps and rejection of timed materials. Its singular-multiplier material has a linear stress law and a cubic zero multiplier residual: the generic elastic predictor reaches the exact material solution, but full-state implicit linearization is singular. Stress-control inversion succeeds via numerical probes while the multiplier stays zero. This is an analytical engine fixture, not an admitted formulation.

To reproduce the native checks using CMake, configure normally, then build **serially**:

```sh
cmake -S . -B build
cmake --build build --target atlas_recorded_tests --parallel 1
./build/atlas_recorded_tests
cmake --build build --target atlas_recorded_fixture_tests --parallel 1
./build/atlas_recorded_fixture_tests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_recorded_path -v
```

Development used small standalone compilations, followed by fresh CMake Debug builds with `-O0 -std=gnu++20`, one target at a time. The final CMake runs pass 56 public cases with 1,850 assertions and 90 transaction assertions; 21 related Python tests pass. Commands and source hashes are recorded in the manifest. Source-matched nonlinear references, path-density studies and full experimental replay remain open before NUM-04 is complete.


## Native JSON replay command

The [closed run schema](../schemas/recorded-run.schema.json) wraps the path with a model ID and optional ordered `parameters`, full `initial` state, `integration_settings` and `control_settings` objects. Omit parameter/state arrays to use model defaults; explicit empty arrays are rejected. Partial settings objects overlay the documented defaults. Full-state restart uses the saved state and accumulated strain as described above.

```sh
python3 -m atlas.cli replay protocols/recorded-linear-elastic-run.json \
  --solver build/atlas_solver --output result.json
ATLAS_RECORDED_SOLVER="$PWD/build/atlas_solver" \
  python3 -m unittest tests.test_recorded_api tests.test_recorded_path -v
```

The [elastic example](../protocols/recorded-linear-elastic-run.json) is illustrative, with no experimental calibration claim. JSON validation runs before launching the engine. Numeric transport uses IEEE binary64; integer inputs that cannot be represented exactly are rejected before execution. The Python command transports numeric rows through temporary files to avoid operating-system argument-size limits at 5,001 knots. It writes successful or failed engine responses, includes the exact `specification`, and records `request_sha256` over UTF-8 Python `json.dumps(spec, sort_keys=True, separators=(',', ':'), allow_nan=False)` output. This identifies the parsed request; it is not a hash of the original file bytes. A failed engine response exits with status 1, retaining any accepted prefix. Malformed JSON/specifications or process/transport errors raise an error without publishing a new result file. The default process timeout is 60 seconds; Python callers may override it.

`atlas.recorded.execute_recorded(spec, solver, timeout=60)` exposes the same bridge. The C ABI is additive:

```cpp
const char* atlas_replay_recorded(const char* model, const char* parameters,
    const char* initial, const char* initial_strain, const char* controls,
    const char* knots, const char* material_settings, const char* control_settings);
```

Arguments are numeric CSV strings except the model ID. `initial_strain` requires six Mandel components. `controls` requires six seven-value rows: stress tag (`0` strain, `1` stress), then six coefficients. `knots` requires 2–5,001 seven-value rows: coordinate, then six absolute targets. All values must be finite; rows stay in supplied order. Material settings use the existing six-value order: residual tolerance, rate tolerance, Newton iterations, depth, substeps, backtracks. Control settings use five values: control tolerance, Newton iterations, backtracks, path material-trial budget, finite-difference step. Null/empty parameter, initial-state and settings arguments select defaults; required wire arguments reject missing values. C callers own the buffers passed in. The returned JSON string uses shared storage, remains valid until the next API call, and is not thread safe.

The native CLI has `--mode recorded`, `--initial-strain`, `--recorded-controls-file`, `--recorded-knots-file`, optional `--integration-settings` and `--recorded-settings`; wire files are bounded to 2 MB each. These options are rejected in other modes, and recorded mode rejects unrelated protocol/time flags. Native responses echo the numeric wire, resolved initial state/parameters/settings, API version and catalogue hash. Coordinate labels live in the JSON request and are preserved by the Python bridge; the numeric C ABI carries only ordering values. Parsed replay failures carry `failed_knot`, `points`, final committed `state`/`strain`, and work counters. Parse/parameter/settings errors return `ok:false` with a message before executing a path and do not publish state. No stress/strain interpolation or initial preparation is added by the bridge.

The [API evidence](../catalogue/investigations/recorded-replay-api-v1/manifest.json) retains 16 native responses, including three failure branches and the 5,001-point case. Analytical normal/shear/oblique controls, all-five-model direct replay and restart, malformed wire/mode separation, and JSON command output are checked separately. Forty-six existing public native commands match the prior binary exactly after excluding elapsed time. This evidence covers the native C entry point through CLI execution; its Emscripten export annotation does not establish Wasm runtime parity.


## Browser recorded paths

The **Recorded paths** view imports a raw recorded-run request, a native JSON result containing `specification`, or a browser replay export. It recalculates the supplied request locally in a dedicated worker, retaining ordered duplicates and reversals. Model sources and the executable definition stay linked beside the run. Default parameters/initial states are explicitly labelled; the resolved values and both sets of numerical settings are inspectable after execution.

Select any of the six orthonormal Mandel components to plot strain or effective stress against the dimensionless ordering coordinate. Shear plots use `sqrt(2)` components. Stress plots use kPa; CSV exports retain Pa. Lines connect accepted observations and do not assert controlled stress between knots. A stopped replay displays and exports only its committed prefix; cancellation/timeout terminates the worker. Replaying starts from the supplied initial state. Import checks catalogue identity when supplied, and rejects unsupported models or malformed paths/settings. The 10 MB file limit and 60-second worker timeout bound browser transport/runtime; files stay local.

Exports preserve the exact parsed `specification`, full engine result and catalogue hash. They can be reimported in this view or passed as `document['specification']` to `execute_recorded`. Unlike Python results, browser exports do not compute Python's canonical request hash. Their engine wire and resolved settings still identify the values actually executed. The elastic example is available directly from the view.

The [browser investigation](../catalogue/investigations/recorded-browser-v1/manifest.json) verifies 16 fresh public native/Wasm replay pairs, including 5,001 observations and three failure branches. It also retains browser export/native replay equality, a source-linked screenshot, and existing protocol/tangent regressions. Its scope excludes timed/research catalogues, arbitrary recorded-measurement overlays, automatic experiment-to-path conversion, source-matched nonlinear references and experimental validity.

```sh
node tools/test_recorded.mjs
node tools/test_recorded.mjs --wasm build-wasm/atlas.js --native build/atlas_solver
```
