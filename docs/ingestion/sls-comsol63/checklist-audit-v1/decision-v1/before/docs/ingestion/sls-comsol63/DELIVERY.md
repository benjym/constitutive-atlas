# sls-comsol63 — end-to-end delivery ledger

- Umbrella: MODEL-sls-comsol63; lead/integration/build/push owner: /root; date2026-11-01.
- Exact formulation: COMSOL6.3 ordinary deviatoric single-Maxwell-branch Standard Linear Solid / Zener with equilibrium shear spring and elastic bulk; dry total Cauchy stress, infinitesimal strain, fixed spatial Cartesian frame/zero spin. Excludes fractional/thermal/volumetric relaxation and finite strain/spin.
- Native/browser scope: common physical-time solver; bounded illustrative relaxation, creep and rate-loading schedules, all12state/6stress components. Broad machine parameter envelope and experimental validation are unqualified.
- Source packet: [README.md](README.md), [crosswalk.json](crosswalk.json); dossier: [exact formulation](../../models/sls-comsol63-deviatoric-zero-spin-ode.md). The frozen packet is a historical specialist handoff; its pending-language is not current delivery status.
- Definition: `models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json`; SHA256 `eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906`.
- Implementation runs: /root and /root/sls_ingestion; independent reviewer: /root/sls_scientific_review, separate fresh-context run. Browser specialist: /root/sls_browser_delivery.
- Ownership: explicit SLS model/packet/review/admission/examples/cmake/web/package/CI whitelist recorded on live board. Coordinator owns shared integration; no handwritten constitutive kernel, schema migration or unrelated staging.
- Remote authorization: user requested “same loop … ingestion through to review and commit/push”; authorization covers that delivery. This audit preserves the later concurrent page-removal commit pending the user's routing preference.

Current status distinguishes the completed exact release from a newer packaging change. All E0–E8 passed for qualified revisionf18db8e7. The current standard builder atf51113bd explicitly removes the SLS laboratory and engine, so current website integration/qualification gates are reopened. Original evidence is preserved; no scientific gate is revoked merely by the later packaging change.

- [X] E0 — Scope/claim: exact variant, owners and separate reviewer recorded. The new full-loop checklist was adopted during the run; no claim that its ledger existed before introduction.
- [X] E1 — Sources: selected complete law,21original readable files plus identical durable ignored private copies; rights and version distinctions recorded. Durable retention receipt: `docs/admission/sls-comsol63-approved-v1/source-retention.json`.
- [X] E2 — Contract: complete v0.3 crosswalk, explicit physical-time/state/initialization/transaction controls and prospective34case acceptance freeze.
- [X] E3 — Transcription: exact candidate validates/generates;10independent algebra groups and400tensor/energy/reference checks pass.
- [X] E4 — Native/Wasm:34cases/68material calls perbackend,7negative/recovery pairs, actual full-state restart and2934parity scalars;18contract tests(3optional skips); durable CI qualification and full regressions passed in the exact release.
- [X] E5 — Independent approval: accepted exact-hash nine-item agent checklist, no blockers; generated approval equals registry member; all21durable source hashes verified again.
- [-] E6 — Atlas: exact model/approval/source/catalogue integration passed in f18; current standalone-page removal breaks normal browser routing/package support. Status/roadmap summaries corrected by retrospective audit. SQLite was not a release artifact; committed exporter is bibliographic only, with an independently owned generic export change still uncommitted.
- [-] E7 — Packaged website: historical full-package216Wasm and324real-browser comparisons, replay/reset/custom history/negative recovery/tamper/layout/catalogue checks passed. New current builder no longer packages SLS; requires retained or replacement routing and qualification.
- [-] E8 — Live delivery: exact f18 CI, Pages and actual live checks passed; implementation and receipt commits pushed. New changed revision must not inherit that pass. Current live SLS files still match the tested f18 upload in this audit; future deployment of the removal can retire the route.

## Current handoff

- Overall state: historical release live/verified; current website integration blocked by later packaging scope change.
- Current owner: coordinator; pending user preference whether to retain SLS availability or keep standalone-page removal.
- Smallest next action: retain/replace routing if SLS should remain interactive, then rerun only affected standard-package/browser/CI/live gates. If removal is intentional, explicitly classify SLS as source/approved executable with historical live evidence rather than current full website delivery.
- Separate generic database work: INT-power-creep-delivery-v2 owns `atlas/research.py`; audit confirms its local change retains exact SLS definition,3source rows,1approval,1accepted review and clean foreign keys. Not claimed committed/released. Do not overwrite that owner's work.
- Known limits: exact passivity assumes traceless q; admitted trace roundoff is numerical, broad parameter bounds unqualified, no material calibration/experiment/finite-spin claim. Full prior failed attempts remain intact.

