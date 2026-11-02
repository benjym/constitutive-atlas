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
- Independent review run IDs: /root/bingham_review (prospective/runtime/integration reviews); /root/bingham_scientific_e5 (separate all-nine scientific review; no Bingham implementation authorship).
- Build/execution owner and handoff: coordinator /root only; queued behind active BUILD-ramberg-osgood-v1; native then Wasm atlas_bingham_solver Release --parallel1. Native/Wasm v5 and physical parity qualified; separate all-nine scientific review accepted. The serial execution slot is released.
- Remote authorization reference (or pending): pending new-model publication. Prior literal instruction scoped OCC; complete reviewed E7 and concrete release before final publication permission.

Use `[ ]` unstarted, `[-]` working/blocked, `[X]` verified complete. Add evidence beside each phase and link the detailed check results. Keep MODEL-bingham-comsol63 open until E8 is verified; specialist task completion closes only that task.

- [X] **E0 — Claim/scope:** exact variant, prior-work inventory, owner/whitelist, dependencies and destination agreed.
- [X] **E1 — Sources:** readable complete law, durable private receipts, source locators, version reconciliation and rights.
- [X] **E2 — Contract:** complete v0.3 crosswalk, preparation/time/transaction/control contract and prospectively frozen references/gates; capabilities resolved.
- [X] **E3 — Transcription:** exact candidate validates/generates; independent equation/reference checks pass.
- [X] **E4 — Native/Wasm:** correct profile/interfaces, complete frozen numerical gates, rollback/recovery/restarts, useful preset, parity and regressions pass.
- [X] **E5 — Agent approval:** separate actual agent run, all nine checklist decisions, blocking findings resolved, exact accepted record and generated approval entry.
- [X] **E6 — Atlas:** qualified model/approval/source/evidence integrated through normal generation; prior models preserved and public metadata/current database checked.
- [-] **E7 — Packaged website:** real controls/plots, source/review scope, import/export/reset/failure recovery, measurement applicability/toggle where relevant, actual browser and package checks pass.
- [ ] **E8 — Live delivery:** authorized scoped commit/push, all CI/deployment gates pass, live assets match tested upload and the live model run works.

## Current handoff

- Current phase: E7 browser disclosure correction. E4/E5/E6 complete within stated scope. Source7f145f2d installed and localcommitted; standardbuilder/all7packageoperations and actualdatabasepreservation pass. Actualbrowser all3presets/fullstates/replay/recovery/cancel/latest/model-switch/narrowlayout pass, but technicaldisclosure falsely claims no definition packaged. Minimal sourcefix plus separate review pending; E7 remains open. No remote authorization.
- Exact source: candidate6c5ee29c unchanged; execution-v5 freeze d1df44cc in /private/tmp/atlas-time-profile-v2 selects generic physical-time-v2 header fd05b08d while retaining common legacy header bytes. All136 histories, references, maximum-step contract and original numerical gates remain unchanged.
- Actual native result:136histories/two repeats,272calls,7771comparisons PASS. Raw95ca533e8c41f17440eebcadca4510a97a2a2ff19b3a53eb20bd89c246d49e6a; report51d368278958e86244adb2ec075186cd0652d1eb4de83ef55a4a7404c97c118f; post8a0078faa983b7ba5c3757cd41cb758730a02e8af5ce142f019653473e7ad555. Binary18ed54a1; actual main dependency selects versioned header and excludes common schedule. All237source/review pins and15preobservation artifact pins unchanged;37linked scalar/compiler pins were captured during collection, explicitly not before observation.
- Generic evidence: separate accepted versioned-profile native regression run passes7operations and18existing Python tests, with new predictor tests. The separate standalone consumer preserves release rootCMake and prior engine source closures; actual seven-operation run and18Python tests pass, independently accepted cb50b5e4/367pins.
- Release preparation: reduced interface-v4 preservation passes3985receipt replays and retains old149/121sourceclosures. Independent review requests CI build/source/dependency receipts before consumer calls. Distinct correction packet in preparation; no installation or E5 approval follows.
- Serial slot: Bingham v5 Wasm collector explicitly RELEASED2026-11-02 after complete passing136case/two-repeat outcome and original accuracy/parity assessments. No Bingham compiled operation active.
- Remaining: finish current imported-tree preservation; install exact source/approval/profile candidates; verify actual catalogue/database, complete package/browser E7 and concrete scoped release commit. No Bingham remote authorization.
- Source/release separation: original b529 capsule plus versioned profile produces v5 engine; release-v2 baseline d74 preserves its own current source bytes. Normal-generator metadata equality and fixed-asset receipt must establish packaging compatibility; no claim of an unseen current-release rebuild.

