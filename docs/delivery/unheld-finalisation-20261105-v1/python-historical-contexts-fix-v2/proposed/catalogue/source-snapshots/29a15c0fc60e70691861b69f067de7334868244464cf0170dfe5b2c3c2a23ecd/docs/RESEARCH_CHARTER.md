# Research charter

The long-term objective is an executable, source-linked atlas of constitutive geomechanics. A release is a bounded evidence snapshot, not a claim to have exhausted the literature.

## Scope and questions

The discovery programme covers soils, granular media, intact and jointed rock, interfaces, damage, creep, unsaturated media, coupled thermal/hydraulic/chemical processes, and nonlocal formulations. The initial engine covers local, 3D, infinitesimal-strain, rate-independent soil models. Researchers developing and comparing models are the primary audience; an educational laboratory is a secondary audience.

The eventual paper asks whether a shared declarative representation can faithfully reproduce distinct constitutive families, and how supported formulations compare under identical, source-traceable experimental conditions. It does not assume one universally best model.

## Search protocol

- Initial cutoff: 2026-10-30. Save query, API URL, retrieval time, cursor, and unmodified discovery response. Crossref batches in `catalogue/discovery` preserve discovery evidence; screening decisions live separately in `catalogue/screening.jsonl`. A batch's saved `status` describes retrieval time and is never rewritten after screening.
- Search themes: constitutive geomechanics; soil plasticity/critical state; bounding/multisurface plasticity; hypoplasticity/barodesy; rock plasticity/damage; creep; unsaturated/coupled models; interfaces/nonlocal theories.
- Combine bibliographic searches with foundational books/reviews, author publication lists, code registries and backward/forward citation tracing. Log source availability and languages; inaccessible texts remain unresolved records.
- Deduplicate publications by normalized DOI, then title/authors/year when DOI is absent. Deduplicate formulations separately by governing equations, assumptions, state variables and documented lineage.
- A screening record includes publication ID, model ID(s), inclusion decision, reason, evidence locator, reviewer, review date and unresolved questions. An automated extraction is never its own independent review.
- Report screened/included/excluded/unavailable counts only after screening. The [screening ledger](../catalogue/screening.jsonl) records metadata decisions against immutable source locators and hashes; [the screening report](LITERATURE_SCREENING.md) distinguishes occurrences, publications, inclusion for full-text review and admission. Discovery or inclusion for full-text review is not admission.

## Admission and identity

Use stable IDs for formulations. Parameter sets, implementations and algorithm choices are related records, not new model families. Corrections and extensions reference a parent. A failure criterion without a flow rule, stiffness and evolution law is not counted as a complete constitutive model.

Statuses: `candidate` (discovery only), `draft` (incomplete or unreviewed transcription), `transcribed` (executable with source locators), `numerically-tested` (named numerical evidence recorded), and `reviewed` (independent equation/numerical review signed). Experimental validation is a separate per-model/per-protocol evidence claim. The software does not promote a model because tests happened to pass.

Each equation must identify its source location and any sign conversion, regularization, correction or ambiguity. Current model files group related equations under section/image locators; equation-by-equation original-paper review remains a release gate.

## Calibration and evaluation

Reproduce published parameter sets before optimization. Record the model variant, material identity, preparation method, consolidation, stress/density, internal-state initialization and calibration source. Published constants from an extension do not automatically reproduce that extension's simulations when transferred to the backbone.

Freeze whole-test calibration and held-out IDs before fitting. Stratify by density, pressure and loading condition; never split adjacent samples of one test between sets. No held-out labels are assigned to the initial five-test demonstration. Freeze parameter bounds, objective channels/scales, optimizer, seeds and evaluation budgets before a controlled study. Preserve failed simulations in results rather than dropping them from summaries.

Use uniform strain/phase grids to avoid overweighting dense recording intervals; never extrapolate or reorder cyclic histories. Report curve and feature errors with applicability and uncertainty. Unit tests establish numerical properties, not predictive accuracy.

## Prior work and novelty gate

MFront/TFEL already provides constitutive DSLs and C++ generation; MGIS, MTest, OpenSees, numgeo, SoilModels, ExCalibre and related material-point tools are relevant comparisons. Prepare an evidence-backed feature comparison before claiming a novel language or benchmark methodology. The present working manuscript makes no novelty claim.

## Rights and reproducibility

Keep raw source files unchanged with checksums. Link publications rather than redistributing full texts. Raw experimental archives and normalized records stay ignored/local until reuse terms are established. Source code and original definitions use MIT terms; referenced third-party materials retain their own terms. No author-contact messages or publication submissions are authorized by this charter.

Publish scientific releases only with a pinned source commit, toolchain versions, model/parameter/protocol/data manifests, test report, and archived reproducibility package. Private software previews may precede a scientific release if their provisional status is clear.
