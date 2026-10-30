# Incremental integration settings and provenance

The shared incremental C++ solver, material linearization and laboratory protocols now accept `atlas::IntegrationSettings`. This advances NUM-03. It exposes existing numerical choices with their previous defaults; the nominal accepted-substep cap is now enforced exactly. The separate physical-time and schedule settings retain their existing contracts.

## C++ contract

```cpp
atlas::IntegrationSettings settings;
settings.rate_tolerance = 1e-8;
auto result = atlas::integrate(model, parent, increment, parameters, settings);
auto derivative = atlas::linearize_update(model, parent, increment, parameters, settings);
// result.settings and derivative.advance.settings retain the requested values.
```

The optional final argument also applies to `controlled_step` and `run_protocol`. `Run.settings` records the material settings used by the protocol. Every outer-control trial forwards the same settings to a fresh update from the committed parent. Settings remain fixed through all internal substeps and tangent replay. Changing them changes the numerical map, not the model definition or its schema/hash.

| Field | Default | Valid range and meaning |
| --- | --- | --- |
| `residual_tolerance` | `2e-10` | Finite positive scaled Newton residual threshold; strict `<` comparison |
| `rate_tolerance` | `1e-6` | Finite positive maximum scaled step-doubling/endpoint-defect threshold; strict `<` comparison |
| `max_iterations` | `45` | Integer 1–1000, per implicit candidate step, including elastic-predictor iterations |
| `max_depth` | `14` | Integer 0–20, binary subdivision depth of a candidate; root depth is zero |
| `max_substeps` | `20000` | Integer 1–1000000, accepted steps per material update, shared across recursive branches |
| `max_backtracks` | `11` | Integer 0–30; try Newton line-search factors `2^-k` for `k=0..max_backtracks` |

Both tolerances are dimensionless in the existing model state scales. The norm remains the maximum absolute scaled component, including the rate controller's defect tests. These settings do not establish relative stress accuracy or a global integration error bound. Componentwise adaptation need not select the same partition under general tensor rotations; see [the geometry investigation](TANGENT_GEOMETRY.md).

A residual candidate contributes one accepted step. A successful midpoint candidate accepts its two half steps, so it requires two remaining budget entries and its fractions are at candidate depth plus one. The old `substeps > 20000` check could overshoot the nominal limit. The updated implementation stops before accepting a step or pair that exceeds the cap, including odd budgets. Thus a case at the former overshoot boundary can now fail where an older binary continued. Other default results in the retained API matrix are identical.

Invalid C++ settings reject before material advancement and retain the supplied parent. Valid settings that exhaust an iteration, depth or step budget also roll back the complete caller state, including preparation/history changes. Diagnostic accepted fractions can describe partial internal work on a failed attempt; they do not commit those states. `max_substeps` is per material call, not a global laboratory-run or outer-trial work budget. The accumulated iteration diagnostic can exceed `max_iterations` across candidates. There is no separate rejection-count limit in this interface; depth and accepted-step limits bound the recursive update. Low-level candidate helpers assume validated settings; use the public update entry point.

## C ABI and CLI

Three additive exports append a settings CSV argument to the corresponding existing signature:

```cpp
const char* atlas_integrate_with_settings(const char* id, const char* parameters,
    const char* initial, const char* strain, const char* settings);
const char* atlas_linearize_with_settings(const char* id, const char* parameters,
    const char* initial, const char* strain, const char* settings);
const char* atlas_run_with_settings(const char* id, const char* parameters,
    const char* initial, int protocol, double target, int steps, int cycles,
    const char* settings);
```

CSV order is the six table fields in order. Empty or null settings select defaults in these new exports. The CLI option is accepted only for `integrate`, `linearize` and `run`:

```sh
solver --mode linearize --model hypoplastic-sand-vw96 --strain 0.0001,-0.00005,-0.00005,0.00002,0,0 --integration-settings 2e-10,1e-8,45,14,20000,11
```

