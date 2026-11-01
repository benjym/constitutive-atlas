# Ensemble full-site release qualification

User explicitly authorized rebuilding Wasm and full deployment on 2026-11-01.
The release uses an isolated worktree based on committed main f8252c16, preserving
concurrent uncommitted research. Only the ensemble implementation and additive
hooks, its evidence, release CI checks, and the previously requested standalone
page retirement regression are included. No model definition or numerical code
changed. The source-only power-creep approval is preserved; its reintroduced
standalone public page/route is removed again. J2/SLS/Burgers remain integrated
inside the individual model tester.

[Prospective policy](POLICY.md) was frozen before rebuilding. All builds ran
serially with one explicit target and `--parallel 1`: native `atlas_solver`,
Wasm `atlas_solver`, `atlas_burgers_solver`, `atlas_sls_solver`, `atlas_j2_solver`.
Emscripten6.0.8; SLS Debug and other targets Release, matching their CI definitions.
See configure/build logs and [artifact hashes](rebuilt-artifacts.json).

Local qualification passed:

- 77 Node tests and 10 Python package tests. Original Python failure is retained:
  an older assertion required republishing the removed power-creep page. Its
  assertion now enforces the user's requested removal. No numerical gate changed.
- Compiler model validation. Exact native/Wasm model and diagnostic parity;
  17 numerical settings/tangent cases,134 loading pairs,110 same-instance replay
  cases,26 scoped cases/32364 physical scalars,46 recorded-path replay pairs.
  Pure loading:9720 exact cyclic controls,250 ramp samples,60 negatives,11 contracts.
- Full normal packager passed: Burgers594 physical comparisons; SLS324 full-state/
  stress comparisons; J2 327 calls,1264 state and192 tangent comparisons, exact
  replay/recovery/tamper checks. All628 public experiment assets decoded and
  passed checksum/channel tests.
- Supported ordinary/named-input package policy passed for all12 strain-path
  models and the GIS2024 named example. The previously declared GIS2024 ordinary
  default failure is retained under its existing exact policy; it is not relabelled
  as successful or hidden.
- All15 rebuilt-engine ensemble runs completed. Five independent analytical
  elastic checks at95 endpoints passed with the original frozen tolerances;
  maximum stress error1.75e-10Pa and volume strain error3.47e-18. Export/import
  validates exact identities before fresh replay.
- Actual complete-package Chromium checks passed: ensemble default run, selection,
  visibility/context, download/import, stale suppression, excluded invalid inputs,
  rejection, cancellation, navigation and desktop/390px layouts. Ordinary elastic,
  J2 three-increment preset, SLS relaxation and Burgers completed; switching back
  to ordinary hides all special panels. No browser runtime errors.
- Removed J2/SLS/power-creep/publications/recorded pages return404. This is checked
  against the actual completed package, in addition to the regression test.

The original isolated five-model preview evidence under `ensemble-opara-v1/`
is retained unchanged. This directory supersedes its packaging limitation with
actual current full-package qualification; it does not confer new scientific
approval, applicability, calibration or independent experimental validation.

Raw reports larger than512kB are preserved byte-for-byte in deterministic gzip
archives with hashes in [raw-report-archives.json](raw-report-archives.json).
Uncompressed local originals are ignored; archived bytes decompress exactly.
Build/test logs, browser replay functions, screenshots and full local asset hashes
are retained here. Local package identities precede the release commit; GitHub CI
will rebuild/package with the deployed commit identity and be verified separately.

Reproduction uses the commands in configure/build logs and the unchanged workflow;
run `python3 -B tools/build_web.py`, then `tools/test_supported_package.mjs`,
`tools/test_experiments.mjs --built-assets web/dist/experiments` and
`tools/test_ensemble_wasm.mjs` with a new report path. Serve `web/dist` and invoke
`browser-checks.cjs` and `laboratory-browser-checks.cjs` via Playwright CLI
`run-code --filename`. The scripts reuse the browser's current base URL so that
the same checks can be applied beneath the GitHub Pages project prefix.

Deployment status will be recorded separately after CI and exact hosted checks.
