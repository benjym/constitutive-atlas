# Terracotta / Terra Cotta — near-term model target

Catalogue ID: `terracotta-2024`. Status: **candidate; not executable**. Priority: near term, requested by Benjy Marks on 30 October 2026. This is a source and implementation brief, not a completed equation transcription or review.

## Sources and variant identity

- Max Wiebicke and Itai Einav (2024), **A simple hydrodynamic model for clay**, *Journal of the Mechanics and Physics of Solids*, 192, 105789. [Original publication / DOI](https://doi.org/10.1016/j.jmps.2024.105789).
- [Author implementation: MaxWiebicke/Terracotta-pq](https://github.com/MaxWiebicke/Terracotta-pq), formulated in triaxial invariants. Reference revision inspected for this brief: [`a4039d0124d8ff61e766f5201f44ddc163c4cff5`](https://github.com/MaxWiebicke/Terracotta-pq/tree/a4039d0124d8ff61e766f5201f44ddc163c4cff5).
- [Pinned reference README](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/README.md) documents the Python implementation and loading controls, including physical rates, creep and relaxation. [Pinned code licence](https://github.com/MaxWiebicke/Terracotta-pq/blob/a4039d0124d8ff61e766f5201f44ddc163c4cff5/LICENSE): MIT. This identifies the code terms, not the terms for any third-party experimental measurements.

Use the journal paper as the formulation source and the pinned author code as reference evidence. The reference README cites an earlier manuscript, so code/paper equivalence must be checked rather than assumed. No author code has been imported or executed as part of adding this candidate.

The immediate target is the **original triaxial-invariant clay model**, not an unreviewed tensorial extension. The later [Hydrodynamics of Fault Gouges From Constitutive Modelling to the Physics of Friction](https://doi.org/10.1029/2024JB030822) distinguishes the original triaxial model from its tensorial generalization and derived friction law. If either later variant is admitted, give it a separate source-pinned identity and review.

## Why it belongs near term

The published model is rate dependent and uses a mesoscopic-temperature internal variable. It provides a concrete test of physical-time semantics that the existing rate-independent soil implementations do not exercise. The current engine's integration path fraction is not physical elapsed time; adding this candidate does not change that limitation.

## Extraction and representation work

Use roadmap tasks **TC-01–06** and the [temporal integration design draft](../TEMPORAL_INTEGRATION.md). The draft separates physical-time equations, timed controls and numerical methods, with implementation packages and analytical acceptance cases; equation extraction and contract validation remain open. Before implementation, record:

- Equation-level original-paper locators and any differences from the author code.
- State and parameter definitions, units, initialization, admissible domains and sign conventions.
- Elastic, dissipative and internal-variable contributions and their dimensional consistency.
- Physical time, strain/stress rates and durations, including what happens while imposed strain rate is zero.
- Creep and relaxation boundary controls, multi-stage loading and rate changes.
- The distinction between supported axisymmetric invariant paths and a general three-dimensional tensor update.

Retain the declarative implementation requirement. Add generic units, state evolution and integration capabilities only after source extraction establishes the requirements; do not embed a Python or C++ Terracotta kernel behind the schema.

## Reference and acceptance cases

Select concrete cases from the pinned author implementation and publication before setting comparison tolerances. The initial evidence pack should cover monotonic loading at two physical rates, a rate change, relaxation, creep, initial-state/domain failures, time-step refinement and rollback. Record all parameters, internal initial conditions, durations, loading rates and reference revision. Shared-source code agreement does not replace independent equation review.

Native and Wasm must reproduce the same declared cases. A zero-strain hold must retain any time evolution predicted by the law, rather than collapsing to a zero increment because the strain path is stationary. The website must expose rate and duration controls and label the original formulation's restricted scope.

Experimental comparisons require appropriate clay material/preparation data and initialization metadata. The existing Karlsruhe fine sand overlays are not validation of a clay formulation. Any use of Wichtmann kaolin data requires a reviewed importer, applicability assessment and its own reuse review.

## Admission decision still open

Source extraction, numerical implementation, experimental matching and independent review remain outstanding. The candidate increases catalogue breadth to 21 entries while the initial executable release target remains 20. Inclusion of a restricted triaxial implementation in the initial 3D release requires an explicit scope decision or a separately reviewed tensorial formulation; it must not silently weaken the release gate.
