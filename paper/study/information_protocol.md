# Calibration information before the study freeze

The current development runs fit four hypoplastic constants while supplying four others. They therefore cannot answer the core equal-information complexity question. [The information ledger](calibration_information.json) documents this partition without changing the historical configurations or fits.

## Primary comparison: common available information

Define the available laboratory evidence first, then admit formulations able to use it. A package includes curve IDs, independent index measurements and their uncertainty, initial-state observations, preparation and consolidation history, and any source-derived constants or relations. Publish this account alongside fitted counts.

Every model may use the same available evidence. Equal information does not require identical parameter symbols or fitting sequences. It does require that a model's extra input is either accessible to every model, explicitly added to the package, or removed from the primary comparison. A formulation needing unavailable history can remain in the survey and be excluded from that task panel.

For the present sand pilot, the next controlled design must resolve:

| Quantity | Decision before final calibration |
| --- | --- |
| Limiting-density/index observations | Locate original measurements, units, uncertainty and applicability to this material; distinguish observations from fitted constitutive limiting densities. |
| Compression-shape information | Supply eligible compression data to all formulations or investigate fitting the corresponding coefficients from the common package. Inherited constants cannot silently fill a missing experiment. |
| Parameter relations and bounds | Declare their sources and assess sensitivity where they materially constrain predictions. A relation reduces fit dimension while supplying information. |
| Void ratio and stress | Resolve source disagreements or freeze qualified scenarios before opening final responses. Preserve measured initial stresses. |
| Fabric and reversal memory | Use measured or reproducible history where available. Treat assumed or fitted initial states explicitly; a zero state does not remove the information question. |

Do not activate an all-parameter fit just to equalize counts. It needs admissible bounds, initialization checks, numerical verification and enough calibration evidence. A poorly constrained fit can be scientifically informative, but search failure is not proof that a mechanism lacks predictive value.

The selected OE1/OE12 development records now have a [source-pinned initialization feasibility protocol](compression_protocol.json). Published simulations start at 1 kPa axial stress; this does not specify a full initial stress tensor. The data-only diagnostic also quantifies the difference between measured engineering strain and the exponential void-ratio continuity of the native laws. Resolve and qualify the loading coordinate, lateral stress and history before using these observations to replace inherited compression constants. A positive axial-stress threshold alone does not close model admission.

## Secondary comparisons

A source-parameter reproduction asks whether the pinned implementation reproduces a specified published case. It must preserve that case's formulation, constants, preparation, controls and initialization, including qualifications.

A recommended-programme comparison asks what a formulation achieves with its proposed calibration experiments. Different programmes are allowed, but their extra observations, specimen preparation and history requirements must be reported. Compare this practical cost separately from the primary common-information result.

The existing partial-fit development track remains useful for designing these comparisons. It belongs to neither a completed source reproduction nor the primary equal-information benchmark.

## Fixed empirical inputs and source-case fit counts

The [NorSand input-role audit](source_formulations/norsand-1993.json) separates material-input candidates, a fixed empirical coefficient, initialization dependencies and the source example's fitted subset. Its text-based inventory remains provisional pending equation verification. This distinction should apply across the survey: an externally fixed relation contributes information even when it adds no fitted dimension. Record its origin and applicability alongside the available laboratory evidence.

A source reproduction also needs the provenance of all supplied characterization evidence. Holding a coefficient fixed while predicting another curve does not establish that the curve was absent from earlier characterization. Track those evidence dependencies before assigning calibration/evaluation roles; unresolved dependence qualifies the result rather than supplying proof of leakage or independence.

## Companion calculations and measured loading information

The [HCA source-case information audit](source_formulations/hca-sand-2005.json) records accumulation inputs separately from companion-model inputs and initialization. Its visually inspected tables are inventories, not independent parameter dimensions. Calibration burden belongs to the declared prediction workflow, including any companion calculation needed to obtain its inputs.

For future accumulation panels, declare two possible tasks before choosing data:

| Task | Information available | Outcome being assessed |
| --- | --- | --- |
| Accumulation conditional on observed cycles | A specified measured recording cycle and the allowed updates | Transfer of accumulation given observed local loading |
| Accumulation with predicted cycles | Prescribed external loading and a calibrated companion law | Prediction by the combined workflow, including amplitude errors |

These tasks require separate results. If a recording cycle from an evaluation specimen is supplied, name that observation as conditioning information and evaluate later responses. If companion constants are adjusted against that cycle, record an adaptation/calibration stage and its cost. Do not describe the entire specimen response as untouched evaluation. Freeze the observation interval, permitted updates and later evaluation interval before inspecting final responses.

For combined workflows, list shared observations once in the information budget; record which components consume them. Report constants by component and role, leaving a combined independent dimension unresolved until dependencies and reference conventions are audited. This does not admit HCA or its companion to the current sand pilot.

## Observations that distinguish constitutive choices

The partial Carranza-Torres–Fairhurst review in the [full-text ledger](survey_full_text_screening.json) provides a scoped example. Its perfectly plastic cavity problem separates the stress solution from displacement, while considering different plastic potentials (Appendix A, pp. 803–808). Our inference is that matching that stress field alone cannot select the flow rule. This does not establish the same independence for other geometries, loading paths or evolving strength.

For each proposed mechanism comparison, identify which available observables can distinguish the alternatives under the actual controls. Where the selected observable is structurally insensitive, report that limitation rather than interpret equal errors as evidence that the mechanism is unnecessary. Include deformation channels and their measurement uncertainty when the scientific question concerns dilation or displacement. Keep this source example outside the sand pilot and benchmark admission.

The [partial gradient-rock source note](source_notes/gradient-rock-2018.json) adds a spatial comparison question: distinguish parameter selection from parameter identification, and declare the boundary-value observations needed to assess a spatial mechanism. The [conditional operator derivation](spatial_observability.md) establishes homogeneous insensitivity and a single-mode parameter trade-off for its assumed mathematical problem. Its two-mode inversion assumes internal-field information, not experimentally observed loads or displacements; it cannot establish an experimental programme without the full observation map and uncertainty analysis. Source transcription and independent review remain open. The note adds no atlas formulation identity, admitted model or completed full-text screening decision.

The [constant-stress-ratio probe](stress_ratio_probe.md) adds a conditional yield-geometry calculation and a proposed compression task. It distinguishes that task from oedometer loading and from reversal or inherent-anisotropy comparisons. The linked publisher-abstract review establishes discovery questions only; original equations, lineage mappings and task admission remain open. No ISO responses have been inspected.

## Evidence needed to close the gate

The study freeze needs reviewed information records for every admitted model/package, source-linked fixed and fitted partitions, declared treatment of initialization uncertainty, and a completed feasibility pilot using those records. Independent scientific review remains outstanding. This document specifies decisions to resolve; it does not certify that the available experiments can constrain every model.
