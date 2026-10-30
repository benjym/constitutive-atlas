# PM4Sand3D 1.0: old/new and reversal-stage reconciliation

Bounded source review, 31 October 2026. This packet does not define an executable PM4 algorithm. Candidate status and independent scientific review remain unchanged. It concerns **3D 1.0**, not PM4Sand 2D 3.3.

Primary source: [Kippen et al., June 2026 manual](https://itasca-software.s3.amazonaws.com/udm-library/Kippen_et_al_PM4Sand3D_v1_CGM-26-01.pdf). Private file `/private/tmp/atlas-pm4sand-source/pm4sand3d-1.0-itasca.pdf`, SHA256 `6073a97a374d4b947e20a492b5009bbd01e3e5b0b773841b0f3b037c194f7453`, 17,267,510 bytes, 149 PDF pages. Printed page n corresponds to one-based PDF page n+5. May/June edition and exact author-code pairing remain unresolved. Rendered pages were visually inspected at printed 26–27, 31, 36, 71–72, 76–77 and79; text search supplemented navigation. Source PDF, images and text are private and excluded from the public packet manifest.

## What the source establishes

| Source locator | Verified fact | Lifetime consequence |
|---|---|---|
| Sec3.2 pp71–72, PDF76–77 | Constitutive calls occur per subzone; volumetric increment is shared while deviatoric increments can differ. Zone averaging and corrections follow. New D/Kp come from corrected averaged response and are used by all subzones on the next timestep. Explicit integration has no constitutive substepping. | D/Kp are retained incoming caller-step lag, shared read-only across subzone evaluations. Their endpoint replacements cannot affect another subzone in the same caller step. |
| Table3.1 p76 steps5–7; Table3.2 p77 step7iv–vi | Trial stress, direction and plastic correction use incoming state/coefficient values; trial stress/backstress are locally committed before zone processing. | The source's local commit is a stage boundary; it is not an Atlas durable transaction commit. |
| Table3.2 p77 step9 | After the final subzone: area-weighted averaging of volumetric/total strain increment, p, locally committed stress/backstress, n and rotation. | Workspace is incomplete before the final contributing subzone. Averaged n cannot silently be assumed unit length. Exact normalization/recomputation remains open. |
| Table3.2 steps10–12 | Zone penalties/consistency corrections, images/inner products and reversal detection follow averaging. | Reversal event is determined at the corrected-zone stage before the late anchor updates. Exact alpha/n evaluation snapshot remains a source gate. |
| Sec2.5 p26 Eq26 | Reversal criterion is `(alpha-alpha_in):n < 0`. Previous initial anchor receives the initial anchor; initial anchor receives current alpha. | Copy must preserve the pre-copy initial value. Source does not state which Table3.2 substage supplies each operand. |
| Sec2.5 pp26–27 Eq27 | Apparent anchor uses componentwise directional extrema with zero bounds; transition involving the previous anchor uses strict `<0`. | Apparent anchor is not automatically an independently stored tensor or a proved alias of named Min/Max storage. Componentwise extrema are not proved trace-free or rotation covariant. |
| Table3.2 step13 | D/Kp are computed for the past averaged zone step. | These are candidate next-step values, not coefficients retroactively used by the completed subzone plastic solve. Dependencies on late anchors/fabric remain unresolved. |
| Table3.2 steps14–16; Sec2.8 p36 | Plastic volumetric increment drives fabric; cumulative/peak/product memory follows. Reversal fabric z_in is sampled at the same reversal times as the anchors. | Same event cadence does not identify whether z_in copies pre- or post-fabric-update z. Exact D used for the volumetric-to-shear conversion and the D=0 branch remain unresolved. |
| Table3.2 steps17–18 | Lode/state/surface/modulus quantities are updated for the next step. | Candidate G/K have next-step lifetime; read dependencies on updated fabric need explicit edges. |
| Table3.2 steps19–20 | Both steps mention initial-anchor updates; step19 also mentions previous anchors and unnamed strain accumulators. | Do not implement two unconditional copies: the previous anchor would be overwritten. These steps may describe different operations, but that separation is not supplied. |
| Table3.2 steps21–23 | Zone mechanical memory commit, selected tensor rotation and PostShake reductions occur late. | The listed rotation includes sigma/alpha/r/z; a complete rule for historical anchors, extrema and reversal fabric is not given here. Zero-spin scope avoids this unresolved extension. |
| Table3.3 p79 steps5–7 | Four named anchors/extrema initialize to alpha; D=0, Kp=100G; z/z_in/z_alpha initialize to zero. | Restore must not repeat initialization. z_alpha has no identified evolution/consumer in this bounded manual review. |

## Additional branch discrepancy and singularity

At printed31 Eq47, the previous-anchor condition is `<=0`; printed27 Eq27 uses `<0`. They describe related stiffness branching, not Eq26's separate strict reversal predicate. Preserve all three source locators rather than replacing them with one generic event condition.

Eq47 divides the apparent-anchor projection by the true-anchor projection. Table3.3 initializes the named true/previous/extrema anchors to current alpha, so the true-anchor denominator vanishes. If the apparent anchor also coincides, the expression is 0/0; its exact initialized construction remains unresolved. The positive `C_gamma1` in Eq46's separate exponential-distance denominator does **not** by itself regularize Eq47. At a reset to current alpha, the true-anchor projection also vanishes. A finite limit/branch, its exact evaluation stage, and whether the formula is evaluated before or after anchor copying require clarification. No epsilon, clipping or inferred ratio of one is justified by this packet.

The equality witness uses abstract coordinates along a unit deviatoric tensor: alpha=previous=.4, true=.1, apparent=-.2. Eq27's predicate is false, Eq47's is true, and its ratio is2 rather than the alternate branch's1. This distinguishes the printed expressions algebraically; **it is not evidence that this anchor tuple is reachable by the complete PM4 history algorithm**. A source-matched reachable equality trace is still required.

## Reconciliation with the existing Atlas contract

The existing [history inventory](../../catalogue/source-audits/pm4sand3d-1.0-history-inventory.json) and [transaction proposal](../HISTORY_TRANSACTIONS.md) correctly keep unresolved chronology disabled. Relevant repository locators: `docs/models/pm4sand3d-1.0-history.md:15–32,38`; `proposals/pm4sand3d-history-contract.json:717–720,778,809,844,886,969,1105–1113`. The generic Python history runtime now exists; that does not make these PM4 phases executable.

Use these **stage names for a future dependency map**, not as a chosen source algorithm:

1. `parent`: complete committed state/preparation/modes/lag and any host subzone state.
2. `subzone_trial[i]`: private outputs using shared `parent.D/Kp/G/K`.
3. `zone_complete`: all weighted reductions complete.
4. `zone_corrected`: source corrections/images and an explicitly bound reversal decision.
5. `coefficient_candidate`: next-step D/Kp, with unresolved anchor/fabric read edges declared.
6. `fabric_candidate`: evolved fabric/scalars, with unresolved D source and z_in copy stage declared.
7. `surface_candidate`: next-step surfaces/G/K.
8. `anchor_candidate`: one resolved old-to-new history operation, not two assumed resets.
9. `final_candidate`: permitted rotation/PostShake complete.
10. Atomic publication after full candidate acceptance.

Stages5–8 are a **transcription skeleton only**. The table's textual sequence is evidence of order, but does not resolve every expression's old/new inputs or possible staged copies. Do not infer an executable DAG just from this numbering. In particular, recomputing Eq26 after setting alpha_in=alpha changes its strict guard to false; a declared earlier event must remain the same event wherever its consumers run.

Atlas isolation/atomicity rules are engineering requirements, not claims about FLAC's external control solver: every rejected outer Newton candidate starts from the same parent; a failure after fabric/anchor/lag computation rolls back all retained fields; incomplete zone reduction publishes nothing. Diagnostics may describe rejected work but no durable event survives. Caller subdivision changes lag/event boundaries; this source does not promise partition invariance.

## Discriminating evidence and next source questions

`catalogue/investigations/pm4-order-reconciliation-v1/illustrations/pm4_order_witnesses.py` and retained `catalogue/investigations/pm4-order-reconciliation-v1/synthetic-order-witnesses.json` demonstrate distinguishable old/new choices. Four pure-Python test groups pass. These fixtures test arithmetic consequences and encode desired envelope assertions; they do not exercise the actual Atlas history engine, simulate PM4, or resolve source chronology.

Before admitting a homogeneous zero-spin PM4 source algorithm, obtain independently reviewed answers to:

1. Precisely which corrected alpha and n feed Eq26, and is n normalized after averaging? Freeze that decision once, with a source-matched reversal trace.
2. For step13, identify old/current anchors, apparent extrema, z/z_in/peak/pressure and G read snapshots. Resolve Eq27/Eq47 equality and Eq47's zero-true-anchor-distance branch.
3. For steps14–16, identify the plastic volumetric increment and D epoch, zero-D branch, and pre/post-z sample used for z_in. Confirm z_alpha's role or authoritative non-use.
4. Disambiguate step19 from20: names/shapes of accumulators, copy/update order, extrema/app construction and reset cadence. Compare tiny repeated reversal loops that would reveal duplicate anchor copying.
5. Define complete single-subzone reduction scope and excluded hourglass stabilization; establish correction/n normalization identities before treating reduction as an identity.
6. Obtain exact source/manual/code version pairing and permitted reference access. Do not execute unreviewed author binaries to settle these questions.

A code/pseudocode trace answering these exact questions is the smallest useful next acquisition. A generic runtime extension, bigger state capacity, or guessed chronology would not close this scientific source gate.
