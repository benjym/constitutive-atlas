# perzyna-comsol63 — end-to-end delivery ledger

Follow `docs/MODEL_DELIVERY_CHECKLIST.md` from the repository root; this ledger tracks its E0–E8 gates without creating a second assignment registry.

- Umbrella task: MODEL-perzyna-comsol63
- Lead / date: /root coordinator,2026-11-02
- Exact formulation and publication/version: COMSOL6.3 Perzyna, isotropic linear elasticity, associative von Mises, constant positive yield/no hardening; printed equation073: A·max(q/sigma_y−1,0)^n, n≥1; source UI discrepancy SC-PERZ-01 explicitly retained.
- Intended native/browser scope and exclusions: BE schedule only; three uniform public strain-hold/stress-hold/six-rate modes. No direct midpoint, finite strain/rotation, hardening, thermal/pore or experimental-validation claim.
- Source packet / dossier: source-v1/README.md and docs/models/perzyna-comsol63.md.
- Public profile / content provenance: `web/model-profile-data.mjs` entry, packet draft and [content contract](../../PUBLIC_MODEL_PROFILES.md)
- Detailed model-local checklist: [CHECKLIST.md](CHECKLIST.md) (copy every E0–E8 check and exit condition; retain evidence per item)
- Canonical checklist at assignment: current root docs/MODEL_DELIVERY_CHECKLIST.md SHA256 3b7448281ec0429a1425f71d53a1d9f048900442dca0ab8c30735b800f499efb,2026-11-02; exact policy copies in policy-v1/.
- Candidate definition path / SHA-256: `models/research/perzyna/perzyna-comsol63-mises-perfect-zero-spin-ode.json`,7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac.
- Worktree / authorized path whitelist: /private/tmp/atlas-perzyna-delivery-v1 on codex/perzyna-comsol63-delivery-v1, baseline54f409b37deaed0ab82a85cdac9f489bc65e1309. Coordinator owns new Perzyna packet/model/generic-profile build wiring/CI/tooling/web/catalogue integration only after scoped proposals and preservation review; no existing model migration or root shared Git operation.
- Implementation run ID(s): /root
- Independent review run ID: /root/perzyna_source_review, bounded E1–E3 ACCEPT; source-contract-review-v1/MANIFEST.json98fa6f52 verified88inputs/3outputs;1041checks. Actual E5 ACCEPT: /root/perzyna_scientific_e5, scientific-review-v1/MANIFEST.json979bc009, canonical record7cfcd238; all nine items pass.
- Build/execution owner and handoff: /root coordinator; explicit serial E4 and E7 board handoffs with terminal releases.
- Remote authorization reference (or pending): session prior push/main/CI/Pages authorization followed by new model end-to-end instruction; carry through concrete E7 release before remote action.

Use `[ ]` unstarted, `[-]` working/blocked, `[X]` verified complete. Add evidence beside each phase and link the detailed check results. Keep MODEL-perzyna-comsol63 open until E8 is verified; specialist task completion closes only that task.

- [X] **E0 — Claim/scope:** exact variant, prior-work inventory, owner/whitelist, dependencies and destination agreed.
- [X] **E1 — Sources:** readable complete law, durable private receipts, source locators, version reconciliation and rights.
- [X] **E2 — Contract:** complete v0.3 crosswalk, preparation/time/transaction/control contract and prospectively frozen references/gates; capabilities resolved.
- [X] **E3 — Transcription:** exact candidate validates/generates; independent equation/reference checks pass.
- [X] **E4 — Native/Wasm:** correct profile/interfaces, complete frozen numerical gates, rollback/recovery/restarts, useful preset, parity and regressions pass.
- [X] **E5 — Agent approval:** separate actual agent run, all nine checklist decisions, blocking findings resolved, exact accepted record and generated approval entry.
- [X] **E6 — Atlas:** qualified model/approval/source/evidence and source-backed public profile integrated through normal generation; profile-coverage check passes, prior models preserved and public metadata/current database checked.
- [X] **E7 — Packaged website:** public profile/card, parameter units, example guidance, related/laboratory links and narrow-screen layout inspected; real controls/plots, technical source/review disclosure, import/export/reset/failure recovery, measurement applicability/toggle where relevant, actual browser and package checks pass.
- [-] **E8 — Live delivery:** authorized scoped commit/push, all CI/deployment gates pass, live assets match tested upload and the live model run works; task-owned cleanup verified and any retained resources handed off explicitly.

