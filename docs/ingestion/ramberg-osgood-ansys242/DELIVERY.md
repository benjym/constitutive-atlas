# ramberg-osgood-ansys242 — end-to-end delivery ledger

Copy to `docs/ingestion/ramberg-osgood-ansys242/DELIVERY.md`. Follow `docs/MODEL_DELIVERY_CHECKLIST.md` from the repository root; this ledger tracks its E0–E8 gates without creating a second assignment registry.

- Umbrella task: MODEL-ramberg-osgood-ansys242
- Lead / date: /root-power-successor-ramberg-20261102,2026-11-02
- Exact formulation and publication/version: ANSYS Material Reference2024R2 §4.17 full 3D reversible constant-parameter small-strain mechanical law.
- Intended native/browser scope and exclusions: full 3D reversible isotropic small-strain mechanical compliance, constant parameters and dry total Cauchy stress. No plastic history, energy, thermal coupling, pore-pressure law, finite deformation or experimental qualification.
- Source packet / dossier: [README.md](README.md), [source-v1/README.md](source-v1/README.md), [dossier](../../models/ramberg-osgood-ansys242.md).
- Detailed model-local checklist: [CHECKLIST.md](CHECKLIST.md) (copy every E0–E8 check and exit condition; retain evidence per item)
- Canonical checklist at assignment: docs/MODEL_DELIVERY_CHECKLIST.md, copied in CHECKLIST.md at claimed source8718467f915c5f7c2aa87a7cef0903f493fde2d5,2026-11-02.
- Candidate definition path / SHA-256: models/ramberg-osgood-ansys242.json / c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2
- Worktree / authorized path whitelist: /private/tmp/atlas-ramberg-osgood-delivery-v1; model-local evidence, model/dossier/checkers/tests and additive ordinary atlas registries, policies, workflow, applicability, named examples and exact-byte source archive sidecars.
- Implementation run ID(s): /root-power-successor-ramberg-20261102; qualified current engine in execution-v3.
- Independent review run ID: /root/ramberg_review; actual separate run and accepted nine-item canonical review.
- Build/execution owner and handoff: parent, explicitly claimed BUILD-ramberg-osgood-v1; serial native then Wasm; slot released after qualification.
- Remote authorization reference: user explicitly replied “Yes” to the concrete push/CI/deploy request. See release-v1/publication-authorized.json. Earlier automatic rejection retained in release-v1/authorization-pending.md.

Use `[ ]` unstarted, `[-]` working/blocked, `[X]` verified complete. Add evidence beside each phase and link the detailed check results. Keep MODEL-ramberg-osgood-ansys242 open until E8 is verified; specialist task completion closes only that task.

- [X] **E0 — Claim/scope:** exact variant, prior-work inventory, owner/whitelist, dependencies and destination agreed.
- [X] **E1 — Sources:** readable complete law, durable private receipts, source locators, version reconciliation and rights.
- [X] **E2 — Contract:** complete v0.3 crosswalk, preparation/time/transaction/control contract and prospectively frozen references/gates; capabilities resolved.
- [X] **E3 — Transcription:** exact candidate validates/generates; independent equation/reference checks pass.
- [X] **E4 — Native/Wasm:** correct profile/interfaces, complete frozen numerical gates, rollback/recovery/restarts, useful preset, parity and regressions pass.
- [X] **E5 — Agent approval:** separate actual agent run, all nine checklist decisions, blocking findings resolved, exact accepted record and generated approval entry.
- [X] **E6 — Atlas:** qualified model/approval/source/evidence integrated through normal generation; prior models preserved and public metadata/current database checked.
- [X] **E7 — Packaged website:** real controls/plots, source/review scope, import/export/reset/failure recovery, measurement applicability/toggle where relevant, actual browser and package checks pass.
- [X] **E8 — Live delivery:** authorized scoped commit/push, all CI/deployment gates pass, live assets match tested upload and the live model run works.

## Current handoff

- Current phase / overall state: E0–E8 verified complete. Exact delivered revision ecd1f3b12381dd8edec34fe6121b80a0bd5792aa; all six workflow jobs pass and Pages deployment succeeded.
- Current owner: coordinating parent /root; delivery complete.
- Blocker / missing evidence: none within the stated mechanical and browser scope.
- Smallest next action / next owner: none required for this delivery; experimental calibration remains a separate study.
- Resume when: a separately scoped extension is requested.
- Known limitations / retained failures: original native/Wasm strict parity failure retained under execution-v1/original-v1; distinct prospective build policy qualified in v3. Source energy-printing issue retained and energy excluded. No measured comparison or broader host/kinematic validation.

