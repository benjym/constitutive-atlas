# EMC2013 exact generalized-flow realization proposal

Status: project formulation proposal for independent review, not an admitted model or reproduction of the unavailable original UMAT. Identity: **EMC2013-exact-generalized-work-BE-v1**. Parent source is [Doherty & Muir Wood (2013)](https://doi.org/10.1680/geot.12.P.008); [accepted six-question assessment](../complete-law-v1/independent-review/decision.json) binds the original private PDF and source inconsistencies. This document deliberately selects a whole law, with exact unrounded yield, generalized through-point potential flow, work-conjugate hardening and backward Euler. None of those choices can be inferred from approval of the assessment alone.

## Source, corrections and project choices

Source Eqs7/11/12/55 supply the exact yield, through-point potential, hardening curve and regular work-scalar rate. The source rounded-normal numerical recipe is not used. EMC01/02 are bypassed by equivalent spectral expressions with independent checks; no inverse Lode derivative or dimensionful determinant argument is evaluated. EMC03 uses phi_cv throughout the potential. EMC04 selects the source work-conjugate scalar, expressly declining to identify it with Eq9's Euclidean plastic-strain norm. EMC05 uses named tensor components and a work-preserving Mandel conversion. EMC06 uses the derivative/subdifferential of the same exact criterion whose values define admissibility. Generalized flow at repeated nonhydrostatic principal stresses and backward Euler are explicit project extensions of the source regular differential law. No title, DOI or source publication is relabelled as having supplied these extensions.

## Constitutive definition in source signs

Use tension-positive stress S and infinitesimal strain E, including all shears. The eventual Atlas adapter sets S=-sigma and E=-epsilon in compression-positive Mandel order xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz. All formulas here use source signs until that final transport. Constant isotropic elasticity C:A=2G dev(A)+Kb tr(A)I, Kb=2G(1+mu)/(3(1-2mu)). Material inputs: G>0 Pa; -1<mu<1/2; beta>0; attraction a>=0 Pa; 0<phi_peak<pi/2; 0<phi_cv<pi/2. These are disclosed project domains, not source universal ranges. In particular phi_cv may exceed phi_peak: the source's20/30/40degree examples at peak30 remain representable. Neither a frictionless nor zero-phi_cv limiting extension is asserted.

Let p=tr(S)/3, s=dev(S), J=sqrt(s:s/2). For any angle f define

    q_f(S) = (lambda_max(S)-lambda_min(S))/2
             + sin(f)*((lambda_max(S)+lambda_min(S))/2-p).
    F(S,phi) = (p-a)*sin(phi)+q_phi(S).

Equivalently F=max over the six ordered pairs i!=j of

    F_ij = (S_i-S_j)/2 + sin(phi)*((S_i+S_j)/2-a).

The eigenvalues in these expressions refer to a common principal basis. This max is exact Mohr-Coulomb, not rounded or Drucker-Prager. Positive phi makes every admissible state satisfy p<=a; equality implies J=0. No added tensile cap is present.

At p<a,J>0 the source through-point gradient, with the selected p_r held fixed during differentiation, is

    m in partial q_cv(S) + c I,
    c = (-q_cv(S)/(p-a)-sin(phi_cv))/3.

The subdifferential is with respect to the full symmetric stress tensor; q_cv already has zero hydrostatic derivative. For an extreme pair i,j,

    b_ij,k = (delta_ki-delta_kj)/2
             + sin(phi_cv)*((delta_ki+delta_kj)/2-1/3),
    m_ij = b_ij+c*I.

Only pairs attaining the extreme-principal maximum are allowed. At a smooth face there is one; at an upper or lower repeated-principal edge, convex combinations of the two limiting b_ij are admitted. This is the full convex spectral subgradient, not an arbitrarily chosen eigenvector. Equivalently, upper/lower eigenspace density matrices are positive semidefinite of unit trace, supported in their respective extreme eigenspaces. Since q_cv is convex and homogeneous for this angle domain, s:m=q_cv for every such selection. Thus the one work accumulator obeys dκ=Lambda*q_cv/J>=0, including edges. No second independently advanced norm accumulator is introduced.

## Hardening, preparation and restart

Persistent minimal state is six stress components plus κ>=0. An immutable preparation input phi_0 obeys 0<phi_0<=phi_peak. It is the initial maximum previously mobilized friction, not a new fitted seventh material constant. κ is measured from that specified preparation origin. Define

    phi(κ) = phi_peak - (phi_peak-phi_0)
             /(1+κ*(phi_peak-phi_0)/(beta*phi_peak)).

This is Eq12/13 with its origin made explicit; dphi/dκ=(phi_peak-phi)^2/(beta*phi_peak). It also handles phi_0=phi_peak as a separately declared constant-friction endpoint without dividing by phi_peak-phi_0. At phi_cv=phi_peak this endpoint has zero volumetric flow on yield, as the source specialization requires. For phi_0<phi_peak, exact finite κ never reaches peak; floating-point rounding to equality must be reported as representability failure rather than silently clipping the angle or converting to perfect plasticity.

A fresh preparation supplies S and κ=0, phi_0 and all material constants. A restart supplies S, κ and exactly the same phi_0/parameter identity. Restarting with current phi as a fresh phi_0 and κ=0 is not permitted to erase the recorded preparation origin. Validate finite values, κ>=0, all material domains and F<=0 within an explicitly frozen numerical initialization policy. Never project an overstressed input. A hydrostatic compressive state has J=0 but F<0 and is admissible without computing q/J. Source examples remain examples, not defaults. Optional plastic strain may be recovered per successful substep from C^{-1}:(S_trial-S_return); if stored it is persistent, needs an explicit origin and participates in rollback/restart. It is not needed for the seven-state stress recurrence. No void-ratio, fabric, creep clock or density law is invented.

## Complete coupled backward-Euler step

From immutable (S_n,κ_n), compute S_trial=S_n+C:dE. If F(S_trial,phi(κ_n))<=0, accept the elastic result and unchanged κ. This branch includes exact zero strain and unloading; no potential or q/J evaluation is required even for a hydrostatic state. Otherwise solve the following **coupled** relation. Let S_i be returned principal stresses in decreasing order in a trial principal basis; Γ_ij>=0 are six transient multipliers, Γ=sum Γ_ij, and κ is returned history:

    S_i - S_trial,i + 2G*sum_ij Γ_ij*b_ij,i
        + Kb*Γ*(-q_cv/(p-a)-sin(phi_cv)) = 0  (three equations)
    κ - κ_n - Γ*q_cv/J = 0
    F_ij<=0, Γ_ij>=0, Γ_ij*F_ij=0              (six pairs)

In the first line b_ij,i means the i-th component of the vector b for a pair; a transcription should rename the pair indices r,t to avoid that visual index collision. Equivalently the tensor equation is S-S_trial+C:sum Γ_rt*m_rt=0. The hardening angle in **every** F_rt is phi(κ), not the parent angle. q_cv and c are evaluated at the same returned state. Multipliers are dimensionless increments, not stored history and not the physical clock. Yield residuals have Pa units. No product-complementarity residual alone is sufficient: both inequalities must actually be checked. A future Fischer-Burmeister/min residual must normalize yield by a declared Pa scale before combining it with Γ; prospective tolerances and AD/generalized-derivative rules need separate freezing.

This is a full finite-step project discretization, not the printed source Euler controller and not a claim of exact continuous-path integration. For a regular active face its infinitesimal consistency limit is the accepted assessment's n:C:m+H law with n=grad F and H=-F_phi*h*q_cv/J. This derivative must include phi(κ). Nonassociation can lead to loss of regular consistency or multiple incremental roots for some parameters; positive elastic moduli alone do not prove universal uniqueness. Qualify loading continuation and report singular/ambiguous solutions rather than silently accepting a different branch or retuning material parameters.

## Edges, trial multiplicity, apex and activation

All six inequalities are retained: face and both edges are one coupled complementarity problem. At a returned edge, the two active multipliers determine the flow mixture and the tensor plastic increment. Do not transfer the approved constant-dilation perfect-plastic MC return map: its potential and hardening differ. A candidate solution must satisfy returned ordering, all six inequalities, multiplier signs, complementarity, stress residual and history residual.

Coaxiality follows because every generalized flow commutes with returned S and isotropic C preserves that property; therefore S_trial commutes with S. Ordered trial and returned principal stresses share an ordering: for any strict returned pair, its b difference has the same order, so adding 2G times nonnegative multipliers cannot reverse that pair in the trial. In particular, repeated trial principal stresses must remain repeated in a valid return. Reconstruct a repeated upper returned/trial block as S_upper*(I-P_min)+S_min*P_min; the analogous lower block uses P_max. Never choose an individual projector inside a repeated trial block, reject an ordinary edge merely because a basis is nonunique, or use a numerical gap merge as physical rounding. Hydrostatic trials that are admissible remain elastic. A hydrostatic inadmissible trial cannot have a coaxial nonhydrostatic return with the above ordering property.

At p=a,J=0 the source potential and work ratio are undefined. This project does **not** invent an apex flow. An exact admissible apex parent may be held unchanged or leave elastically into F<0; an increment requiring an active apex or p>=a plastic endpoint fails with `unsupported_apex_flow`, with full rollback. That is an explicit unclosed source-domain boundary, not an apex return claimed to work. Interior repeated-principal edges at p<a,J>0 remain in scope. A future tensile/apex continuation is a separate physical formulation requiring source/derivation/review; this proposal cannot be advertised as a full-apex EMC implementation. Steps from an apex into the interior which need plastic loading are assessed by the same interior implicit equations without evaluating the potential at the old apex. A failed or nonunique return is not repaired by clipping p, J, phi or Γ.

For one constitutive substep enumerate/furnish all potentially valid active face/edge solutions, keeping every inequality. If distinct physical returned (S,κ) states survive the frozen verification tolerance and no independently justified continuation selects one, return `ambiguous_return`; equivalent multiplier representations of the same physical state do not make a new state. No general existence/uniqueness theorem is asserted. Event crossing from an elastic parent is handled by the coupled backward-Euler inequality problem; finite unsplit backward Euler is not an exact yield-entry integrator. Reversals inside yield are elastic with memory retained, and no kinematic reset is added.

## Temporal/controller and transaction requirements

Prospective v0.3 profile: strain_path/incremental_residual, small_strain_3d, fixed_spatial, objective_rate none, Mandel, compression_positive stress and strain, effective Cauchy stress bound to persistent sigma, explicit de and empty advance inputs. κ is persistent scalar_invariant; sigma is persistent symmetric_spatial_tensor. Stress is first in the layout, temporary solve variables use increment_unknown/plastic_multiplier roles, and initialization.required_state contains only sigma,κ. Immutable phi_0 belongs to resolved preparation/material provenance, without pretending it is a seventh material constant calibrated by this source. A purely rate-profile transcription would fail to express these complementarity steps. There is no seconds-based evolution: holding de=0 cannot change history.

To approximate the rate law over a caller path, an optional project step-doubling controller compares one backward-Euler step to two equal half steps from the same original internal parent. Accept the two-half-step persistent state only. Define e=max(||S_two-S_full||F/(atol_S+rtol_S*max(||S_two||F,||S_full||F)), |κ_two-κ_full|/(atol_κ+rtol_κ*max(|κ_two|,|κ_full|))). Require positive finite atols, nonnegative finite rtols; no componentwise orientation-dependent norm. Success requires e<=1 and every local residual/branch check. Suggested prospective first-order controller is h_new=h*min(2,max(0.2,0.9/sqrt(e))) with e=0 growth2, exact endpoint clipping and all numerical scales/budgets explicitly supplied. This algorithm is proposed, not frozen qualification policy. Failures cause bounded bisection; exhausted work/depth/representability or active apex gives caller failure. Never increase budgets after observing failure to obtain a pass.

Freeze the exact local nonlinear method, residual/inequality tolerances, scales, ambiguity discrimination, finite-difference/generalized derivative policy, controller constants and work/depth budgets **before compiled execution**. This packet does not fill missing runtime behavior with defaults. Every full/half/active-set trial uses scratch copies of the same immutable parent. Commit all persistent fields only after the whole caller increment succeeds. A late failure restores original stress, κ, optional histories, preparation and incoming temporary slots; earlier successful internal substeps cannot leak. An outer mixed-control trial must also start from its own immutable parent. Track trial statistics separately from physical history. Failures remain observable, not converted into zero strain or elastic response.

## Existing common-code capability assessment and next integration gate

The current DSL already supplies trigonometric functions, scalar min/max, principal extrema and isolated projectors; no inverse-trig extension is needed for exact q. Existing v0.3 residual and transient roles can describe dimensions and lifecycle, but they do not supply a reviewed coupled principal complementarity algorithm, grouped reconstruction derivative for this implicit law, preparation-origin handling or the proposed error controller merely by declaration. A possible reduced solve has three principal stress unknowns, κ and six Γ values, followed by grouped tensor reconstruction; it is a common generic spectral/multisurface capability candidate, not permission for a handwritten EMC C++ kernel. No model/schema/runtime change is made here, and the proposal is not executable JSON.

Next integration work must demonstrate the complete declarative representation and a generic solver path (or specify the exact missing generic operation), including repeated trial groups and inequalities, before choosing library/API changes. Existing MC spectral primitives should be reused under their actual contracts; a source-only model record must not masquerade as a new runnable definition. Separate independent review of this full proposal precedes transcription; prospective face/edge/corner-crossing, hydrostatic, apex-rejection, phi_cv above/below peak, perfect-plastic endpoint, covariance/units, refinement, full rollback and recovery evidence must precede native/Wasm admission. Off-diagonal Cartesian references and mixed-control derivatives are required; principal certificates alone are insufficient.
