# HP/extracted-ASBS + GIS2024 research rates

The isolated schema `models/research/gis2024/hp-extracted-asbs-gis-2024-research.json` flattens the selected source pairing into the existing model schema and common generated C++ engine. It retains sigma6,e,h6,Omega,18 physical parameters and a separate numerical p_scale. Its source hyperlinks identify [Mugele, Stutz & Mašín2024](https://doi.org/10.1016/j.compgeo.2024.106480), the pinned institutional paper and equation locators. This is the extracted-ASBS HP pairing; it does not substitute the separate S=Y variant. No new DSL primitive, hand-coded material kernel, hidden preparation or state reset is needed for these continuous zero-spin rates.

The typed host/action fragment and full Cartesian/dense oracle are independently implemented. All38 retained14-component cases agree with the flattened interpreted model, isolated native target and real-C-ABI Wasm target. Cases include full symmetric memory, reversal/tangency, zero direction, noncoaxial random states, rotation and analytical differential identities. The oracle is an instantaneous reference; its scalar aligned-memory and frozen-memory checks do not establish a coupled finite trajectory.

The full pairing requires computed Mandel norm(h)<=R with no expanded tolerance shell or projection. Earlier staged policies differed between relative epsilon and ulp(R), and accepted a just-oversized h at Omega=0 whose Omega rate pointed negative. The stricter coupled guard removes that accepted shell. The old supplied-host fragment retains its historical policy; the full wrapper adds the stronger restriction. The isotropic-full test input is deliberately prepared at nextafter(R/sqrt(3),-infinity), not silently clamped at evaluation. Coordinate norm rounding can still matter at an oblique sphere boundary; a finite integrator's stage/boundary policy needs separate verification. See [boundary review](../reviews/gis2024-boundary-review.md).

Nonzero-direction suppression must remain positive; underflow is rejected rather than treated as a physical zero. Exact-zero direction skips the irrelevant nested exponent and returns all14 zero rates, even for a parameter set whose nonzero-direction suppression underflows. The direction-dependent k is undefined at zero; internal lazy placeholders are not a unique limiting modulus. The default state and source Table1 parameters are software/source fixtures, not a source-matched Wichtmann calibration.

```sh
cmake --build build --target atlas_gis2024_solver --parallel 1
python -m tools.gis2024_rate_study --output /tmp/gis-native.json
cmake --build build-wasm --target atlas_gis2024_solver --parallel 1
node tools/test_research_matrix_wasm.mjs --native-report /tmp/gis-native.json --wasm build-wasm/gis2024.js --output /tmp/gis-wasm.json
python -m tools.verify_research_matrix_wasm /tmp/gis-wasm.json
```

Retained reports and implementation/source pins are in `catalogue/investigations/gis2024-coupled-rates-v1/`. The isolated target does not enter the public five-model catalogue or existing research catalogue hash. Catalogue/browser sources link the draft and evidence while its public candidate remains non-executable.

Next gates are independent coupled finite histories with refinement and caller partitioning, failed-update rollback and persistent recovery, exact/near-boundary arithmetic, source-backed preparation and admissibility, author implementation/license/discretization reconciliation, applicable experimental comparisons and scientific review. This milestone verifies representation and bounded instantaneous arithmetic; it does not claim finite GIS integration, finite-spin objectivity or scientific admission.
