# Drucker–Prager — bounded source reconciliation

Task REVIEW-drucker-prager; coordinating parent, 1 November2026. This packet reconciles the current ideal-cone specialization and corrected apex algorithm, with a complete explicit v0.3 state/init crosswalk. It closes the bounded reconciliation/gap-report task, **not REV-02 or independent scientific admission**. Root bytes, existing dossiers/reports, compiler, solver and model status remain unchanged.

## Sources and exact identity

The [OpenSees primary documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/DruckerPrager.html) describes a broader model with hardening, backstress and a separate tensile surface. The [pinned source](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/DruckerPrager.cpp), commit `8a0273db3e2f5a14c05924a179c1e439500c852c`, was read statically at its trial invariants, smooth-cone correction and stress update. [Source receipts](source-receipts.json) hash the retrieved source/documentation bytes. No source was built, executed or vendored. Documentation is mutable; the source commit is pinned. This is review of the implementation references already selected by Atlas, not a new reading of the original1952 paper or every OpenSees code path.

The [Itasca formulation](https://docs.itascacg.com/itasca930/common/models/drucker/doc/modeldrucker.html), Eq9/12/17–23 and “Apex Stress Correction,” supplies a separate radial-return comparison, also with a tensile surface. The URL currently returns a9.4documentation title. No immutable version/hash or executed cross-code comparison is claimed for that page.

Atlas selects constant isotropic elasticity, perfect plasticity, no backstress/hardening and no separate tensile cutoff. In its compression-positive Mandel convention:

`f=q-M*p-c<=0`, `g=q-Md*p`, `q=sqrt(3*s:s/2)`.

Parameter conversions matter. After eliminating OpenSees hardening/backstress and reversing paired stress/strain signs, multiply its yield function by sqrt(3/2): M=3sqrt(3/2)rho, Md=3sqrt(3/2)rhoBar and c=sigmaY. Atlas gamma=sqrt(2/3) times the OpenSees smooth shear multiplier. The Itasca shear branch instead uses M=sqrt(3)q_phi, Md=sqrt(3)q_psi, c=sqrt(3)k_phi, gamma=lambda_s/sqrt(3). Atlas c is a yield intercept; it must not silently be treated as Mohr–Coulomb cohesion. Removing the separate tensile surface is a specialization decision, not full-algorithm equivalence.

## Corrected apex and numerical choices

The preserved [apex dossier](../../models/drucker-prager-apex.md) gives the full project derivation. For elastic trial p_t,s_t,q_t, the smooth return gives q=q_t-3Ggamma, p=p_t+K*Md*gamma. The ideal-cone norm subgradient at q=0 admits zero deviatoric stress once gamma>=q_t/(3G). The root residual implements both using min(3Ggamma/q_t_safe,1) times s_t.

At q_t=0, s_t=0; the selected denominator p_ref only prevents division by zero. It is not a nonzero stress floor or regularized apex. This derivation is restricted to the stated constant-isotropic-elastic, perfect-plastic law. It cannot be carried unchanged into hardening or anisotropic elasticity. Fischer–Burmeister complementarity and exponential e bookkeeping are project numerical choices. e is uncoupled from stiffness/strength; its positive-domain requirement can reject a stress update for bookkeeping reasons. No finite-strain kinematics follows from the exponential.

The [preliminary dossier](../../models/drucker-prager.md), failed v1 evidence and passing apex v2 evidence retain their historical identities. The corrected law addresses the observed old shear/apex failure; it does not establish arbitrary-path nonlinear convergence.

## Parameter-admissibility finding

OpenSees explicitly documents0<=rhoBar<=rho. The positive scaling above gives0<=Md<=M. Atlas's current parameter boxes permit Md>M and its domain does not impose that relation.

On the smooth yield surface, plastic work for a multiplier increment gamma is

`D=gamma*(q-Md*p)=gamma*((M-Md)*p+c)`.

For M=1.2,Md=2,c=10000Pa,p=100000Pa, q=130000Pa, gamma=.001, this is exactly -70Pa. The witness has compressive principal stresses and is admitted by the current initializer without projection. It is a local hypothetical plastic increment at a yield state, not a newly integrated experimental trajectory. A diagnostic pass reproduces the limitation; it does not accept negative dissipation scientifically.

For M>0,c>=0,0<=Md<=M on the ideal cone, p>=-c/M and the above expression is nonnegative (its minimum over p is c*Md/M times gamma). The frictionless limit M=Md=0 is the pressure-independent J2 case. This proof and the source recommendation justify a separate parameter-domain correction study. Do not silently rewrite the hash-pinned root or retrospectively relabel its evidence. Md0 with M>0 still has no volumetric apex correction when p_t<-c/M; transactional failure remains expected even after enforcing Md<=M. Source recommendations do not imply universal solvability.

## v0.3 state, initialization and integration contract

[formulation-crosswalk.json](formulation-crosswalk.json) maps all six parameters, eight derived quantities and three residual equations. The complete profile declares infinitesimal3D, fixed spatial zero-spin incremental residuals and compression-positive Mandel effective Cauchy stress. Effective stress is the Atlas soil-host interpretation; no coupled pore-pressure process is inferred from these stand-alone source files.

Persistent sigma is a spatial symmetric tensor and e an invariant scalar. Temporary gamma is a `plastic_multiplier`, zero-filled by explicit initialization and reset per internal solve. Required supplied state is exactly sigma,e; accumulated plastic strain/source hardening variables are not part of this perfect-plastic state. Illustrative100kPaI,e=.7 is not calibrated specimen preparation. Initial yield uses the project scaled tolerance<=1e-8, and the iteration domain admits gamma>-1e-9. These are numerical restrictions, not exact converged complementarity conditions.

Repeated trials start from committed persistent input. Trial stress uses sigma_n and supplied de, while each successful internal step commits sigma/e. Returned gamma belongs to the final internal solve and is not cumulative history. Full failure restores the complete incoming layout despite tentative partial progress. These lifecycle statements describe the existing engine contract; this packet does not execute a fresh rollback/control test. There is no physical clock, hold relaxation or automatic reset event. Admissible zero loading has unchanged persistent fields and gamma0. Finite rotations and a globally smooth tangent through the yield/apex branches remain unsupported.

## Checks and retained evidence

```sh
python3 docs/ingestion/drucker-prager/check_crosswalk.py --repo .
```

[Saved checks](crosswalk-checks.json) validate12 contract/initialization/reference-limit observations, the exact negative-work witness and three independent scalar-reference/current-Python residual cases (elastic,smooth plastic,apex). Diagnostic absolute residual budgets are fixed before calls; no result-dependent adjustment is used. The source-specific reference is verification code, not a production constitutive kernel. A reference rejection at Md0 beyond the apex is not a newly run native rollback test.

Both old report hashes match: [v1 failed](../../../catalogue/evidence/drucker-prager-investigation-v1.json) and [v2 passed73 cases](../../../catalogue/evidence/drucker-prager-apex-v2.json). Neither compiled suite is rerun here. The new [pending v3 review](../../../catalogue/reviews/drucker-prager-source-v3.json) narrows the remaining work without changing old records or claiming independent authorship.

## Handoff

This bounded source/initialization mapping is complete; the existing executable support and numerical evidence remain separate from scientific admission. Remaining actions are the source-supported Md<=M domain correction with archived prior identity and prospectively frozen checks, followed by independent scientific assessment of the source/apex/evidence package. Broader experimental accuracy, convergence and finite kinematics remain unproved. No new model, root migration, generic solver feature, build, compiled call, push or deployment occurred.
