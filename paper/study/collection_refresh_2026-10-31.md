# Collection refresh and paper priorities — 31 October 2026

The expanded collection strengthens the planned mechanism-and-calibration paper. Its immediate value is more demanding source and task coverage; it does not yet justify a larger predictive leaderboard. This is a development snapshot, not a study freeze.

The [machine-readable snapshot](collection_refresh_2026-10-31.json) pins the manifests, definition files and selected shared evidence. The existing command `python3 paper/scripts/audit_public_feasibility.py` regenerates the public-data field inventory. Recheck these inputs before reusing the snapshot after further atlas changes.

## What has changed

The catalogue contains 32 entries: 4 transcribed, 1 draft and 27 candidates. Five entries are marked executable. There are eight definition files: five public and three research definitions. The two SANISAND research definitions add execution policies for one source family; neither is another admitted literature formulation. The existing six paper implementation annotations have not automatically expanded to eight.

The shared original-paper receipt and subsequent reviews now provide primary-source evidence for SANISAND 2004, VW96, IGS97 and Wu–Bauer 1994. These are shared assisted reviews, with independent review pending. The paper's earlier SANISAND web-access failures remain historical, rather than evidence that the original 2004 source is still unavailable. The 2008 source and exact lineage remain separate follow-ups.

The public field audit now contains **628 records under 89 material labels**, an increase of 106 records and five labels from the preceding paper audit. There are 485 measurement series, 94 summaries and 49 normalized experiments. The number meeting the current minimum triaxial field checks remains **12**; 37 normalized experiments retain metadata gaps. The check is deliberately limited to current triaxial requirements: it does not assess whether a DSS, torsion or rock dataset is scientifically useful.

Material labels include specimen and campaign names. Castlegate acquisition blocks, grain populations and per-cycle summaries illustrate why neither record counts nor label counts measure independent experiments or materials. Link phases and summaries to physical specimens before splitting or estimating uncertainty.

## Recommended work order

| Priority | Model/data opportunity | Paper question | Concrete next deliverable |
| --- | --- | --- | --- |
| 1 | VW96 and IGS97 original-source reviews | What does reversal memory add, and what information does its initialization require? | Reconcile the paper annotations against original host specialization, history transport and initialization. Establish a legitimate common host or treat them as independently calibrated formulations; do not assume an exact parent reduction. |
| 2 | SANISAND original equations and two research policies | Can numerical memory policies change an apparent constitutive advantage? | Add a paper evidence review distinguishing continuous equations, initialization, reset policy and numerical refinement. Keep policy sensitivity separate from a literature parent–extension comparison. |
| 3 | Ottawa F65 LEAP DSS and torsion | Do cyclic observables distinguish models that fit monotonic tests similarly? | Design a separate cyclic panel and specimen/phase map before calibration. Review initial density, effective stress, drainage/control conventions and cross-campaign duplicates; assign development/evaluation roles before inspecting response plots. |
| 4 | KFS compression and a coherent second clean sand | Which complementary tests improve state and loading-path transfer? | Resolve the existing KFS initialization gate and second-material metadata. Additional source curves do not supply missing KFS constants or resolve the Hostun worksheet issues. |
| 5 | Castlegate sandstone and hydraulically loaded shale | Where does model choice depend on compaction, stress path or coupling? | Extend survey applicability and evidence annotations; defer executable rock comparisons until appropriate complete laws and apparatus-to-specimen mappings are reviewed. |
| 6 | Grain-resolved stresses and printed assemblies | Can microstructural observations constrain otherwise ambiguous mechanisms? | Treat as exploratory mechanism evidence with explicit observation operators. Grain rows are not loading increments, and sensor displacement is not automatically specimen strain. |

The public inventory contains 17 LEAP 2018 DSS records and 74 torsion records. The latter mix histories, apparatus channels and summaries; they are not 74 cyclic specimens. DSS normal/shear channels must retain their physical meanings rather than being relabelled as triaxial p and q. Constant-volume control, zero-filled channels and effective-stress interpretation require explicit review.

Castlegate has 69 records spanning hydrostatic and true-triaxial acquisition and a summary. Shale has 13 hydraulic-path/summary records. Hurley has 25 grain-stress/summary records, and printed grains has two source curves. These are opportunities for the broad survey and future observation-specific panels. The current record forms do not establish homogeneous continuum loading histories.

## Consequences for the manuscript

Keep RQ1–RQ3 and the focused sand comparison as the core. Use the new source evidence to make the complexity accounting more defensible, and develop one cyclic panel if its review and model admission succeed. Keep rock, coupling and microstructure in the broad survey or explicitly separate future tasks. The central figures remain a mechanism/evidence map, calibration-information requirements, and task-specific predictive benefit.

Do not insert these moving collection counts as final manuscript results. No new parameter counts, physical-state dimensions, calibration fits, numerical solver runs or benchmark admissions were made in this refresh. Private processed datasets remain outside this public inventory and require separate access and reuse review.
