# Catalogue-driven drained ensemble and two Web Workers

Implemented locally on 3 November 2026. The current OPARA drained triaxial
experiment discovers all compatible models from the exact compiled catalogue,
rather than restricting membership to three IDs. Current catalogue: 13 eligible
models, 25 default requests. The original three retain their default OAT sweeps;
new models start with a baseline and two empty, editable variation lists.
All declared parameters remain editable, with p_ref fixed as before.

The consumer requires effective Cauchy stress, Mandel components,
compression-positive strain and a strain-path law. Total-stress models are
listed with exclusions. Dedicated timed/controlled/implicit engines are not in
this common recorded-replay catalogue and need their own execution contracts;
this change does not claim to enable those engines or additional tests.

Measured effective stress replaces sigma. Measured e initializes void ratio,
and 1+e initializes specific volume v. Other persistent scalar/tensor history
uses explicit, editable model example values, identified as unmeasured
assumptions. Temporary unknowns/multipliers use their declared reset values.
Every request retains its full state and exact model definition. Historical
three-model studies and the old 95-observation window still replay exactly;
Reset all models restores catalogue-wide defaults after importing a subset.

Two reusable Web Workers execute independent Wasm instances, each receiving
one request at a time. The queue API defaults to one lane for existing callers;
the explorer explicitly uses two. Job order, IDs, per-run outcomes and exports
remain deterministic when responses arrive out of order. Each active run has
its own abort controller and unchanged 30-second timeout. Cancellation and
input edits abort all active requests; the next study waits for settlement.
Workers close on completion, error, cancellation or page exit. Plot bounds are
accumulated without spreading large arrays into function arguments.

## Verification

- `node --test tests/test_ensemble.mjs`: 17 pass, including discovery,
  complete tensor/scalar state, v mapping, absent-p_ref models, exact replay,
  concurrency bounds, out-of-order completion, independent timeout/failure,
  cancellation of both active requests and suppression of late responses.
- `node --test tests/test_catalogue_browser.mjs < /dev/null`: 11 pass.
- `python3 -m unittest tests.test_ensemble_package`: 2 pass.
- JS syntax checks and owned-source `git diff --check`: pass.
- Actual Chrome/Playwright: 13 controls/25 real Wasm requests; every outcome
  retained; export verified and imported through the current pure contract.
  Nineteen requests completed all 1,438 observations; six stopped. Three sand
  models reject the measured starting state with their illustrative defaults;
  Duncan–Chang, Mohr–Coulomb and Original Cam Clay retain solver-stop prefixes.
  Exact reasons and point counts are in actual-summary.json. No parameter,
  solver, model or measured-state change was made to force completion.
- Parallel full ensemble: exactly two live/busy workers, 25 requests, zero
  duplicate in-worker requests, zero workers remaining. About 10.87 seconds
  from first worker creation to final termination on this machine; no measured
  serial timing or universal speedup claim. The complete 52,310,398-byte
  parallel export is byte-for-byte identical to the serial export.
- Rapid edits while both workers are active and explicit Cancel: all old
  workers terminate; max live/active remains two, latest E=34 MPa is retained,
  final outcomes remain 19 complete/6 stopped, zero workers remaining.
- Desktop/mobile layouts and complete colored legend inspected; no horizontal
  overflow, all curve colors defined, browser console zero errors/warnings.

Read PLAN.md for prospective criteria, source-hashes.json for the final source
identity, parallel-worker-audit.json and parallel-cancellation-audit.json for
actual concurrency, parallel-equality.json for export identity, and cleanup.json
for retained private data and stopped resources. Screenshots are under
output/playwright/ensemble-all-models-v1-*. Browser scripts are retained here.

## Retained development failures and scope

Initial regressions used the old three-placeholder discovery assertions; two
failed and were updated to assert actual catalogue membership and fail-closed
explicit requests. An adjacent-test invocation mistakenly included an absent
file and a stdin-driven harness, then was interrupted; adjacent-tests.txt is
retained, not counted as a pass. Correct focused commands above passed.

Initial loopback binding was sandbox-denied, then its first chosen port was
occupied; isolated localhost port 58743 was used and stopped. An early Cancel
reference had already disappeared after completion. Instrumentation attempt
one navigated to the same document and did not install; installing twice then
produced invalid nested counters. These observations are retained separately;
fresh isolated context v2 is the accepted audit. The first timed-edit probe
matched three E fields; the corrected probe explicitly selects the elastic
field and passes. These were test-harness issues, not waived numerical gates.

The preview overlaid only the three ensemble modules on the retained qualified
common engine/package at /private/tmp/mc-current-shared-package-v3/site, without
modifying that package. No new full-site build, scientific model approval,
calibration, live deployment, commit, push or remote CI is claimed. The changed
source is ready for the separately authorized normal release workflow. Existing
model definitions, source evidence, numerical settings and measured data remain
unchanged. All other tests remain the next scope of work.
