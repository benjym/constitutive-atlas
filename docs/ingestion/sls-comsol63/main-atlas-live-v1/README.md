# Published main-atlas SLS qualification

LIVE-sls-main-atlas-v1 passes for exact revision302f2adc06d39b634e1865899e24ff088cc32f72. Actual Chrome156.0.8078.74 observation completed2026-11-01T10:11:55.085Z at https://benjym.github.io/constitutive-atlas/#laboratory?model=sls-comsol63-deviatoric-zero-spin-ode . This is the SLS component in the general atlas laboratory. No standalone page or iframe was used.

The coordinator explicitly authorized live compiled-browser execution only after exact CI41294652646 all-five-job success, Pages deployment7471552199/status21101638675 success, and21live/upload hash comparisons. handoff.json records that prerequisite. Parent terminal receipts are ../main-atlas-v1/release-v1/{ci-terminal.json,deployment-proof.json,upload-verification.json,live-assets-attempt1.json}. The exact tested upload was independently compared at /private/tmp/sls-main-pages-extracted-302; the durable private archive is .local/release-artifacts/sls-main-302/artifact.tar. No builds/native execution/source mutations/remote actions were performed by this worker.

PLAN.md, browser-live.js and check_live.py were frozen prospectively in prospective-freeze.json before the live handoff. All frozen file/reference hashes remained unchanged after observations. Scientific scope and tolerances are the original bounded approved SLS study; no experiment, calibration or broad parameter-envelope claim is added.

Passed observations:

- Actual published8sdefault relaxation with4intervals; full export default.json retains request, controls, all12state and6stress, exact runtime/model/review/approval/source provenance.
- 108independent reference scalar comparisons at all six outputs: eps3e-8, branchq/stress1Pa absolute bounds. assessment.json records reproducible pass.
- 12declared SLS asset bindings plus index.html/app.js/catalogue.json: all15live fetched SHA-256 values exactly match the tested CI upload. Browser identity explicitly names revision302f2adc. Model/checklist/approval and catalogue hashes remain the accepted originals. CI Wasm SHA2561f39471279e8eb01b45f036ef73062c42ab9e3c039bb1ff48e04c7945e7b8e6c.
- Embedded SLS panel selected, ordinary/Burgers panels hidden,3renderedplots,7×19inspectable full-state/stress table, shared equations action routed correctly.
- Primary source, readable review, checklist, approval and exact model links allHTTP200.
- Browser console0errors/0warnings. All recorded atlas network requestsHTTP200, including static assets; browser-network-all.log retains the full receipt.
- 1280pxdesktop and390pxnarrow document widths equal viewport. All four screenshots were inspected; controls, response plots and surrounding atlas layout render without horizontal overflow.

Reproduce saved numerical/hash assessment without compiled execution:

```
python3 docs/ingestion/sls-comsol63/main-atlas-live-v1/check_live.py /private/tmp/sls-main-pages-extracted-302
```

browser-live.log contains exact observation,15asset hashes, links and layout results; browser-completed-snapshot.yml preserves the completed interface. Screenshots are under screenshots/. manifest.json binds the complete packet. This live attempt had no application, loader, harness, identity or gate failure; historical local failures remain untouched in main-atlas-v1/browser/. No scoped blockers remain. Parent owns final delivery-ledger/board closure and evidence commit.