## Evidence index

| Phase | Evidence / reproduction | Result |
| --- | --- | --- |
| E0–E2 | Original packet/crosswalk; execution-v1/PLAN.md,cases.json,freezes; actual board claims | Complete bounded source/profile contract |
| E1/E3 | `python3 -B docs/ingestion/sls-comsol63/verify_packet.py --source` | Pass; packet/source hashes and independent algebra |
| E4 | `python3 -B docs/ingestion/sls-comsol63/execution-v1/verify.py` | Saved native/Wasm reference/parity, archives and retained failures pass |
| E5 | `python3 -B docs/admission/sls-comsol63-approved-v1/check.py` | Exact model/review/approval/registry/saved evidence/private sources pass |
| E6/E7 historical | docs/reviews/sls-atlas-integration-v1/, docs/reviews/sls-web-v1/ | Standard package and actual browser qualification pass |
| E8 historical | docs/reviews/sls-release-v1/, docs/reviews/sls-live-v1/ | Exact CI/Pages,216live comparisons,10SLS+8entry assets pass |
| All53criteria | [checklist-audit-v1/CHECKLIST.md](checklist-audit-v1/CHECKLIST.md), evidence-check.json |265original receipt bindings intact; current integration conflict explicitly reopened |
| Database distinction | checklist-audit-v1/database-check.json | Committed bibliographic versus uncommitted exact approved-definition export distinguished |

## Review and integration identity

- Accepted record: `catalogue/agent-reviews/sls-comsol63-agent-v1.json`; SHA256 `eda7775348b6b5fbd40cfedf2876d1550505f17c83fdd148b83eb153c2d7582c`.
- Approval: `docs/admission/sls-comsol63-approved-v1/approval.json`; SHA256 `763c29f59b7156094fd15f9edb73b24b2de70c44e748704c8612a5d42170399b`; exact registry member in `catalogue/approved-models.json`.
- Native/Wasm toolchains, binaries/source closure and settings: execution-v1/build-input-receipt.json, binary-receipt.json and manifests. Serial explicit targets; no rebuild needed for this saved-evidence audit.
- Packaged SLS catalogue hash: `11dd07e8b896a71bdc72ce4ff93aba664916af583c703fd6b8671a0727a6ff6e`; CI/live Wasm SHA256 `1f39471279e8eb01b45f036ef73062c42ab9e3c039bb1ff48e04c7945e7b8e6c`.
- Reviewed model bytes unchanged. Browser delivery was separately qualified; later packaging removal changes availability, not the governing equations. Original unused helper archive-context delta remains explicit.

## Deployment receipt and retained history

- Implementation commit `9a27359b38671e07150c717934c1248798d0aa65`, pushed.
- Original run41287314779 cancelled; combinedd5 run41287657999 failed legacy GIS/Tresca recorded-path fixture calls, deployment skipped. Neither is counted as passing. Original logs and prospective replacement plans remain unchanged.
- Qualified release `f18db8e75d27cf182f2c03dfcd6534b7f51d5a86`; [CI41289504263](https://github.com/benjym/constitutive-atlas/actions/runs/41289504263), all4native/Wasm jobs plus Pages deployment successful. Scope-aware shared replay fixture correction preserved original rejected calls and numerical tolerances.
- Pages deployment7470820389, successful status21099220266. Fresh upload13076512926; private tar SHA256 `7c2981630798a628e49748a8cf1c115f27072a56d37308863b2bf54900163a5a`. Exact upload/live18asset comparisons are recorded, not inferred from URL availability.
- [Historical verified live laboratory](https://benjym.github.io/constitutive-atlas/sls.html): actual Chromium default/rate216full-state/stress reference comparisons;10SLSasset hashes; source/review/approval/checklist/model links200;0console errors/warnings;1280/390layout checks. Parent inspected live screenshot.
- Final publication receipt commit `e70e3d362b376aa7ea2cd6e3a202478ee3456b41`, pushed. Its new CI and laterf51113bd CI are not substituted for the exact verifiedf18 run; current pending run statuses recorded in audit.

## Completion statement

Source complete for the selected variant; common-engine native/Wasm executable; independently numerically qualified and agent-approved; atlas model/source/approval present. Exact historical standard-package and live website delivery verified. Current later packaging change reopens website gates; this ledger no longer conflates historical delivery with changed current support. Experimental validation remains unassessed.
