# bingham-comsol63 — end-to-end delivery ledger

Copy to `docs/ingestion/bingham-comsol63/DELIVERY.md`. Follow `docs/MODEL_DELIVERY_CHECKLIST.md` from the repository root; this ledger tracks its E0–E8 gates without creating a second assignment registry.

- Umbrella task: MODEL-bingham-comsol63
- Lead / date: /root coordinator,2026-11-02
- Exact formulation and publication/version: COMSOL6.3 perfect associative von Mises Bingham elastoviscoplasticity plus isotropic linear elasticity; constant positive yield stress, dry total stress, small strain fixed spatial frame/zero spin.
- Intended native/browser scope and exclusions: common physical-time ODE native/Wasm, all-six strain-rate and mixed schedule API; main atlas embedded relaxation/creep/rate controls. No hardening, temperature, finite rotation/strain or experimental validation.
- Source packet / dossier: source-v1/README.md; docs/models/bingham-comsol63.md
- Detailed model-local checklist: [CHECKLIST.md](CHECKLIST.md) (copy every E0–E8 check and exit condition; retain evidence per item)
- Canonical checklist at assignment: docs/MODEL_DELIVERY_CHECKLIST.md SHA256b370c525b8650492c8b0fb49e1107a765009b5be8f16818675196541eb128289,2026-11-02. All53checks copied into CHECKLIST.md.
- Candidate definition path / SHA-256: models/research/bingham/bingham-comsol63-mises-perfect-zero-spin-ode.json /6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850
- Worktree / authorized path whitelist: /private/tmp/atlas-bingham-delivery-v1/ baseb529a0ef. Parent owns new model packet, models/research/bingham/, cmake/bingham/ and model-specific study/tools/tests/dossier; interface worker owns only four new files in WEB task. Shared hooks require exact scoped archival before edits.
- Implementation run ID(s): /root coordinator; /root/bingham_source source/transcription; /root/bingham_interface transport/UI/builder.
- Independent review run ID: /root/bingham_review (separate run, no implementation)
- Build/execution owner and handoff: coordinator /root only; queued behind active BUILD-ramberg-osgood-v1; native then Wasm atlas_bingham_solver Release --parallel1. No compiled Bingham observation yet.
- Remote authorization reference (or pending): pending new-model publication. Prior literal instruction scoped OCC; complete reviewed E7 and concrete release before final publication permission.

Use `[ ]` unstarted, `[-]` working/blocked, `[X]` verified complete. Add evidence beside each phase and link the detailed check results. Keep MODEL-bingham-comsol63 open until E8 is verified; specialist task completion closes only that task.

- [X] **E0 — Claim/scope:** exact variant, prior-work inventory, owner/whitelist, dependencies and destination agreed.
- [X] **E1 — Sources:** readable complete law, durable private receipts, source locators, version reconciliation and rights.
- [X] **E2 — Contract:** complete v0.3 crosswalk, preparation/time/transaction/control contract and prospectively frozen references/gates; capabilities resolved.
- [X] **E3 — Transcription:** exact candidate validates/generates; independent equation/reference checks pass.
- [-] **E4 — Native/Wasm:** correct profile/interfaces, complete frozen numerical gates, rollback/recovery/restarts, useful preset, parity and regressions pass.
- [ ] **E5 — Agent approval:** separate actual agent run, all nine checklist decisions, blocking findings resolved, exact accepted record and generated approval entry.
- [ ] **E6 — Atlas:** qualified model/approval/source/evidence integrated through normal generation; prior models preserved and public metadata/current database checked.
- [ ] **E7 — Packaged website:** real controls/plots, source/review scope, import/export/reset/failure recovery, measurement applicability/toggle where relevant, actual browser and package checks pass.
- [ ] **E8 — Live delivery:** authorized scoped commit/push, all CI/deployment gates pass, live assets match tested upload and the live model run works.

## Current handoff

- Current phase / overall state: E0–E3 complete; E4 externally blocked by reserved shared build slot; E6/E7 static integration prepared and independently reviewed
- Current owner: /root coordinator
- Blocker / missing evidence: E4 not yet executed; shared BUILD-ramberg-osgood-v1 active. R1–R3 assessor findings corrected and independently accepted; REPORT-v4 accepts138current build closure pins prospectively.
- Smallest next action / next owner: shared Ramberg build owner explicitly releases slot; parent then claims serial native qualification before Wasm.
- Resume when: BUILD-ramberg-osgood-v1 owner explicitly releases slot, or user confirms that run finished and releases it. Fresh shared-board re-read then claim Bingham before native configure/build; Kelvin/MD queues follow Bingham. Async user coordination question pending; no publication approval requested.
- Known limitations / retained failures: Python attempt1 harness keyword error retained; original prospective assessor R1–R3 reports/bytes retained; routing-checks-attempt1 retained14pass/1fail because old exact five-controller membership needs deliberate sixth-controller policy extension, with old test archival being prepared. No numerical gate changed.

