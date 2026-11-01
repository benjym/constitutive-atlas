# sls-comsol63 — end-to-end delivery ledger

- Umbrella: MODEL-sls-comsol63; lead/integration/build/push owner: /root; date2026-11-01.
- Exact formulation: COMSOL6.3 ordinary deviatoric single-Maxwell-branch Standard Linear Solid / Zener with equilibrium shear spring and elastic bulk; dry total Cauchy stress, infinitesimal strain, fixed spatial Cartesian frame/zero spin. Excludes fractional/thermal/volumetric relaxation and finite strain/spin.
- Native/browser scope: common physical-time solver; bounded illustrative relaxation, creep and rate-loading schedules, all12state/6stress components. Broad machine parameter envelope and experimental validation are unqualified.
- Source packet: [README.md](README.md), [crosswalk.json](crosswalk.json); dossier: [exact formulation](../../models/sls-comsol63-deviatoric-zero-spin-ode.md). The frozen packet is a historical specialist handoff; its pending-language is not current delivery status.
- Definition: `models/research/sls/sls-comsol63-deviatoric-zero-spin-ode.json`; SHA256 `eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906`.
- Implementation runs: /root and /root/sls_ingestion; independent reviewer: /root/sls_scientific_review, separate fresh-context run. Browser specialist: /root/sls_browser_delivery.
- Ownership: explicit SLS model/packet/review/admission/examples/cmake/web/package/CI whitelist recorded on live board. Coordinator owns shared integration; no handwritten constitutive kernel, schema migration or unrelated staging.
- Remote authorization: user requested “same loop … ingestion through to review and commit/push”; authorization covers that delivery. The user subsequently instructed “Leave the standalone page removal”; retain it without restoration.

Current scope is interactive SLS inclusion in the **general atlas laboratory**. Standalone pages remain removed. The earlier retirement interpretation is superseded; preserved audit/decision/clarification receipts retain that history. Original source, model, numerical qualification and approval remain unchanged. The previous standalone release is historical evidence and does not certify the new interface.

- [X] **E0 — Claim/scope:** exact formulation, coordinator whitelist and independent review roles recorded on MODEL-sls-comsol63 and INT-sls-main-atlas-v1.
- [X] **E1 — Sources:** selected complete law and21readable originals retained privately; source-retention receipt and exact hashes verified.
- [X] **E2 — Contract:** explicit v0.3 physical-time/state/initialization/transaction contract and prospective34case acceptance freeze.
- [X] **E3 — Transcription:** exact candidate validates/generates;10independent algebra groups and400tensor/energy/reference checks pass.
- [X] **E4 — Native/Wasm:**34cases/68material calls perbackend, seven failure/recovery pairs, full-state restart and2934parity scalars;18contract tests(three optional skips). Original CI/native/Wasm gates passed for exact unchanged model/common runtime.
- [X] **E5 — Agent approval:** accepted exact-hash nine-item independent checklist, no blockers; approval equals registry member. Experimental validation remains unassessed.
- [X] **E6 — Atlas:** main selector/catalogue/controller routing and normal generation qualified in the composed release source. Committed generic SQLite exporter now retains exact SLS definition, three source rows, one approval and accepted review, with no foreign-key violations ([current check](main-atlas-v1/database-current.json)). Shared owner handoff5ae90008 is complete; exact additive source is retained in main-atlas-v1/proposed-source/. Scoped commit is E8.
- [X] **E7 — Packaged website:** embedded controls, all12state/6stress values, physical-time protocols, exact replay checks and guarded dedicated common Wasm implemented. Component324reference comparisons and contract/router tests pass. Actual full-atlas browser qualification passes all three protocols, custom full state, replay twice, tamper rejection, invalid recovery, latest-request cancellation, ordinary/Burgers/SLS switching, source/equations links, desktop/narrow layout and final catalogue→Explore navigation. The unsupported initialization-hook failure and supported-hook correction remain preserved. [Separate final interface review](../../reviews/sls-main-atlas-v1/decision.json) accepted exactv3 with no blockers.
- [-] **E8 — Live delivery:** new scoped commit/push, terminal exact CI/Pages success, tested-upload/live identity comparisons and actual live main-atlas run remain required.

## Current handoff

- State: working on general-atlas E8; lead/integration owner /root.
- Shared dependency: handed off in5ae90008; SLS preserves all unrelated concurrent changes.
- Next action: commit/push reviewed owned paths, then verify exact CI/upload/live main-atlas run.
- Limitations: exact passivity requires traceless branch stress; admitted trace roundoff is numerical; illustrative parameters; broad parameter envelope, finite strain/spin, calibration and experimental validation unqualified.
- Retained failures: original CLI observer fixture, original release cancellations/legacy replay fixture failure, imported-result/same-file defects and full-browser unsupported Wasm initialization. Corrections have distinct receipts; no numerical gate was relaxed.

## Evidence index

| Phase | Evidence | Result |
| --- | --- | --- |
| E0–E3 | README.md, crosswalk.json, verify_packet.py, execution-v1/PLAN.md and frozen references | Source closure and independent algebra pass |
| E4 | execution-v1/verify.py, archived native/Wasm outputs and manifests | Original exact model qualification and parity pass |
| E5 | docs/admission/sls-comsol63-approved-v1/check.py; independent review | Exact approval/source/evidence checks pass |
| Retrospective audit | checklist-audit-v1/CHECKLIST.md and manifest |53criteria mapped;265original bindings preserved; scope clarification additive |
| Current E6–E7 | main-atlas-v1/ | Prospective composed freezes, complete package and actual main-browser receipts |
| Historical E6–E8 | docs/reviews/sls-atlas-integration-v1/, sls-web-v1/, sls-release-v1/, sls-live-v1/ | Historical standalone release only |

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

Source complete; exact common-engine native/Wasm model independently qualified and approved. Current main-atlas integration and packaged/live delivery remain in progress until the current E6–E8 evidence above is complete. No experimental validation is claimed.
