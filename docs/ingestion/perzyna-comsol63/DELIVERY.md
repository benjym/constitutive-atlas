# Perzyna COMSOL 6.3 — delivery ledger

This ledger follows [the E0–E8 checklist](../../MODEL_DELIVERY_CHECKLIST.md) and the [model-local checklist](CHECKLIST.md). Exact assignment policies remain in [policy-v1](policy-v1/).

- **Umbrella / lead:** MODEL-perzyna-comsol63; /root coordinator, 2 November 2026.
- **Exact formulation:** the printed COMSOL 6.3 yield-normalized Perzyna law, isotropic linear elasticity, associative von Mises flow, constant positive yield stress and no hardening. Flow rate is `A max(q/sigma_y - 1, 0)^n`.
- **Definition:** `models/research/perzyna/perzyna-comsol63-mises-perfect-zero-spin-ode.json`; SHA-256 `7bfc33578593fab8c806dd1cd6473f54b9e2cd5cbf07ecacaffd328118e103ac`.
- **Contract:** explicit schema 0.3; physical-time, infinitesimal 3D, fixed spatial axes/zero spin, compression-positive Mandel tensors and dry total Cauchy stress. Complete state is six total strains, six viscoplastic strains and accumulated equivalent viscoplastic strain.
- **Supported execution:** backward-Euler schedules; public strain-hold relaxation, stress-hold creep and six-component constant strain rate. The frozen study samples `n = 1, 1.5, 2, 3` and the disclosed custom tuple; it does not establish accuracy over the entire editable parameter envelope.
- **Source / profile:** [source and contract](source-v1/README.md), [scientific dossier](../../models/perzyna-comsol63.md), and the exact entry in `web/model-profile-data.mjs`.
- **Independent runs:** /root/perzyna_source_review for source/contract; /root/perzyna_scientific_e5 for actual scientific approval. Implementation and integration belong to /root.
- **Assignment:** isolated `/private/tmp/atlas-perzyna-delivery-v1`, branch `codex/perzyna-comsol63-delivery-v1`, baseline `54f409b37deaed0ab82a85cdac9f489bc65e1309`. Ownership covers only Perzyna and its explicitly scoped additive integration. Shared root staging and unrelated files remain untouched.
- **Remote authority:** the session's main/CI/Pages instruction followed by the next-model end-to-end assignment; no additional human scientific signature is required.

## Stage status

- [X] **E0 — Claim and scope:** exact variant, source inventory, ownership, dependencies and delivery policy recorded.
- [X] **E1 — Sources:** readable equations and version reconciliation; 20 original private source files retained with exact receipts.
- [X] **E2 — Contract:** complete formulation/state/units/time/control/transaction contract and prospectively frozen references and gates.
- [X] **E3 — Transcription:** normal validation/generation and independent source-derived checks pass.
- [X] **E4 — Native/Wasm:** the frozen numerical study, solved creep rates, restart, retained-prefix failure/recovery and backend parity pass.
- [X] **E5 — Agent approval:** separate actual nine-item review accepts the exact bytes and bounded numerical scope.
- [X] **E6 — Atlas:** normal catalogue, approval, sources, public profile and database export integrated; prior entries and profiles preserved.
- [X] **E7 — Packaged website:** full standard package and actual desktop/mobile browser controls, plots, replay/recovery and source/review disclosure pass.
- [-] **E8 — Live delivery:** application, all CI jobs, Pages, actual upload/live assets and live browser pass. Pending final clean worktree removal.

## Current handoff

- **State:** live delivery verified; final clean worktree removal remains.
- **Owner / next action:** /root will commit the final browser/cleanup evidence, retain and verify the branch bundle, remove the clean completed worktree through Git, and publish the evidence-only closeout.
- **Scientific blockers:** none within the approved scope.
- **Limitations:** no experimental calibration/validation, vendor-software equivalence, finite deformation/rotation, hardening, thermal or pore-fluid response, FE-host tangent or broad custom-input accuracy claim. The source theory/settings discrepancy SC-PERZ-01 is disclosed rather than silently reconciled.

## Evidence index

