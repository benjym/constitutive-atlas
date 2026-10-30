# Clay2013 coupled research integration

The [seven-component draft](../../models/research/clay2013/hypoplastic-clay-2013-research.json) now runs through the common schema compiler and C++ engine, with an isolated `atlas_clay2013_solver` / `clay2013.js` target. The public catalogue and previous research catalogue are separate. The public clay entry remains a non-executable candidate.

The material law uses effective compression-positive Mandel stress plus void ratio, zero spin, and the five explicit constitutive parameters in the [source-rate audit](clay2013-source-rate.md). The [primary publication](https://doi.org/10.1007/s11440-012-0199-y) and [pinned author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_AG12-pp.pdf) remain linked in the model itself. `p_ref` is fixed at1000Pa by equal lower/upper bounds; `p_scale` only weights numerical stress errors. Defaults are illustrative software fixtures, with no calibration claim. Parameter bounds are project limits, not a complete source domain.

The model retains the stable Fm reduction and exact isotropy branch. Its positive-stress checks use the three elementary invariants of a symmetric matrix: positive trace, pairwise principal sum and determinant. These are equivalent to SPD in exact arithmetic. They do not certify eigenvalue signs arbitrarily close to a singular floating-point boundary. All named rate terms receive explicit magnitude/domain checks; derived expressions are evaluated before final domain predicates. No floor or projection is introduced.

The [initialization review](../reviews/clay2013-initialization-policy.md) distinguishes density conversion and declared preparation from material evaluation. A regular source-rate state on ASBS has an outward derivative, so ASBS containment cannot be a universal accepted-stage criterion. Research callers supply stress/e explicitly. The schema's default state is only a software fixture; arbitrary outside-ASBS physical initialization is unverified. Optional preparation policies, provenance and ASBS diagnostic export still need a dedicated initialization interface.

## Independent integration evidence

The [Decimal closed form](../../tools/reference_clay2013_isotropic.py) solves coupled isotropic pressure and density evolution, including arbitrary initial density and sign reversals. It imports neither Atlas nor a numerical ODE solver. Its [derivation and broader test plan](../reviews/clay2013-isotropic-trajectory.md) explain the reciprocal density-ratio transformation. Float inputs preserve actual binary64 identity; fixtures use exact decimal strings.

The retained [native matrix](../../catalogue/investigations/clay2013-integration-v1/native.json) contains33 trajectories and115 updates: pressures10,10000,1000000Pa; compression, unloading and reversal; tolerances1e-4,1e-6,1e-8; plus seven caller partitions at the middle pressure and loose/tight tolerances. Each trajectory fixes `p_scale` to its initial pressure. Every returned state is checked against the exact solution for the actual supplied increments. Both pressure and void-ratio final errors improve under refinement; caller-partition discrepancies shrink. Local tolerances are scaled error criteria, not global relative-error guarantees. An exploratory run using the fixed default100kPa scale gave substantially larger relative pressure errors at10Pa, motivating the explicit scale choice.

Eight additional native noncoaxial rates match independent Cartesian fourth-order contractions. Native tests cover zero increments, invalid initial domains, partial-progress budget failure and domain failure with exact returned-state rollback. Persistent Wasm probes repeat failed calls followed by valid calls to check contamination. These are numerical research checks, not experimental validation.

The [Wasm matrix](../../catalogue/investigations/clay2013-integration-v1/wasm.json) replays the same115 requests through the real C ABI, compares against native results and is separately assessed against the Decimal solution. The [manifest](../../catalogue/investigations/clay2013-integration-v1/manifest.json) records code, model, engine, evidence and source hashes. The [bounded independent review](../reviews/clay2013-engine-draft-review.md) covers the draft algebra, not scientific admission.

## Reproduction

Build one target at a time locally:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target atlas_clay2013_solver --parallel 1
python -m unittest tests.test_clay2013_engine tests.test_clay2013_isotropic_reference tests.test_clay2013_initial_policy -v
python -m tools.clay2013_integration_study --output /tmp/clay-native.json
emcmake cmake -S . -B build-wasm -DCMAKE_BUILD_TYPE=Release
cmake --build build-wasm --target atlas_clay2013_solver --parallel 1
node tools/test_clay2013_wasm.mjs --native-report /tmp/clay-native.json --wasm build-wasm/clay2013.js --output /tmp/clay-wasm.json
python -m tools.verify_clay2013_wasm /tmp/clay-wasm.json
```

Still open: nonisotropic finite-trajectory verification, boundary precision studies, publisher/manuscript reconciliation, source-matched preparation/calibration and experimental comparisons, independent scientific review and admission. Finite spin,2014 anisotropy and GIS coupling are separate extensions. The research target is not packaged as a public website model.
