# Orthotropic OGS — delivery ledger

Lead /root; MODEL-orthotropic-ogs, 2026-11-02. Exact full nine-constant 3D linear orthotropic elasticity from OpenGeoSys commit b5d0f115c75ee74a7cdbfad533625a550a416fda, fixed aligned material/Cartesian axes and constant parameters. Main atlas catalogue and laboratory; no standalone page.

Candidate `models/research/orthotropic/orthotropic-linear-elastic-ogs.json`, SHA256 `60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14`. Common v0.3 incremental-residual strain-path solver, six persistent total Cauchy stresses and six Mandel strain increments, compression positive as an explicit Atlas host convention. The source does not explicitly label scalar stress sign. No physical-time, finite-rotation, thermal/poro, mixed-stress-control, calibration or experimental claim.

[Source packet](source-v1/README.md); [all detailed checklist criteria](CHECKLIST.md). Canonical checklist at assignment SHA256 b370c525b8650492c8b0fb49e1107a765009b5be8f16818675196541eb128289. Parent coordinator owns integration/build/release; source worker /root/orthotropic_source, UI worker /root/orthotropic_interface, independent reviewer /root/orthotropic_review, actual-browser worker /root/sls_browser_delivery. Each had distinct explicit path ownership on the board. Builds only coordinator, one explicit target --parallel1, serial native then Wasm; workers received bounded saved-output/browser handoffs.

Isolated release worktree `/private/tmp/atlas-orthotropic-release-v1` starts at8718467f. Exact committed common-engine source excludes unrelated root WIP. Authorized new model/source/dossier/CMake/tools/UI/test/review/approval paths plus separately claimed additive app, builder, workflow, catalogue/registry and own board/status/roadmap rows. Exact previous shared bytes retained in atlas-v1/shared-before/. No shared schema/compiler/runtime or handwritten-law change.

User's2026-11-02 request “another constitutive model … end to end” continues the explicitly accepted ingestion/review/commit-push/live loop; no additional scientific human sign-off is required.

## Verified stages

- [X] **E0** — Board MODEL-orthotropic-ogs and dependent scoped claims; DELIVERY.md; source-v1/acquisition.json and source-v1/README.md.
- [X] **E1** — source-v1/README.md, source-receipts.json and immutable manifest.json: seven pinned readable originals, OGS b5d0f115c75ee74a7cdbfad533625a550a416fda, exact locators, BSD3/private retention.
- [X] **E2** — source-v1/candidate.json and README.md; execution-v1/PLAN.md, freeze.json, freeze-v2.json and references.json, all fixed before compiled observations.
- [X] **E3** — source-v1/checks.json and verify.py: 16 materials,128 endpoints,768 stress residuals,576 inverse identities and128 energies; normal common compiler generation recorded execution-v1/.
- [X] **E4** — execution-v1/native/assessment.json, wasm-assessment.json, parity.json and artifacts.json:121requests/backend,648state entries,144tangent entries,13reject/recovery pairs, partition/restart, full6state; native/Wasm exact metadata.
- [X] **E5** — scientific-review-v1/report.md, independent Decimal checks and manifest.json; catalogue/agent-reviews/orthotropic-ogs-agent-v1.json accepted all9items; docs/admission/orthotropic-ogs-approved-v1/approval.json exact frozen definition.
- [X] **E6** — atlas-v1/prospective-package.json, build-attempt1.log, revision-v2/asset-delta.json and package-attempt2.log, database.json, ordinary-package.json. Standard generation, three unique exported sources, exact approval/review/definition; ordinary12 policy unchanged.
- [X] **E7** — browser-v1/README.md, assessment.json and manifest.json; interface-review-v1/: actual main atlas default/custom6state, replay/tamper/recovery/latest/switch/layout,13asset hashes and6links200;267package calls/786source comparisons,1e-6Pa bound. No applicable permitted experimental dataset; UI states overlay unavailable.
- [-] **E8** — Scoped release commit, authorized push, all exact-revision CI/Pages gates and actual live asset/browser verification remain with parent.

## Exact review and artifacts

Scientific reviewer is a separate actual agent run, not the implementation lead. Accepted record `catalogue/agent-reviews/orthotropic-ogs-agent-v1.json`, SHA256 a2862129dd393f2c73923b06706e12b75767f8b360b57bd1cfbb67c6069ef50f; generated approval SHA256 3cb73256ceea7dcdb592275a40cd0685cd2dc6f0c8fc49eb2288f92348d89b79. Approval scope covers bounded native/Wasm integration and full update derivative; interface review separately covers packaged main-laboratory behavior. All nine scientific items accepted.

AppleClang21.0.0.21000401 native and Emscripten6.0.8 Wasm; exact artifact receipts in execution-v1/artifacts.json and durable ignored `.local/private-evidence/orthotropic-ogs/execution-v1/`. Dedicated catalogue hash5f394a724f409f9e1cbdea9f7ff536bd1566550eb7071c39987c1cb03f528abc. Both backends satisfy frozen source references independently; parity alone was not used as equation verification. Independent review uses Decimal80 Cholesky, separate from source Fraction inversion and production closed-form stiffness.

Retained failures include source structural/transcription validation, initial CMake missing optional scalar include, ENOSPC writes, wrong-root registry packaging attempt, wrong ordinary-policy path, and browser link/route synchronization harness attempts. Gates were not relaxed. The actual source-sign attribution finding F1 was corrected only in UI text; exact prior module retained in atlas-v1/revision-v2/before/, prospective revision plan precedes affected package rerun. Model/source/scientific/engine bytes unchanged. Of895package assets,893 are unchanged; only corrected module and its manifest changed. Browser qualification uses corrected v2.

SQLite exports exact candidate/approval/review and no foreign-key failures; six source rows represent three unique source identities because the existing exporter combines definition and catalogue sources. No deduplication or six-independent-source claim. Unaffected ordinary12 engine and supported-input policy retain the declared GIS default failure and successful named example.

## Release and live receipts

Pending E8: exact application commit, Actions run URL, terminal native/Wasm/package/deployment jobs, tested upload inventory, live fetched asset comparison and actual live main-laboratory numerical run. A separate integration study is required for concurrently committed runtime/application changes before final release. The premerge895-file package remains immutable evidence.

## Limitations

Source complete and declarative; native/Wasm and actual packaged-browser behavior qualified in bounded synthetic cases. Broad modulus/Poisson conditioning envelope, physical rotations, coupled fields, arbitrary finite deformation, mixed controls and experimental validation remain unqualified. Presets are illustrative engineering constants. Live deployment is not claimed until E8 receipts are complete.