## Evidence index

| Phase / claim | Exact inputs or revision | Command / checker | Result and evidence path | Owner / date |
| --- | --- | --- | --- | --- |
| E1–E3 | exact c949cb14 definition and primary source | source-v1/check_algebra.py; independent review spotchecks | 26 algebra +96 independent checks pass; source-v1/ and review-v1/ | parent/reviewer,2026-11-02 |
| E4 | execution-v3/ freeze and83cases | tools/check_ramberg_osgood.py; strict parity | 1141/backend and3276 parity values pass; retained v1 failure separate | parent,2026-11-02 |
| E5–E6 | canonical f0fa1a6b review | atlas.agent_review; merged preservation | accepted exact model; all prior entries preserved | parent/reviewer,2026-11-02 |
| E7 | full standard merged package | supported package, profile/browser and actual UI | 41 cases/15models; controls/recovery/export/import pass; browser-v1/ and release-v1/ | parent/reviewer,2026-11-02 |

## Review and integration identity

- Accepted agent-review record / hash: catalogue/agent-reviews/ramberg-osgood-agent-v1.json / f0fa1a6b56c4cbdeff70e10603fb804fc617cde53facc322f765b517d7095eed
- Approved model path / hash / scope: models/ramberg-osgood-ansys242.json / c949cb14269846ec46a7e8f25718e17e8c8eab394b6ee09204f029e1ca15a3e2; exact scope in canonical review and registry.
- Registry entry: catalogue/approved-models.json, ramberg-osgood-agent-v1-approval.
- Native / Wasm toolchain and artifact receipts: execution-v3/ source freeze, build receipts, logs and independent checker reports; 1141 checks/backend and3276 exact parity values.
- Packaged engine / catalogue hash: 29c12dec5d2ec9ce1ea84b8991757e4f03af1122a92095689c5b6f81b64c342f; release-v1/local-package-identities.json records exact asset hashes.
- Changed bytes after review (none, or new review/qualification): approved model and canonical review unchanged; additive merged integration separately checked in review-v1/merged-integration-assessment.md.

## Deployment receipt

- Delivered revision: ecd1f3b12381dd8edec34fe6121b80a0bd5792aa. Original authorized push37d70660 and failed correction runs remain in release-v1/v2/v3/v4; the final revision includes reviewed concurrent integration and test-only repairs.
- Actions run: https://github.com/benjym/constitutive-atlas/actions/runs/41357170257 — terminal success for both native, both Wasm, controlled-path and deploy jobs; release-v4/ci-terminal.json.
- Pages deployment: succeeded for that exact revision. The subsequent documentation closeout commit is distinct from the deployed source revision.
- Tested upload: authenticated artifact13103773962, ZIP SHA2563ff3890d82e3159492957a027a4f3d8b1805f207356f74627a32457d7dd5df6c; all1049 extracted files independently verified. release-v4/artifact-receipt.json and artifact-review.md.
- Live assets: release-v4/live-assets-v1.json passes80 exact HTTP200/hash comparisons, including engine, catalogue, model, database, source/review/approval and retained numerical records. No mismatches.
- Live model: https://benjym.github.io/constitutive-atlas/index.html#laboratory?model=ramberg-osgood-ansys242 . Actual browser initial run and explicit Reset recomputation succeeded,100increments, meaningful total-stress and volumetric plots, correct units and no console warnings/errors. release-v4/live-browser.txt, live-browser.png and live-console.json.
- Source/review links: live-disclosure.txt and live-catalogue.txt show primary ANSYS2024R2 link, exact accepted review, registered approval and scope, current/failed numerical records and accurate applicability limitation. Public internal targets match the tested upload; copyrighted original sources remain private.
- Database: all47 prior public manifest rows and24 approvals preserved;48 database identities,47 public entries. release-v4/upload-database.json.
- Remaining limitations: illustrative parameters, no experimental calibration/validation, energy, plastic memory, pore-pressure coupling or finite-deformation qualification. Fractional exponents have bounded integration coverage; direct tangent coverage is default n=5.

## Completion statement

Source complete; common native/Wasm executable scope independently numerically qualified; exact model independently agent approved; included in the general atlas and main laboratory; packaged controls/recovery/import/export verified; live deployment and example run verified. Experimental validation remains unassessed. All E0–E8 gates are complete for the named mechanical formulation. Previous failures and original frozen references are retained unchanged.