## Evidence index

| Phase / claim | Exact inputs or revision | Command / checker | Result and evidence path | Owner / date |
| --- | --- | --- | --- | --- |
| E1–E3 source/contract/transcription | candidate6c5ee29c, source-v1 exact receipts | source324identities; tests/test_bingham_candidate.py |108analyticcases,4passingPythonchecks; first harnessfailure retained | sourceworker / parent2026-11-02 |
| Prospective independent review | freeze-v1/v2/v3/v4 + build-inputs-v1 | independent-review-v1/REPORT-v1.md through REPORT-v4.md | R1–R3 resolved;7syntheticcorruptions rejected;138sourcepins exact | separate /root/bingham_review |
| Preservation and shared hooks | release-bindings-v1/prepared-v1/applied.json |49archive/review/export/evidence tests (attempt2 after routing-test preservation) | allpass archive-checks-attempt1.log;9oldsourcebytes+11logicalmaps preserved | coordinator2026-11-02 |
| Interface preparation | interface-v1/POLICY-v2.json |7staticcontracttests; executable checker notyet run | fixed reviewed-engine binding;3mode full-state checks prepared | interfaceworker / coordinator |

## Review and integration identity

- Accepted agent-review record / hash: catalogue/agent-reviews/bingham-comsol63-agent-v1.json /61022026949f2ce9b9a536ab564239edd97ac0b5b3ba66f4ffe3f0066aa6b836; all nine pass,88artifactpins verified.
- Approved model path / hash / scope: models/research/bingham/bingham-comsol63-mises-perfect-zero-spin-ode.json /6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850; exact bounded backward-Euler physical-time schedule API with maximum step5/12288s, illustrative parameter/protocol corpus. Full exclusions in canonical review.
- Registry entry: actual generated approval prepared in actual-integration-v3-candidates-v1/catalogue/approved-models.json; coordinator installation pending complete imported-context preservation.
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

## Historical pre-v1 execution handoff (superseded by actual E4 outcome)

At the time of this historical handoff, no Bingham compiled model call or compilation had occurred. All138build-inputs-v1 pins rechecked exact in pre-build-bindings-check.json. Actual versions are saved in toolchain-versions.json; a private writable Emscripten cache was copied from installed6.0.8 and all1778initial cachefiles pinned separately. The canonical source/model/numerical gates are unchanged.

After slot release, run from `/private/tmp/atlas-bingham-delivery-v1`:

1. Re-read current shared board and explicitly claim BUILD-bingham-comsol63-v1.
2. `cmake -S cmake/bingham -B build-native -DCMAKE_BUILD_TYPE=Release`, then `cmake --build build-native --target atlas_bingham_solver --parallel 1`, logs retained.
3. Exact generated metadata/describe checks and `python3 -B tools/test_bingham_native.py --solver build-native/atlas_bingham_solver --output docs/ingestion/bingham-comsol63/execution-v1/native-attempt1.json`.
4. Understand every native observation before Wasm. Configure/build same explicit target using `EM_CACHE=$PWD/.local/emscripten-cache`, serial; copy original bingham.js bytes to bingham.mjs. Use frozen collect_wasm.mjs, study.py assess and parity.py. No gate relaxation.
5. Bind actual toolchain/flags/artifacts/outputs in real build-receipt.json; create E5-bound three-file sealed ZIP/index. Actual separate-agent all-nine final review, additive approval/catalogue/database and evidence, full normal builder with restored prior engines, real browser qualification, concrete scoped release. Only then remaining remote permission if still absent.

