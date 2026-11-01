# Independent checklist-v1 approval: original NorSand active axial law

Reviewer `/root/norsand_original_review`, 2026-11-01; task
`REVIEW-norsand-final-checklist-v1`. **Accepted within the exact scope below.**
All nine checklist items pass; no blocking finding remains in that scope.
This reviewer is separate from author `/root`, inspected all 13 original pages
and authored independent source algebra before this executable review. The
reviewer did not write the material candidate, generic runtime, production
reference builder or backend results. No compiled calls or builds were performed
by this reviewer. This is a new E5 decision; earlier source/static reviews remain
limited to their original scopes.

Exact model: `models/research/norsand/norsand-jefferies-1993-active-axial.json`,
SHA-256 `67ff78f8cd56fd8812ba42f4456105b6e7ae217090dbcf40d8f8d5f839995d2c`.

Approval covers the original active, monotonic, drained rigid-plastic axial
formulation, explicit current-volume/incompressible-grain reconstruction and
adaptive midpoint numerical policy, through the generic Python controlled-path
API, flat native C ABI and Node-hosted Wasm harness. Callers must retain the
complete initialization, coordinate, parameters and control context. Numerical
accuracy is qualified for the nine frozen Latin-square reference cases and
associated restart/rejection/zero-progress requests, not every value admitted by
the declared parameter box. The cases use M=1.2,h=280,lambda=.0135,Gamma=.82,
pref=1000Pa, N=0,.2,.39, initial psi=-.16,0,+.075 and progress .16,
with constant cell, constant mean and the specified linear changing controls.
Use the frozen settings absolute1e-10,relative1e-8,min_step1e-12,
max_step.001,max_depth40,max_trials100000. Changing-control examples establish
numerical control handling, not new experimental validation.

## source_provenance

The private original is Jefferies (1993), *Nor-Sand: a simple critical state
model for sand*, Geotechnique43(1),91–103, DOI10.1680/geot.1993.43.1.91;
SHA-256 fee99108e493f34eb987c759eddf73cfc86e77102c73e42d099c00f1209851b9.
The reviewer previously visually inspected every page in this same separate run;
the current retained-source hash is independently rechecked. The supplied receipt
and accepted source report identify equation/page locators and distinguish later
elastic/cyclic/3D NorSand variants. No later law or supplied binary is used.

## equation_fidelity

Every candidate derived quantity, evolution equation and observable was compared
against original Eqs5–12 and p102 notation. Eq10 reconstructs pi/p with the
negative (N-1)/N exponent and exact N=0 exponential branch. Eq11 uses current
image psi_i, retains the corresponding negative exponent and zero-N branch.
Eq6 supplies D. Differentiating original yield gives
eta'=M*Y*(pi'/pi-p'/p); differentiating C=p-Kq and substituting original Eq12
gives precisely the candidate eta_rate, including the negative Ks term and
B+K*M*Y denominator. No later elasticity, clipping, regularization, fabric or
model-specific runtime dispatch is present. Source log/ln notation is reconciled
using Eq9 and p102. Current-volume e'=-(1+e)D and midpoint integration are
explicit Atlas choices, not falsely attributed printed equations.

## conventions_dimensions

Compression-positive effective triaxial stress and source work-conjugate
p,q,eps_v,eps_q are preserved. Stress uses the fixed axial Mandel embedding
[p+2q/3,p-q/3,p-q/3,0,0,0] in Pa. The implementation declares axisymmetric_x,
fixed_spatial and no objective rate; it does not claim general 3D or finite-spin
transport. The independent coordinate is dimensionless shear progress, not
seconds. Cs and Ks are control derivatives per that coordinate. Gamma is paired
with pref; the source report and algebra checks verify pressure-reference
conversion. Accumulated principal strains are sums of source increments, not
exact finite stretch or nominal specimen strains.

## initialization_domain

All six declared parameter entries are explicit; pref is a fixed pressure
reference, not a new fitted sand property. eta,e,ev,eq plus parameters,
coordinate and both named controls form complete active initial context. pi is
reconstructed from active yield and controls rather than an independently
projected history value. Explicit domains enforce positive pressure/e and power
bases, N=0 or 0<N<=.39, nonnegative eta, B>0 and positive consistency denominator.
Parameter boxes are numerical admission bounds, not source-wide validity or
verified accuracy ranges. Interior/overconsolidated loading response and physical
specimen preparation are not inferred. No unqualified illustrative defaults are
counted as a tested specimen; the named loose example matches a qualified case.

