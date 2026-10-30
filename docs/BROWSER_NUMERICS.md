# Public browser numerical settings

The laboratory now exposes the incremental solver settings through the tested `atlas_run_with_settings` export. This advances NUM-01/02/03 and WEB-03/06 for the five public formulations. It does not complete those milestones or admit additional scientific models.

The expanded Solver settings section provides both scaled tolerances and four work limits. Changes participate in the existing live-update sequence, validation and export invalidation. Reset restores the documented defaults. The worker and response handler check that the returned version, norm and six settings exactly match the request before accepting a result. An older cached engine cannot silently ignore a custom setting.

Exports retain settings in both `specification.integration_settings` and `result.integration_settings`. Imports validate versions, field names, finiteness, bounds and integer limits before replay. A legacy specification lacking the settings object explicitly receives the defaults. The settings version remains separate from the existing run schema and catalogue identity; broader engine-version provenance is still REP-01 work.

## Executed evidence

The [manifest](../catalogue/investigations/browser-numerics-v1/manifest.json) records source/toolchain/artifact hashes, retained comparisons, browser export and screenshot. A standalone unoptimized Emscripten build and matching native build completed normally. Emscripten automatically compiled missing debug system libraries despite the attempted frozen-cache environment flag; the record discloses this. Subsequent checks reused these outputs. No full CMake, external-reference or optimized build was run.

- Seventeen serial native/Wasm pairs pass recursive metadata/status/state/diagnostic/matrix comparisons, with floating tolerance `1e-7 * max(1, abs(native))`. They cover configured drained runs for all five public models, default and configured full-update tangents for each, a budget-limited failed run retaining its initial point, and invalid numerical settings. Elapsed runtime is excluded from equality.
- The existing parity program passes 25 public model/protocol pairs, four diagnostics/rollback cases, two Cartesian hypoplastic rate states and six independently targeted IGS crossing/cycle increments. This supports the tested public catalogue, not research/timed/schedule catalogues.
- Pure JavaScript checks cover default/legacy normalization, versions/norms/shape, all field bounds, wire argument mapping, returned-setting mismatches and stale-engine rejection. Six Python groups cover static required DOM targets and existing measurement/publication packaging behavior.
- The isolated website packages 626 public experiment assets using existing approved-release rules. Browser observation confirms default and custom-tolerance calculations; exported settings equal the engine result; custom import restores `1e-8`; legacy import restores `1e-6`; zero residual tolerance blocks calculation/export; Reset restores defaults.
- Console inspection exposed an existing response-handler exception: its `result-note` target was commented out. Restoring that element allows the handler to update the scientific scope note and pore-pressure caption and reach pending-work handling. A regression test checks required static JavaScript targets against real HTML elements. After reload and a further custom update, both texts update correctly and no new console errors were observed. Earlier error entries remain historical in the browser log.

## Local reproduction

Generate only the public catalogue into a temporary engine directory. Compile `cpp/main.cpp` directly for native and Emscripten with the flags recorded in the manifest; copy or point to a writable SDK cache. No system-library cache flag should be assumed to suppress library generation without verifying the actual toolchain behavior. Then run:

```sh
node tools/test_numerics.mjs --wasm /private/tmp/atlas-browser-settings/atlas.js --native /private/tmp/atlas-browser-settings/native-solver
node tools/test_wasm.mjs --wasm-dir /private/tmp/atlas-browser-settings --native /private/tmp/atlas-browser-settings/native-solver
python3 tools/build_web.py --wasm-dir /private/tmp/atlas-browser-settings --output /private/tmp/atlas-browser-settings/site
PYTHONPATH=tests python3 -m unittest tests.test_browser_numerics tests.test_web_experiments tests.test_web_publications -q
```

Without `--wasm`/`--native`, the numerical JavaScript test runs pure validation checks only. Existing default build/package paths remain supported. GitHub Actions now includes the new 17-pair test after its existing parity suite, but no push, workflow run or deployment has occurred for this change. Local Node was 26.7.0; CI remains pinned to Node 24.

The website exposes configured protocol runs, not a tangent viewer. Research-model Wasm parity, outer-control settings, complete release regression, general branch/partition policy, global work budgets, mobile/keyboard checks and broader engine/schema provenance remain open. Fixed-frame covariance and native/Wasm agreement do not establish finite-rotation objectivity, independent equation review or experimental predictive validity.
