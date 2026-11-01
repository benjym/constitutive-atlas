# Actual-component pure runtime tests

WEB-kelvin-voigt-comsol63-v1 followup. Only new routing test and this directory were edited; the frozen component, contract, worker and original five contract tests remain unchanged.

The six tests invoke the actual component and shared controller router with a small DOM adapter, fake Worker and synthetic transport result. They cover all explicit six-component inputs, six plot selections and complete state/stress table; latest generation, reset, outgoing cancellation, stale callbacks, invalid-input/error/timeout recovery; complete imported-output replay and finite tampering rejection; stale asynchronous imported-file reads; outgoing timed-profile order; and the coordinator's additive Kelvin router plus ordinary asynchronous guards. These are lifecycle/transport evidence, not constitutive numerical evidence or actual-browser qualification.

Reproduce against the coordinator's prepared source:

```
KELVIN_RELEASE_APP=/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/web/app.js node --test tests/test_kelvin_voigt_routing.mjs
```

All six tests pass, retained in results-v2.log. results.log retains the initial six-pass run before making the isolated app path explicit through an environment variable. In the integrated checkout/CI, `node --test tests/test_kelvin_voigt_routing.mjs` reads the normal web/app.js. Missing integrated Kelvin hooks fail honestly; there is no skip or silent fallback to a different source.

No compiled calls/builds or actual browser actions occurred. Known untested browser-platform fault boundary: the frozen component does not wrap synchronous Worker construction/postMessage exceptions. Normal worker asynchronous errors and timeouts are tested and recover. Coordinator has been notified; any change to the frozen component needs distinct source/review evidence. Exact tested source hashes are in manifest.json.
