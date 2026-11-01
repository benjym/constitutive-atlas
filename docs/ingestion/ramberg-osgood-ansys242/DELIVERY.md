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
- [ ] **E8 — Live delivery:** authorized scoped commit/push, all CI/deployment gates pass, live assets match tested upload and the live model run works.

## Current handoff

- Current phase / overall state: E0–E7 verified; E8 first authorized release failed two Python checks; separate reviewed corrections and focused Python3.12/3.14 tests pass. Corrected full CI/live qualification pending.
- Current owner: coordinating parent /root.
- Blocker / missing evidence: awaiting terminal CI, actual upload, deployment and live comparison/browser verification.
- Smallest next action / next owner: parent monitors run41348645083, retains tested upload and verifies live assets/browser before closing E8.
- Resume when: work continues under explicit authorization; no additional human scientific approval required.
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

- Release commit: 37d70660e3561c342bb114716c233a3d06651bcb, pushed main under explicit authorization.
- Actions run URL and terminal result: https://github.com/benjym/constitutive-atlas/actions/runs/41348645083 (Linux native Python failed; original log retained in release-v2).
- Pages deployment revision/result:
- Tested upload / live asset comparison:
- Live model URL / actual browser run evidence:
- Source/review link checks:
- Remaining limitations:

## Completion statement

Record separately: source complete; executable scope; independent numerical qualification; agent approval; atlas inclusion; packaged browser; live deployment; experimental validation. An absent experimental comparison can be an explicit limitation. Missing website support or unverified deployment cannot be called full delivery.
