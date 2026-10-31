# Tresca — source-only ingestion packet

Task ING-tresca; owner clay2013_source_closure; 2026-10-31. Select **Tresca-associated-perfect-BK2022v1-BE**, research ID `tresca-associated-perfect-bk2022v1-be-research`: infinitesimal isotropic linear elasticity, associated normal-cone plasticity, constant positive maximum shear strength, no hardening, and a separately identified project backward-Euler update. This is a complete constitutive closure, not the yield criterion alone. No executable transcription, Atlas evaluation, build, compiled run or scientific admission is supplied.

## Identity and sources

Primary source: Tahar Z. Boulmezaoud and Boualem Khouider, *Unification of the mathematical model of elastic perfectly plastic solids: a convex analysis approach*, [arXiv2207.12719v1](https://arxiv.org/abs/2207.12719v1), [exact version PDF](https://arxiv.org/pdf/2207.12719v1), submitted26July2022,25pages. The local byte/hash receipt is in `source-receipt.json`. This is the named author preprint, not an asserted journal version or the historical1864 Tresca publication. No equivalence to later versions is claimed.

Read Downloads filenames and existing atlas inventories first: no matching Tresca primary file/dossier was found. The discovery entry only links OpenGeoSys and is not source evidence for a complete closure. The ROADMAP requests complete closure/corner treatment. An attempted primary2012 computational-plasticity lecture download failed expired TLS; that failure is retained, with no certificate bypass. The arXiv primary acquisition succeeded. The PDF skill was used read-only; complete pp1–3,6–7,15–21 were rendered and visually inspected. Raw PDF, extracted text and renders remain private; redistribution permission is not assumed.

Source locators: pp2–3 Eqs1–8 additive decomposition, admissibility, constant yield set, Hooke law, maximum plastic work/normality; p6 Eqs27–31 tangent/normal cones, projection and small-strain definition; p7 Eqs32–45 pressure invariance, constant positive Lamé moduli, inverse elasticity and projected rate; pp15–16 Eqs77–81 Tresca domain, convexity, pressure invariance, k>0 and explicit nonsmooth cases; p17 Eqs82–87 distinct-principal-stress rate; pp18–21 Eqs89–108 repeated-eigenspace normal projection and exact constrained minimization. The source's smooth polynomial discussion on p16 explicitly warns that its inequality is not equivalent to the Tresca set; that polynomial is not adopted.

## Complete law, units, signs and state

Use source Cauchy stress tau, total infinitesimal strain epsilon, elastic/plastic strain epsilon_e/epsilon_p. The source equations are

    epsilon_dot = epsilon_e_dot + epsilon_p_dot,
    tau_dot = C:epsilon_e_dot,
    C:A = 2mu A + lambda tr(A)I,
    tau in K = {A : (eigmax(A)-eigmin(A))/2 <= k},
    epsilon_p_dot in N_K(tau).

The normal cone is N_K(tau)={Z:Z:(eta-tau)<=0 for every eta in K}. This is the associated flow rule and handles corners without choosing one gradient. Constant K means perfect plasticity; no multiplier hardening variable, density, cap, tensile cutoff, viscosity or smoothing is introduced. The source also states instantaneous consistency epsilon_p_dot:tau_dot=0 under its stated time-regularity assumptions. Do not impose that rate identity as a finite-increment equality.

Parameters lambda>0, mu>0, k>0 are in Pa; lambda/mu are constant Lamé elasticity and k is maximum shear yield strength. Source p7 Eq37 gives E=mu(3lambda+2mu)/(lambda+mu),nu=lambda/[2(lambda+mu)], so this particular source range is E>0,0<nu<.5. General positive-definite elasticity permits wider nu, but this packet does not silently extend the selected source assumptions. Uniaxial yield stress Y=2k. No measured/calibrated geomechanical parameter set is supplied; fixture lambda3Pa,mu2Pa,k5Pa are analytical examples only. k is not automatically a soil strength calibration.

Source Eq30 is the positive infinitesimal symmetric displacement gradient. Adopt host compression-positive sigma=-tau, de=-delta epsilon, ep=-epsilon_p. The centrally symmetric yield set and isotropic elasticity make this simultaneous sign change preserve the same host equations: N_K(-tau)=-N_K(tau), and stress/plastic work is invariant. This is an explicit host mapping, not an inferred pore-pressure law. Declare total Cauchy stress, no pore pressure or effective-stress coupling, small_strain_3d, fixed_spatial, objective_rate:none. The source is infinitesimal and supplies no finite-spin transport; covariance does not supply one.

For a full history crosswalk select persistent stress sigma6 and plastic strain ep6. Plastic strain is included to preserve the source irreversible-strain history; it does not affect future stress in this constant perfect-plastic closure. A separately named minimal stress-only reduction could omit ep, but is not silently substituted here. Both use orthonormal Mandel order [xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz], with stress Pa and strain1; no engineering-shear factors. No total-strain state is required: initial total strain, if needed, is ep0+C^-1:sigma0. This avoids hiding a stress-free reference behind a nonzero supplied initial stress.

Initialization requires explicitly supplied finite complete sigma0 and ep0, positive finite parameters and sigma0 in K. Stress-free and arbitrary hydrostatic starts are admissible for k>0; an initially outside-yield stress must reject, not be projected silently. ep0 is a supplied history/reference; source normality gives trace-free *increments*, not permission to overwrite ep0. Example ep0=0 and sigma0=0 are software examples, not specimen preparation. There is no source pressure floor, positive-definite stress cone, nonnegative mean-pressure requirement or restriction against tension for this metal-style law.

## Discrete update — independently derived project choice

The preprint supplies continuum rate/normal-cone laws, not the following branch-by-branch backward-Euler implementation or its Atlas tolerances. Freeze it under the named BE suffix. Given parent sigma_n,ep_n and strain increment de, define trial T=sigma_n+C:de. Backward Euler requires

    sigma=T-C:dep, dep in N_K(sigma), sigma in K,
    ep=ep_n+dep.

Equivalently sigma uniquely minimizes (A-T):C^-1:(A-T)/2 over A in K. This follows directly from the convex first-order optimality condition, not a source quotation. Pressure invariance gives trace(dep)=0 and trace(sigma)=trace(T), reducing the objective to Frobenius projection of deviatoric stress. C is positive definite in the selected range, so the projection is unique even when multipliers/eigenvectors are not.

Let trial eigenvalues t1>=t2>=t3 and Y=2k. Coaxial reconstruction is the isotropic spectral projection (alignment maximizes trace(TA) for fixed eigenvalues). Exact branches:

| Test, in this order | Corrected eigenvalues |
|---|---|
| t1-t3<=Y | (t1,t2,t3), elastic |
| 3t2>tr(T)+Y | (a,a,a-Y), a=(tr(T)+Y)/3, upper double |
| 3t2<tr(T)-Y | (b+Y,b,b), b=(tr(T)-Y)/3, lower double |
| otherwise | (t1-q,t2,t3+q), q=(t1-t3-Y)/2, face |

The latter three tests apply only after elastic exclusion. At exact face/edge boundaries the listed face convention returns the same stress with one zero edge multiplier; it is a branch convention, not a unique classical tangent. Both edges cannot be strict simultaneously because Y>0. There is **no hydrostatic apex** for positive-strength Tresca: the admissible set is an unbounded cylinder, and hydrostatic stress is strictly inside. The k=0 degenerate cylinder is outside this selected model.

For smooth face the principal plastic multiplier for g13=sigma1-sigma3-Y is gamma13=q/(2mu). At upper edge, gamma13=(t1-a)/(2mu),gamma23=(t2-a)/(2mu); at lower, gamma12=(b-t2)/(2mu),gamma13=(b-t3)/(2mu). They are nonnegative in their sectors; dep=sum gamma_ij(Pi-Pj), with each active gap=Y, and all six ordered gaps<=Y. These exact KKT certificates prove the selected return, rather than relying on branch labels alone. Tensor dep=C^-1:(T-sigma)=(T-sigma)/(2mu) because its trace is zero.

## Tangents and existing generic capabilities

Existing [symmetric spectral helpers](../../SYMMETRIC_SPECTRAL.md) are sufficient building blocks; their installed numerical limitations still apply. Do **not** force strict-positive-phi/psi Mohr-Coulomb formulas to zero. This is a separately derived associated Tresca law with different pressure/apex structure.

Use lazy value-only principal comparisons for classification. Elastic returns T directly, avoiding spectral derivatives at repeated hydrostatic trials. Face returns T-q(Pmax-Pmin), using isolated extrema. Upper edge returns aI-Y*Pmin; lower returns bI+Y*Pmax. Repeated trial upper/lower pairs therefore need only the isolated opposite extreme, not arbitrary eigenvectors within the repeated eigenspace. Keep restricted spectral operations inside executed lazy arms; eager aliases can still fail before a safe branch is selected. The existing1024epsilon-scaled gap/isolation policy is a numerical limitation, especially when Y is tiny relative to a hydrostatic offset; it is not a physical Tresca exclusion.

For a strict smooth trial branch, directional derivative with respect to trial perturbation A is

    DR[A]=A - (n:A)n/2 - q(DPmax[A]-DPmin[A]), n=Pmax-Pmin,
    DPi[A]=sum_j!=i (Pi A Pj+Pj A Pi)/(ti-tj).

Upper edge: DR[A]=tr(A)I/3-Y*DPmin[A]; lower: tr(A)I/3+Y*DPmax[A]. Elastic DR[A]=A. Compose with C for the stress/de algorithmic tangent. Complementary repeated eigenvalues do not invalidate the isolated projector derivative; never divide by an unresolved selected gap. ep tangent is Dep[A]=(A-DR[A])/(2mu) with trial A=C:dde. The principal face Jacobian is [[1/2,0,1/2],[0,1,0],[1/2,0,1/2]]; strict edges give all entries1/3. Full tensor tangents additionally require the projector rotation terms; principal checks alone do not validate them.

Elastic/yield and face/edge boundaries generally lack a unique classical derivative. A selected branch Jacobian/generalized Newton policy must be declared and independently tested; arbitrary AD of sorted repeated values is not a substitute. Source pp18–21 separately describes the repeated-eigenspace continuum normal projection; six exact witness directions compare its Eqs93–99 against the constrained minimizer Eq108, preserving the distinction from this finite BE map.

## Schema v0.3 and temporal integration

`schema-crosswalk-v03.json` is a non-executable crosswalk with a **complete explicit** formulation: strain_path/incremental_residual, small_strain_3d,fixed_spatial,objective_rate:none,Mandel,compression-positive stress/strain,de finite increment input and empty advance context,total Cauchy state binding. Persistent sigma/ep must both be initialized; no legacy integration field. Mathematical residuals are sigma-return(T)=0 and ep-ep_n-C^-1:(T-sigma)=0. These are a proposed declarative branch representation, **not a model transcription or validated installed record**.

There is no physical clock, rate effect, creep or relaxation. An admissible parent and de0 return exactly the parent stress and plastic history; unloading is elastic until a new trial reaches yield. Reverse paths must remain signed and ordered; no reversal reset exists. Every attempted internal step and mixed-control trial uses the same committed parent; only accepted updates commit both histories, and failure must return complete incoming state. Transaction/rollback, tolerances, adaptive partitioning and mixed-control iteration are project requirements, not stated author software behavior. BE under subdivision follows an incremental path and need not equal a single unsplit projection for changing loading directions. Source instantaneous consistency is not a reason to force finite partition invariance.

## Independent checks and status

`prospective-freeze.json` SHA256 `223aee7e05330cbe80b55bb48bf9cc1d0e1dbc421eac50aafa9d18ab7fc8e3d7` was created before evaluation. Inputs, expected principal returns, exact rational rotations, corner directions and exact gates are frozen. `check_fixtures.py` uses only Fraction arithmetic and known eigenframes; it neither imports Atlas nor calls a numerical eigensolver. Twelve exact base certificates and twelve rotated stationarity certificates pass, including both repeated-trial pairs, hydrostatic tension/compression, zero, elastic, face, both edges, yield hold and exact face/edge boundaries. Seventy-two coordinate-permutation identities, nine strict principal tangent directions (two-sided), and six repeated-upper-corner normal/tangent checks pass. Repeated-eigenspace rational rotations also leave the tensor reconstruction unchanged. No failed assertion was observed. Acquisition failures remain in `acquisition-failures.json`.

Fixtures contain exact rational Cartesian matrices and principal strain increments from explicit sigma0=0,ep0=0. They are analytical references, **not** actual rounded binary64-Mandel spectral fixtures or a compiled acceptance corpus. There is no full38-column AD, floating-spectral, generated DSL, native/Wasm, finite path, experiment or scientific admission claim.

Reproduce: `python3 -B docs/ingestion/tresca/check.py --root /Users/bmar5496/code/constitutive-atlas`. It verifies packet/source/context hashes and exact fixture regeneration; raw private source unavailability is reported separately. No shared file is edited.

Handoff: source closure acquired for the named preprint; BE return and local principal/corner algebra independently checked; executable transcription absent; source-derived soil calibration absent; scientific review open. Coordinator should first review the selected full sigma/ep state and total-stress scope, then assign a separate declarative transcription with lazy branch construction. Freeze exact rounded tensor cases, both repeated spectra, large hydrostatic offsets/near-isolation, selected branch derivatives/all38seeds, initialization rejection, same-instance complete rollback/recovery and partitions before serial native/Wasm studies. A full algorithmic tangent review must include rotated off-diagonal directions. No model-specific handwritten kernel or new core primitive is requested by this source packet.
