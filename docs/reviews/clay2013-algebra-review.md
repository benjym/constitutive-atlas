# Clay-2013 invariant algebra: bounded independent diagnostic

This packet checks algebra and selected limits only. It does not admit a model or close source, parameter, initialization, integration or scientific-review gates. No production DSL evaluator or native solver is used. `tools/clay2013_invariant_reference.py` implements Cartesian arithmetic with 180-digit Decimal; `tests/test_clay2013_invariants.py` has four passing groups. Evidence contains full Cartesian inputs/results and generator hash. This record retains the independent review and diagnostic fixtures.

## Stable Fm identity

Let S=tr(sigma)>0, r=sigma/S=I/3+a, tr(a)=0, j2=a:a, j3=tr(a^3), with source T=-sigma. Newton identities give

- det(r)=1/27-j2/6+j3/3.
- I1=-S, I2=S^2(-1/3+j2/2), I3=-S^3 det(r).
- 9I3+I1I2=S^3(j2-3j3).
- I3+I1I2=S^3[8/27-(j2+j3)/3].

Therefore the proposed `Fm=(j2-3*j3)/(8/27-(j2+j3)/3)` is exactly equivalent in real arithmetic to source Eq.(50), provided the source's negative-second-principal-invariant convention is retained. It avoids the cancellation of the source numerator at isotropy. It is not immune to all floating-point cancellation near the compressive-domain boundary.

For strictly SPD r, let positive eigenvalues rho_i sum to1, s2=sum_{i<j}rho_i rho_j, delta=product(rho_i)>0. Then `Fm=(s2-9delta)/(s2-delta)` and `s2/delta=sum_i 1/rho_i>=9`, with equality only at isotropy. Thus denominator>0 and 0<=Fm<1, with Fm=0 only isotropic. This is a sufficient mathematical domain for the invariant factor, not proof of full material admissibility. Boundary rank-one states can give0/0. Some indefinite states may also give an evaluable Fm, so Fm bounds alone are not an SPD validator.

For x=sin(phi_c)^2 in(0,1), `omega=-ln(1-x)/ln2 + .3(Fm-x)` is positive throughout this SPD scope: `omega >= x(1/ln2-.3)+.3Fm>0`. Strict SPD with positive angle also prevents dA=0: at a!=0 its deviatoric part is nonzero; at a=0 its spherical coefficient is strictly negative. Other material/domain factors still need their own checks.

## Isotropy, continuity and Lode endpoints

At exact isotropy Fm=0 and a=0. For0<phi_c<pi/2, Eq.(56) gives `dA=-(2/3)*sin(phi_c)^xi/(1-sin(phi_c)^xi)*I`, hence exact normalized limit `d=-I/sqrt3`. Eq.(57) itself is undefined there; this is a derived limiting branch. No arbitrary isotropic Lode angle is required. The phi→0 limit is a distinct degenerate joint limit and is not covered.

Along a=tB with a fixed nonzero traceless symmetric B, Fm=(27/8)t^2(B:B)+O(t^3); cos3theta remains bounded although its isotropic limit depends on B. The spherical correction in dA is O(sqrt(abs(t))) and tends to a nonzero negative constant. Normalization therefore gives d→-I/sqrt3 independent of B, with direction distance O(abs(t)). Decimal axisymmetric fixtures at t=±10^-2 through ±10^-45 demonstrate this without clipping. They use sigma=diag(1+2t,1-t,1-t); since trsigma=3, a=(t/3)diag(2,-1,-1). Their source Lode cosines are exactly -sign(t) in real arithmetic. Rotated general-SPD examples separately compare direct source invariants with the stable expression.

Floating-point warning: current ordinary `dev(sigma/trsigma)` does not reliably recognize exact isotropic input. For sigma=.3 I, normalized diagonal is `.33333333333333337`; subtracting its ordinary trace/3 produces three identical residuals `5.551115123125783e-17`. j2 is spuriously positive and Eq.(57) gives approximately -sqrt2, outside[-1,1]. Merely switching to dev(sigma)/trsigma fails similarly for sigma=.1 I. A project numerical policy must preserve exact spherical tensors (e.g a reviewed pairwise-diagonal-difference deviator or robust exact-spherical branch), test the chosen implementation, and expose rejection/rounding policy near Lode endpoints. Do not clip silently.

Another numerical boundary: a strictly SPD rotated diag(1e-30,1,2) has real Fm<1 but rounds to1 in binary64. A conservative implementation can reject after that loss; if it intends to retain the state, independently compute/guard a stable positive `1-Fm=8delta/(s2-delta)` rather than manufacture a floor. This packet does not choose that policy.

## Source scope

