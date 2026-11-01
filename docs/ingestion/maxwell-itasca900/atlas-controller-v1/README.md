# Maxwell main-laboratory worker/controller checkpoint

New [main panel](../../../../web/maxwell-laboratory.mjs), [engine loader](../../../../web/maxwell-atlas-engine.mjs), [dedicated worker](../../../../web/maxwell-atlas-worker.mjs) and [run lifecycle](../../../../web/maxwell-atlas-runner.mjs) build on the independently accepted transport contract. They remain staged source prerequisites: shared router, standard builder and public discovery are unchanged.

The panel exposes relaxation, creep, prepared oedometer and load–hold–reverse, with all initial stresses/strains/rates and explicit physical-time component controls. It shows all six stress/strain/rate channels, complete history/event table, model/review identities, governing equations and persistent primary source/schema links. Missing compatible measurements and experimental validation are explicit. Custom histories remain exploratory.

The loader verifies exact model, module/Wasm/catalogue, approval/review and six interface-component hashes before importing the verified module bytes via Blob URL and explicitly instantiating the verified Wasm bytes through instantiateWasm. A raced rejection propagates asynchronous instantiation failure; unverified locateFile fallback and factory completion before instantiation are rejected. The complete catalogue definition must match the hashed model, followed by embedded descriptor agreement. This is served-package provenance, not external authentication; native/Wasm build identity and standard packaging still require qualification. Actual generated-module Blob loading is not demonstrated by mocked tests.

The lifecycle terminates old workers, rejects stale messages, clears output/export on edits/failure/deactivation, enforces the120second UI timeout and permits subsequent recovery. Main-thread result/ABI checks repeat the worker contract. Imported histories must match the actual returned package provenance and deterministic complete result before export is enabled.

## Reproduction and retained findings

```sh
node --test tests/test_maxwell_atlas_runtime.mjs tests/test_maxwell_atlas_contract.mjs tests/test_sls_laboratory_contract.mjs tests/test_timed_route.mjs
```

[Current output](tests-instantiation-final.log):27groupsPASS (13new runtime groups,8Maxwell contract and6existing SLS/timed-route groups). Runtime tests use mocked module/factory/Wasm payloads and a small DOM adapter; they never execute compiled material code. They test exact-byte handoff, asset/semantic identity rejection, all4visible presets, cancellation/stale/latest-only behavior, timeout/failure/recovery, async import/deactivation, complete replay and table/plot handlers.

[Initial7/8 output](tests-initial.log) retains the DOM adapter failure: it stored numeric input.value without browser string coercion. Corrected only the adapter. Later regression/race logs remain retained. Independent review found that the original loader bound the catalogue only by model ID; fixed to compare its complete model with the exact hashed definition, with a same-ID changed-metadata rejection test. Mock catalogue now contains the real model instead of minimal metadata. Exact final implementation identities are in [inputs](inputs.json); separate review closure must bind them.

Next: independent acceptance, then separate standard-builder/router/discovery integration and exact-byte source/build freeze. Current-release native/Wasm qualification and actual main-atlas browser tests remain mandatory. No source law/model/approval/experiment changed; no build, compiled call, public package, standalone page, deployment or remote CI was performed.

Read-only inspection of the historical generated module showed it ignores the wasmBinary factory option while supporting instantiateWasm. The original mocked factory concealed that generated-code API mismatch. The loader now uses the supported instantiation hook and tests asynchronous failure, ignored hooks, fallback file lookup and premature factory completion. Earlier logs remain retained. [Inspection receipt](generated-loader-inspection.json) identifies the existing module read; it was not executed. Static interface imports are fetched separately for component-hash checks: actual executed-interface/cache identity still requires the future real-browser package gate.
