# Ensemble Plotly and compact selectors — local qualification

The ensemble now uses locally bundled Plotly basic 4.1.1 for both physical response plots. It supports hover, curve selection, zoom, pan, reset and PNG export. Existing model visibility and run selection preserve the current view; a new study resets axes. The library loads on the first ensemble visit, with pinned bytes and MIT notices packaged locally. Plot data retain every measured row and available computed prefix.

The model selectors use short labels, full-name tooltips and accessible checkbox names. The responsive grid measured 67px high in five columns at 1440px and 160px high in two columns at 390px. Desktop, mobile and route-return checks found no horizontal overflow and exact chart/container width agreement. Screenshots are in output/playwright/ensemble-plotly-v1-final-*.png.

## Verification

- `node --test tests/test_ensemble.mjs tests/test_ensemble_plots.mjs`: 20 passed; see node-tests-final.txt.
- Package tests: 3 passed; see package-tests-final.txt.
- Fresh headed Chrome: hover, real curve click, zoom preservation during selection/visibility, pan, reset, PNG export and new-study reset passed. See browser-final-interactions.txt, final-layout.txt and layout-results.json. Final console: zero errors and warnings (one browser autofocus info message).
- Default study retains 19 completed and 6 stopped runs. Export is byte-identical to the preceding worker qualification: 52,310,398 bytes, SHA-256 2bcebd206db2a12c3e232574a3defe65d31151b4cb15f5bc448f7c9ba050c5b6. See export-identity.json for the retained private evidence path. No numerical acceptance policy or outcome was changed.

## Retained failures and limits

The first browser probe exposed raw job IDs containing colons being used as Plotly trace UIDs, which broke trace removal through internal CSS selectors. This was fixed using stable CSS-safe encoded UIDs while preserving original job IDs in trace metadata. The failing source and diagnostics remain under failures/ and the initial browser logs. Later probe retries exposed retained toolbar/visibility state in the test harness; final probes explicitly initialize that state. Fresh final qualification passed without app console errors.

This is local frontend qualification against the retained shared Wasm package with a narrow source overlay. No new compiled build, scientific validation, commit, push or deployment occurred. All previous numerical stops remain visible. The task browser and preview server were stopped; duplicate downloads were hash-checked and removed after retaining script copies and the unique export reference. See cleanup.json. Shared package and unrelated workspace changes were preserved.
