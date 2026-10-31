# Multilaminate proposed correction ledger v1

Task DECIDE-multilaminate-correction-ledger-v1, 1 November 2026.

This records eight proposed repairs or explicit choices against the existing
LAW-01–04 findings. **All are unapproved; scientific review is unsigned and
unassigned.** The bounded ledger task is complete; full model ingestion remains open.
The working identity is **Atlas Schädlich-2012 corrected candidate v1 (incomplete
proposal)**. It is neither a canonical model record nor a complete v0.3 crosswalk.

The selected full target remains spectral cross-anisotropic stiffness, logarithmic
degradation, four-contour recovery, Hvorslev strength and regular post-peak spatial
nonlocal behavior. This proposal claims neither exact thesis transcription nor
journal equation equivalence. Primary source: Bert Schädlich, *A Multilaminate
Constitutive Model for Stiff Soils*, TU Graz, 2012,
[DOI and institutional source](https://doi.org/10.3217/wmxdh-rg587).
The private PDF SHA-256 is
`43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9`.
Sources and page renders remain private; redistribution rights are unestablished.

## Proposed patch set

[ledger.json](ledger.json) records the printed alternatives, locators, proposed
expressions, assumptions, domains and reviewer questions for every row below.
“Derived” means conditional on the stated source definitions, not approval or proof
of historical author intent.

| Patch / gate | Proposed disposition | What remains undecided |
| --- | --- | --- |
| 01 / LAW-01 | Use the Appendix D **minus** hardening denominator. C.3 total local primary compliance minus N–T elastic compliance fixes plastic compliance under additive strain. The plus expression instead adds twice the elastic compliance to the intended total. | Scientific confirmation of C.3's total-strain/factor-three reading and reference-law use with degraded anisotropic stiffness. |
| 02 / LAW-01 | Negative signed cap root, or equivalently positive magnitude Q. This follows from the declared compressive-intercept convention, not from the squared yield surface alone. | Missing GetAcap, minimum/cohesion and prestress branches. |
| 03 / LAW-01 | Propose an explicit nonnegative POP magnitude interface, subtracting it from source tension-positive stress. | Historical encoding and OCR/POP precedence; no silent abs() conversion. |
| 04 / LAW-02 | Reconstruct ordered low/high projectors from Eq94, with low-angle atan2(-2b,d-a)/2 where defined. A tangent ratio alone does not preserve mode ordering. | Repeated-eigenspace nonlinear history continuation. |
| 05 / LAW-02 | Replace raw xz normal-traction coefficient by 2 n_x n_z. | Singular projection matrices and actual prepared directions. |
| 06 / LAW-03 | Declare raw/engineering to Kelvin conversion for all shear columns and repair the repeated normal label under xx,yy,zz order. | Complete local work metric and coupled assembly reconciliation. |
| 07 / LAW-03 | Propose the listing's nu_hv interpolation, deriving nu_vh by reciprocity. This is an explicit lineage choice, not a mathematically forced repair. | Review against Fig29's different nu_vh interpolation and pathwise positive definiteness. |
| 08 / LAW-04 | Positive Bcs=p_cs tan(phi_cs)/qe_cs; repair C.5's first signed ratio to -tau_cs/sigma_ne_cs. | At tan(phi_e)=tan(phi_cs), Bcs cancels; extension there must be declared. |

Positive finite cap hardening under patch 01 requires
Eur_ref > 3(1-2nu_ur) Eoed_ref in the stated scalar reference limit.
Equality gives zero plastic compliance and infinite hardening; it is not permission
to divide by zero or clamp the denominator. This does not establish the full
macroscopic oedometer response. Real-power bases must be positive; the printed
m=1 singularity remains a separate unresolved definition.

The [cap technical review](technical-reviews/cap-choice/README.md) supplies the
compliance derivation and three exact rational witnesses. The
[algebra technical review](technical-reviews/algebra-choice/README.md) preserves
ordered spectral projectors, Kelvin conversion, interpolation alternatives and the
nondegenerate cap/Hvorslev/critical-state intersection factorization. Both are AI
technical analyses, not independent scientific signoff. The cap worker made one
targeted visual recheck of C.3 (PDF197); no source acquisition or numerical campaign
was added. Prior immutable packets and their retained failures remain unchanged.

## Finite next gate

An independent scientific reviewer should accept, reject or amend this explicit
patch set and its assumptions, then settle the remaining preparation, branch and
temporal choices listed in the [full-formulation decision](../full-formulation-v1/README.md).
No reviewer is assigned by this packet. Approval of these eight entries alone would
still leave the full formulation incomplete: actual directions and conditioning,
GetAcap/prestress, repeated-mode histories, four-contour reset events, damage/peak
semantics and the lagged nonlocal transaction contract require closure.

After a coherent definition, scope generic retained-memory/solve-layout and coupled
plane/multipoint capability work separately. Do not raise the state limit or write a
model-specific kernel on the strength of this ledger. No additional source pass or
journal retry is warranted without a new lead. Other roadmap ingestion can proceed
while scientific/source decisions remain pending.

[manifest.json](manifest.json) pins the payload and immutable inputs. Integration
checks cover strict JSON, unique patch IDs, LAW coverage, unsigned status, local
links and SHA-256 bindings. No model/backend calls, author-code execution, native or
Wasm builds, model-count changes, deployment or admission accompany this slice.
