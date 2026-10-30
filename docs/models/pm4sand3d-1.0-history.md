# PM4Sand3D 1.0: state, events and lagged-update inventory

This is a **candidate documentary inventory**, not a complete constitutive implementation. Independent review and numerical admission remain pending. The [machine-readable inventory](../../catalogue/source-audits/pm4sand3d-1.0-history-inventory.json) records 30 field groups, their shapes, units, initialization, update stages, dependencies, aliases and uncertainties. It is intended to define the schema requirements before choosing storage capacity.

The selected source is the [June 2026 vendor manual](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf), SHA256 `6073a97a374d4b947e20a492b5009bbd01e3e5b0b773841b0f3b037c194f7453`. Printed page n corresponds to PDF page n+5. The May author citation, Box edition and matching constitutive DLL/source have not been reconciled. No 2D PM4Sand 3.3 state assumptions are imported.

Algorithm and initialization printed pp76–79/PDF81–84 were visually inspected; p79 was rechecked for this inventory. The constitutive-history prose and dependencies in Sections2.2,2.5–2.9 and4.1 were located in private text extraction, with exact equation transcription and further visual equation checks pending. No constitutive code/DLL was inspected or executed. The PDF and extracted text are not included in the repository.

## Retained fields and stage-dependent values

| Group | Shape and units | Role and source location |
|---|---|---|
| Effective stress sigma | symmetric3D; stress | Subzone trial followed by corrected zone commit; Table3.1 steps5–8 and Table3.2 steps9–10,21 |
| Backstress alpha | symmetric3D; dimensionless | Yield-surface center, not generally current stress ratio; same tables |
| alpha_in, alpha_inP | two symmetric3D tensors; dimensionless | Current and previous true reversal anchors; Sec2.5 pp26–27 Eqs26–27; Table3.3 p79 step5 |
| alpha_inMin, alpha_inMax | two symmetric3D tensors; dimensionless | Named initialization extrema supporting apparent-anchor logic; exact evolution unresolved; Table3.3 p79 step5 |
| Fabric z, reversal fabric z_in | two symmetric3D tensors; dimensionless | Current fabric and immediate branch snapshot; Sec2.8 pp35–38 Eqs64–71; Table3.2 steps15–16 |
| z_alpha | symmetric3D; dimensionless | Explicitly initialized to zero; no consuming/evolution law identified in this bounded review; Table3.3 p79 step7 |
| z_cum, z_peak | two scalars; dimensionless | Cumulative fabric-increment norm and historical maximum fabric magnitude; Sec2.8 Eqs65–66; Table3.3 initializes peak to z_max/100000 |
| p_zp and fabric-pressure peak zxpPk | two scalars; stress, subject to product-definition resolution | Formation pressure at greatest fabric-pressure peak and peak comparator; pp36–38, Table3.3 p79 step7 |
| D and Kp | two scalars; dimensionless and stress | **Next caller-step lagged numerical memory** shared by subzones; Sec3.2 pp71–72 and Table3.2 step13 |
| G and K | two scalars; stress | Next-step caches; initialize then update at step18 and optionally reduce at step23; Sec2.6, Eq93, Eqs94–99 |
| Current density/volume representation | one provisional scalar; dimensionless | Relative state update needs evolving density/volume information. The exact representation and update remain unresolved; Eqs10–11, Table3.2 step18, Table4.2 e_max/e_min |
| Initial CSR normalization | one provisional scalar; dimensionless | Preserve initialization normalization or an equivalent preparation record; Sec2.6 pp27–28 Eqs30–31 |
| p, r, n | scalar plus two symmetric tensors; stress, dimensionless | Algebraically derived pointwise, but explicitly averaged/cached in host algorithm; Table3.2 steps9,21 |
| Strain increment accumulators | names/shapes unknown; strain | Explicitly updated at Table3.2 step19; not automatically total/plastic strain |
| Zone reduction workspace | host collection; mixed | Weighted sums and final-subzone completion; Table3.2 step9, Figure3.1 p80 |
| Parallel hourglass resistance | unknown state per subzone | Independent deviatoric elastoplastic stabilization, with initialization-fixed properties; Sec3.2 p72 |
| FirstCall, PostShake | two flags | Preparation/reset event and user-controlled postshaking mode; Sec4.1 pp83–85 |
| Effective initialization parameters | named typed parameter record | Defaults/overrides and preparation provenance, not automatically evolving physical state; Tables3.3 and4.1–4.2 |

Apparent alpha_inapp and true alpha_intrue must not be counted as automatically independent tensors. The latter appears to name alpha_in; the former uses directional component extrema and zero clipping (Sec2.5 p26). The mapping from alpha_inMin/Max to that prose remains a source-reconciliation task. Componentwise tensor extrema need not remain trace-free; five-component compression is not justified by deviatoricity of the input tensors alone.

Image backstresses, Lode factor g, relative state index, Mb/Md/MdR, flow B/C/R, loading index L, fabric modifiers, Fsed and p_sed are derived stage terms. In particular p_sed is algebraic in Eq97; no autonomous sedimentation time evolution is inferred. A derived quantity may still need an explicitly tagged cache when its source inputs belong to an earlier stage.

## Initialization and control events

[Table3.3 pp78–79](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=83) first reads the current host stress and can modify it to satisfy initialization bounds. It initializes backstress from the resulting stress ratio, all four reversal/extrema anchors to alpha, G/K from initial pressure, **Kp=100G and D=0**. Fabric tensors and cumulative fabric start at zero, but z_peak starts at z_max/100000. Initial p_zp=p0/100 and zxpPk=−z_max*p0/50 retain the host sign convention pending reconciliation.

