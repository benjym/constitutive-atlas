# Selected full-formulation contract, v1

Selected identity: **clay2014-trace-calibrated-igs-fixed-plane-v1**. This is a project-reconciled realization of Mašín's 26 November 2013 author manuscript for the 2014 paper, not a claim of literal printed equations, final-publication equivalence or vendor reproduction. The independent [source decision](source-decision-review.json) supports preparing this contract; E2/E3/E5 qualification remains separate.

## Source reconciliation and retained behavior

Retain the anisotropic Eqs2–8 stiffness, Eqs34–50 base law with the proposed Eq49 exponent in both density factors, and complete Eqs51–57 IGS. Change only (a) `Am` in Eq15 to `T=trace(L:I)`, and (b) the printed denominator2 in Eqs19/56 to9, solving Eqs16–18 for the requested shear stiffness. These are disclosed project choices supported by the manuscript's calibration relations, not uniquely established author intent. Keep the historical printed-Am seven-state model unchanged.

The trace choice gives the base-law instantaneous mean unloading slope at hydrostatic stress on the normal-compression density, under imposed isotropic expanding strain. It does not imply a hydrostatic stress-controlled path, continued hydrostatic stress, arbitrary-density slope, or full-IGS zero-memory kappa slope. Anisotropic stiffness generally generates deviatoric stress under isotropic strain. At zero IGS the tangent is instead `mR*fs*L`. Saturated positively aligned IGS recovers the base law.

## Explicit v0.3 meaning

```
schema_version: 0.3
time_dependence: strain_path
equation_form: strain_path_rate
kinematics: small_strain_3d
frame: fixed_spatial
objective_rate: none
tensor_representation: mandel
stress_sign: compression_positive
strain_sign: compression_positive
inputs.equation.de:
  quantity: strain_increment
  measure: infinitesimal_strain
  shape: sym
  unit: 1
  configuration: current
  sampling: increment
  constraint: finite
inputs.advance: {}
stress: {source: state, name: sigma, measure: cauchy, scope: effective}
```

Persistent layout is `sigma` (symmetric effective Cauchy stress, six Mandel components, Pa), `e` (scalar void ratio, dimensionless), `H` (symmetric compression-positive IGS, six Mandel components, dimensionless). Stress and H transform as symmetric spatial tensors under a passive orthonormal basis change; e is scalar invariant. Mandel ordering is xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Norms and contractions are Frobenius. A caller supplies all three named states; example values never substitute for omitted history. Initialization is explicit_state/examples_only/domain_and_initial_checks, required_state `[sigma,e,H]`.

The fixed unit material normal `(n1,n2,n3)` is explicitly supplied; `P=n outer n` is used unchanged. No hidden normalization, material-axis transport, finite-spin or fabric evolution is supplied. Basis covariance requires transforming the material normal, stress, memory and strain together; it does not establish finite-rotation behavior.

## Equations and signs

Use `r=alpha_E`, `v=alpha_nu`, `g=alpha_G`, `nu=nu_pp`, `B=1-nu-2*r*nu^2/v^2`. Coefficients a1–a5 and the Cartesian action L are exactly those already transcribed in the retained base model. Set `T=3*a1+9*a2+6*a3+2*a4+a5`. With `p=trace(sigma)/3`,

```
fs = 9*p/(2*T)*(1/lambda_star+1/kappa_star)
Gtarget = p_ref*Ag*(p/p_ref)^ng
mR = Gtarget*4*T*g/(9*p*r)
     *lambda_star*kappa_star/(lambda_star+kappa_star)/B
mT = mrat*mR
```

Here `p_ref=1000Pa`, not1000kPa. Eqs36–50 supply pe,fd,fdA,d and the proposed Eq49 exponent; use the previously checked source invariant sign mapping and exact spherical limit, without modifying the old model. Scalar density intercept N is distinct from source nonlinear tensor N. Define

