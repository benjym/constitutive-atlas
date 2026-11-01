# Orthotropic OGS main-atlas interface v1

Task WEB-orthotropic-ogs-v1, implementation agent `/root/orthotropic_interface`, 2 November 2026. This is a source/interface specialist handoff, not scientific approval or browser/live completion. Coordinator `/root` owns integration, builds, separate review and actual browser qualification.

Exact model: `orthotropic-linear-elastic-ogs`, definition SHA-256 `60a734a0c40fb0f03642752d22c046d4a05ea66bbf53a3c8e7be06fe71287c14`. The complete nine-constant fixed-axis infinitesimal law is executed exclusively through common `atlas_integrate_with_settings`; no production constitutive kernel is introduced.

## Files and integration

- `web/orthotropic-contract.mjs`: nine-parameter SPD/domain/input checks, six persistent stress entries, frozen settings, common-engine transport and complete committed-prefix records; strict duplicate/nonfinite/lossy-integer JSON decoding; exact complete-document replay comparison.
- `web/orthotropic-laboratory.mjs`: `setupOrthotropicLaboratory({cancelOrdinary})`, returning `modelId`, `active`, `select`, `run`, `showEquations`. Mounts a shadow panel under the main laboratory, appends the selector option and hides/restores ordinary controls, workspace links and ordinary import. Add this controller to the existing shared laboratory-controller router, import/call setup in the application and provide model/catalogue discovery routing. No standalone page.
- `tests/test_orthotropic_contract.mjs`: five pure Node test groups with a transport-only mock and no compiled calls.
- `tools/test_orthotropic_package.mjs`: coordinator-only actual compiled package gate; not executed in this specialist task.

All nine material constants are editable in order E1,E2,E3,G12,G23,G13,nu12,nu23,nu13, with Pa/dimensionless labels and the source Poisson convention. Initial stress has all six editable Mandel components. Each of 1–200 rows prescribes all six strain increments. Two plots show selectable total stress in kPa and relative cumulative strain in percent; the complete six-stress state table and exported engine records remain in SI units. Fixed aligned material axes, compression signs, reciprocal coupling, initialization, commit/rollback, zero hold, sources, equations, approval/review and experimental-overlay unavailability are visible.

The public illustrative preset uses `[30000000,45000000,60000000,12000000,18000000,15000000,0.2,0.25,0.15]`, zero six-stress initial state, and rows `[0.001,-0.0002,0.0003,0.0004,-0.0005,0.0006]`, its negative, and zero. Parent confirmed these were included as `public-0..2` before compiled observations. Settings `[1e-11,1e-6,60,0,1,20]` have depth zero and one substep; there is no physical clock.

## Package contract

Parent packager must copy both modules and create `material-point-orthotropic/` with `orthotropic.js`, `orthotropic.wasm`, `models.json`, `model.json`, `approval.json`, `review.json`, `review.html`, `identity.json`, `package-manifest.json`.

Identity has exactly these keys: `model`, `model_sha256`, `catalogue_hash`, `catalogue_sha256`, `module_sha256`, `wasm_sha256`, `approval_sha256`, `review_sha256`, `review_html_sha256`. All digests are lowercase SHA-256. The catalogue descriptor has exactly the single named model; approval status is approved and review status accepted, both bound to the exact model hash. `package-manifest.json` is a flat mapping of site-relative paths to hashes and must include both interface modules and all nine package files except itself. It may include additional safe relative assets. The worker fetches and hashes all manifest entries, verifies identity/model/review/approval bindings, imports the already-verified JS module through a Blob, compiles the already-verified Wasm bytes and supplies them through supported `instantiateWasm`. No second module or Wasm URL fetch supplies executed engine bytes.

Every run owns a dedicated worker. Edits/reset/switch/new run terminate and reject the prior request. Only the latest token can publish results; selecting the already-active model preserves its inputs/results. Import clears the file field before replay, allowing same-file reselection. Imported output is displayed only after a fresh engine execution exactly matches its entire saved document, including all state, request, wire records, metadata and failed-prefix data.

## Checks and retained failures

`node --test tests/test_orthotropic_contract.mjs` passes five groups (`pure-tests.log`), checking coupled invalid compliance, all six state dimensions, immutable inputs, failure rollback/prefix/recovery, cancellation hook before compiled calls, malformed response rejection, finite result/record/path tampering and strict JSON. `node --check` passes for both production modules, test file and package checker. These are source/mock checks; no browser, native or Wasm execution was performed by this specialist.

The package check is run only after coordinator authorization:

```
node tools/test_orthotropic_package.mjs SITE_DIR REPORT_JSON
```

It reads the immutable repository `source-v1/references.json` and `checks.json` (not web assets): 128 independent Fraction/compliance-derived cases, all six stresses compared at the unchanged absolute `1e-6 Pa` source gate, with exact repeat replay. Six source component witnesses reconstruct the public preset by linear superposition; all 18 committed state entries use the same frozen gate. It checks exact source identity and manifest bytes, actual embedded metadata, full-document replay, finite-tamper rejection, overflow failure after a valid prefix and subsequent recovery. Parent owns broader native/Wasm/tangent/reference qualification.

A temporary ENOSPC infrastructure failure occurred while attempting new test/document writes. No constitutive test failed and no prior evidence was removed; the parent recovered space using an independently archived, regenerable old extraction. The initial error is retained in `retained-enospc.txt`. Writes and source checks then completed.

Remaining work: coordinator packager/application/catalogue hooks, separate independent scientific/interface review, actual matching-engine package execution, actual packaged-browser edits/reset/same-file replay/latest-worker and cross-model switching, plots/layout/links/console/network verification, then exact CI/upload/live checks. No scientific admission, experimental validation, general-parameter qualification or deployment is claimed here.
