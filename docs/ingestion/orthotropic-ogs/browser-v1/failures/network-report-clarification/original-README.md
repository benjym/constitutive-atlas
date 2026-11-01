# Orthotropic OGS actual main-atlas browser qualification

BROWSER-orthotropic-ogs-v1, owner /root/sls_browser_delivery, 2 November2026. Scoped browser qualification passes for the coordinator's corrected v2 normal atlas package. This packet is functional E7 evidence; independent interface/scientific review and E8 release/live delivery belong to the coordinator. No experimental calibration, arbitrary material-axis rotation, physical-time or broad parameter-envelope claim is made.

Only this new browser-v1 directory and output/playwright/orthotropic-v1/ were written. No production/shared sources, models, approvals or historical evidence were edited, no builds/native/vendor programs executed, and no commits/remote actions performed. The coordinator explicitly handed off only the exact served approved common Wasm through actual browser after standard package gates. execution-handoff-v2.json binds the tested package before browser opening: source /private/tmp/atlas-orthotropic-release-v1, package /private/tmp/atlas-orthotropic-site-v2, actual URL http://127.0.0.1:18882/index.html#laboratory?model=orthotropic-linear-elastic-ogs . Actual browser Chrome156.0.8078.74; first default observation2026-11-01T19:00:21.751Z. Exact model60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14.

PLAN.md and the acceptance/oracle/scripts/source inputs were bound by prospective-freeze.json before any browser/compiled observation. The public preset loads all six strain components, reverses, and holds zero increment; there is no elapsed clock. prepare_references.py uses the existing independent source Fraction compliance inversion, not production stiffness expressions. references.json freezes default and custom expectations. The custom fixture changes all nine constants and starts with six nonzero stresses and all six prescribed increment components. It qualifies that bounded fixture only.

Passed evidence:

- default.json and custom.json match all six stress and six cumulative applied-strain values at all four points (48stress plus48strain comparisons); default additionally matches18saved execution-v1 public reference stress values. Stress bound1e-6Pa and strain bound1e-15 remain unchanged. assessment.json reports66stress-reference comparisons and48strain comparisons.
- Two meaningful stress/relative-strain plots, all six selectable channels, and complete5×7stress-state table. Export/request/records retain full SI state, all six relative-strain values, all nine constants and immutable initial state.
- Importing the same file twice clears the file field and verifies a fresh complete document; replayed.json/reset.json exactly equal default.json. Two ordinary fresh custom runs exactly match (custom.json/custom-fresh.json), proving original initial-state restart.
- Finite later point+record stress tamper and duplicate JSON key rejected; stale export disabled. Subsequent valid import/reset recovers. Coupled nonpositive-definite compliance rejected before execution, followed by recovery.
- Pending200row input replaced by latest2row request without stale export; latest.json confirms final2row request. Switching ordinary→SLS→orthotropic cancels superseded work and preserves one visible active laboratory. Direct route and shared selector work. Actual catalogue card→Explore route passes in browser-catalogue-v2.log.
- Shared equations route opens the orthotropic shadow section. Both exact pinned OGS source links and readable review/approval/checklist/model links returnHTTP200 on the completed acceptance run.
- All10declared orthotropic manifest assets and main index/app/catalogue (13fetched files) exactly match the tested coordinator package; identity/module/Wasm/model/catalogue/review/approval are retained in browser-assets-links-layout.log. Exact package Wasm SHA256a0dd300fb833fb2795b1a915a35afedee548b8a6831834fe1b5aeffcf7d9934a.
- Browser console0errors/0warnings. All260recorded atlas GET requests returnedHTTP200. Desktop1280/narrow390document widths match viewport. Six screenshots in output/playwright/orthotropic-v1/ were visually inspected; the six-state table fits desktop and scrolls locally inside the narrow card without document overflow.

Retained failures and corrections:

1. failures/links-attempt1.log preserves the initial HTTP-link gate failure; the original frozen script threw before emitting the failing status, so its exact offending link/status is unknown. failures/links-diagnostic1.log immediately records all six links200. Repeating the unchanged frozen script passed all links/assets/layout. No link/source change or relaxed gate was used.
2. failures/catalogue-attempt1.log preserves an early route assertion. The predicate saw the previous completed status before the hash route made the main section visible; failures/catalogue-postfailure-snapshot.yml shows the actual route correctly selected and visible immediately afterward. Distinct browser-catalogue-v2.js waits for the requested hash and visible panel, then repeats the same actual card/Explore acceptance successfully. The original frozen script and prospective freeze remain untouched; no production change was needed.

Reproduce the saved-output/source/hash assessment without compiled execution:

```
python3 -B docs/ingestion/orthotropic-ogs/browser-v1/assess.py /private/tmp/atlas-orthotropic-site-v2
```

Full output documents: default, replayed, reset, custom, custom-fresh, latest JSON. Scripts/logs/snapshots preserve the actual interface actions. closure.json records visual/network/retained-failure status; manifest.json binds this packet and the six owned screenshots. No scoped blocker remains. Parent's next action is independent interface review and E7 integration, then exact revision CI/upload/live E8 qualification.