```
Q = fs*(L:d) - sigma*trace(d)/lambda_star
h = H/norm(H) if norm(H)>0, else zero
rho = norm(H)/R
q = dot(h,de)
w = rho^chi
c = w*mT+(1-w)*mR

q>0:
  sigma' = c*fs*(L:de) + w*(1-mT)*fs*(L:h)*q
           + w*(fd/fdA)*Q*q
  H' = de - h*rho^beta_r*q
q<=0:
  sigma' = c*fs*(L:de) + w*(mR-mT)*fs*(L:h)*q
  H' = de
e' = -(1+e)*trace(de)
```

Prime denotes derivative with respect to dimensionless path fraction for the supplied straight strain increment. These signs use `sigma=-sigma_source`, `de=-D_source`, `H=-delta_source`; q is invariant under the mapping. d retains its normalized source-stress definition and is not negated again. The positive correction tensor is Q outer h; reversing that order changes the law.

Evaluate fs, density factors, mR/mT and all tensor actions from the same current stage state. They are not lagged at the committed parent. No physical time, rate effects, aging or relaxation is inferred. Zero strain produces zero stress/e/H rates in the supported domain. A hold does not erase memory. Reset is an explicit caller-supplied new complete state, not an internal event.

## Domains and preparation

Require finite explicit parameters, positive p_ref=1000Pa, numerical pressure scale, Ag and R, lambda_star>kappa_star>0, friction angle strictly between0 andpi/2, positive Eq49 logarithm argument and positive resulting exponent; positive g,r,v, T,B and stiffness. Keep the existing conservative Poisson interval and normalized stress interior checks. Positive definiteness of stiffness follows for an exact unit normal from r>0,g>0,B>0,nu>-1; numerical checks must also cover the accepted unit-normal tolerance. Conservative numerical support is not a published calibration interval.

Require e>=0; positive-definite compression stress; the existing real nonsingular ASBS interior, finite positive pe/fs/fd/fdA/mR/mT; `0<mrat<=1`, beta_r>0 and chi>0. Source example chi0.9 must remain supported; do not import the original IGS97 chi>1 restriction. The definition must declare finite parameter intervals and retain the existing fixed roundoff policies, with no silent epsilon changes. Near-hydrostatic Lode evaluation uses the separately reviewed exact spherical branch and existing bounded roundoff policy, not arbitrary flattening of a neighborhood.

Require `norm(H)<=R`. At H0, define h0 andrho0 exactly; positive chi/beta make the rate continuous, but a classical state Jacobian need not exist. At q0, both stress corrections vanish and memory rate is de; do not assert matching branch derivatives. At rho1, positive radial growth vanishes in the continuous equation. Do not cap rho, project H, replace a zero denominator by epsilon, or reset memory at reversal. A discrete stage outside the declared domain must cut back or fail transactionally. Boundary integration remains an explicit qualification risk, not permission to relax the domain after failure.

Use table-parameters.json as provenance for the source example coefficients. For a software example, select project-labelled r2,v2 and normal `(0,0,1)`, p100000Pa, e=`exp(N-lambda_star*ln(p/p_ref))-1`, H0. This is an explicit synthetic hydrostatic normal-compression density with zero-memory assumption. It is not a London Clay preparation or experimental calibration; the reconciled law has not been refitted to data. Supplying H0 does not reconstruct a consolidated specimen's recent history. A later useful browser preset must explain these assumptions.

## Integration and acceptance prerequisites

Advance all thirteen scalars together using the existing generic strain-path-rate adaptive integrator. Complete caller updates commit atomically. Rejected internal stages and substeps remain trial-local; any terminal domain/nonfinite/budget failure returns every original stress/e/H component. Repeated trials, recovery after late failure and restart must preserve the complete parent. No tangent or FE-host coupling is claimed by the initial laboratory delivery.

Before observing any interpreted candidate or compiled output, freeze the exact candidate, independent Cartesian rate reference, corpus and numerical acceptance policy. Required coverage is the seven groups in source-decision-review.json: anisotropic stiffness/covariance; on/off normal-compression calibration; zero-memory targetG across pressure and ng; both IGS branches/origin/q0/rho1; independent converged full-state finite paths with reversals/holds/strain controls; complete rollback/recovery/restart; native/Wasm parity. Compare stress Frobenius norms plus e and H separately, not only final plots or shared-backend agreement. Preserve original FAIL4/144 and any new failures. Source/scope review acceptance is not numerical qualification or admission.
