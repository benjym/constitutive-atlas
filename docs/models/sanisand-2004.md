# SANISAND-2004: source and implementation brief

**Research candidate; not executable or source-complete.** The target is Dafalias & Manzari, *Simple Plasticity Sand Model Accounting for Fabric Change Effects*, Journal of Engineering Mechanics 130(6), 622–634, [DOI](https://doi.org/10.1061/(ASCE)0733-9399(2004)130:6%28622%29). The bibliographic identity is pinned; the full original article has not yet been inspected. SAN-01 remains open. Later SANISAND-F, memory-surface, semifluidized and other extensions require separate identities.

The [SoilModels entry](https://soilmodels.com/sanisand/) is a discovery source. A primary implementation cross-check is [OpenSees `ManzariDafalias.cpp`, revision `8a0273db3e2f5a14c05924a179c1e439500c852c`](https://github.com/OpenSees/OpenSees/blob/8a0273db3e2f5a14c05924a179c1e439500c852c/SRC/material/nD/UWmaterials/ManzariDafalias.cpp). This is an implementation variant to reconcile, not a substitute for the paper or a reference execution. The [inventory](../../catalogue/source-audits/sanisand-2004-opensees.json) records hashes and locators. No third-party source is copied into Atlas or linked into its Wasm bundle. Reuse terms need assessment before redistribution or external-code packaging.

## Required state and algebra

The proposed Atlas layout is stress (six Mandel components), void ratio (one), backstress ratio (six), fabric (six), and reversal backstress ratio (six). That is **25 persistent components**, or 26 with a residual plastic multiplier. This is a planning layout, not a claim that every implementation must store exactly these quantities. Five-component deviatoric storage would change the representation and require a separately verified basis map. Elastic/plastic strain outputs, if retained, increase storage further.

The flow direction needs the symmetric square of its normalized deviatoric direction. A scalar cubic invariant cannot replace that tensor. The required [tensor-square primitive](../TENSOR_SQUARE.md) is now implemented and verified; the [state-capacity gap](../STATE_CAPACITY.md) is also resolved; an [experimental parent-increment reset scope](../PARENT_INCREMENT_RESETS.md) is available, while selection of the canonical history policy remains open. The [capability analysis](../SANISAND_CAPABILITIES.md) separates this algebraic gap from state capacity and history transactions.

## Implementation cross-check observations

Pinned source locators are `GetF`, `GetStateDependent`, `integrate`, `commitState`, and the 3D wrapper. Reversal uses `(alpha_n-alpha_in_n):C_el:delta_epsilon < 0` to select `alpha_in=alpha_n` before integration. The code includes pressure floors/offsets, a finite near-singular hardening replacement, low-pressure dilatancy modification and elasticity depending on initial void ratio. These must not silently become original-paper equations. The 3D wrapper negates external stress/strain conventions. Its engineering-shear conversion still needs a complete mapping audit. The base rollback method is unimplemented at this revision; do not infer transactional reference behavior from its name.

The [official OpenSees documentation](https://opensees.github.io/OpenSeesDocumentation/user/manual/material/ndMaterials/ManzariDafalias.html) supplies parameter definitions and a 3D example. Its displayed deviator formula subtracts `p I/3` after defining `p=tr(sigma)/3`; that is inconsistent with a trace-free deviator and with the source's `GetDevPart`. The bounding-direction display also has damaged markup. Verify these against the original article rather than transcribing the rendered page literally.

## Extraction and admission checklist

- Obtain and inspect the complete original article, including generalized flow direction, Lode-angle convention, parameter scaling and initialization. Record equation numbers and inspection evidence.
- Extract complete elasticity, yield/loading, bounding/dilatancy surfaces, backstress, fabric and reversal laws. Define units, admissible domains and all singular limits.
- Reconcile publication, documentation and pinned implementation; record every numerical correction and release-specific behavior.
- Specify the relation between laboratory initialization, geostatic loading, elastic-stage settings and initial memory. Do not treat the website example as a calibrated Wichtmann baseline.
- Decide event scope, derivative policy, state capacity and tensor-square semantics through SAN-02–04. Keep mathematical equations declarative.
- Execute an independently sourced, source-matched reference and verify monotonic, extension, reversal and cyclic cases before model admission. Preserve unsuccessful attempts.

The model remains a catalogue candidate. No equation review, external numerical agreement or six-model milestone is claimed by this brief.
