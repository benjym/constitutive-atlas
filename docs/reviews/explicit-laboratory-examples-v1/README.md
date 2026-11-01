# Explicit named laboratory examples — capability checkpoint

Completed 2026-11-01. This is a generic browser/packaging capability. The production catalogue remains ten models and its new example registry is empty. GIS is exercised only in a private eleven-model test fixture; its installation and scientific admission remain pending.

## Contract

`catalogue/laboratory-examples.json` registers documents under `protocols/`, with model identity, exact model/document SHA-256, label, description and HTTPS evidence link. The packager binds the generated catalogue hash, checks safe local paths and validates the complete registry before writing example assets. The browser verifies both exact assets, compares the definition with the compiled model, and uses the existing laboratory document validator. It rejects stale catalogue/definition identity, missing full persistent history, invalid loading/settings and corrupt assets.

Selecting a named example previews amplitude, protocol units, increments, cycles, full state/parameter counts and solver settings. Only **Replace inputs with this example** replaces the run inputs. It uses the same validated application path as run import, cancels pending work and starts a fresh replay. A saved final state is never silently resumed. Reset/model changes invalidate prepared selections. The global defaults remain unchanged.

## Verification

[Results](results.json), [private fixture frozen before observations](browser-fixture.json), [browser export](browser/explicit-memory-run.json) and [plot screenshot](browser/explicit-memory-run.png) record the bounded check. Preview preserved 1%/100 increments/depth14 and zero memory. Explicit loading restored all14 state components,19 parameters,0.001%/8 increments/depth20 and nonzero memory. Real existing Wasm produced9 points; exported specification exactly equals the source fixture. A deliberately corrupt document was rejected without input mutation; reset restored depth14/zero memory and model switching invalidated the selection. Screenshot inspected: plot and controls render correctly.

Commands (from repository root):

```sh
node --test tests/test_laboratory_examples.mjs tests/test_web_package.mjs tests/test_state_contract_browser.mjs
python3 -B -m unittest tests.test_laboratory_document tests.test_state_contract tests.test_web_effective_scope -q
python3 -B tools/build_web.py --wasm-dir /private/tmp/atlas-tresca-mixed-catalogue-v1/wasm --output /private/tmp/atlas-explicit-examples-v1/production/constitutive-atlas
node tools/test_web_package.mjs --directory /private/tmp/atlas-explicit-examples-v1/production/constitutive-atlas --output /private/tmp/explicit-examples-package-check.json
```

23Node tests pass;13Python tests pass with3optional skips. All ten production default runs pass (101points each). Existing qualified engines were reused: zero native/Wasm builds. The browser fixture uses the separate already-qualified eleven-model engine. Source hashes are bound in `browser-fixture.json`; test/package stdout, stderr and smoke output are retained in `checks/`.

## Retained failures and scope

Initial HTML anchor mismatch was corrected before UI mutation. First verification used a nonexistent Python test module and exposed a stale assertion that all models were the original nine effective-stress models; the corrected assertion keeps their exact comparison checks and excludes total-stress Tresca overlays. A mistaken direct Node invocation of a stdin-based laboratory-document helper blocked; only its owned process was terminated, then the proper Python wrapper passed. A browser automation callback used the wrong argument shape, then a model switch used an unregistered model ID; corrected calls passed. These were tooling failures, not numerical acceptance failures. Raw failed test outputs are retained.

Historical receipt documents were preserved byte-for-byte with document-bound archive maps before changing shared sources/test files. `archive-result.json` and `test-archive-result.json` identify the exact archived paths and preserved receipt edges.

The tiny-path example comes from the already-qualified laboratory-route packet, not the later failed-default diagnostic. No model math, numerical tolerance, global default or scientific gate was relaxed. The unchanged GIS1%/100step/depth14failure remains in the separate local-draft packet. No model installation, build, push, deployment or remote CI occurred. Next: resume the separately claimed GIS local-draft package/browser stages; this capability checkpoint does not satisfy B01–B12.
