# Decision 0004: distinguish shared-host numerical admission from applicability

Date: 2026-11-01. Status: **adopted project reporting policy; scientific model review pending**.

Applies to the current VW96 and IGS97 host definitions pinned by the [boundary diagnostics](../reviews/vw96-igs-applicability-v1/checks.json). It does not change their equations, runtime guards, parameter defaults, solver, model status or schema version. The complete proposed v0.3 contracts remain in the [VW96](../ingestion/hypoplastic-sand-vw96/formulation-crosswalk.json) and [IGS](../ingestion/hypoplastic-sand-igs97/formulation-crosswalk.json) packets; existing-root migration belongs to its separate task.

The full [VW96 original-paper technical review](../ingestion/hypoplastic-sand-vw96/original-equation-review-v2/README.md) supports Eqs1–2/40–46 on the inspected common domain. AppendixC p270 characterizes its shape function at isotropy and for 0<u<sqrt(2), but it does not prescribe a universal runtime rejection rule. The [IGS review](../ingestion/hypoplastic-sand-igs97/README.md) separately identifies physical history saturation and Atlas's numerical overshoot band. Treating successful execution as proof of applicability would erase these distinctions. Inventing an original-paper principal-stress guard would also misrepresent the source.

Keep the existing runtime admission unchanged. Use three distinct statements in future model comparisons and their reports:

1. **Runtime accepted:** the selected implementation accepted the supplied state/path under its recorded numerical settings. This says nothing by itself about physical admissibility, original-code equivalence or experimental prediction.
2. **Within the declared comparison scope:** a study has prospectively identified material/parameter provenance, preparation, loading coordinates, state bounds and numerical exceptions. This is a project study restriction; it is not a new universal source validity theorem. Record whether checks cover only initialization, saved outputs, or all evaluated material stages.
3. **Scientifically supported:** named source/reference/experimental evidence supports the particular claim, subject to independent review and its recorded limits. Neither of the first two statements implies this one.

For new conventional compressive-soil comparisons, use strictly compressive principal effective stresses, positive pressure and ed<e<ei as the default **project comparison restriction**. Explicitly label the principal-stress restriction as a project choice, not a requirement proved by VW96. Exact isotropy remains included. Other material regimes may be investigated under a distinct, source-supported study scope; they must not inherit a compressive-soil applicability claim merely because the engine returns a result.

| Boundary | Source / actual implementation | Reporting and study policy |
| --- | --- | --- |
| u=0, isotropic stress | AppendixC gives F=1; root returns F=1 | Include exact isotropy. Its indeterminate cosine is not a physical singularity of F. |
| 0<j2<=1e-24 | Root substitutes cosine=0 for a nonzero deviator | Identify the project near-isotropic continuation. Do not describe it as exact original invariant evaluation. A study requiring exact near-isotropic accuracy needs its own frozen reference and precision checks. |
| u>=sqrt(2) | Some states still satisfy all root guards and yield finite F | Treat as algebraic-continuation diagnostics unless separately justified. Do not infer a mandatory source guard or silently patch the host. |
| Mixed-sign principal stresses | Positive mean and even u<sqrt(2) allow them | Outside the default compressive comparison restriction. Record them as applicability diagnostics, not validated tensile-soil predictions. |
| e=ed or e=ei | Source describes limiting states; root strictly excludes both | Report a numerical-domain exclusion, not “the source forbids this state.” No epsilon shift, projection or default substitution to obtain admission. |
| Pressure at/below p_ref*1e-8 | Root rejects it | Numerical pressure cutoff. Do not equate p_ref or its cutoff with a calibrated material parameter. |
| IGS norm(h)<=R | Source physical saturation ball; root admits its surface | Use explicit history and distinguish zero history, prepared history and saturation. |
| R<norm(h)<1.01R | Root admits the state and caps rho at1 without projecting h | Numerical overshoot continuation, not a physical initial condition by default. If a trajectory enters it, report that fact when observed; do not call a whole trajectory confined to the physical ball based only on initialization/endpoints. |
| norm(h)>=1.01R | Root rejects the boundary and beyond | Preserve failure and rollback; no automatic projection to turn it into a pass. |

Original material constants must retain their identity: VW96 TableI beta=1.5, NH97's original host beta=1, current illustrative defaults beta=1.05, and the qualified TMD2 published case beta=2.5 are not interchangeable. Source recommendations and exploratory parameter boxes are also different claims. Figure10/13/14 preparation-density ambiguities remain unresolved; this policy selects no original-figure reproduction deck.

The supported kinematic interpretation remains infinitesimal and zero-spin, with strain-path rates rather than elapsed-time evolution. The existing [0–25% TMD2 reconstruction](../benchmarks/kfs-tmd2-research-range-v1/README.md) retains its operational coordinate convention and explicit unverified finite-kinematics flag. This policy does not retrospectively certify its stage-domain coverage, resolve historical strain conversion, or convert it into a finite-strain validation. Preserve that useful qualified benchmark and its original acceptance criteria.

[check_policy.py](../reviews/vw96-igs-applicability-v1/check_policy.py) reproduces 19 initialization observations across both pinned definitions: isotropy, two mixed-sign witnesses, both sides of the invariant cutoff, strict density/pressure endpoints, and IGS history surface/band/boundary. All expected admissions/rejections agree. It validates complete v0.3 profiles in memory and verifies no projection of accepted initial state. These are Python diagnostics, not a compiled integration test, full-path scope check or scientific acceptance gate. No new numerical tolerance was selected from these outputs.

No solver/schema extension follows from this decision. Before the next comparative study, freeze its parameter/preparation identity and applicability exceptions alongside its existing reference and numerical criteria. A future change to guard, cutoff, projection or finite-spin behavior requires a distinct revision, preserved prior evidence and prospective numerical/source tests. REV-04/REV-05 remain open for independent scientific review and the still-unproved scope-specific claims. The bounded applicability-policy task is complete; it does not create another solver-development workstream.
