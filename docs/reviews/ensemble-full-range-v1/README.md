# Full-range ensemble explorer — 2 November 2026

Default OPARA replay and both plots now use all 1438 acquired observations,
ending at 15.99% axial strain. Removed the obsolete context toggle and 0.992%
marker. Model definitions, initialization, parameters, numerical settings and
30-second per-job timeout are unchanged. Historical95-row exports retain their
exact prefix when imported; new runs and exports use the full test.

Full-range exports require a larger upload allowance: the default export is
about25MB. The guard is now100MB, accommodating the existing39-run limit.
Exact source/catalogue/request/result checks still apply. The first browser
failure and the upload-sizing correction are retained separately.

## Verification

- 33Node regression checks and9Python package/recorded/catalogue checks pass.
- Existing matching build-wasm/atlas.js executed serially without rebuilding:
  all15default requests complete1438points. All five elastic variants pass the
  frozen independent axial-stress and volume formulas at every endpoint.
  See wasm-summary-v1.json and the complete wasm-results-v1.json.
- Actual browser-v2: all15full-range runs; both charts have16polylines each
  containing1438points; final requested strain.1599; selection/visibility,
  export/edit-stale/import-and-replay, invalid excluded fields, rejection,
  cancellation, navigation and390px layout all pass. CLI exited0 and captured
  output/playwright/ensemble-full-range-{desktop,mobile}.png (visually inspected).
  Complete script and CLI transcript retained. browser-failure-v1.txt records
  the initial10MB-guard failure; the same script passes after correction.
- JavaScript syntax and whitespace checks pass for the four owned code/test
  files. Shared board diff has unrelated pre-existing trailing whitespace at
  the Duncan row; left unchanged.

The isolated preview at /private/tmp/atlas-ensemble-full-range-v1 uses current
frontend modules with the exact existing tested Wasm and matching generated
catalogue. Four unrelated app asset requests return404 (named examples,
experiment browser, evidence, applicability); retained browser console lists
them. This qualifies the ensemble route, not a current full-site release.
No commit, push, deployment, remoteCI or runtime rebuild performed.

## Reproduce

```sh
node --test tests/test_ensemble.mjs tests/test_catalogue_browser.mjs tests/test_web_package.mjs
python3 -B -m unittest tests.test_ensemble_package tests.test_web_recorded tests.test_web_catalogue
python3 -B tools/build_ensemble_web.py --output /private/tmp/atlas-ensemble-full-range-v1
node tools/test_ensemble_wasm.mjs --wasm build-wasm/atlas.js --experiment /private/tmp/atlas-ensemble-full-range-v1/ensemble-experiment.json --output /private/tmp/ensemble-full-range-new.json
playwright-cli -s=ensemble-full run-code --filename docs/reviews/ensemble-full-range-v1/browser-checks.cjs
```

Serve an isolated preview on127.0.0.1:18869 with web modules, ensemble assets,
atlas.js/atlas.wasm and the matching build-wasm/generated/models.json. Use a
fresh output filename for each numerical run; never overwrite prior reports.
