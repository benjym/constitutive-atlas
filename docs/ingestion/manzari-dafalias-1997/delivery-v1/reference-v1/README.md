# Independent original-1997 triaxial reference v1

NUM-md1997-reference-v1. Owned scope is this directory. This calculation derives from the original paper, not the candidate JSON, generated code, Atlas evaluator, later SANISAND, or a compiled result. Original equations (7)–(13), (18)–(24), (26)–(29), pp259–263, were read in the private public-preview OCR; pp260,262,263 were also inspected visually here. The source specialist independently verified all source equations and Table 1. Exact source acquisition receipt remains in ../../source-v1/. The first of the two source b_ref alternatives is selected; evolving-m Appendix A is outside this record.

## Scalar derivation

Let t=absolute axial strain, z=+1 compression or -1 extension, p=(sigma_a+2sigma_r)/3, q=sigma_a-sigma_r (signed), alpha=alpha_a-alpha_r (signed backstress ratio), and eta=q/p. Axisymmetry gives n=z(2,-1,-1)/sqrt(6), backstress tensor alpha*(2,-1,-1)/3, and active yield eta-alpha=z*m. Define S=sqrt(2/3). On each fixed active branch:

- ec=.8-.025 ln(p/160), psi=e-ec.
- B=1.14+kb*max(-psi,0)-.05, with kb=3.975 or2 according to z.
- Bd=1.14+kd*psi-.05, with kd=4.2 or.07.
- b:n=S*(B-z*alpha); b_ref=2*S*(1.14+3.975*max(-psi,0)-.05).
- h=1200*abs(b:n)/(b_ref-abs(b:n)); C=h*(z*B-alpha).
- D=2.64*S*(Bd-z*alpha), clipped to zero only if psi>0 and D<0.
- alpha'=L*C; e'=-(1+e0)*epsilon_v'.

The scalar alpha evolution is obtained by subtracting radial from axial components of equation (24). Consistency differentiates eta-alpha=z*m to give q'=eta*p'+p*C*L. It does not invoke the candidate plastic modulus expression as an oracle.

For undrained strain epsilon_a'=z, epsilon_r'=-z/2, equation (13) gives p'=-K*L*D and q'=3G*z-sqrt(6)*G*z*L. Eliminating q' using consistency gives L=3G*z/[sqrt(6)*G*z-eta*K*D+p*C].

For drained constant sigma_r, q'=3p'. Put T=p*C/(3-eta), so p'=T*L. Axial elasticity plus plastic strain gives z=p'/(3K)+q'/(3G)+L*(z*S+D/3), hence L=z/[T*(1/(3K)+1/G)+z*S+D/3]. Radial strain follows epsilon_r'=p'/(3K)-q'/(6G)+L*(-z/sqrt(6)+D/3). These radial strains are included in every checkpoint.

For isotropic initialization, the elastic first-yield point is exact. Undrained: p=p0, q=z*m*p0 and |epsilon_a|=m*p0/(3G(p0)). Drained: q=3(p-p0), p=3p0/(3-z*m). Because G=K for this calibration, epsilon_a=(4/3)*integral(dp/K), and epsilon_r=-epsilon_a/8. The elastic integral is analytic for exponent a=.6. Void ratio during this elastic preparation uses fixed initial e0; no e=e0 approximation is used after a drained elastic leg.

## Execution and results

Run `python3 docs/ingestion/manzari-dafalias-1997/delivery-v1/reference-v1/reference.py` from repository root. Standard Python only. It overwrites only the reproducible report and manifest in this owned directory. Policy was written before the first execution, and has not been relaxed. Both RK4 resolutions are independently evaluated; the first-yield switch is split analytically. The report retains every fixed axial checkpoint and complete tensor stress/backstress.

All eight prospective cases pass the refinement and yield-drift gates. Maximum stress refinement difference is 0.000046513 Pa. All pressures stay positive and hardening-distance denominators stay positive. Hydrostatic compression and unloading match the analytic power-integral pressure solution to sub-nanopascal roundoff. A quarter-yield elastic loading/unloading cycle returns to the exact initial state.

`requests.json` declares source targets for downstream backend execution; it is not an Atlas API schema or a claim that backend execution occurred. `reference-results.json` is the independent oracle. Stress is serialized in Pa; calculations use kPa. Each initial state contains both e and fixed e0. Parameter pat=100 kPa is an explicit project reference choice, not a Table 1 measurement. Source pref is160 kPa.

## Boundaries

This qualifies scalar axisymmetric monotonic paths and elastic reversals. It does not independently verify general non-axisymmetric Lode interpolation, plastic reversal across the opposite yield branch, arbitrary initial anisotropy, evolving-m variants, p=0 behavior, b_ref singularities, full cyclic liquefaction, or measured experimental curves. The extension parameters were fit to source cyclic examples with weaker agreement; this reference establishes equation integration, not experimental validation. No compiled artifact has been executed by this worker. Unexpected backend failures must be retained and must not be converted to passes by changing the frozen tolerances.
