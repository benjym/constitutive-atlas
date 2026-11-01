# Verified module import and imported replay provenance v4

WEB-kelvin-integrity-v4. Exact all six current v3 file bytes were checked against interface-v3/freeze.json and preserved in prior/ before changes. Earlier freezes/evidence remain unchanged.

The worker imports the exact verified kv.mjs bytes through a Blob module URL, eliminating its prior second unchecked URL fetch. locateFile accepts only kv.wasm and supplies its absolute project URL for Emscripten initialization; the actual instantiation still consumes the already verified Wasm buffer. The Blob URL is revoked after initialization on success, factory rejection or asynchronous Wasm rejection. An explicit failure race prevents a rejected Wasm hook from leaving factory initialization pending indefinitely.

Imported replay now carries the complete identity used to validate the imported document into the pending run. A worker response with different provenance fails before exact full-result replay and before export, even if its numerical output is identical. A subsequent import under matching identity recovers. No equation, numerical acceptance, solver or control changed.

Fifteen pure contract/runtime tests pass in results-final.log. The new source-only worker VM test mocks fetch, module import, factory and Wasm instantiation; it confirms the Blob holds the verified bytes, exactly one module fetch, correct absolute Wasm URL, guarded fallback paths and URL revocation on success/factory failure/asynchronous Wasm failure. No module or Wasm artifact executes. The test fixture substitutes the exact model-definition hash because its fake definition is not the real scientific record; this fixture only exercises transport/control flow and claims no numerical or admission evidence.

results-first.log retains an initial missing verifyResult import in the new test harness (14pass,1failure), corrected without changing production gates. results-second.log retains the initial passing15test run before adding the asynchronous Wasm failure case; final results again15pass. Reproduce:

```
KELVIN_RELEASE_APP=/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/web/app.js node --test tests/test_kelvin_voigt_routing.mjs tests/test_kelvin_voigt_contract.mjs
```

Worker syntax check passes. freeze.json binds six current files before any compiled/browser observation of v4. Coordinator package refresh and separate review remain required. No compiled calls, builds, shared writes or commits occurred.