| Stage | Reproducible check / exact evidence | Verified result |
| --- | --- | --- |
| E1–E3 | [source packet](source-v1/), source seal `be6cf9f2…`, [source review](source-contract-review-v1/) | 180 cases / 1,106 author checks; 1,041 independent review checks; exact candidate validates/generates. |
| E4 | [execution-v2](execution-v2/), freeze `7dcc4a01…`, E4 seal `2ae273fb…`; `study.py`, `collect_wasm.mjs`, `parity.py` | 107 cases / 214 calls / 6,574 state-stress comparisons per backend, 264 solved-rate checks; 15,667 physical numbers agree exactly. |
| E5 | [scientific review](scientific-review-v1/), [canonical record](../../../catalogue/agent-reviews/perzyna-comsol63-agent-v1.json); `python3 -B -m atlas.agent_review … --for-approval` | All nine items accepted; 194 direct artifact bindings. Final normal validator still accepts unchanged bytes. |
| E6 | [integration preservation](atlas-integration-v1/PRESERVATION.json), [database](atlas-integration-v1/DATABASE.json) | All 15 ordinary definitions, 48 prior public profiles and prior catalogue/approval records preserved; 49/49 profiles covered. |
| E7 | [package-v2](package-v2/), [actual local browser](browser-v1/) | Genuine standard builder exit 0; all existing supported gates; three modes / 342 independent scalar comparisons, complete history, replay/recovery and narrow-screen checks. |
| E8 CI | [terminal release receipt](live-release-v1/release-receipt-v1/RESULT.json), [four actual CI uploads](live-release-v1/ci-artifacts-v2/) | All six required jobs pass. Both OS pairs independently pass the original study and 15,667 exact physical-value comparisons. |
| E8 upload/live | [upload/live result](live-release-v1/upload-live-v1/RESULT.json), [scope](live-release-v1/UPLOAD-SCOPE.json) | 1,465 authenticated upload files; 20 critical tested inputs unchanged; 469 selected live assets exact. All nine prior SQLite row bags preserved, integrity and foreign-key checks pass. |
| E8 browser | [live checks](live-release-v1/browser-v1/CHECKS.json), [numerical checks](live-release-v1/browser-v1/EXPORT-CHECKS.json), [raw observations](live-release-v1/browser-v1/ACTUAL-TOOL-RESULTS.json) | Three real UI runs / 342 reference comparisons; complete results exactly match E7; 25 browser-fetched identities; four technical links HTTP 200; five parameter rows, 375 px no overflow, zero console warnings/errors or request failures. |

## Approval and transaction identity

- **Accepted record:** `perzyna-comsol63-agent-v1.json`, SHA-256 `7cfcd2381a1ced8cf97a98b7b3e9d197b883582f8c2365efe607e0ae2dd5cbb7`.
- **Registry entry:** `perzyna-comsol63-agent-v1-approval`, generated through the normal approval exporter.
- **Public engine:** module SHA-256 `722a6314c05361b3c737fc1e93ad45047b89c7a3a36b0e638b36e3e41a7a3d78`; Wasm `9ac88126bc0759c9bafb10e7f8fa1f0cee3c3c118e3a550f8910fc81de1bbaea`; metadata `dc65a68912251b2986a49481a0a0b7eeb4ede258a9a332eeae577a759b0b8d6a`.
- No candidate or accepted scientific artifact changed after E5. Additive web/CI integration was separately qualified at E6–E8.
- A failed schedule preserves completed samples and returns its last committed prefix; it does **not** atomically reset the entire schedule. The original prospective wording is retained and explicitly reconciled by the independent review.

## Deployment receipt