## Evidence index

| Phase / claim | Exact inputs or revision | Command / checker | Result and evidence path | Owner / date |
| --- | --- | --- | --- | --- |
| E1–E3 source/contract/transcription | candidate6c5ee29c, source-v1 exact receipts | source324identities; tests/test_bingham_candidate.py |108analyticcases,4passingPythonchecks; first harnessfailure retained | sourceworker / parent2026-11-02 |
| Prospective independent review | freeze-v1/v2/v3/v4 + build-inputs-v1 | independent-review-v1/REPORT-v1.md through REPORT-v4.md | R1–R3 resolved;7syntheticcorruptions rejected;138sourcepins exact | separate /root/bingham_review |
| Preservation and shared hooks | release-bindings-v1/prepared-v1/applied.json |49archive/review/export/evidence tests (attempt2 after routing-test preservation) | allpass archive-checks-attempt1.log;9oldsourcebytes+11logicalmaps preserved | coordinator2026-11-02 |
| Interface preparation | interface-v1/POLICY-v2.json |7staticcontracttests; executable checker notyet run | fixed reviewed-engine binding;3mode full-state checks prepared | interfaceworker / coordinator |

## Review and integration identity

- Accepted agent-review record / hash:
- Approved model path / hash / scope:
- Registry entry:
- Native / Wasm toolchain and artifact receipts:
- Packaged engine / catalogue hash:
- Changed bytes after review (none, or new review/qualification): provision_bingham_assets.py destination safety v2 after prospective REPORT-v5; prior helper retained atlas-v1/provision-before-v2.py; final E5/interface review must bind current version.

## Deployment receipt

- Release commit:
- Actions run URL and terminal result:
- Pages deployment revision/result:
- Tested upload / live asset comparison:
- Live model URL / actual browser run evidence:
- Source/review link checks:
- Remaining limitations:

## Completion statement

Record separately: source complete; executable scope; independent numerical qualification; agent approval; atlas inclusion; packaged browser; live deployment; experimental validation. An absent experimental comparison can be an explicit limitation. Missing website support or unverified deployment cannot be called full delivery.

## Exact next execution handoff

No Bingham compiled model call or compilation has occurred. All138build-inputs-v1 pins rechecked exact in pre-build-bindings-check.json. Actual versions are saved in toolchain-versions.json; a private writable Emscripten cache was copied from installed6.0.8 and all1778initial cachefiles pinned separately. The canonical source/model/numerical gates are unchanged.

After slot release, run from `/private/tmp/atlas-bingham-delivery-v1`:

1. Re-read current shared board and explicitly claim BUILD-bingham-comsol63-v1.
2. `cmake -S cmake/bingham -B build-native -DCMAKE_BUILD_TYPE=Release`, then `cmake --build build-native --target atlas_bingham_solver --parallel 1`, logs retained.
3. Exact generated metadata/describe checks and `python3 -B tools/test_bingham_native.py --solver build-native/atlas_bingham_solver --output docs/ingestion/bingham-comsol63/execution-v1/native-attempt1.json`.
4. Understand every native observation before Wasm. Configure/build same explicit target using `EM_CACHE=$PWD/.local/emscripten-cache`, serial; copy original bingham.js bytes to bingham.mjs. Use frozen collect_wasm.mjs, study.py assess and parity.py. No gate relaxation.
5. Bind actual toolchain/flags/artifacts/outputs in real build-receipt.json; create E5-bound three-file sealed ZIP/index. Actual separate-agent all-nine final review, additive approval/catalogue/database and evidence, full normal builder with restored prior engines, real browser qualification, concrete scoped release. Only then remaining remote permission if still absent.

Prior engines restored under `.local/prior-engines/` for ordinary,SLS,Burgers,J2,power-creep,Maxwell,implicit-path. Controlled-path uses existing exact `docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand`. Restoration order mistake for implicit-path retained; correct existing interface witness restore then provision succeeded. No prior engine was executed here. Baseline-public-records.json and atlas-v1/POLICY.md prospectively freeze complete coverage and row preservation. Publication graph remains unchanged because vendor manual has no verified DOI; exact URLs remain source records.
