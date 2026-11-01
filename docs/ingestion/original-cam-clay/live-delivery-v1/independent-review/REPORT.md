# Independent main-integration merge review

**Accepted: the resolved worktree merge may be continued and pushed through the authorized main CI/deployment process. No blocking merge regression or unsupported scientific approval claim was found.** Acceptance binds the current substantive file hashes in [merge-check-results.json](merge-check-results.json); it does not assert that the merged application has already passed remote CI, been deployed or been exercised live.

Reviewer `/root/occ_e1_e2_closeout_review`, separate from merge owner `/root`. Worktree `/private/tmp/atlas-occ-main-integration-v1`; latest-main input `f8252c16a9cac492561a7cd25e58b089a63d7eb2`; reviewed release `82a5961ddc781f6f67f39be2748637e76b39be9f`. Ownership confined to this new review directory. Zero reviewer builds, compiled calls, remote actions, production edits or stage/commit operations.

## Conflict resolutions

Independently inspected all seven formerly conflicted files: IMPLEMENTATION_PLAN.md, approval registry, Tresca source-archive map, catalogue manifest, tests/test_catalogue.py, tools/build_web.py and web/app.js. Worktree content has no conflict markers. The index still held unmerged stages at inspection time; coordinator staging/continuation remains necessary and must use these resolved bytes.

- Every existing latest-main catalogue entry and complete approval record is semantically unchanged, including both historical approval records for Burgers and power creep. OCC's manifest and approval entries equal the reviewed release. Nothing downgrades or removes the newer SLS/Burgers/J2 routes, scientific status, exact definitions or approvals.
- Archive-map entries and document bindings from both sides survive; archived bytes match their hashes. Every prior board row survives. Its earlier waiting-authorization/no-push statements remain historical release checkpoints; the current authorized live-delivery phase must retain its own outcome evidence.
- tests/test_catalogue.py remains byte-identical to latest main. This correctly retains current live-laboratory provenance checks rather than restoring the old release's now-obsolete removed-laboratory assumptions.
- The builder preserves latest-main timed/J2/SLS/Burgers packaging arguments, bundles and dedicated package checks, while adding OCC support metadata/dossier handling. Fifty-two dedicated model, route, builder and admission/dossier files remain byte-identical to latest main.
- The app retains all special-laboratory controllers, timed routing, descriptions and async coordinator hooks. OCC adds its bounded summary, support exclusion, dossier and delayed approval status. Non-OCC descriptions continue through recordedDescription; special-model selectors are outside ordinary models so the new summary returns without overwriting their headers. Catalogue status preserves existing special-laboratory branches. No interpreter/kernel behavior is inserted into the UI.

## Scientific and engine identity

The installed OCC definition remains637ba723.. and its E5 record remains a02f6524.., byte-identical to the reviewed release; the approval validator passes. All thirteen ordinary model files equal that release exactly. No production atlas/cpp/schema changes exist from cea9badd to latest main or from latest main to this working merge.

Independently generated the complete ordinary catalogue using the current compiler: header SHA-256 `c23f3a09184a7d8037b2b6da286634aa6e3339bbb3cab109f1209082c248196e` and metadata `1e5e00c1ecd1739d13ea3f171894e87bd751f767ef75b114bddc906c4414b5d5` equal the already qualified common engine artifacts. This is complete generated-source/metadata equivalence, not a new compiled observation. Separate-engine SLS/Burgers/J2 delivery files are preserved; no claim that they belong to the ordinary thirteen-model engine is made.

## Checks and remaining delivery work

Reviewer checks pass:

```sh
python3 -B docs/ingestion/original-cam-clay/live-delivery-v1/independent-review/check_merge.py
node --test tests/test_j2_main_routing.mjs tests/test_timed_route.mjs tests/test_laboratory_support.mjs tests/test_laboratory_profile_policy.mjs
python3 -B -m unittest tests.test_catalogue tests.test_ci_profiles tests.test_native_fixture_contracts -q
```

Twenty JavaScript tests pass, including the J2 coordinator's157mock/static checks; ten Python tests pass. These are portable source/contract checks, not actual browser/network execution. The identity harness initially assumed one registry record per model; corrected to preserve the complete preexisting array because historical Burgers/power-creep approvals legitimately share model IDs. No input or scientific gate changed.

The merged app intentionally incorporates newer main routes, so the prior simplified-site package/browser receipt must not be relabeled as a test of these merged app bytes. Proceed through required CI/package gates, then verify exact deployed assets and exercise OCC plus preserved delivered routes through the actual project-path browser. User push/CI/main-integration/deployment authorization is recorded by the coordinating parent; this technical acceptance adds no broader numerical, experimental or live-delivery claim.
