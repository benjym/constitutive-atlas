# Minimal main-atlas integration plan

Source-read plan by /root/lade_interface_review, 2026-11-02. This new document does not amend the accepted interface receipt or MODEL_REVIEW.md. No shared source was edited, build performed, material executed or browser run. All proposed public approval statements remain conditional on the exact scientific E5 decision and complete numerical qualification.

## Main application and controller

1. In web/app.js import setupImplicitPathLaboratory from ./implicit-path-laboratory.mjs, and append setupImplicitPathLaboratory({chart,cancelOrdinary:()=>cancel('')}) to the existing createLaboratoryControllerRouter array beside timed, SLS, controlled-path and Maxwell. Keep J2's existing outer selection handling. The implicit controller already adds exactly its public model option. Do not append its three witness options to the ordinary models array or selector.
2. No change to web/laboratory-controller-router.mjs is needed. Its existing select clears every view before activating a target, including views that restore ordinary visibility. timedView is currently the name of a general special-controller router; avoid an unnecessary broad rename. Existing specialLaboratoryActive, selectLaboratory, route direct-link recognition, simulate dispatch and equations-button dispatch then cover the added controller through supports/active/run/showEquations. Confirm each in focused tests.
3. Introduce discovery property implicit_path_laboratory: "index.html" on the exact Lade entry. Do not reuse path_laboratory: that currently causes NorSand-specific descriptions, or timed_laboratory: that implies physical time. Four small app branches need the new property: catalogueCards executable availability; refreshCatalogueStatus for "Approved bounded scope · implicit strain-path laboratory"; showCatalogueModel's formulation description; and the explore button's special-controller availability predicate. The existing status/availability CSS checks already recognize any router.supports(id). Keep exact route #laboratory?model=lade-duncan-1975-midpoint-elastic-eq19-gap-v4.
4. The catalogue dialog receives no ordinary spec for this id. Add an implicit-path description before the generic formulationSection fallback, with direct exact model/review/approval links under engine-implicit-path/. Reuse the existing dossier link. Preserve source convention/limitations, fixed eight-setting transport, total mechanical stress and no reconstructed pore pressure. Do not pass this model through ordinary populate, validateSupport, numericalValues or runScopedLaboratory.
5. index.html places #import-run in the laboratory header outside the hidden ordinary lab-layout/workspace-links. The implicit controller does not hide it. In selectLaboratory's router-supported branch explicitly hide #import-run for the selected special route, restoring it in the existing ordinary branch; preserve J2 behavior. The visible import action must be the implicit panel's complete import/replay action. applyRunSpecification already returns when specialLaboratoryActive is true; still exercise old asynchronous ordinary import/experiment responses while switching to Lade to verify that protection. Any generic fix belongs to a separately reviewed app hook, not an unrecorded edit of the accepted five implicit components.

## Discovery, evidence and database

Add a separate manifest row for the exact variant id, preserving the existing lade-duncan-1975 family discovery row as family context. Follow the existing family/variant treatment of NorSand. Update the family note to point to the exact reviewed variant and remove obsolete "transcription pending" wording only after E5. Do not convert the family id into an alias for an ordinary engine or claim two delivered formulations.

Proposed exact-row shape, conditional on E5:

```json
{
  "id": "lade-duncan-1975-midpoint-elastic-eq19-gap-v4",
  "name": "Lade–Duncan 1975 · midpoint-elastic local Eq. 19",
  "family": "elastoplasticity",
  "status": "reviewed",
  "executable": false,
  "implicit_path_laboratory": "index.html",
  "dossier": "docs/models/lade-duncan-1975-midpoint-elastic-eq19-gap-v4.md",
  "note": "Exact independently reviewed bounded implementation; main-laboratory implicit strain-path route. Total mechanical Cauchy stress; illustrative source parameters, no experimental validation or general 3D event theorem.",
  "catalogue_sources": [
    {
      "url": "https://doi.org/10.1061/AJGEB6.0000204",
      "role": "Original Lade–Duncan 1975 formulation",
      "locator": "Exact equation/page locators from the accepted source receipt and dossier"
    }
  ]
}
```