Prior engines restored under `.local/prior-engines/` for ordinary,SLS,Burgers,J2,power-creep,Maxwell,implicit-path. Controlled-path uses existing exact `docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/qualified-norsand`. Restoration order mistake for implicit-path retained; correct existing interface witness restore then provision succeeded. No prior engine was executed here. Baseline-public-records.json and atlas-v1/POLICY.md prospectively freeze complete coverage and row preservation. Publication graph remains unchanged because vendor manual has no verified DOI; exact URLs remain source records.

## Current-atlas and reader-profile continuation v2

Current release integration uses isolated `/private/tmp/atlas-bingham-release-v2` at d74f8c34; frozen E4 source remains `/private/tmp/atlas-bingham-delivery-v1` at b529. New current baseline captures15ordinary/48database models/24approvals/20reviews/202sources, before Bingham integration; v2 policy preserves every old row. Source specialist completed public-profile-v1 draft and provenance. Current mandatory profile checklist additions adopted with original53criterion checklist retained in checklist-history-v1. E6 installation and actual E7 reader-profile/browser checks pending. No compiled observations and no remote authorization for Bingham.

## Actual BE v2 diagnosis and bounded-step preparation

The unchanged v2 study has actual physical-budget failures in completed radial reversal cases. Independent saved-output diagnosis reproduces one endpoint and62,278accepted halfsteps, locating an initially active to inactive step where full and both halfstep endpoints are inactive and the estimator reports zero error. The original closed forms agree; no reference or accuracy gate is changed. Full136case collection finished with frozen assessor exit1, all evidence retained. No Wasm or E5 approval follows from this failure.

A separate source-only step-bound analysis is deriving exact-BE and event-local missing-flow bounds. A possible smaller maximum-step contract is under independent review as a prospective bounded empirical-study choice. It does not prove global finite-Newton error control or general transition robustness. Any subsequent study must have a distinct frozen identity, all136histories, original state/stress tolerances and strict fivefold refinement; public controls must enforce any accepted maximum-step contract. Generic runtime/schema/compiler and exact model bytes remain untouched.

## Capped v3 prospective decision

Independent execution-v3-review-v1 accepts exact freeze b3f72df24459d66a15b45ef9912f6baf78d65fd869d533cb67c52290c807f0e1 before v3 observations. Every136 full record is identical to v2 apart from maximum_step in its three request representations. Fixed cap0.0004069010416666667s applies equally to coarse/fine, public presets, invalids and recoveries. All original physical, parity, strict refinement, domain, transaction and actual-state restart gates remain. Seven helpers are byte-identical; independent136manufactured positives/25original+2cap-tampering negatives pass. This is prospective acceptance, not actual numerical success or E5 approval.

V2 serial slot explicitly released after full failure; MD requested four-operation verification slice acknowledged before Bingham v3 fresh claim. Public cap candidate and distinct interface-v3 policy are prepared. A separate review found omitted sibling document pins in proposed new source sidecars; correction is being prepared in a distinct directory. No interface/workflow replacement or approval installation has occurred.

## Actual capped v3 outcome and generic capability handoff

The complete136-case/two-repeat native v3 study finished with frozen assessor FAIL (return-status assertion), raw SHA807b58b88d78134b8f6a312406dd2f379689f8af2e0b7a16c87544c0e9b6d61c. All153 combined source/freeze inputs and native binary8adc8189 were unchanged after execution. Three exact-yield shear unloading histories reject before a final sample; these are solver rejections, not completed-endpoint accuracy failures. Independent execution-v3-failure-review-v1 derives an outward accumulated-strain Newton direction at the nonnegative domain boundary for every permitted step; backtracking cannot repair it. Full failures and original domains/references/gates are retained.

