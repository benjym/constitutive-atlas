# Worker startup cleanup v2

FIX-kelvin-worker-startup-v2. The laboratory now catches synchronous Worker construction and postMessage exceptions and routes both through the existing failure cleanup: terminate any acquired worker, clear its timer, invalidate generation/results, disable export, enable Run and show the failure. A subsequent valid run recovers.

No constitutive equation, model identity, input control, numerical acceptance, solver setting or asset guard changed. Exact previous bytes of all five interface-v1 frozen files, plus the prior routing test, are preserved under prior/ with verified hashes. Original interface-v1 freeze and runtime evidence remain unchanged.

The additional actual-component pure DOM/fakeWorker test exercises both failures, no thrown UI exception, cleanup state and successful recovery. All twelve contract/runtime tests pass; results.log retains output. Reproduce:

```
KELVIN_RELEASE_APP=/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/web/app.js node --test tests/test_kelvin_voigt_routing.mjs tests/test_kelvin_voigt_contract.mjs
```

Syntax validation `node --check web/kelvin-voigt-laboratory.mjs` passes. freeze.json binds the current five interface files and routing test before any compiled/browser observations of v2, and pins all prior bytes. No compiled calls, builds, shared edits, scientific approval or commits occurred. Coordinator integration and separate review remain required.
