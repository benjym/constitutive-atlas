# TMD2 benchmark Appendix A: bounded equation review

Task REVIEW-kfs-tmd2-appendix-law-v1, 1 November 2026. **The printed 2016 equations support the current eight-constant VW96 backbone composed with IGS, with the source-selected Karlsruhe parameters, after the stated paired sign conversion. No constitutive transcription correction was identified.** This closes one technical reading gap. It does not supply a scientific-admission signature, verify a solver, or resolve the historical large-strain coordinate.

A second technical agent inspected the exact private PDF, rather than relying on the earlier raster/input audit: complete Appendix A on PDF/printed pages18–19 and its continuation on20, visually at full-page resolution; context pp2–5 visually for execution provenance, history, Table2, named curves and Table3. The original VW96 p252/Eq2 and NH97 p280 sign paragraph were separately visually inspected to identify conventions missing from Appendix A. Source hashes/coverage are in sources.json. Private PDFs, extraction and renders are excluded from this deliverable. No Atlas evaluator, helper material call, author code or compiled artifact was run.

## Equation crosswalk

Let S be Atlas compression-positive effective stress, d its compression-positive strain-path rate and H its history tensor. For the source tension-positive tensors use sigma_s=-S, D_s=-d, h_s=-H. This convention is explicit in NH97 p280 and consistent with 2016's negative mobilized history in p3. Physical pressure maps to p=trace(S)/3. The 2016 Appendix does not independently define a tensor stress-sign/pressure relation; its plots and pressure tables use positive compression magnitudes. Do not infer the constitutive tensor sign from those plot axes alone.

| Printed 2016 locator | Current root expression(s) | Review |
| --- | --- | --- |
| A.1 p18: contractions, norm, normalization, trace and deviator | dot, norm, hat, hsdev, eta | Tensor Frobenius products. Mandel uses sqrt(2) times tensor shear components for stress, strain and history alike; its Euclidean dot preserves the printed double contraction. This is not engineering-shear Voigt notation. |
| Eq7 p18: stress rate L:D+N norm(D), and M:D | equations.sigma with overlay | Under zero spin the Jaumann stress rate reduces to the ordinary material derivative. The root is the IGS modification of this equation, not the unextended backbone. No finite-spin equivalence is claimed. |
| Eq8 p18: linear fourth-order L | factor, linear, linear_eta | C=fb*fe/(hat:hat); L:d=C*(F^2*d+a^2*(hat:d)*hat). Hat=S/trace(S) is invariant under simultaneous stress sign change. Symmetric identity contraction gives d, including shear. |
| Eq9 p18: nonlinear N | nonlinear | Printed source N_s=C*fd*a*F*(hat+dev(hat)); compression-positive N_c=-N_s. Root's leading minus is required. Eq9 includes fd; it must not be counted again outside N. |
| Eq10 p19 | a | sqrt(3)*(3-sin(phi))/(2*sqrt(2)*sin(phi)); degrees in Table2 converted to radians for root sin. |
| Eqs11–13 p19 | j2, tanpsi, lode, F | F=sqrt(u^2/8+(2-u^2)/(2+sqrt(2)*u*cos(3theta)))-u/(2*sqrt(2)); u=sqrt(3*j2); cos(3theta)=-sqrt(6)*tr(dev(hat)^3)/j2^(3/2). Signs, square-root grouping and powers agree. |
| Eq14 p19 | fd | ((e-ed)/(ec-ed))^alpha; no extra density multiplier is missing. |
| Eq15 p19 | fe | (ec/e)^beta; beta is a free eighth host constant, not fixed to1. |
| Eq16 p19 | fb | hs/n*(ei0/ec0)^beta*(1+ei)/ei*(3p/hs)^(1-n), divided by 3+a^2-a*sqrt(3)*((ei0-ed0)/(ec0-ed0))^alpha. Current order is algebraically identical. The zero-pressure ratios, not pressure-dependent e ratios, appear in this denominator. |
| Eq17 p19 | compression, ed, ec, ei | All three share exp(-(3p/hs)^n). hs and stress must share units; MPa to Pa scales both consistently. |
| A.3 p19: mobilization and direction | hn, eta, rho, projection | Source rho=norm(h)/R and eta=h/norm(h). Root agrees for physical 0<norm(H)<=R. Paired signs preserve eta_s:D_s=eta_c:d, so branch inequality does not reverse. Zero-history convention is separate below. |
| Eq18 p19 | overlay, linear_eta, equations.sigma | B=rho^chi*mT+(1-rho^chi)*mR. For t=eta:d>0, rate=B*L:d+rho^chi*((1-mT)*L:eta+N_c)*t; for t<=0, rate=B*L:d+rho^chi*(mR-mT)*(L:eta)*t. Exactly the contracted root structure. No norm(d) belongs on the overlay correction. At t=0 both corrections vanish. |
| Eq19 p19 | equations.h | H'=d-rho^beta_r*eta*(eta:d) when t>0, otherwise d. No 1/R factor occurs in H evolution; R only nondimensionalizes rho. Root strict >0 selection agrees with printed branch and equals d at t=0. |
| Not printed in Appendix A | equations.e | Root e'=-(1+e)*trace(d) follows the sign conversion of original VW96 Eq2, p252. Attribute this closure to that source; Appendix A alone is not a fully self-contained state-evolution specification. |