## Current handoff

- Current phase / overall state: E0–E7 verified; exact scientific/native/Wasm, normal atlas/profile/database, fullstandardpackage and actualbrowser scope pass. E8 CI/Pages and exact upload/liveHTTP verified; actual live browser and final cleanup remain.
- Current owner: /root coordinator
- Blocker / missing evidence: No in-scope numerical or browser failure remains. Release106a9cf8 is pushed; all six CI jobs and Pages7489622279 pass. All469selectedliveassets match the authenticated1465file upload,20critical E7inputs unchanged and all9priorSQLite rowbags preserved. Actual live browser and final cleanup remain. Package-v1 missing local evidence failure and browser output-root denial are retained.
- Smallest next action / next owner: Complete brief queued actual live browser after MD1997 boundedpreflight terminal handoff, then final owned cleanup and evidence closeout.
- Resume when:
- Known limitations / retained failures:

## Evidence index

| Phase / claim | Exact inputs or revision | Command / checker | Result and evidence path | Owner / date |
| --- | --- | --- | --- | --- |
| E1–E3 source and transcription | Candidate7bfc3357, source-v1 sealbe6cf9f2 | source-v1/check_source_v2.py; separate source-contract-review-v1 |180cases/1106checks; reviewer1041checks ACCEPT | /root and separate reviewer,2026-11-02 |
| E4 numerical qualification | execution-v2 freeze7dcc4a01, E4seal2ae273fb | execution-v2/study.py, collect_wasm.mjs, parity.py |107cases/214calls/backend,6574comparisons/backend,15,667exact parity values | /root,2026-11-02 |
| E5 independent approval | Review7cfcd238;194direct bindings | atlas.agent_review --for-approval | All nine items ACCEPT; scientific-review-v1 | /root/perzyna_scientific_e5,2026-11-02 |
| E6 preservation | atlas-integration-v1 | PRESERVATION.json, DATABASE.json | All prior records/profiles preserved,49/49profile coverage | /root,2026-11-02 |
| E7 standard package and actual browser | package-v2, browser-v1 | Genuine standard builder; actual connected Playwright; check_exports.py |1466files;3modes/342reference values, replay/recovery, desktop/mobile PASS | /root,2026-11-02 |
| E8 published revision |106a9cf8c327c9c262a97eb86aa04dae3f6cadb8 | Current Actions41415383260 | SUCCESS all6jobs, Pages7489622279 SUCCESS; separate controlled41415383105 SUCCESS | /root,2026-11-02 |

## Review and integration identity

- Accepted agent-review record / hash: catalogue/agent-reviews/perzyna-comsol63-agent-v1.json7cfcd2381a1ced8cf97a98b7b3e9d197b883582f8c2365efe607e0ae2dd5cbb7, actual separate /root/perzyna_scientific_e5; all9pass194directartifacts.
- Approved model path / hash / scope: exact candidate7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac; accepted107case BE schedules/three presets, no broad exploratory/experimental claim.
- Registry entry: perzyna-comsol63-agent-v1-approval; exact generated atlas-integration-v1/approval-entry.json integrated into catalogue/approved-models.json.
- Native / Wasm toolchain and artifact receipts: execution-v2/actual-v1/, E4-EVIDENCE.json2ae273fb; original native then Wasm complete actualargv/exits/tool/source/artifactprepost,185pinned members.
- Packaged engine / catalogue hash: module722a6314c05361b3c737fc1e93ad45047b89c7a3a36b0e638b36e3e41a7a3d78; Wasm9ac88126bc0759c9bafb10e7f8fa1f0cee3c3c118e3a550f8910fc81de1bbaea; generatedmetadatadc65a68912251b2986a49481a0a0b7eeb4ede258a9a332eeae577a759b0b8d6a.
- Public-profile coverage check / packaged browser inspection:49/49profiles pass; browser-v1/MANIFEST.json/CHECKS.json/EXPORT-CHECKS.json and actualsaved UI artifacts.
- Changed bytes after review (none, or new review/qualification): no model or194acceptedartifact changes. Additive atlas/profile/browser/CI integration separately qualified at E6/E7; all prior scientific records and48profiles preserved.