- **Application revision:** `106a9cf8c327c9c262a97eb86aa04dae3f6cadb8`, published to main.
- **CI:** [Verify and publish 41415383260](https://github.com/benjym/constitutive-atlas/actions/runs/41415383260), all six jobs SUCCESS; [separate controlled-path run 41415383105](https://github.com/benjym/constitutive-atlas/actions/runs/41415383105), SUCCESS.
- **Pages deployment:** `7489622279`, exact application revision and run, SUCCESS.
- **Authenticated upload:** artifact `13131654461`, 240,242,482-byte ZIP, SHA-256 `de43be9ba3e3465a0b573d5d8866829fcde15cda16a5928922497bdffb71a6bb`.
- **Live model:** [Perzyna in the general laboratory](https://benjym.github.io/constitutive-atlas/index.html#laboratory?model=perzyna-comsol63-mises-perfect-zero-spin-ode). [Public profile](https://benjym.github.io/constitutive-atlas/index.html#catalogue/perzyna-comsol63-mises-perfect-zero-spin-ode).
- **Live export:** 50 model identities, 208 sources, 60 publications, 27 approvals and 23 agent reviews. All prior rows remain, with multiplicity, across nine tables.
- HTTP verification covers every selected served application/document asset. The full authenticated manifest also retains 995 unrelated raw experiment payloads and the ephemeral implicit-path guard report; those 996 files were excluded by the prospectively frozen HTTP selector. Local `.nojekyll` and random temporary guard-report names are documented separately.
- Final evidence-only `[skip ci]` commits record these results; they do not change the tested application, scientific scope or deployed engine.

## Cleanup and retained resources

| Resource | Disposition / durable evidence |
| --- | --- |
| All 11 task-owned ignored build/cache/site/private-copy roots | Removed after fresh source hashes and lossless archive recovery. [First cleanup](live-release-v1/IGNORED-CLEANUP-1.json): 3,411 files / 1,151,149,126 bytes. [Second cleanup](live-release-v1/IGNORED-CLEANUP-2.json): 1,489 files / 1,102,505,310 bytes. |
| Exact ignored originals | Retained privately in root `.local/perzyna-retained-v1/task-ignored-resources-v1.tar.gz`, 498,199,596 bytes; SHA-256 `7c9f2968bdd0df6bb4b2d43ee7ac1160b9c6ea5da266ec6c5693787f54fbe11e`. All 4,900 members recovered and verified. [Receipt](live-release-v1/PRIVATE-CACHE-RETENTION.json). |
| Original copyrighted source files | All 20 durable private copies reverified before removing worktree duplicates. [Original retention receipt](PRIVATE-SOURCE-RETENTION.json), [final check](live-release-v1/FINAL-PRIVATE-SOURCE-CHECK.json). No originals published. |
| Actual browser evidence and temporary Python caches | Exact public browser copies retained in the packet; owned root duplicates/automatic files and dedicated-worktree caches archived and removed. [Final small-resource cleanup](live-release-v1/FINAL-SMALL-RESOURCE-CLEANUP.json), plus retained E7 cleanup receipts. |
| Raw CI and Pages uploads | Retain authenticated original ZIPs privately under root `.local/perzyna-retained-v1/`; public digests/manifests and genuine reports are committed. |
| Owned processes and browser | E7 preview 54116, board monitor 58655, CI watch 95361, download 29807, HTTP check 17098 and cleanup 99079 ended. Browser returned to `about:blank`; cache and 1280 × 900 viewport restored; no live preview was started. [Slot release](live-release-v1/browser-v1/SLOT-RELEASE.json). |
| Completed isolated worktree | Pending final clean worktree removal. The retained commit and verified branch bundle must precede `git worktree remove`; no forced removal or shared root index operation. |
| Other owners' resources | Borrowed Bingham assets, other worktrees, shared SDKs/caches and root `paper/` are untouched. |

The two large cleanups remove 2,253,654,436 duplicate regular-file bytes. Free space after the second cleanup was 20,294,062,080 bytes; concurrent owners may change global free space. Required archives, private originals and raw authenticated uploads remain deliberately retained by /root.

## Retained failures and corrections

The original source harness failure, rejected unexecuted execution-v1 plan, independent-review harness corrections, CI mock failure, package-v1 missing local witness and browser CLI/output-root failures remain in their separately identified packets. No numerical gate was relaxed. E8 also retains the [collector stdout-location correction](live-release-v1/CI-COLLECTOR-CORRECTION-V2.json), [automatic-download cleanup mismatch](live-release-v1/E7-AUTO-CLEANUP-ATTEMPT1.json) and [checkpoint audit correction](live-release-v1/CHECKPOINT-AUDIT-CORRECTION.json). These extraction/housekeeping failures are distinguished from the genuine successful model/CI/live results.

## Completion statement

Source complete; declarative executable scope qualified; independent numerical references and separate agent approval accepted; normal atlas/public profile and packaged browser complete; CI, exact Pages delivery, live bytes/database and actual live browser verified. Experimental validation is not claimed. Final clean worktree removal remains before E8 is closed.
