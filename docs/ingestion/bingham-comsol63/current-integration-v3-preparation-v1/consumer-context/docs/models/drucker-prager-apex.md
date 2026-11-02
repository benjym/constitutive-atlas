# Drucker–Prager: declarative apex correction

This revision replaces the previous `q`-direction regularization with an explicit apex branch for the ideal cone. The stable formulation ID remains `drucker-prager`; model hashes distinguish the algorithm revisions. No generic C++ solver, generated-model dispatch or tolerances were changed. Scientific status remains **transcribed; independent review pending**.

## Evidence for the change

The [v1 investigation](../../catalogue/evidence/drucker-prager-investigation-v1.json), pinned to the previous definition, retains the failure from `sigma_n=100 kPa I`, `e_n=.7` and `de=(-.002,-.002,-.002,.00001,0,0)`. Its ideal cone reference is `p=-c/M=-8.333333 kPa`, `s=0`. The old solver transaction rolls back after unsuccessful subdivision.

A temporary instrumented single-step Newton run of that definition showed the shear component repeatedly changing sign while pressure remained near the tensile trial value. At iteration 29 the scaled residual was about `.269`; line search then failed. The evolving direction `s/max(q,1e-12 p_ref)` is poorly behaved for this trajectory toward zero deviatoric stress. Increasing iteration limits would not establish a correct apex treatment.

## Governing law and project derivation

Let `p=tr(sigma)/3`, `s=dev(sigma)`, `q=sqrt(3 s:s/2)`. Both stress and strain are compression positive and use six Mandel components. Constant isotropic elasticity, perfect plasticity and a nonassociated potential give

\[
f=q-Mp-c\leq0,\quad g=q-M_d p,\quad
\gamma\geq0,\quad \gamma f=0.
\]

The [OpenSees documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/DruckerPrager.html) and [pinned implementation](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/DruckerPrager.cpp), `plastic_integrator`, provide the smooth-cone comparison. Their hardening and separate tensile surface are excluded here. The [Itasca formulation](https://docs.itascacg.com/itasca930/common/models/drucker/doc/modeldrucker.html), equations 17–23 and “Apex Stress Correction,” separately describes radial deviatoric scaling and apex stresses; it also includes a tensile cutoff absent here. These are formulation references, not an executed external-code benchmark.

For constant `K,G`, form the elastic trial:

\[
p_t=p_n+K\operatorname{tr}(\Delta\varepsilon),\quad
s_t=s_n+2G\operatorname{dev}(\Delta\varepsilon),\quad
q_t=\sqrt{3s_t:s_t/2}.
\]

On the smooth cone, backward Euler gives `s_t=(1+3G gamma/q)s`. Thus `s` is coaxial with `s_t` and `q=q_t-3G gamma`. At the apex the norm has a subgradient: choose the deviatoric plastic strain needed to remove `s_t`, permitted when `gamma>=q_t/(3G)`. Both cases are represented by

\[
s=\max(1-3G\gamma/q_t,0)s_t,\qquad
p=p_t+KM_d\gamma.
\]

For `q_t=0`, define the target deviator as zero. The JSON uses `select(trial_q > 0*p_ref, trial_q, p_ref)` only as a safe denominator multiplying `s_t`; it introduces no stress floor. In the smooth branch the normalized stress residual is algebraically equivalent to the original implicit flow relation. At the apex this expression supplies the norm's subgradient rather than extending a regularized direction.

The actual declarative residual is

\[
R_\sigma=\sigma-\sigma_n-K\operatorname{tr}(\Delta\varepsilon)I
-2G\operatorname{dev}(\Delta\varepsilon)
+\min(3G\gamma/q_t^{safe},1)s_t-KM_d\gamma I.
\]

The existing Fischer–Burmeister residual still enforces complementarity; the common solver still determines `sigma,e,gamma` together. This trial-direction elimination is a project derivation specific to this constant-elasticity, perfect-plastic law. Do not reuse it for hardening, anisotropic elasticity or other flow rules without deriving the corresponding equations.

## Verification and limits

The independent reference in `tools/verify_plasticity.py` computes scalar invariant returns and reconstructs stress. It does not evaluate the model DSL. All **73 native cases pass** under the original absolute/relative tolerances: the original 19 cases plus 36 apex cases across three dilatancy slopes, two cohesion intercepts and six deviatoric directions, and 18 cases below/on/above the smooth/apex junction. Directions include all shear planes, both axisymmetric signs and a mixed tensor. The matching native/Wasm regression includes the originally failing increment.

The 73-case run is now a native CI regression gate. Its hashed v2 evidence is separate from the immutable failed v1 report. Mathematical independence of the scalar calculation is not independent authorship; a human source/numerical review remains required. The correction does not establish global convergence, arbitrary parameter admissibility, finite-strain objectivity or experimental validation. Parameter bounds still allow `Md>M`; this physical-admissibility question remains open. Hydrostatic tensile loading beyond the apex with `Md=0` still has no admissible volumetric correction and must fail transactionally.
