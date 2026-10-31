# Multilaminate full-formulation decision v1

Task DECIDE-multilaminate-full-formulation-v1; coordinating parent, 1 November 2026.
This closes the current consolidation pass, not full ingestion or scientific admission.
No new executable model, schema change, build or author-code execution accompanies it.

## Decision and scope

Keep the selected **2012 thesis spectral cross-anisotropic stiffness, logarithmic
degradation, four-contour recovery, Hvorslev strength and regular post-peak spatial
nonlocal formulation** as the ingestion target. Do not substitute Basic, local-only
or recovery-disabled variants to fit the current engine. The modified pre-peak
nonlocal option and microstructure-tensor stiffness are separate source alternatives.

The primary source is Bert Schädlich, *A Multilaminate Constitutive Model for Stiff
Soils* (TU Graz, 2012), [DOI](https://doi.org/10.3217/wmxdh-rg587), PDF SHA-256
`43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`.
Journal identities are established; equation equivalence to those papers is not.
Raw sources remain private; redistribution rights have not been established.

Use pressure approach 1 (Eq108, mean effective pressure) as a **provisional scope
proposal** for this fine-grained target. This is a new proposal, not a claim that
older packets selected it or that approaches 2/3 are equivalent. Strength-anisotropy
and research parameters still require explicit branch selection and provenance.
The proposal is not sufficient to authorize an executable definition.

[decision-register.json](decision-register.json) holds the ordered issues, source
locators and evidence needed to close them. Reviewer assignment is unfilled.
A mathematically supported repair remains a proposed correction until reviewed;
it must never silently replace a conflicting printed equation.

## Stop reading repeatedly; resolve these gates

1. **Constitutive definition:** settle the cap hardening denominator (Eq36 versus
   Appendix D), Hvorslev C.5 sign, spectral angle/projection corrections and
   Poisson interpolation convention. The hardening alternatives give materially
   different values. Existing witnesses preserve both readings.
2. **Preparation and branch identity:** specify the missing cap/prestress and
   direction preparation, conditioning of every plane transformation, pressure
   branch and strength-anisotropy scope. List each adopted correction explicitly.
3. **Temporal and host contract:** reconcile four-contour creation/reset events,
   global step versus internal substep, damage definition, first-contact sentinel,
   frozen neighbour values and simultaneous commit/restart semantics.
4. **Generic capability design:** only after the preceding definition is coherent,
   propose a separately scoped engine/schema extension with the requirements below.
   Source clarification can proceed independently of design sketches, but implementation
   must not freeze an unresolved equation or lifecycle by accident.

Closure can use a readable primary clarification, or an independently reviewed,
explicitly named corrected Atlas variant with a patch ledger. The latter must not
claim exact transcription or journal equivalence. No author enquiries have been sent.
Do not retry journal downloads without a new access lead or repeat the completed
micro-audits. Work on other roadmap models may proceed while this model is pending.

## Generic capability requirements

The advertised 1,056 history slots are a vendor storage layout, not proof of 1,056
independent physical state variables or Newton unknowns. First classify each item as
prepared constant, committed per-plane history, temporary scratch, local multiplier,
global solve unknown or neighbour/mesh input. Preserve all required physical memory;
do not copy unused vendor slots blindly or discard recovery to meet a capacity limit.

The present engine caps scalarized state at 32; AD reserves six additional mixed-control
columns. v0.3 distinguishes persistent and temporary roles, but each still occupies
one equation/state layout. The experimental immutable history facility also caps
retained scalar components at 32. It already supplies trial/rollback semantics;
composition across coupled planes and spatial points is a further requirement.
Existing symmetric tensor spectral functions do not establish the complete general
6x6 compliance/projection and plane-coupled update needed here. Scalar unrolling is
one possible representation; this record does not mandate a new array DSL.

| Requirement | Acceptance evidence required before implementation admission |
| --- | --- |
| Separate storage from solve layout | Explicit field inventory, bounded allocation, per-plane indexing and restart mapping; no assumption that all retained values enter Newton/AD. |
| Compliance and plane projection | Independent tensor/Mandel work identity, all-plane quadrature moments and conditioning, isotropic limit, reconstructed global compliance, repeated-eigenvalue cases. |
| Preparation and coupled plasticity | Independent prestress/cap fixture, active cone/cap/tension/Hvorslev and corner cases, source-supported saturation and domain failures. |
| Recovery transactions | Zero increment, hold and reversal fixtures, fifth-contour policy, parent-step versus substep events, rejected outer-iteration rollback and no partial durable writes. |
| Spatial nonlocal host | Frozen accepted neighbour snapshot at the declared parent-step boundary, volume/kernel normalization, explicit zero-weight failure, point-order invariance and atomic commit/restart. Internal cutbacks must not refresh neighbours. |
| Derivatives and backends | Independent local residual/tangent reference with the declared frozen histories; only then serial native and Wasm agreement. Backend parity alone is not a scientific reference. |

These are planned acceptance gates, not passing results. Host policies above describe
proposed Atlas requirements; omitted source helper implementations remain unresolved.
The source nonlocal option needs multiple material points and mesh/neighbour inputs;
a single material-point plot cannot demonstrate its spatial regularization.

## Evidence and handoff

The six immutable packets are [thesis/quadrature](../thesis-2012-v1/README.md),
[base laws](../base-laws-v1/README.md), [host contract](../host-contract-v1/README.md),
[publication/variant identity](../variant-identity-v1/README.md),
[spectral stiffness](../spectral-v1/README.md) and [Hvorslev/nonlocal laws](../hvorslev-v1/README.md).
Their analytical witnesses identify source conflicts; they do not establish complete
formulation, executable verification, experimental validation or independent signoff.

[manifest.json](manifest.json) pins these inputs and current capability observations.
Verification for this documentation slice checks JSON structure, issue identifiers,
local links and file hashes. No new numerical campaign is justified by consolidation.
The next bounded deliverable is a resolution/patch ledger for gates 1–3 with review
status, followed by a separate capability design task. The full ingestion row stays open.