Source algebra is the existing project extraction in `docs/reviews/clay-2013-2014-source-packet.md`, Appendix Eqs.(50),(53)–(58), source PDF pp.13–14; this review visually checked rendered pp.13–14 Eqs.(43)–(58). The original published/preprint reconciliation and complete source-independent scientific review remain open. These fixtures are mathematical identities and proposed numerical-limit diagnostics, not material trajectories, experiment comparisons, or native/Wasm evidence.

## Follow-up staged-fragment review

Reviewed `catalogue/source-audits/clay-hypoplasticity-2013-rate.json` and `tools/inspect_clay2013_rate.py` after the typed-zero correction. No remaining algebra or compression-sign blocker found against the visually inspected source equations. In particular source Ad maps to `fs*L:d-(sigma/lambda_star)*tr(d)`, and source stress equation maps to the positive nonlinear term in compression-positive sigma/stretching. Source 1 kPa reference pressure is represented as1000 Pa. This is a zero-spin per-unit-path rate diagnostic, not a time integrator.

The revised `dev(dev(sigma/trace(sigma)))` and exact-isotropic input test remove the demonstrated spherical-roundoff issue. Actual staged evaluation at p=.1,.3,1,1e5,1e-80,1e80 produced exact j2=Fm=0 and d=-I/sqrt3; staged load/typecheck passed. The helper rejects zero j2 from genuinely nonisotropic input, out-of-domain raw Lode values beyond its explicitly documented64ulp allowance, and nonfinite intermediates. It does not silently clip. This supports the bounded numerical policy; it does not prove that every SPD binary64 input is retained, or that every near-endpoint evaluation is accurate. The near-compressive-boundary Fm rounding example above remains a deliberate reject-or-reformulate policy boundary. Tiny positive phi can likewise lose precision in literal cos(phi)^2; practical accepted numerical domain is narrower than the mathematical open interval.

## Optional GIS supplied-host review

Reviewed `catalogue/source-audits/gis-2024-supplied-host-rates.json`, `tools/inspect_gis2024_rates.py`, `tests/test_gis_fragment.py` and `docs/models/gis-2024-supplied-host-rates.md`. Visually checked source Mugele–Stutz–Masin2024 PDF pp.5–7 Eqs.(33)–(43), SHA25639ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3, DOI10.1016/j.compgeo.2024.106480. No source-expression/sign blocker found in the supplied-host contract.

Eq.(33) positive-loading h rate, Eq.(39) two loading branches, full symmetric h, rho=h norm/R, Eq.(40) nested S^(k^gamma) and outer k multiplying the entire host E action, and Eqs.(41)–(43) chi/gamma/Omega dependence agree. With rho=1 the0/90/180degree values are k=1/mT/mR; rho=0 gives mR. Mapping stress, strain-like h and supplied m/f together under the compression sign change is consistent. Source's possible gammaOmega=gamma choice is not mandatory and the fragment appropriately keeps it explicit. Exact zero direction returns zero rates while q/k/suppression remain undefined; it requires zero supplied f. These are declared continuation policies, not an invented host model.

All8 GIS pure-Python test groups passed, including Cartesian oracle, covariance, sign mapping and positive rate homogeneity. Those tests do not validate an actual HP/IS host, ASBS, chosen initialization, frame/objective transport, coupled integration or experimental paths. E/m/C/S/f consistency and homogeneous f remain caller obligations. The stage uses a bounded finite-arithmetic evaluator and conservative domain rejection, with no clipping or claim of closed scientific review.

## Final normalization/interpolation follow-up

The final staged clay expression `dev(dev(sigma))/trace(sigma)` is algebraically equivalent and improves near-isotropic fidelity by removing the spherical component before normalization. Independent100-digit Decimal calculations initialized with `Decimal.from_float` on the actual supplied diagonal stresses at eps=1e-2,1e-4,1e-8,1e-12 found relative Fm errors at most2.47e-16 and absolute cos3theta errors at most3.34e-16. Exact isotropic p=.1,.3,1e-80,1e80 remained exact j2=Fm=0. No new algebra blocker found; finite intermediate overflow/underflow still gives conservative rejection rather than full-SPD coverage.

Final GIS convex interpolation is algebraically correct on each loading branch. Actual staged helper with rho=1, mR=2e20, mT=1e20 returned k=1,1e20,2e20 at q=1,0,-1 respectively. This removes the demonstrated unit-term cancellation. The existing raw-q allowance stays explicit and unclipped; extremely large multipliers can amplify accepted q roundoff, so these endpoint regressions do not establish uniform relative accuracy for arbitrary huge parameter ratios. No additional source-expression blocker found.
