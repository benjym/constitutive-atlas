# Modified Cam Clay — bounded source reconciliation

Task REVIEW-modified-cam-clay; coordinating parent, 1 November2026. This packet reconciles the implemented material/finite-step identity and makes the v0.3 persistent-state/initialization contract explicit. It closes the bounded reconciliation/gap-report assignment, **not REV-03 or independent scientific admission**. Root bytes, model status, historical dossiers/reports and the shared solver remain unchanged.

## Sources, identity and reading scope

The [Silbermann–Nagel report, 28 June2023](https://github.com/ufz/ogs/blob/b5d0f115c75ee74a7cdbfad533625a550a416fda/web/content/docs/benchmarks/small-deformations/ModifiedCamClay/ModifiedCamClay_report.pdf) is pinned to OGS commit `b5d0f115c75ee74a7cdbfad533625a550a416fda`. The retrieved27-page PDF matches the historical checksum `a03df6d05d777bfc4d484e6e12a2aecdebcbbf16bfca3b6601e699178620e9ce`. Relevant Sections2.1–2.3 and3.1 were text-read; pages2,3,5,6 were visually inspected. This is not a full27-page review or review of every derivative/implementation/benchmark in that report.

The [Itasca formulation](https://docs.itascacg.com/itasca930/common/models/camclay/doc/modelcamclay.html) provides a separate primary comparison of continuous stiffness, yield and flow, with different finite-step updates. The versioned URL currently returns a documentation title identifying9.4; it is not an immutable revision. Web-tool access succeeded; a direct raw fetch returned403, so no raw HTML checksum is invented. [Source receipts](source-receipts.json) distinguish the pinned PDF from this access-limited comparison. Sources/PDF/renders/full extracted text are linked and kept private, not redistributed. No source code or author binary was executed.

## Source equations, ambiguities and selected identity

The [historical dossier](../../models/modified-cam-clay.md) states the complete implemented residuals and scalar reduction. The inspected source supports effective stress (p2 footnote2), infinitesimal strain, p/q invariants, associated flow and pressure/volume-dependent stiffness. Atlas reverses both stress and strain from the source's tension-positive tensors, preserving positive pressure. Mandel contraction preserves the source tensor invariants.

Two printed inconsistencies remain explicit:

- Eq11 p3 has a single M, while Eq30b p6 uses M². The stated critical-state slope and separate Itasca yield equation support the selected M² form. The exact witness p=pc/2,q=Mpc/2 satisfies the selected ellipse but generally not the single-M form.
- Eq7 p2 prints phi_dot-phi*div(u_dot)=trace(strain_rate). With div=trace, it implies phi_dot=(1+phi)*volumetric_strain_rate. Eqs8–9 instead imply (1-phi) times that rate, as does the later porosity step Eq30d. Atlas's exponential v=1+e update follows Eq9. At phi=1/3 and source tension-positive volume rate1/100, the two implied porosity rates are1/75 and1/150. This is an unresolved source inconsistency, not a reason to replace the current volume law silently.

Text extraction also drops the minus in Eq14; rendered p3 confirms its minus agrees with Eq16. This is an extraction hazard, not another printed hardening-sign conflict.

| Part | Source support | Atlas choice / limitation |
| --- | --- | --- |
| K=vp/kappa; G=3K(1-2nu)/[2(1+nu)] | Continuous Eq17 plus constant-nu relation Eq21 | Current endpoint v,p. Eq21's illustrative derivation linearizes v to v0; the report also discusses lagged stiffness in Eqs26–27. Do not claim a verbatim full source algorithm. |
| f=q²+M²p(p-pc) and associated flow | Eq30b and Eq12, with Eq11 conflict retained | Project p_ref² yield scaling and Fischer–Burmeister complementarity. |
| Normalized plastic volume | Flow direction from gradient of chosen yield surface | gamma/pc_n scales the gradient; source Eq12 instead divides by gradient norm. Multiplier normalization changes, direction does not. |
| e update | Differential volume relation Eq9 | Exponential total-volume bookkeeping, different from source porosity finite-step Eq30d and Itasca Eq8. |
| pc update | Continuous log-hardening implied by Eqs14–16 | Backward-Euler update of log(pc), with endpoint v/plastic increment, then exponentiation. Different from direct pc step Eq30c and Itasca Eq31. |

The exponential updates do not extend the stress law to finite strain. No equivalence to the complete OGS/MFront or Itasca algorithm is claimed.

## Complete v0.3 contract and initialization

[formulation-crosswalk.json](formulation-crosswalk.json) maps all five parameter declarations, six derived quantities and four state equations. It declares compression-positive Mandel incremental residuals, infinitesimal3D fixed spatial components, zero spin and effective Cauchy stress. Persistent sigma is a symmetric spatial tensor; persistent e and pc are invariant scalars. Passive tensor covariance does not implement finite-step objective transport.

The normalized multiplier gamma is a `plastic_multiplier`, not a persistent state. The v0.3 initializer requires exactly sigma,e,pc and fills the temporary slot with zero. A caller must not supply accumulated gamma or infer a preparation history from it. Parameters include the natural-log v–ln(p) indices lambda_c/kappa and the project numerical scale p_ref. The root requires lambda_c>kappa, positive e, pressure and pc, and an iteration-domain allowance gamma>-1e-9. Its initial yield check allows scaled yield<=1e-8. A retained small-positive-yield witness shows why this is numerical admission rather than exact yield admissibility. Nothing is projected onto the surface.

Default100kPaI,e=.7,pc200kPa gives illustrative OCR2. No NCL intercept or calibrated specimen history is supplied. Yield admissibility alone does not prove consistency of e,p,pc with a chosen material's consolidation line. Initialization/preparation must be supplied explicitly for an experimental comparison.

## Temporal integration and transactions

There is no elapsed-time/creep law. Within an internal residual solve, committed sigma_n,e_n,pc_n remain fixed; stiffness, flow and hardening use endpoint quantities. A zero increment has unchanged persistent fields and gamma0. Each new internal solve resets gamma; repeated trials begin from the same committed state.

The project solver may subdivide. Independent replay must compose scalar references on the recorded accepted increment fractions; returned gamma belongs to the final internal step. A raw full-step reference is a different discrete problem and remains visible. Full parent failure must roll back all incoming fields despite any tentative substeps. Source mapping and Python residual checks here do not rerun compiled subdivision, controls or rollback. Complementarity is nonsmooth, and neither scalar branch uniqueness nor adaptive accuracy throughout the parameter boxes is established.

## Checks, evidence and reproduction

```sh
python3 docs/ingestion/modified-cam-clay/check_crosswalk.py --repo .
```

[Checks](crosswalk-checks.json) pass13 contract/initialization observations, the two exact source-conflict witnesses and three scalar-reference/current-Python residual cases (elastic, wet hardening, dry softening). The source-specific scalar oracle is verification code, not a production material kernel, and executes no compiled solver. Diagnostic absolute residual budgets are fixed before calls; no threshold was adjusted from observed output. A source witness reproducing a printed inconsistency is not a scientific acceptance pass.

Four existing Python-only oracle groups also pass: isotropic consolidation/hardening, general-versus-special isotropic agreement, wet/dry response and rejected partition traces. The two native test methods were not run.

Both historical report hashes are checked: [failed v1](../../../catalogue/evidence/modified-cam-clay-investigation-v1.json) retains its mismatched unpartitioned yield-crossing comparison; [passing57-case v2](../../../catalogue/evidence/modified-cam-clay-scalar-v2.json) retains wet/dry tensor, noncoaxial, actual-partition and refinement evidence. Neither compiled corpus is rerun or relabelled by this source task. Partition agreement verifies a solution on the accepted partition, not the quality of partition selection or a continuum solution for every path.

## Handoff and remaining gates

The additive [pending v3 review](../../../catalogue/reviews/modified-cam-clay-source-v3.json) preserves old records and narrows source questions to the explicit printed conflicts, endpoint/normalization/discretization choices, initialization and the numerical reference's scope. Independent scientific sign-off remains outstanding. Experimental applicability, nearly singular parameter limits, global branch selection, finite strain/spin and generic accuracy control are not proved.

Source completeness for this bounded mapping, executable support, numerical evidence and scientific admission remain separate. No new model, migration, schema feature, native build, compiled call, promotion, push or deployment is part of the task. Subsequent work can continue the existing review/benchmark lanes; no new solver workstream is needed to close this reconciliation.
