# Independent interface v4 source and integration review

Reviewer `/root/kelvin_scientific_review`;2026-11-02; separate follow-up to the accepted scientific/API record. Decision: **source/pure-test review passes; actual package/browser/live qualification remains pending**. No accepted review JSON, README or bound artifact was changed. This report does not extend scientific approval to unobserved browser execution.

## Exact scope and preservation

Read interface-v4 README/freeze/prior files and all current component/worker/contract/package-test source, the browser-v2 prospective plan/reference/freeze, isolated release app/builder/workflow and native/Wasm CI wrappers. Independently verified every current and prior v4 hash, exact prior equality against interface-v3/freeze.json, the three production components copied into the isolated release, and browser-v2 plan/reference/interface bindings. Browser-v2 expected-default.json is byte-identical to the original prospective browser-v1 reference. Model, constitutive equations, six-state layout, settings and physical accuracy gates remain unchanged.

V4 interface freeze SHA25638fe2e833e32981a85de20aeb9a5f65423124b4de3fae5a1a1ae00c4e864826b binds:

- laboratory c7c47a746b07454b174765532da655b22a8376267d9ce32c3023dd01b468b5d5
- contract b2324915a6329166019fa48a07262e932f357048c7be73f7448c03209b1dba0c
- worker b9c7c5aad0b17e1a19a4c501b9efbd383e052b6088bba058d8ba3947b35b26c4

No handwritten constitutive calculation was added to the production worker. The accepted scientific model remains080fa946ea5d7743b133b62bbd39098b6b50ecf09d835f1a9966fa9283b6f8da; the API review explicitly leaves browser delivery separate.

## Verified module bytes and lifecycle

The worker fetches kv.mjs once through the hash-checking bytes helper, then creates the imported Blob from that exact ArrayBuffer. Dynamic import therefore consumes the verified module bytes rather than making the former second unchecked module-URL fetch. The Wasm buffer is separately fetched/hashed and supplied directly to WebAssembly.instantiate. Explicit locateFile accepts only kv.wasm and resolves it against the worker's absolute project-path location. It rejects unexpected engine-file fallback requests.

Inspected the actual generated Emscripten module source without executing it: browser/worker scriptDirectory construction catches blob-relative URL failure; findWasmBinary uses the supplied locateFile when present, and the supplied instantiateWasm hook provides the verified Wasm rather than an unguarded fallback. Actual Blob support/CSP/network/browser compatibility still requires the planned real browser run.

The try/finally surrounding dynamic import and factory initialization revokes the Blob URL after successful initialization and on import/factory failure. A Promise.race includes explicit asynchronous instantiation rejection, so a Wasm hook failure cannot leave the outer initialization waiting indefinitely; the finally still revokes. Errors go to the existing worker error message and main generation-guarded failure cleanup. A worker terminated by outgoing selection/input invalidation cannot publish afterward. Late callbacks after successful or failed initialization remain scoped to the short-lived per-run worker. No blocking source-level lifecycle defect found.

The new pure worker VM test substitutes only the dynamic-import factory and uses fake bytes, explicitly avoiding compiled/module execution. It verifies one module fetch, exact Blob payload, explicit project-prefixed Wasm location, rejection of other filenames, and URL revocation on success/factory failure/asynchronous instantiation failure. These are appropriate source/control-flow tests, not a substitute for actual Emscripten browser execution.

## Imported replay identity

The identity fetched while validating an imported document now travels as expectedIdentity into that pending replay. Before accepting any worker output, the main component compares the entire returned identity to it through the canonical exact replay comparator, then compares the entire result exactly. Changing provenance while retaining identical numerical output therefore fails before render/export. The normal generation/active guards also reject stale imported reads or outgoing workspace callbacks. A matching-identity import recovers. The new pure test demonstrates identity replacement/rejection and matching recovery; actual deterministic browser injection is a separate optional tooling limitation explicitly addressed by the plan.

## Integration and durable checks

The actual isolated app installs Kelvin in the existing shared timed-controller router. Existing ordinary asynchronous render/worker/experiment guards remain intact; deactivation precedes the next controller's activation. Root app.js contains unrelated work and is intentionally not the reviewed release hook.

The normal web builder invokes the Kelvin bundler unconditionally and its compiled package checker. The bundler verifies exact approval registry membership, review/model/supporting artifact bindings and regenerated catalogue equality before copying dedicated engine/model/review/approval/components. The package checker verifies the actual embedded descriptor and hashes, rejects a standalone page, exercises all360default state/stress comparisons across creep/rate/hold, strict replay and invalid-request recovery. This is a meaningful required package gate, but was not executed by this reviewer.

Native and both Wasm workflow paths build the explicit Kelvin target with --parallel1 in Release and run the frozen execution-v3 study. Native wrapper retains per-request capture and assesses the exact frozen cases. Wasm wrapper creates a fresh output directory, runs the same unchanged collector in one persistent module, preserves raw output and assesses independently derived references. Existing serial target/regression work remains present. These are durable gate hooks; actual CI completion remains unobserved by this source review.

## Independent pure checks and prospective browser plan

Independently ran:

`KELVIN_RELEASE_APP=/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/web/app.js node --test --test-reporter=spec tests/test_kelvin_voigt_contract.mjs tests/test_kelvin_voigt_routing.mjs`

Result:15/15pass, retained in interface-v4-tests.log. Includes prior lifecycle/startup/roundoff/replay regressions plus identity-race and verified-byte loader tests. The author's initial test-harness missing-import failure remains preserved in interface-v4/results-first.log; it does not indicate a changed production gate.

Browser-v2 prospectively preserves3e-8strain/1Pa stress over360default comparisons and exact replay. Its plan covers actual main route/catalogue entry, desktop/mobile layout, source/review/approval links and hashes, all six plots/state channels, three modes, parameter/initial-state/history changes, invalid recovery, actual downloads/import/replay/tamper, directed controller transitions/cancellation, console/network behavior and real v4 Blob module initialization. It distinguishes synthetic tests from actual browser evidence and explicitly records limitations where deterministic race/revocation injection cannot be observed. Live delivery additionally requires exact-source CI/Pages and served-asset equality. The plan is appropriately bounded; no future pass is inferred.

No unresolved source-only blocker found. Parent must still execute the standard packaged gate and actual browser plan against matching v4 assets, retain failures and compare final live deployment bytes. Scientific/API acceptance, package qualification, browser function and live delivery remain distinct.
