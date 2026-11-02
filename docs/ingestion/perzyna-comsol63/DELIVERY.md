# perzyna-comsol63 — end-to-end delivery ledger

Copy to `docs/ingestion/perzyna-comsol63/DELIVERY.md`. Follow `docs/MODEL_DELIVERY_CHECKLIST.md` from the repository root; this ledger tracks its E0–E8 gates without creating a second assignment registry.

- Umbrella task: MODEL-perzyna-comsol63
- Lead / date: /root coordinator,2026-11-02
- Exact formulation and publication/version: COMSOL6.3 Perzyna, isotropic linear elasticity, associative von Mises, constant positive yield/no hardening; printed equation073: A·max(q/sigma_y−1,0)^n, n≥1; source UI discrepancy SC-PERZ-01 explicitly retained.
- Intended native/browser scope and exclusions: BE schedule only; three uniform public strain-hold/stress-hold/six-rate modes. No direct midpoint, finite strain/rotation, hardening, thermal/pore or experimental-validation claim.
- Source packet / dossier: source-v1/README.md and docs/models/perzyna-comsol63.md.
- Public profile / content provenance: `web/model-profile-data.mjs` entry, packet draft and [content contract](../PUBLIC_MODEL_PROFILES.md)
- Detailed model-local checklist: [CHECKLIST.md](CHECKLIST.md) (copy every E0–E8 check and exit condition; retain evidence per item)
- Canonical checklist at assignment: current root docs/MODEL_DELIVERY_CHECKLIST.md SHA256 3b7448281ec0429a1425f71d53a1d9f048900442dca0ab8c30735b800f499efb,2026-11-02; exact policy copies in policy-v1/.
- Candidate definition path / SHA-256: `models/research/perzyna/perzyna-comsol63-mises-perfect-zero-spin-ode.json`,7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac.
- Worktree / authorized path whitelist: /private/tmp/atlas-perzyna-delivery-v1 on codex/perzyna-comsol63-delivery-v1, baseline54f409b37deaed0ab82a85cdac9f489bc65e1309. Coordinator owns new Perzyna packet/model/generic-profile build wiring/CI/tooling/web/catalogue integration only after scoped proposals and preservation review; no existing model migration or root shared Git operation.
- Implementation run ID(s):
- Independent review run ID: /root/perzyna_source_review, bounded E1–E3 ACCEPT; source-contract-review-v1/MANIFEST.json98fa6f52 verified88inputs/3outputs;1041checks. Actual E5 pending.
- Build/execution owner and handoff:
- Remote authorization reference (or pending): session prior push/main/CI/Pages authorization followed by new model end-to-end instruction; carry through concrete E7 release before remote action.

Use `[ ]` unstarted, `[-]` working/blocked, `[X]` verified complete. Add evidence beside each phase and link the detailed check results. Keep MODEL-perzyna-comsol63 open until E8 is verified; specialist task completion closes only that task.

- [X] **E0 — Claim/scope:** exact variant, prior-work inventory, owner/whitelist, dependencies and destination agreed.
- [X] **E1 — Sources:** readable complete law, durable private receipts, source locators, version reconciliation and rights.
- [X] **E2 — Contract:** complete v0.3 crosswalk, preparation/time/transaction/control contract and prospectively frozen references/gates; capabilities resolved.
- [X] **E3 — Transcription:** exact candidate validates/generates; independent equation/reference checks pass.
- [X] **E4 — Native/Wasm:** correct profile/interfaces, complete frozen numerical gates, rollback/recovery/restarts, useful preset, parity and regressions pass.
- [X] **E5 — Agent approval:** separate actual agent run, all nine checklist decisions, blocking findings resolved, exact accepted record and generated approval entry.
- [-] **E6 — Atlas:** qualified model/approval/source/evidence and source-backed public profile integrated through normal generation; profile-coverage check passes, prior models preserved and public metadata/current database checked.
- [ ] **E7 — Packaged website:** public profile/card, parameter units, example guidance, related/laboratory links and narrow-screen layout inspected; real controls/plots, technical source/review disclosure, import/export/reset/failure recovery, measurement applicability/toggle where relevant, actual browser and package checks pass.
- [ ] **E8 — Live delivery:** authorized scoped commit/push, all CI/deployment gates pass, live assets match tested upload and the live model run works; task-owned cleanup verified and any retained resources handed off explicitly.

## Current handoff

- Current phase / overall state: E0–E5 verified; accepted exact scientific/native/Wasm scope. E6 atlas/profile/database preservation passed; standard package and actual browser/live gates remain.
- Current owner: /root coordinator
- Blocker / missing evidence: actual independent nine-item E5 review, atlas integration, packaged/live browser and CI delivery remain. No in-scope numerical failure.
- Smallest next action / next owner: seal exact E0–E4 commit; dispatch independent scientific reviewer against E4-EVIDENCE.json2ae273fb.
- Resume when:
- Known limitations / retained failures:

## Evidence index

| Phase / claim | Exact inputs or revision | Command / checker | Result and evidence path | Owner / date |
| --- | --- | --- | --- | --- |
| | | | | |

## Review and integration identity

- Accepted agent-review record / hash: catalogue/agent-reviews/perzyna-comsol63-agent-v1.json7cfcd2381a1ced8cf97a98b7b3e9d197b883582f8c2365efe607e0ae2dd5cbb7, actual separate /root/perzyna_scientific_e5; all9pass194directartifacts.
- Approved model path / hash / scope:
- Registry entry:
- Native / Wasm toolchain and artifact receipts:
- Packaged engine / catalogue hash:
- Public-profile coverage check / packaged browser inspection:
- Changed bytes after review (none, or new review/qualification):

## Deployment receipt

- Release commit:
- Actions run URL and terminal result:
- Pages deployment revision/result:
- Tested upload / live asset comparison:
- Live model URL / actual browser run evidence:
- Source/review link checks:
- Public profile / related links / profile asset identity checks:
- Remaining limitations:

## Cleanup and retained resources

Update throughout the task and at every final/blocked/ready-to-publish handoff. Follow [the repository cleanup rules](../../AGENTS.md#cleanup-and-storage-at-handoff); preserve required evidence and resumption inputs before deleting temporary copies.

| Task-owned path or process | Purpose / owner | Disposition (remove, stop, retain or hand off) | Retention reason / durable location | Verification / date |
| --- | --- | --- | --- | --- |
| | | | | |

- Removed paths / stopped process identities:
- Evidence retained: exact hashes, archive recovery checks and usable receipt locations:
- Worktree removal: clean status, retained commit and preserved required ignored outputs:
- Cleanup remaining / blocker / next owner: active task worktree and private source originals retained by /root for full delivery; no build/package/server yet.
- Space reclaimed / free space after substantial cleanup:

## Completion statement

Record separately: source complete; executable scope; independent numerical qualification; agent approval; atlas inclusion and public profile; packaged browser; live deployment; experimental validation. An absent experimental comparison can be an explicit limitation. A missing public profile, missing website support or unverified deployment cannot be called full delivery.

Active resource inventory: isolated worktree /private/tmp/atlas-perzyna-delivery-v1 and its ignored private originals/cache retained for E4–E8 by /root; durable original copies verified under shared ignored .local/private-sources/perzyna-comsol63/source-v1; no preview process or compiled artifact yet.

E5 transaction clarification: accepted schedule scope preserves completed samples and returns the last committed prefix on failure; it does not roll the whole schedule back to its initial state. Source-v1 prospective wording is retained; independent scientific-review-v1 explicitly reconciles this boundary against actual late-budget evidence.