## Deployment receipt

- Release commit:106a9cf8c327c9c262a97eb86aa04dae3f6cadb8, main.
- Actions run URL and terminal result: https://github.com/benjym/constitutive-atlas/actions/runs/41415383260 SUCCESS all6jobs; separate controlled-path https://github.com/benjym/constitutive-atlas/actions/runs/41415383105 SUCCESS.
- Pages deployment revision/result:106a9cf8c327c9c262a97eb86aa04dae3f6cadb8,7489622279 SUCCESS; exact run-bound status in live-release-v1/release-receipt-v1/.
- Tested upload / live asset comparison: artifact13131654461,ZIPde43be9ba3e3465a0b573d5d8866829fcde15cda16a5928922497bdffb71a6bb/240242482bytes;1465uploadfiles,20critical tested E7inputs exact,469selectedpublic HTTP200/SHA/size exact; all9priorSQLite rowbags preserved. live-release-v1/upload-live-v1/RESULT.json and full manifests.
- Live model URL / actual browser run evidence:
- Source/review link checks:
- Public profile / related links / profile asset identity checks:
- Remaining limitations:

## Cleanup and retained resources

Update throughout the task and at every final/blocked/ready-to-publish handoff. Follow [the repository cleanup rules](policy-v1/AGENTS.md#cleanup-and-storage-at-handoff); preserve required evidence and resumption inputs before deleting temporary copies.

| Task-owned path or process | Purpose / owner | Disposition (remove, stop, retain or hand off) | Retention reason / durable location | Verification / date |
| --- | --- | --- | --- | --- |
| Worktree ignored roots,11explicit paths | Own builds, cache, both site attempts and private sources | Retained until live consumers finish; then remove exact verified duplicates | Private task-ignored-resources-v1.tar.gz in shared .local/perzyna-retained-v1 |4900file lossless recovery, receipt live-release-v1/PRIVATE-CACHE-RETENTION.json |
| Root output/playwright/perzyna-comsol63-e7-v1 | Actual E7 browser artifacts | Removed16exact duplicate files | Original files in committed browser-v1/artifacts at106a9cf8 | live-release-v1/E7-DUPLICATE-CLEANUP.json,2026-11-02 |
| Preview54116; board monitor58655 | Finished local E7 consumers | Stopped/finished exit0 | Actual E7 records retained | browserabout:blank, no owned preview active |
| Root .local/perzyna-retained-v1 | Authenticated CI uploads and recovery archive | Retain private | Reproducible original upload and cleanup evidence | /root owns; digests verified before use |

- Removed paths / stopped process identities:
- Evidence retained: exact hashes, archive recovery checks and usable receipt locations:
- Worktree removal: clean status, retained commit and preserved required ignored outputs:
- Cleanup remaining / blocker / next owner: active task worktree and private source originals retained by /root for final live delivery; full local package/browser finished, preview stopped. Borrowed Bingham assets remain read-only and outside task cleanup ownership.
- Space reclaimed / free space after substantial cleanup:

## Completion statement

Record separately: source complete; executable scope; independent numerical qualification; agent approval; atlas inclusion and public profile; packaged browser; live deployment; experimental validation. An absent experimental comparison can be an explicit limitation. A missing public profile, missing website support or unverified deployment cannot be called full delivery.

Active resource inventory: isolated worktree /private/tmp/atlas-perzyna-delivery-v1 and its ignored private originals/cache retained for E4–E8 by /root; durable original copies verified under shared ignored .local/private-sources/perzyna-comsol63/source-v1; qualified native/Wasm artifacts and approved public assets retained for E8; completed preview stopped.

E5 transaction clarification: accepted schedule scope preserves completed samples and returns the last committed prefix on failure; it does not roll the whole schedule back to its initial state. Source-v1 prospective wording is retained; independent scientific-review-v1 explicitly reconciles this boundary against actual late-budget evidence.

CI orchestration source checks: ci-driver-check-v1/RESULT.json passes five manufactured scenarios with zero compiled calls. Native/paired serial ordering, consumer-failure post-verification, capture failure and stale metadata rejection checked. The original mock classifier failure is retained in ATTEMPT1.txt; these checks do not substitute for actual CI.

E7 package-v1: genuine normal builder exit1,416s; source inventories unchanged (exact gzip recovery retained). New Perzyna all3modes/342comparisons/replay/recovery passed. Existing implicit-path guard stopped on absent ignored local numerical evidence, restored exactee7e4ad4 from qualified prior tree and retained locally in package-v1/restored-evidence/. All remaining implicit/orthotropic/Hill pure packaging guards now pass, without compiled calls. Serial slot released; v2 full retry queued after md1997 local CI. No browser/live claim yet.

E6/E7 completion: standard package-v2 genuine exit0 in374s, all tracked sourcepre/post exact;1466file manifest. Existing supported ordinary/named gate exit0; all prior scientific package gates pass. Actual browser profile/laboratory/default3modes and342independent scalar comparisons PASS; edited coefficients/full13history, all6stress/3plots, cancelled/latest requests, exact real-file import/rerun, stale import rejection, invalid and true backend error/recovery,23fetched identities,375px localtable scroll/no pageoverflow, relatedBingham route and4technical links HTTP200,0console/networkerrors. See immutable package-v2/ and browser-v1/ manifests. Server54116 stopped exit0; browserabout:blank. Session58655 readonly board monitor ended exit0 at actual MD release.

E8 retention checkpoint: all4900task-owned ignored resource files (2,253,654,436bytes) preserved in private .local/perzyna-retained-v1/task-ignored-resources-v1.tar.gz, SHA7c9f2968bdd0df6bb4b2d43ee7ac1160b9c6ea5da266ec6c5693787f54fbe11e,498199596bytes. Every archive member recovered and hash/size checked. Includes both local site attempts, exact local caches/builds and private source copies; borrowed coownerBinghamresources excluded. Retention receipt and script in live-release-v1/. Deletion waits until fresh CI/live verification.

E8 actual native CI receipts: both macos26 and Ubuntu107cases/214calls/6574comparisons PASS, all5actualoperations exit0, source/buildrecords unchanged; authenticatedZIPdigests verified. Separate CIstillrequires bothpairedWasm/fullpackage and remainingnative/controlled/deploy jobs. See live-release-v1/ci-artifacts/.

E8 cleanup checkpoint1: live-release-v1/IGNORED-CLEANUP-1.json records3411ownfiles/1,151,149,126duplicatebytes removed from9explicitroots after fresh source and losslessarchive verification. Currentqualifiedsite and privateoriginal copies remain until liveconsumersfinish; all originalbytes remain in private498MBarchive. E7rootbrowserduplicate16files also removed after exactGitblob comparison. No coownerasset or paper path touched.

E8 actual CI complete: allsix41415383260 jobsSUCCESS at106a9cf8; controlled41415383105 SUCCESS and Pages7489622279 SUCCESS. All4authenticated PerzCIuploads pass original107/214/6574gates; bothpairedOS15,667physicalvalues exactly equal. CIcollectorv1 expected nonexistent Wasm reportfile; frozen study emitsassessment stdout instead. Originalfailedcollector/RESULT retained, distinct extraction-onlyv2 readsactualstdout withunchangedgates and all4PASS. See CI-COLLECTOR-CORRECTION-V2.json/ci-artifacts-v2/. No CI/scientific gatefailure inferredfromcollectorpathassumption.