Replace the illustrative locator with actual reviewed locators. executable:false is intentional: all current consumers define that flag as ordinary atlas.js membership, not every interactive profile. tools/test_web_package.mjs requires the executable:true set to equal ordinary models.json exactly. Never add the research model to top-level models/*.json, ordinary models.json, laboratory-control-support.json, ordinary laboratory-package-policy.json or ordinary profile-policy solely to make it discoverable.

The exact approved definition stays at models/research/implicit-path/<exact-id>.json with SHA256 120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63. E5 generates a new catalogue/agent-reviews record and the exact approval registry entry. atlas.research.approved_definitions already resolves approved paths anywhere inside models/, and export_database merges them with ordinary definitions while setting SQL executable only for ordinary membership. tools/build_database.py already expects ordinary union approved definitions, validates exact E5 reviews, captures research-path definition inputs and leaves ordinary_engine_model_ids unchanged. No database schema/exporter edit is needed for this integration.

Add the exact variant to the existing 1975 publication's model_ids in catalogue/publications.json, retaining the family mapping and existing DOI identity. The exact manifest row is also required so tools/build_evidence.py / atlas.review_export can attach E5 evidence rather than omit a review without a canonical catalogue binding. Use actual bounded evidence/limitations in any evidence/applicability update; an interface receipt is not scientific approval. Counts in STATUS/ROADMAP should distinguish the family row, exact approved formulation and actually browser-qualified route. Do not alter release_target merely because a new row exists.

## Standard web builder

In tools/build_web.py add an explicit --implicit-path-wasm-dir argument pointing to the eventual qualified artifact directory. Avoid a default pointing at the still-unqualified initial runtime/build. Import and invoke tools/build_implicit_path_laboratory.bundle(dest,args.implicit_path_wasm_dir) after the other profile bundles, before .nojekyll/final success. Require the argument/profile artifacts for a release containing the new discovery row; no silent omission or fallback. Run a focused profile package gate immediately after bundling.

The guarded bundle already copies all five implicit components and engine-implicit-path assets; do not add those components to the ordinary copy list as an alternate unguarded path. laboratory-controller-router.mjs is currently supplied by both controlled-path and Maxwell bundlers. Leave it byte-identical and ensure both still copy the same current source. The new builder's helper does not overwrite it. The ordinary generated catalogue freshness check, database step, experiment rights policy and all existing profile package gates remain mandatory.

build_database currently runs before dedicated profile bundles. This order remains valid because database membership depends on exact approvals and manifest, not compiled engine assets; a failed later profile guard must still fail the overall build. Use a fresh output directory and do not publish a partial package. Add final profile-manifest/import-closure checks so a failed build cannot be mistaken for a completed artifact. The implicit helper currently writes only its allowlisted assets and does not remove old unrelated files from a reused engine-implicit-path directory, making fresh staging the smaller safe integration choice.

The helper renders MODEL_REVIEW.md into review.html; that accepted report is explicitly interface-only. review.json and approval.json remain the scientific E5 artifacts. In the final UI, preserve this distinction or add a separately named scientific report asset through a new reviewed helper revision. Never rewrite the accepted MODEL_REVIEW.md to silently substitute a different decision.

## Durable CI and package coverage

Keep the current native/wasm/wasm-linux/deploy dependency gates. Add pure contract/saved-response/lifecycle/fetched-asset tests and normal canonical regeneration as durable tests under tests/, or invoke the retained scripts without overwriting historical results. The retained review scripts write their owned result files and the missing-E5 historical guard intentionally fails after legitimate E5 integration; adapt a new durable test identity with temporary outputs and a controlled missing-approval fixture. Do not edit/reinterpret the retained proof.

Add an explicit profile input policy and required package check bound to the exact public id/hash, both source dense/loose defaults (protocol1,target.005,400 steps), fixed settings, changed input, hold, cyclic/domain/accepted-prefix behavior and full export/import/replay. This complements existing ordinary strict/default policy rather than widening its ordinary catalogue. A top-level required special-profile registry/check should enumerate existing timed/SLS/Burgers/J2/NorSand/Maxwell plus Lade, so future profile discovery cannot be silently untested. At minimum CI must invoke the new profile check unconditionally whenever its manifest row is present.

Before compiled invocation, test guarded packaging mutations for absent/stale model, generated catalogue, loader/Wasm, qualified runtime binding, each of eleven gates, independent build reviewer, E5 review/registry and all interface pins. Validate full four-model atlas_describe identity while ensuring only the exact public id is in discovery/controller routing. Test every local module import and URL beneath a project prefix, model/review/dossier links, all fetched hashes and package manifest consistency. Query SQLite for exact definition/approval/review/source/publication identity and executable=0; confirm the public and ordinary model sets remain unchanged except the intentional exact discovery row.

After qualification, choose one honest artifact lifecycle: serially build and qualify the versioned target in CI under a frozen policy, or restore exact independently qualified artifacts from a committed permitted archive using a guarded provisioner analogous to Maxwell. Do not regenerate a PASS receipt or independent decision in CI. If building, use cmake/implicit-path-v1, the explicit atlas_implicit_path_v1 target and --parallel 1; preserve toolchain/platform scope and requalify rebuilt byte identities. Add provisioning/required guarded package regression to both wasm jobs before tools/build_web.py. Upload new numerical/profile/package failure logs as artifacts even on failure.

Current CI includes no actual browser automation step for these special controllers. Add a real browser qualification job (or provide separately retained E7 evidence before publication) covering direct URL/card/dropdown activation, dense/loose requests and plots/table, source/review/download links, input editing, zero hold/reversal, import/export/replay/tamper rejection, invalid-state recovery, failed prefix, latest-request/model-switch cancellation, 120s deadline, mobile layout and console/network/worker errors. Compare captured requests/results with qualified same-request fixtures and fetched hashes. Include ordinary and Maxwell smoke runs in the same package. A Node injected worker or direct engine run cannot satisfy this browser gate.

## Shared ownership and conflicts

The integration owner should archive exact shared bytes before edits and serially own app.js, build_web.py, manifest/publications/approval/evidence hooks and workflow/tests. Coordinate with active Maxwell and other model leads; do not overwrite their uncommitted changes or stage broad directories. No router/source cleanup or shared compiler/solver modification is required for this bounded change.

Important current conflict: tools/build_maxwell_laboratory.py source_manifest recursively hashes all atlas/*.py, schemas/*.json and cpp/**/*.cpp/.hpp, including cpp/profiles/implicit-path-v1. Installing the future qualified FMA profile changes Maxwell's closure even though Maxwell does not compile those versioned sources. tools/provision_maxwell_assets.py pins an existing exact qualification/review/archive and invokes that current closure guard. The forthcoming runtime installation can therefore block both provisioning and build_web. atlas/research/database/compiler edits also affect this broad Maxwell closure. Coordinate a separately reviewed impact assessment and new bound Maxwell qualification/provisioning identity if required; do not remove manifest entries, loosen source checks or repin historical records just to pass. The controlled-path source closure also pins atlas/schema/common-runtime bytes, though its current required set does not include the versioned profile directory.