## integration_transactions

The current Python runtime and generic C++ runtime were read. Both form local
stage/substep state and publish final context/output only after whole success.
The adaptive midpoint algorithm compares one full versus two half steps using
Richardson factor3, accepts the two-half result and validates stages and accepted
states. Closed linear controls, derivative channels, start-control matching,
coordinate offset, exact zero-progress identity and full-parent rollback agree
with the contract. Negative progress, invalid controls/domains/settings and
representational/budget failures reject. Source p98 forward differences do not
prescribe this finite algorithm; it remains identified as Atlas numerics.
Retained interpreter and actual-backend chained/cold restart, rejection/recovery,
input preservation and failed-output sentinel checks support the claimed scope.
No physical-time relaxation, cyclic reversal or analytic tangent is promised.

## independent_numerical_evidence

Independent source algebra checks yield inversion, limiting flow, triaxial work
and finite-difference normality. Parent source algebra provides850 checks. The
reference builder was read: Decimal RK4 evolves pi/e/strain directly and solves
original Eq7 plus mixed control at every stage; it does not use production
eta_rate. Its nine cases meet unchanged4096/8192 refinement and50/75-digit
adequacy bounds (max1.93137e-11 versus2e-8; max1.84653e-48 versus1e-35).
The reviewer independently recomputed original-yield/control/volume endpoint
identities and every retained interpreter/reference error: max2.726941911e-7
versus2e-6. The reference volume invariant max1.03821e-15 passes1e-10.
The numerical evidence covers sampled endpoints, not experimental data or the
whole parameter box. Local derivative evidence is appropriate to the fixed-axis
scope; finite-rotation covariance and analytic tangents are excluded.

## backend_delivery

The separate durable-target review by `/root/norsand_path_review` was read and
accepted only after its final result report. This E5 reviewer independently
verified all18 artifact/result hashes in target-qualification-v2 and ran the
unchanged strict retained-result checker:58native+58Wasm requests pass,
40successes/18expected rejections each. Full result rows are exactly equal.
Material outputs equal the qualified interpreter; analytic fixture max error
3.274515703e-8 passes2e-7. Source accuracy is supplied by the independent pi/e
references, not backend parity. Exact generated target/artifact identities,
serial build order and retained packaging failures are preserved. The repaired
incoming Wasm option changes packaging, not equations or numerical gates.
Approval concerns conforming flat-C-ABI buffers and Node Wasm harness calls;
there is no separate user-facing CLI, main-atlas/browser/package/live claim.

## applicability_claims

This is the original source's active monotonic drained axial law, including dense,
critical and loose sampled starts, associated flow and current-image hardening.
Excluded: inactive/interior unloading, cyclic paths, elasticity, fabric evolution,
general Lode/3D/rotation/FE/MPM use, arbitrary histories/parameter accuracy,
experimental validation, main-atlas user flows and live deployment. Post-peak
calculated strains concern the intense shear zone as the source warns. Model
metadata is retained exactly, including its historical draft/staged wording;
the separate approval registry conveys this bounded decision. Editing that
metadata requires a newly bound review rather than reusing this hash.

## reproducibility_rights

The record hashes the exact model, source receipt/reviews, numerical policy,
reference construction/results, generic contract, durable target evidence and
this review's audit. Reproduce this review's retained-evidence check with
`python3 -B docs/ingestion/norsand-1993/approval-v1/check_review_evidence.py`.
It neither imports a material evaluator nor calls compiled code. Historical
identifier findings, original access failures and packaging failures retain
distinct identities; no observed-failure tolerance was relaxed. Source PDF/text/
images remain private and unredistributed. Numerical references are independently
constructed; figures are not digitized or called experimental replication.

E5 acceptance does not close E6–E8. Coordinator may integrate this exact decision
without a human scientific signature. Actual atlas inclusion, real packaged
browser qualification and authorized live delivery remain separate work.