The serial slot is explicitly released; no Wasm run or E5 approval. Separately tracked CAP-bingham-generic-schedule-predictor-v1 owns a generic admissible-predictor initialization improvement in isolated /private/tmp/atlas-schedule-predictor-v1. Source/prospective regression review precedes compiled observations. This does not change the constitutive model or promise a general nonsmooth solver proof. Existing qualified engines require an honest source-identity compatibility treatment after any shared runtime change.

## Generic predictor prospective preparation

Isolated capability worktree /private/tmp/atlas-schedule-predictor-v1 contains the generic admissible forward-Euler Newton guess and explicit utility include. No model-specific branch, clipping, domain relaxation or residual/acceptance change. Three new v0.3 fixtures cover a unilateral boundary discrete root, invalid-predictor fallback and endpoint clock/domain checks; mixed-control and axisymmetric rate tests use existing fixtures. Parent prospective FREEZE-v3 SHA23df49f9226d15637e83f47a4df1b3c828b0b2b0fffd389542ead0ca80fcc5af binds191source/tool inputs. Earlier incomplete freezes remain retained; independent review pending before compiled observations.

Distinct execution-v4 freeze7987a33133a3575578d3c4e6cb58ec176a760aa846f8fd9bf182cadd6b03ab97 preserves every136 full v3 case record and seven helpers byte-for-byte, including all settings, references and strict gates, with a195-file new-runtime source closure. Synthetic136positive/25negative assessor checks pass; no material result inferred. Generic native regressions queue after MC and MD bounded slices explicitly release. Frozen old engines need a separately reviewed packaging-context adapter; no false rebind to changed runtime is permitted.

## Versioned-runtime v5 actual native result

The new generic runtime lives outside the common cpp/atlas/schema source sets so existing engines retain their qualified identities. Actual versioned-profile native generic regressions passed and were independently accepted. V5 native now passes all136histories/two repeats and7771comparisons with the original analytical/RK4 references, strict refinement, restart, invalid/recovery and retained-sample gates. The three v3 exact-yield shear rejections now complete; v1/v2/v3 failures remain retained. The actual source capsule ZIP is e092bad2e673d52addda6a98ebfdfb2e3f649c5c5f85b636efa7f54814c91e6e; INDEX801d7f333b6fced51661fb4cedf338c6c37823c83a87792ebc022f38ec5928fb. This is bounded native numerical evidence, not Wasm parity, E5 scientific admission, experimental validation or website delivery.

## Actual v5 Wasm build and active collection

Serial Wasm configure/build both passed. Target20file receipt1e63b2d6 and linked37file receipt dfe4317c were captured before the first module instantiation. Actual main-object dependency selects profilefd05 and excludes common schedule; exact include order is in the pinned Emscripten includes_CXX.rsp. Generated metadata7e5bf735/header8132512e match testednative and currentnormalgenerator exactly. Module22316dc4/Wasm586239f8 are pinned, with byteidentical MJS copy. Preflight451cd8b9 binds2231source/SDK/cache/build files; original collector is now running136histories/two repeats in one persistent module. Direct five-tool supplementary recheck67248b9c happened during collection; accepted build recorder had verified those same tool binaries pre/post build before collector start. No Wasm accuracy/parity claim yet.

Receipt-composer v5 source review found real anchor, binary-chain and backend-metadata-path blockers. Original packet/review retained; source-only v6 correction is in progress before any actual receipt/archive or E5 approval.

## Actual v5 Wasm qualification and exact physical parity