Appending the new controller needs no router mutation, avoiding a shared component hash change. Editing one of the accepted five implicit components, its generator, guarded builder or CMake file changes an interface receipt pin and requires a new exact review. App/manifest/standard-builder hook edits are outside that acceptance and need focused independent hook review. The existing receipt's 24 file pins must remain valid. Scientific E5 and final numerical artifact approval remain the separate review owner's task.

Smallest implementation sequence: finish qualification/E5; install exact runtime with archived old bytes and reconcile affected Maxwell closure; make the small app/discovery/build hooks; add required profile/package/database tests; independently review the hook diff; build one fresh guarded main package; execute package and actual browser gates; prepare the scoped release with truthful E7/E8 status. No push/deploy is authorized by this plan.

## Observed source identities

These hashes identify the source-read snapshot; they do not freeze concurrent integration ownership.

- web/app.js — `5cccb3f87e4b7354c64f6afbe56d2669db5ac02fff7787df31f4ed547eb77475`
- web/laboratory-controller-router.mjs — `e6f5f85ba95b909608015e974cbb0c919e97b9fd68d5d9d6202482e4a46eb934`
- web/index.html — `5d24970cbfc2fc7e3f32345bdd16e174d01436c684f0f7c4004bf0e3a7ff4e25`
- tools/build_web.py — `85fbb595b7db24a219da4119d05b0c5c65cb36378a599860dc7392163042e9a8`
- tools/build_database.py — `11f523a95587f826de46bd953486655eb4f3a86261912f38c6d0648c80f9f4bc`
- atlas/research.py — `279f5564d9484514f9d66db9b8a5fa4482dc534a6c9d4954b0e10001ad7b2c0a`
- atlas/model.py — `ed8ec50839bf1c35ca45703f6d45d68fdd2888795b86482f850f56d9e4a8feef`
- atlas/review_export.py — `db2a0a39f323df64c8bde5471ac54224430cafc18c1adf11241aaa797014f6a8`
- catalogue/manifest.json — `d9a16ce8370d76807ed3270265765cad48386bd517d4b806f1220ca9bdd7fe7d`
- catalogue/publications.json — `7905ef8a56638441e25f836ea276d082cf2d49ce2c4bdfae254c503b3e6900fb`
- .github/workflows/verify.yml — `784185ebf94466569e3426a14798f144a06f7b82e451afa4c3e92c377e91fed5`
- tools/build_maxwell_laboratory.py — `d79fed104b6934fe44dfc557b12c85f72dea05f9b9246665f05eebc24d3c9cfb`
- tools/build_controlled_path_web.py — `2fe5bf29b0e6a58bd18012a526fa910a30ca97eb11341dfd718ea8089852e3f1`
- tools/provision_maxwell_assets.py — `f58e3aa0fb61d142c91c59cfabd10ff3cebb56ed037789a09adaa1e7e758e244`
- tools/check_maxwell_ci.py — `599fdc0737c6d522a72cec48d4529d9ef762c331ed3c07422f2d4371e13dccd6`
- tools/test_web_package.mjs — `7b4bbb5c50147acbcea3221427d5aa47d5484fde59ad210cddada37f96ee450f`
- tools/test_supported_package.mjs — `d06f4acb99c8b4963eac41b63b96fe65868056dbc2fef9c69a5f97d437b9bb3c`
- tests/test_laboratory_controller_router.mjs — `340b0ee278d433c00106c31de59ec2fc3bc4b5561116f64d132536254a17aad4`