[FirstCall, pp83–85](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=88), is unspecified or zero on assignment; initialization sets it to one internally. Setting it back to zero reinitializes the internal terms from current host stress, erasing fabric and backstress history. This must be a visible preparation/reset event. It does not mean returning to the original strain, stress or original specimen history. Which effective secondary defaults are recomputed on a later reset remains unverified. Secondary parameter input zero selects the default (p86), so raw user values and resolved values must remain distinguishable.

PostShake starts at zero and changes only on user instruction. Setting it to one after strong shaking activates Eqs94–99 stiffness reduction; the source warns against activating it during strong shaking. The multiplier is applied to the conventional current G/K, rather than repeatedly multiplying already reduced moduli. Preserve the original density used in Fsed_min and user overrides. On/off transition and zero-denominator/domain behavior still need an explicit source-matched contract.

## Caller-step ordering and host scope

[Sec3.2 pp71–72](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=76) and [Tables3.1–3.2 pp76–77](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf#page=81) establish the following order:

1. Initialize/reset if requested. Each subzone consumes committed parent state and the shared previous-step D/Kp, computes an elastic or plastic trial, applies penalties and returns stress to the host.
2. Only after the final subzone, area-weight the listed strain increments, p, sigma, alpha, n and rotation quantities. Correct the averaged zone state and compute image surfaces and reversal predicate.
3. Compute new D/Kp for the **past averaged response**, retaining them for the next caller step. This precedes the new fabric, Lode g, surfaces and moduli stages.
4. Compute plastic volumetric increment; update fabric and related cumulative/peak/pressure/reversal memory. Compute new g, relative state, surfaces and G/K.
5. Update reversal anchors and unnamed strain accumulators (steps19–20), commit sigma/p/alpha/r, apply large-strain rotations where enabled, then apply PostShake stiffness changes.

The source explicitly uses integration without constitutive substeps. Adding hidden subdivisions changes when lagged values and events advance. A homogeneous single-subzone material-point reduction must declare how it reduces the averaging/stabilization operations; it is a separate reference contract from FLAC3D equivalence. Average of unit normals need not be a unit normal, and average of ratios need not equal ratio of averages. Their exact source treatment needs checking before deleting p/r/n caches.

The hourglass law belongs to **each subzone independently**, unlike most zone-shared PM4 histories. It supplies deviatoric resistance only, with initial moduli 1% of the main initial moduli and strength from the larger applicable specified chg or crhg-based value (default crhg=.005). Its exact plastic internal state and stress combination are not given sufficiently to reproduce or budget. It cannot be silently folded into the main zone state.

The Atlas adapter must make the whole update transactional: trial events, caches and reductions remain provisional, a successful caller update commits once, and a failed update restores the exact parent. This is a design requirement inferred for safe replay, not a claim that the manual itself specifies rollback. No partial zone reduction may advance history. The initial implementation should declare zero spin; rotating only the tensors explicitly named at step22 does not establish a complete objective-history implementation.

## Storage budget: a ledger, not a capacity recommendation

Using six raw components per named symmetric tensor gives **9 tensors ×6=54 slots**: stress, alpha, four reversal/extrema tensors, z, z_in and unresolved z_alpha. Add the four named scalar histories z_cum, z_peak, p_zp and peak product comparator: **58**. Keeping D/Kp/G/K explicitly gives **62**. Keeping p/r/n as documented caches gives **75**. Provisional current density and initialization CSR normalization bring that scenario to **77**, and two flags to **79**.

These are allocation scenarios, **not a proven minimum independent state count**. Possible aliases/reconstructions may reduce them. Conversely they exclude resolved parameter/preparation records, unnamed strain accumulators, zone reduction workspace, transaction copies, all per-subzone hourglass state, host total strain and derived scratch values. The current fabric-pressure product is a possible additional cache, not counted as retained history. Do not change a global state-array capacity from this arithmetic. Define a typed per-model history, cache, preparation and host-context contract first.

## Unresolved gates and next bounded work

The JSON retains the full conflict ledger. The immediate gates are:

- Reconcile reversal extrema/app/true aliases, ordered old/new snapshots, steps19/20 and the unexplained z_alpha field against a constitutive implementation or author clarification.
- Define density/volume evolution and exact initialization CSR normalization; preserve preparation provenance.
- Resolve the ill-typed printed fabric-pressure product, peak aliases/comparators and D=0-safe fabric increment. Eq65 cumulative norm and step15/16 wording also need reconciliation.
- Reconcile Chapter2 and host tension-positive pressure signs, pressure floors, trace notation, equality branches at sigma11=0, xi_R=0 and Mfin=Mcut, hydrostatic Lode direction, and the Ado critical-state limit.
- Define an explicit zero-spin homogeneous reduction and lag boundary, then verify reset/replay equivalence, reversal microcycles, caller-step partition sensitivity and failed-trial rollback.

Table3.1's initialization cross-reference is wrong (it points to Table3.2; initialization is Table3.3). Its printed plastic stress correction also needs reconciliation with Eqs35–37. No source ambiguity here is repaired silently, no executable registration is added, and no reuse permission is inferred from availability of the manual or driver examples.

## Proposed engine contract

The [experimental history/transaction design](../HISTORY_TRANSACTIONS.md) and [non-executable PM4Sand3D example](../../proposals/pm4sand3d-history-contract.json) map this inventory to typed storage lifetimes, immutable phase snapshots, caller boundaries and atomic commit/rollback. All source-blocked update phases remain disabled. The current model parser, solver and state capacity are unchanged.
