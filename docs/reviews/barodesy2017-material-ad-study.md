# Barodesy 2017 regular material Jacobians

Native C++ and persistent-module Wasm pass 21 regular instantaneous 7×13 Jacobians against independent Cartesian finite differences and source identities. Twenty rejection/recovery pairs pass in each backend. This is an instantaneous derivative at fixed soil parameters, not an integrated consistent tangent or scientific admission.

## Seed and branch contract

The isolated C ABI atlas_barodesy_material_ad(model, parameters_csv, state_csv, increment_csv) seeds all seven current-state components and six Mandel loading components simultaneously. Columns are sigma_xx, sigma_yy, sigma_zz, sigma_xy_Mandel, sigma_yz_Mandel, sigma_xz_Mandel, e, then the six loading components. Previous-state values and soil parameters are unseeded; the selected law has no previous-state dependency. Unused derivative slots must stay zero.

Responses bind complete model/hash/request/column identities and either finite values plus a 7×13 Jacobian, or null outputs. Exact zero and hydrostatic loading are excluded pending separate derivative-limit review. Hydrostatic classification uses exact input-component equality, including ±0.1I; a computed deviatoric norm alone can be contaminated by rounding. Near-hydrostatic cases are outside this first derivative corpus.

## Independent evidence

Seven regular cases per Table 2 soil cover oedometric, noncoaxial, reversal, rotated/reflected and positive-scaled loading. The independent Cartesian oracle uses adaptive 100-digit Decimal matrix exponentials. Scalar stages remain binary64. Central differences perturb all 13 scaled coordinates at fixed steps 8e-5, 4e-5, 2e-5 and 1e-5. Stress coordinates scale by max(1 Pa, ||sigma||), void by max(1, |e|), loading by ||de||.

A derivative-column comparison uses its scaled seven-component norm divided by max(1, primal-rate norm, reference-column norm). Final mismatch and last-pair refinement each have a fixed 2e-8 budget. Maximum observed final refinement difference is below 9.2e-11; maximum compiled-versus-final-grid discrepancy is below 6.2e-11. These are bounded observed refinement results, not rigorous derivative uncertainty bounds or per-entry relative guarantees. The frozen difference table is independently regenerated in tests; each runtime assessment recomputes its own differences.

Additional checks use the unchanged 2e-10 normalized identity budget:

- Loading homogeneity: J_loading loading = rate.
- Coordinate covariance for one fixed skew generator W: J acting on (W sigma - sigma W, 0, W loading - loading W) equals (W rate_sigma - rate_sigma W, 0). This does not define finite-spin transport.
- Density/void coupling: partial stress_rate / partial e = c3 ||de|| c5 density^c5 sigma / (1+e).
- Pressure scaling: J_sigma sigma = stress_rate + lambda_star (1+e) J_e, on the stress rows.

Void-rate derivatives of -(1+e) trace(loading) require exact algebraic zeros and at most four representable steps for nonzero values. AD primal values also satisfy the hardened rate channel checks. Synthetic tests reject small void-column corruptions and source-identity violations that the looser finite-difference norm could hide. Synthetic Richardson controls exercise the verifier only; they are never represented as native AD evidence.

Maximum scaled native/Wasm Jacobian difference is below 3.8e-16, against the fixed 2e-12 parity budget. Twenty finite invalid/recovery cases include the rate rejection corpus and zero/hydrostatic exclusions. Malformed CSV conformance, parameter sensitivities, zero/near-hydrostatic limiting tangents and full finite integration remain separate gates.

## Transport, replay and reproduction

Both collectors checkpoint raw/partial reports and transport companions before acceptance. Native exit/status correspondence, artifact path/hash shape, complete model description and original transcript SHA bindings are checked. Stored row metrics remain null; the independent verifier computes them. Historical numerical replay can explicitly skip unavailable backend bytes while preserving structure/source/numerical checks, and reports artifacts_verified_now=false.

```sh
python3 -m tools.barodesy2017_material_ad --native build/atlas_barodesy_material_ad_probe --output /tmp/barodesy-ad-native.json
node tools/test_barodesy2017_material_ad_wasm.mjs --native-report /tmp/barodesy-ad-native.json --wasm build-wasm/barodesy-material-ad.js --output /tmp/barodesy-ad-wasm.json
python3 -m tools.barodesy2017_material_ad --verify /tmp/barodesy-ad-wasm.json --native-report-path /tmp/barodesy-ad-native.json
```

Build each target separately with --parallel 1. See the [implementation report](../models/barodesy2017-research-rates.md) and [immutable runtime evidence](../../catalogue/investigations/barodesy2017-runtime-v1/manifest.json) for source selection and remaining gates. Source body/appendix differences, physical preparation, experimental/scientific review and public admission remain open.
