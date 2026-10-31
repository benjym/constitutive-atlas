# Barodesy material AD independent numerical/core review

Read31October2026 installed `tools/barodesy2017_material_ad.py`, `tests/barodesy_material_ad_driver.cpp`, `tests/test_barodesy2017_material_ad.py`, independent Cartesian oracle and corrected body-law source selection. No native/Wasm/builds/core edits. Transport/archive fixes are being handled in another lane. This report covers regular instantaneous material derivatives, not zero/hydrostatic limits, integration or scientific admission.

## Core mathematics

No blocker found in driver seed layout: seven current-state entries get derivative0..6; previous entries get constant Jets; six Mandel loading entries get7..12; material parameters remain double constants. Output7x13 matches sigma6/e rows and stated stress6/e/loading6 columns. It also verifies unused Jet slots13..37 are zero. The history-free source law needs no previous-state derivative; this does not establish a general previous-state contract or parameter sensitivities.

Exact zero and exact componentwise hydro loading are excluded before material evaluation. The explicit hydro test is needed because dev(.1I) can have floating residue; norm(dev)>0 alone is insufficient. Corrected model's own guards still exclude unsupported normalization/K0/numeric boundaries. Selection currently21regular cases, excluding all72nearhydro cases and zero/hydro branches; no branch-limit derivative claim follows. The fixed orthogonal covariance derivatives are appropriate despite unresolved finite-spin source print.

Scaling is coherent: each FD perturbation is h*s_k in its column's own units; `(fplus-fminus)/(2h)` estimates J[:,k]*s_k. Candidate AD columns are multiplied by exactly s_k before comparison. State stress uses max(1Pa,normsigma); e uses max(1,|e|); loading uses normincrement. For the selected regular corpus these scales are finitepositive and perturbations remain supported. The seven-output norm is dominated by Pa-valued stress and mixes physical units; analytic void checks are therefore essential rather than redundant.

Independent reference imports no Atlas DSL or AD and uses its own Cartesian exponential recurrence. However its constants, invariants, density and rate differences are binary64; only the matrix exponential is Decimal100 on the actual rounded argument. Four central grids h=8e-5,4e-5,2e-5,1e-5 show observed convergence. Last-pair agreement2e-8 plus finalAD-FD2e-8 is **not a rigorous error certificate**, full arbitraryprecision derivative, all-component relative bound or a universal regular-domain claim. Current all21 tests observe final differences<1e-9; do not erase coarse levels when retaining evidence. A future plateau/cancellation study or highprecision entire-rate oracle is useful if tolerances tighten.

Euler `J_de*de=rate` and infinitesimal rotation `[W,sigma]`/`[W,de] -> [W,rate]` are derived correctly. The latter uses one fixed skew generator; testing all three independent skew generators would cover the whole rotation Lie algebra, while current full13column FD remains the principal numerical comparison. Positivehomogeneity does not imply reversal oddness; corpus includes reversal explicitly.

## Concrete channel blindspot

`assess_case` analyticvoid loop uses abs(error)<=2e-12*max(1,abs(expected)), so exact algebraic zeros are not exact constraints. Retained `probes.json` reproduces a synthetic Richardson mock accepted after setting row6column0,10or12 to1e-12. FD/Euler/rotation still pass because the large stressnorm masks this small dimensionless corruption. Recommend exact zero whenever expected analyticvoid derivative is zero; require at most4binary64 representable steps for nonzero analytic values, using the same checked numeric/type policy as scalar/rate studies. This is a verifier hardening issue, not evidence of a production AD bug. Staged boundary regressions intentionally target this gap and are **not claimed passing against the original verifier**. They also reject a5ULP normal-loading void derivative that currently slips under the absolute floor.

AD primal acceptance currently uses only the old seven-component norm budget. Reuse the hardened rate exact-zero/voidULP/stress-envelope checks on AD values, with independently regenerated source derived quantities, to avoid weakening the primal rate contract merely because Jacobians are being studied. A tiny nonzero primal shear/void corruption can otherwise be hidden by a large stress norm.

## Additional source identities

Let r=||de||, d=(1+e)/(1+ec), c5 be sourceTable1, with pressure-dependent ec chosen from the body2p formulation. Since only g contains d^c5,

`d(stress_rate)/de = c3*r*c5*d^c5*sigma/(1+e)`.

The input sigma is scaled holding e/loading fixed; d scales as sigma^lambda and both source stress terms have one stress factor. Therefore

`J_sigma*sigma = stress_rate + lambda*(1+e)*J_e`.

These identities target the density derivative and pressure-scale coupling independently of central differences. They do not assume degree-one stress homogeneity, which would be wrong. Synthetic Richardson mock checks give normalized residuals1.445e-11 and2.206e-11, compatible with its FD uncertainty. Actual AD should perform much better; choose and declare an identity budget before checking actual outputs, rather than treating the synthetic residual as measured AD accuracy. Parameter sensitivities remain outside13column scope.

## Retained files

`probes.json` records the bounded accepted-corruption demonstrations and synthetic control metrics; no nativeAD evidence is fabricated. `test_barodesy2017_ad_boundary_regressions.py` is a test suggestion for after hardening, not an authoritative test edit. Source/operator/body-law numerical support gates remain separate from this review.
