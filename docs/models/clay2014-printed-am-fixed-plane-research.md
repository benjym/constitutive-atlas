# Mašín2014 fixed-plane printed-Am base-rate research fragment

This isolated draft transcribes the complete seven-state **base** law, with stress/effective Cauchy stress and void ratio, from the pinned [2014 author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/Masin_Geot14-pp.pdf), [DOI10.1680/geot.13.P.065](https://doi.org/10.1680/geot.13.P.065). SHA256: `2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202`. All locators are one-based manuscript PDF pages. The [source dossier](hypoplastic-clay-2014-original.md) records acquisition, final-publisher access gaps, and the distinct AppendixB IGS normalization problem. This fragment includes no IGS and repairs no printed equation.

The model ID is `hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane-research`. The exact choice is printed Eq14 Am, proposed Eq49 alpha_f, source peak coefficient a=.3, fixed supplied material-plane normal and zero spin. It is neither the optional calibrated-alpha variant nor the old2013 alpha_f=2 model. Even at unit anisotropy ratios only the scaled **linear action** recovers the2013 isotropic action; the exponent choice differs. No full-model, experimental, tangent, preparation, integration or public admission follows from instantaneous algebra checks.

The model lives alone in `models/research/clay2014/`; it must not enter the public or prior research catalogue implicitly. It uses the existing schema0.1 rate engine and scalar parameter contract. No new operator or handwritten constitutive kernel is introduced. `catalogue/source-audits/clay-hypoplasticity-2014-base-rate.json` is the typed equation/locator ledger; `tools/inspect_clay2014_rate.py` validates and evaluates that ledger using the generic finite-intermediate, lazy-branch DSL evaluator. The full model has the same equations expressed in the ordinary `derived`/`equations` form. Scalar diagnostics remain derived terms/typed-ledger outputs because schema0.1 does not expose physical-time observables.

## Source choices and signs

Pages2–3 Eqs2–8 give L. Its symmetric action is

`L:X=a1*X+a2*I*trace(X)+a3*(P*trace(X)+I*dot(P,X))+a4*(P X+X P)+a5*P*dot(P,X)`.

The mixed product is expanded into six Mandel scalar components, not evaluated with a dimensional P+X sum or a new tensor multiplication kernel. This retains the source a1/2 and Eq3 symmetrization factors through contraction to a1*X. Page3 Eq15 gives `fs=9p/(2Am)*(1/lambda_star+1/kappa_star)`.

The printed Eq14 value is retained in `Am`, while `Am_trace=3a1+9a2+6a3+2a4+a5` and `Am_discrepancy=Am-Am_trace` expose its disagreement with the contraction. For alpha_G=2, alpha_E=2^1.25, alpha_nu=2 and nu_pp=.1, the two values are approximately6.6609096228707845 and6.74576243661317. The difference is `2alpha_E^2*nu_pp^2*(1/alpha_nu^2-1)`. No diagnostic or rate substitutes Am_trace for Am, and no claim that the arbitrary-anisotropy unloading calibration identity is consistent is made. Publisher reconciliation or an explicit corrected variant remains separate work.

Pages9–10 AppendixA Eqs34–50 give the nonlinear base rate. With source T=-Sigma and D=-E, compression-positive zero-spin rates are

`Sigma_rate=fs*(L:E)+(fd/fdA)*(fs*(L:d)-(Sigma/lambda_star)*trace(d))*norm(E)`.

The source d is unchanged by the simultaneous stress/stretching sign map. Eqs36 and38 both use the proposed Eq49 exponent: `fd=(2p/pe)^alpha_f` and `fdA=2^alpha_f*(1-Fm)^(alpha_f/omega)`. The factor2 is retained. d=dA/norm(dA), pe, Fm, omega and xi follow the AppendixA definitions. The source a=.3 in omega, Eq50 friction_a, and Eq49 alpha_f are distinct quantities. Void closure `e_rate=-(1+e)*trace(E)` is inherited incompressible-grain host physics, not a newly printed2014 equation.

## Inputs, orientation and numerical support

Ordered scalar parameters are p_ref,p_scale,phi_c,lambda_star,kappa_star,N,nu_pp,alpha_G,alpha_E,alpha_nu,n1,n2,n3,source_a,lode_roundoff_allowance,orientation_allowance,stress_interior_margin. p_ref is fixed1000Pa; p_scale is only a numerical stress error scale. source_a=.3 and the three64-binary64-epsilon policies are fixed. phi_c is in radians. All defaults are illustrative software fixtures, not a London-clay or other source calibration. The bounded scalar ranges are implementation support, not published calibration intervals.

The three finite axis components specify the actual P=n outer n in Mandel xx,yy,zz,xy,yz,xz order. Each component lies in[-1,1] and `abs(n:n-1)<=64epsilon`. Invalid axes are rejected; none is normalized. P is rankone by construction, while unit trace/idempotence hold to the declared supplied-axis arithmetic tolerance. n and -n give the same material plane. This is fixed global material orientation under zero spin; finite-rotation/fabric transport is absent. Rotating stress, loading and axis together is a change-of-basis test, not a fabric evolution law.

Selected support requires e>=0,lambda_star>kappa_star>0,positive anisotropy ratios,-1<nu_pp<.5,positive pressure,positive Eq49 logarithm argument and positive alpha_f. Positive alpha_f is an explicit bounded research restriction, not a claim that every algebraically evaluable Eq49 parameter tuple requires it. B=1-nu_pp-2alpha_E*nu_pp^2/alpha_nu^2 and printed Am must be positive. For an exact unit axis the printed coefficients give canonical normal-block minor2=alpha_E^2 B(1+nu_pp), determinant=alpha_E^2 B^2(1+nu_pp)^2 and Mandel shear eigenvalues alpha_E B and alpha_E B/alpha_G. The draft also checks finite normalized canonical normal minors/determinant and both shear values against64epsilon. This is a conservative numerical interior; it is not a certified floating-point stiffness theorem for all rounded axes or physical calibration admission.

Stress support uses positive normalized Cartesian diagonal entries plus leading minor and determinant above64epsilon, scaled by the supplied Mandel Frobenius norm. Ill-conditioned positive tensors may be rejected. This numerical interior is not an exact SPD certification. All executed intermediates must be finite; fd/fdA/fs/pe/d normalization and power/log domains remain explicit. Fm uses the stable deviatoric invariant reduction and double projection before stress normalization. Exact spherical stress uses the inherited reviewed algebraic isotropic d limit, while a nonisotropic input whose j2 underflows to zero is rejected. Raw Lode cosine may exceed[-1,1] only within64epsilon; it is not clipped. The ASBS value is diagnostic, not an enforced yield barrier.

The schema0.1 path coordinate is dimensionless: supplied E is the symmetric loading direction per caller coordinate and stress_rate is per the same coordinate. Homogeneity supplies rate independence. No physical elapsed-time kinetics, material-plane time transport or implicit time discretization is added.

## Verification scope and remaining gates

Ten staged Python groups pass, including all37 independently authored Cartesian four-index reference cases in `tools/reference_clay2014_cartesian.py`, every stress/void output, zero/hydro loading, noncoaxial/shear/rotation and axis-sign cases, printed-Am selection, both density exponents, orientation boundaries, numerical domains, typed-source corruption and failed generic preparation without mutating the supplied parent. The Cartesian oracle uses direct determinant invariants and independent source sign conventions; it is binary64 and avoids near-isotropic determinant cancellation in its general-stress corpus. Agreement is bounded algebra verification, not an exact mathematical proof or integration result.

No native/Wasm build or execution was performed in this packet. Next gates are independent source/model review, source-bound generic native/Wasm instantaneous parity with retained raw failures, finite-path convergence/rollback, explicit preparation/initialization studies, final-publisher reconciliation and experiments. AppendixB IGS must remain separate until its normalization issue is resolved as an explicitly identified source choice.