Wasm full136histories/two repeats completed with272persistent-module calls, source postcheck true and zero transport errors. Original assessor passes all7771comparisons. Raw874a07dd6aac2088ad381fd08162be663c264b3ab6a244a7bd50727b8a791021; report51d368278958e86244adb2ec075186cd0652d1eb4de83ef55a4a7404c97c118f (byteequal native report); terminalstatus217d8d55. Original native/Wasm parity passes19617physical values with worst scaled difference0, receipt13014af53ce511c3da9bdf54c4f255445ef9a0497bede1ba2a391751a9e02983. Post801c681438518c88b8ca2a283a1e877600357f2acd703118cd1728af8571141f verifies all2231preflight files and20target/37linked inventories plus5tool binaries unchanged; honest supplementary tool timing retained. Full serial slice released. Final independent all-nine E5 must inspect exact candidate assets and these actual results; numerical success alone is not approval or website delivery.

Fresh current-release worktree /private/tmp/atlas-bingham-release-v3 at e6f06114 is source-only preparation. Its actual baseline retains48database models/25approvals/21reviews/202sources and47readerprofiles. Prospective Bingham totals49/26/22/205 and48profiles are distinct from earlier d74 baseline. Existing Barodesy and reader-card updates are preserved. No integration/remote delivery claimed.

### Current candidate staging · 2026-11-02

The accepted v7 composer produced actual immutable candidate build receipt `ef32ea37db081c1c6c30492159b561cb1e5dd7739e1c122f1dfc1447025f1662`, asset index `27889e72c5114caf238db8949cc96551249278e75e5aecc71c989bec3f75f1b2` and three-member asset ZIP `def66cb4704d3af4bdf92cb4a1bef7f2285145dbdda5f58b0d114b697572f1f2`. All 53 durable role hashes and 224 historical source-capsule members were verified in the fresh e6f06114 release worktree. No scientific acceptance is inferred from staging.

The separate all-nine E5 scientific reviewer `/root/bingham_scientific_e5` is inspecting original source images, model equations and saved native/Wasm results with independently reconstructed references. The separate current-main integration draft review accepted its exact 28 candidates and bounded draft preservation context (486 binding pins). Complete imported-tree preservation, canonical scientific approval/registry installation, real package/browser checks and E8 remain pending.

### E6 preservation review finding — 2026-11-02

Before sealing the final imported-context proof, the independent reviewer found that its first path-prefilter expansion omitted immediate sibling JSON receipts lacking target tokens. That partial attempt is retained; sibling loading and affected-map/reverse closure are being corrected and require independent acceptance before source installation. The exact scientific review61022026, model bytes, native/Wasm results and frozen accuracy gates are unchanged. E6 remains open; no package/browser/live pass is claimed.


2026-11-02 E6 installation milestone: exact106-path proposal f2883c68 installed after independent accepted final-context review0e8c93b1/744bindings; allbaselineandcandidate bytes reverified. Canonical E5/registry and53qualified-engine roles pass; publicprofiles48/48 and ordinary generation pass. Initial directcomposer invocation lacked PYTHONPATH and failed import before work; unchanged invocation with PYTHONPATH=. passes, retained in installation-v3/CHECKS.json. Complete database/package/browser gates remain pending. No remote action authorized or performed.


2026-11-02 actual E7 attempt1: package-v3 and browser-v3 preserve passing numerical/interface/layout evidence and blocking false technical-disclosure message. Fullsite retained privately in .local/bingham-site-v3-before-disclosure-fix.zip with SITE-MANIFEST.json. Browserabout:blank/preview52494 stopped; serialslot RELEASED. Sourceauthor/reviewer fixing only Bingham appbranch with oldbytes retained; no numerical/model/runtime/policy changes. E8 remains pending new explicit Bingham publication authorization.


2026-11-02 disclosure fix installed: exact browser-disclosure-fix-v1/manifest6478fed5 and appf7b09ec2 after independent1a5b1511/51pins; all188other-model rendercomparisons unchanged, all181mainrouting assertions/27transitions pass with0compiledcalls. Only Bingham technicalscope text changes. Source/model/runtime/profile/numericalpolicy bytes unchanged. Actualnewpackage/disclosure recheck remains queued behind current sharedslot owner; no E7completion or publication claim.
