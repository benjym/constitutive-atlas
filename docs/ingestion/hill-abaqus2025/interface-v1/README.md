# Hill main-laboratory interface — v1 handoff

Task WEB-hill-abaqus2025-v1; implementation agent `/root/hill_interface`; 2026-11-02. This packet supplies the interface and pure transaction contract. It does not certify the law, native/Wasm behavior, packaged browser behavior, scientific approval or live delivery.

Owned new files:

- `web/hill-contract.mjs`
- `web/hill-laboratory.mjs`
- `tests/test_hill_contract.mjs`
- this directory

The contract binds model `hill-abaqus2025-perfect-be`, candidate SHA-256 `1f98a70a68098d95804639e3abeb69da57e7ceeaf302d621e4738db4340e2621`. The parent supplied this candidate identity and its bounds; a changed model requires a deliberate identity update and affected requalification. Ten parameters are ordered p_ref, K, Gmod, sigma_y, F, Gh, Hh, L, M, N. Seven state entries are six Mandel total stresses and the temporary multiplier gamma. The displayed shear modulus is Gmod; source Hill G is the separate Gh input.

`setupHillLaboratory({cancelOrdinary})` mounts a shadow-root panel inside the existing main laboratory, adds its model option and returns `{modelId, active, select, showEquations}` for the existing controller router. It does not create a standalone page. Parent integration must import/register this controller, ship both Hill modules, expose the exact model in the atlas/database and construct the guarded package.

The package path is `material-point-hill/`, containing `identity.json`, `hill.js`, `hill.wasm`, `models.json`, `approval.json`, `review.json`, `hill-abaqus2025-perfect-be.json` and `review.html`. Identity shape matches the J2 contract: model, model_sha256, catalogue_hash, catalogue_sha256, module_sha256, wasm_sha256, approval_sha256, review_sha256. The six digest-bound files are checked before use; module import uses the already verified JavaScript bytes and Wasm instantiation uses the already verified binary. Catalogue, model, approval, review and the instantiated engine descriptor must agree. `review.html` is supporting presentation; its bytes are not part of this runtime identity contract.

The interface accepts all six increment components, ten parameters and the complete initial state. It displays all seven state entries at each accepted row, every stress and cumulative-strain component, and latest gamma. Inputs are immutable within a run. Changes cancel superseded work before another step; failed increments preserve the accepted prefix and failed engine responses must echo the exact request and full rolled-back state. Reset starts the named preset; import checks exact package identity and replays the saved initial request. Saved results are never trusted. Export includes request, complete states and row-level wires/responses. Zero rows are strain holds without elapsed physical time.

The scope and equation section declares fixed aligned material axes, compression-positive Mandel components, dry total stress, isotropic elasticity, associative Hill perfect plasticity and Atlas backward Euler. It discloses row-partition dependence, exploratory custom inputs and the absence of compatible experimental overlays. No physics integration occurs in JavaScript.

## Reproducible checks

From repository root:

```sh
node --check web/hill-contract.mjs
node --check web/hill-laboratory.mjs
node tests/test_hill_contract.mjs
```

Current saved output: `contract-test-v2.json`; current file identities: `manifest-v2.json`. Original `contract-test.json` and `manifest.json` are retained unchanged, with the former contract bytes under `superseded-v1/web/hill-contract.mjs`. The only interface change in v2 is the final model digest after source-supported metadata corrections; no constitutive or request-contract behavior changed. Result: 102 assertions pass; zero compiled calls. Checks cover six directional yield limits including the physical-shear/Mandel mapping, hydrostatic admissibility, coefficient bounds, malformed requests, immutable run inputs, package identity, returned state/settings/request echoes, failure rollback/prefix, reset-style recovery, exact replay and supersession. Synthetic responses exercise transaction validation only and supply no equation or runtime validation.

Retained failures: none in these checks. No builds, compiled calls, approval decisions, shared edits or commits were performed by this specialist. Remaining work belongs to the parent: finalize source/model identity, native/Wasm and independent law review, ordinary atlas/router/build/CI hooks, package creation, actual desktop/mobile browser qualification (including invalid recovery and exact replay), scoped release and authorized live verification.