The fourth-order source dyads in Eq18 mean `(L:eta) tensor_product eta`, followed by contraction with d. Mistaking this for componentwise multiplication would lose the scalar eta:d and change the branch response. The independent checker preserves Cartesian shear weighting and verifies this contraction/sign structure with exact rational coefficient surrogates.

## Binding to the selected benchmark

The source's Table2 p4 contains all thirteen material constants: phi=33.1degrees, hs=4000MPa, n=.27, alpha=.14, beta=2.5, ei0=1.212, ec0=1.054, ed0=.677, R=1e-4, mT=1.1, mR=2.2, beta_r=.1, chi=5.5. They match the named published selection by symbols, including the order mT then mR. General beta in Eqs15–16 directly supports beta2.5; substituting NH97's beta1 specialization or the root illustrative default beta1.05 would be a different benchmark. p_ref is an Atlas scale, not a fourteenth material constant.

Table3 p5 identifies TMD2 e0=.975, ID0=.21 and p0=100kPa; Figure4a,b p4 explicitly names its curve. Section3.2 p3 says the simulations with isotropic consolidation start with fully mobilized isotropic history h_s,ii=-R/sqrt(3). Thus S0=100kPa*I, e0=.975 and H0,ii=+R/sqrt(3), off-diagonals zero, are source-supported nominal initial data. This directly initialized internal state is not evidence that Atlas reproduced the physical preceding consolidation. No measured first-point replacement, guessed zero-history state or default substitution is warranted. The selected binary64 rounded history has 3*Hii^2/R^2 slightly below1 in exact arithmetic (~3.03e-17 below), not an intentional history overshoot.

All eight backbone constants and five IGS constants have an explicit role above. hs/stress scale covariantly with pressure units; e, h, R and the remaining factors are dimensionless. Positive rescaling of d scales the rates without introducing an elapsed-time parameter. An accumulated strain-path coordinate therefore supports a rate-independent operational reconstruction; it does not determine the source software's finite-strain/output conversion.

## Source law versus project choices

These differences do not reveal an Eq7–19 transcription defect, but they prevent an exact historical-implementation claim:

- Appendix A gives an indeterminate direction at h=0. Root defines eta=0 there; with positive chi the resulting stress rate is mR*L:d and H'=d. This is a continuous extension, not an explicitly printed zero-history branch. TMD2 starts at nonzero saturated history.
- Root substitutes cosine=0 for j2<=1e-24. At exact isotropy F=1 follows from Eq11 independently of that indeterminate cosine. At small nonzero j2 this is a numerical continuation. TMD2 starts at exact isotropic stress.
- Printed rho=norm(h)/R has no cap. Root caps rho at1 and admits norm(h)<1.01R, without projecting H. Equivalence is established on the physical ball, not throughout that overshoot band. Eq19 preserves saturation for exact continuous forward-aligned loading: when rho=1 and d is a positive multiple of eta, H'=0; Eq18 then recovers L:d+N_c*norm(d). It supplies no finite-step overshoot algorithm.
- Positive pressure cutoff, strict ed<e<ei, F/fb positivity and current parameter boxes are runtime restrictions. Appendix A does not print them as a universal source validity domain. p_ref and scaled-state error norms are project numerics. Existing applicability decision0004 remains applicable.
- The continuous source has no prescribed physical clock, hold relaxation, numerical subdivision, rollback algorithm or error tolerance here. Atlas midpoint/subdivision, endpoint-defect checks and trial/commit behavior require their own evidence. A zero d gives zero rates; that does not independently authorize a resting-history reset.
- Source stress rate is objective; zero-spin axisymmetric material-point loading is the common scope. Extending this result to finite spin, arbitrary finite deformation or transport of history would require additional source/implementation evidence.

No full-path stage-domain audit was performed. Initial admissibility does not prove that internal integration stages remained inside the physical history ball or any compressive comparison restriction. Preserve that qualification rather than infer it from successful endpoint/output checks.

## Checks, limits and next action

Run `python3 check.py > /private/tmp/tmd2-law-checks.json` and compare with checks.json. All24 exact structural fixtures pass stress sign conversion, history sign conversion and unchanged branch projection; Ten separate transformation checks construct full Cartesian3x3 matrices, map their components to Mandel vectors in exact Q(sqrt(2)) arithmetic and independently contract both representations; paired signs and the hydrostatic invariant limit are also checked. A rational unit direction with a nonzero shear component participates in the24 branch fixtures. These fixtures use independently chosen rational coefficients and exponents to exercise structure, not the TMD2 material rates. They do not import or evaluate the root expressions and cannot certify their runtime execution. The equation-by-equation table is a visual/manual reading claim, distinct from these algebra fixtures.

No failures occurred in these checks. No model/schema change, integration request, build, calibration, acceptance adjustment or scientific admission was performed. The model remains a draft. The exact historical 2016 Incremental Driver and 2019 Abaqus decks, versions and engineering/logarithmic/output conversion are still unavailable. The prior frozen source envelopes and retained numerical outcomes are untouched.

Smallest next action: integrate this source-law reading with the coordinator's exact model/parameter/initial-state/request binding audit, and update the benchmark's open-gate wording from an unaudited Appendix law to the explicit remaining numerical-policy, historical-coordinate, scientific-review and rights limitations. No new numerical framework or repeat material sweep follows from this review.

The coordinator identified that the first Mandel assertion merely repeated the weighted-dot definition. That weak check is retained in initial-check.py and initial-checks.json; it is superseded by the explicit Cartesian-to-Mandel checks above. No model or acceptance policy changed.