New responses include `integration_settings` with `version="incremental-settings-0.1"`, `norm="scaled_component_max"` and all six resolved values. Settings-enabled integrate responses also include model/catalogue identity, resolved parameters, parent and increment. Linearize/run retain their existing request provenance. Malformed, nonfinite, out-of-range and fractional integer settings fail without publishing a decoded material result. The settings API uses the existing shared response-string lifetime and concurrency constraints. CLI status still follows material success separately from tangent availability.

Existing C exports and CLI calls without the option retain their previous response structure and use defaults. Their historical responses do not carry this new settings object. For an explicit default-settings run with provenance, use the option with an empty string or all six default values. Source annotations provide future Emscripten exports; no new Wasm or browser runtime has been verified.

## Verification and reproduction

The [record](../catalogue/investigations/incremental-settings-v1/manifest.json) retains 30 custom-settings responses and a separate 21-case default API capture. All default responses equal the previous retained responses exactly, including eleven full tangent matrices. Custom cases cover settings provenance, midpoint/implicit derivative replay, five bounded rollback failures, fourteen malformed/unsupported requests, exact budgets, no-backtracking operation and protocol forwarding.

For the synthetic `x' = x` fixture over total coordinate change `-1`, rate tolerances `1e-4`, `1e-6`, `1e-8` use 32, 128, 512 midpoint steps. Absolute endpoint errors against `exp(-1)` decrease from `6.1302e-5` to `3.7643e-6` to `2.3423e-7`. The independently computed discrete recurrence also matches the returned tangent.

For the two-step quadratic implicit fixture, residual tolerances `1e-4`, `2e-10`, `1e-12` give endpoint discrepancies against sequential closed-form roots of `5.4134e-5`, `3.5718e-10`, and zero at recorded double precision. Tangent discrepancies decrease from `4.5832e-4` to `3.0248e-9` to `8.89e-16`. Zero discrepancy here is not a general exact-root guarantee. These synthetic checks establish configuration/refinement behavior, not a universal tolerance-to-error formula or an independently validated constitutive law.

The existing five-model native numerical program passes residual-Jacobian, frame-covariance and hidden IGS-crossing checks, plus new direct C++ tests for nonfinite settings, exact/odd midpoint budgets, late rollback, depth exhaustion and laboratory propagation. Four new offline Python groups bring the related total to 33 passing groups. Three small API compilations during implementation and one standalone numerical-test compilation completed normally; no full CMake build was invoked.

```sh
python3 tools/verify_linearization_api.py prepare /private/tmp/atlas-settings-models
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-settings-models/generated cpp/main.cpp -o /private/tmp/atlas-settings-solver
python3 tools/verify_integration_settings.py capture --solver /private/tmp/atlas-settings-solver --output /private/tmp/atlas-settings-responses.json
python3 tools/verify_integration_settings.py verify catalogue/investigations/incremental-settings-v1/responses.json.gz --output /private/tmp/atlas-settings-report.json
python3 -m atlas.compiler /private/tmp/atlas-settings-public/generated
c++ -std=c++20 -O0 -Icpp/include -I/private/tmp/atlas-settings-public/generated tests/test_solver.cpp -o /private/tmp/atlas-settings-public/numerical-tests
/private/tmp/atlas-settings-public/numerical-tests
python3 -m unittest tests.test_integration_settings tests.test_tangent_geometry tests.test_linearization_api tests.test_update_tangent tests.test_atlas.LanguageTests tests.test_parent_reset.ParentResetLanguageTests -q
```

Preparation and offline verification do not run native code; captures execute serial native requests with 45-second individual bounds. Outer mixed-control stopping rules, linear pivot cutoffs, tangent replay tolerances, global resource budgets, website/export settings controls and native/Wasm parity remain open. NUM-03 is not complete; no solver default tolerance is changed by these refinement results.
