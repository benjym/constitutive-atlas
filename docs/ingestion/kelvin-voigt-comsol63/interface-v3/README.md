# Qualified controls proposal v3

WEB-kelvin-qualified-controls-v3. Parent reported original native v2 failures against the unchanged3e-8 strain gate: default creep3.655e-8; tau20 2.714e-7. Original strict code and all six v2 frozen files are archived exactly in prior/; their pins were verified before modification. Original failure evidence remains parent-owned.

This new prospective study uses relative tolerance3e-11, absolute scale fraction3e-14 and maximum substeps1000000. All other solver settings, controls, model/source physics and the package360-comparison physical gate remain unchanged (3e-8 strain,1Pa stress). No claimed pass is inferred from tighter controls: future native/Wasm execution and review must qualify this distinct proposal.

The generic engine independently accumulates strain and strain state. Observed input from the parent was state .019633524432590872 versus strain .019633524432590876. A separate transport check now allows only `abs(a-b) <=64*Number.EPSILON*max(1,abs(a),abs(b))`, roughly1.42e-14 below unit magnitude, far below the physical acceptance gate. The added pure test accepts the one-ULP example, rejects1e-9 corruption, and confirms even one-ULP differences still fail exact saved/fresh replay. Replay comparison is untouched.

All thirteen pure contract/runtime tests pass in results.log. Reproduce with `KELVIN_RELEASE_APP=/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/web/app.js node --test tests/test_kelvin_voigt_routing.mjs tests/test_kelvin_voigt_contract.mjs`. No compiled calls/builds occurred; freeze.json records current six files and unchanged numerical acceptance before compiled/browser observation of v3. Separate review and coordinator execution remain required.
