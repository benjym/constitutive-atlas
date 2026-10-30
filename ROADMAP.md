# Constitutive Atlas roadmap

Last updated: 30 October 2026. Maintainers: [Benjy Marks](https://github.com/benjym) and [François Guillard](https://github.com/Franzzzzzzzz).

This is the implementation and research plan for the [repository](https://github.com/benjym/constitutive-atlas) and [public laboratory](https://benjym.github.io/constitutive-atlas/). Progress is milestone-based, without a fixed deadline. Unchecked work below is planned, not delivered. The [research charter](docs/RESEARCH_CHARTER.md) governs admission and scientific claims; [architecture](docs/ARCHITECTURE.md) describes the current implementation.

## 1. Destination and immediate priority

The project has three final products:

1. A versioned, source-linked database of constitutive formulations expressed declaratively and executable through a common C++ codebase.
2. A reproducible paper explaining the representation, verification and experimental comparisons, including limitations and negative results.
3. An interactive WebAssembly website for exploring models, sources, assumptions, numerical behaviour and applicable experimental evidence.

Literature discovery has broad geomechanics scope. The first executable release targets local, three-dimensional, infinitesimal-strain soil models and **twenty distinct, source-pinned formulations**. Broad discovery does not imply broad solver support or exhaustive coverage.

**The next major milestone is a reviewed six-model collection, a representation proven against SANISAND-2004, and one reproducible experimental benchmark.** Terracotta (Wiebicke & Einav, 2024) is an additional near-term priority: begin source extraction and the physical-time capability design alongside that work, with a separate execution gate below. Review the existing models before expanding the count. Do not freeze schema v1 until this proof exposes and resolves the necessary history and initialization semantics.

## 2. Starting point

| Area | Existing foundation | Outstanding evidence or capability |
| --- | --- | --- |
| Models | Elasticity, Drucker–Prager, Modified Cam Clay, von Wolffersdorff sand hypoplasticity, hypoplasticity + IGS | Independent equation/source review for all five; IGS is explicitly draft |
| Catalogue | Twenty-one seed entries, including the near-term Terracotta candidate; fifty unscreened discovery records | Reviewed admission, exact variants and literature coverage accounting |
| Representation | Restricted expressions, dimensional/shape checks, Python interpretation, C++ generation | Equation-level provenance, history/event semantics, richer initialization and version migration |
| Numerics | AD residual Jacobians, implicit/rate integration, substepping, rollback, five axisymmetric drivers | Independent references, public update tangent, configurable tolerances and recorded-path replay |
| Data | Seventeen normalized Wichtmann tests; five early-strain drained transfer demonstrations | Preparation metadata, missing initial states, broader importers and controlled evaluation |
| Delivery | Native/Wasm checks, Linux/macOS CI, public GitHub Pages deployment | Evidence-backed model pages and a scientific release package |
| Paper | Editable working manuscript and generated preliminary results | Completed study, novelty assessment, independent review and archival release |

Passing interpreter/native/Wasm comparisons establishes agreement between paths sharing the same equations. It does not independently verify the transcription. The present five-test demonstration is neither calibration nor held-out validation.

## 3. Working rules and evidence

- Keep all constitutive mathematics declarative. Extend generic language/integration capabilities when justified; do not add handwritten model kernels or model-ID-specific branches to bypass the schema.
- Separate publication, formulation, implementation, integration algorithm, parameter set, experiment and benchmark result identities. A changed parameter set or numerical regularization is not automatically a new model.
- Keep persistent publication hyperlinks in model definitions and generated pages. A source link alone is insufficient: record equation/page/section locators, conventions and transcription decisions.
- Use separate evidence for source review, numerical verification and experimental comparison. A model can pass one and remain unresolved in another.
- Preserve unsuccessful runs and unresolved source ambiguities. Never silently substitute a variant, invent initial-state metadata or discard a difficult experiment.
- Keep original experimental files immutable and checksummed. Continue linking to providers rather than bundling raw or normalized measurements until reuse terms have been reviewed.
- Specify error metrics and numerical tolerances before evaluating acceptance. Use physical scales and reported precision; do not tune tolerances after seeing a disagreement merely to pass it.

For every work item, record an ID, owner, dependencies, deliverable, acceptance evidence and unresolved questions. Benjy and François are the maintainers; lead/reviewer assignments remain to be agreed per item. An automated transcription or a second run of the same implementation is not independent review.

## 4. Milestones and dependencies

| Milestone | Outcome | Dependencies | Completion gate |
| --- | --- | --- | --- |
| M0 | Auditable project baseline | Existing foundation | Current inventory, evidence records and issue-sized backlog |
| M1 | Five reviewed model definitions | M0 | Source dossiers and independent numerical evidence for each |
| M2 | Six-model representation proof | M1; SANISAND source dossier | SANISAND, history/initialization semantics and regression evidence |
| M2T | Terracotta source dossier and time-dependent execution proof | M1 review process; TC-01–03 capability design | Original triaxial variant, timed reference cases and explicit scope limits |
| M3 | Representation and numerical interface v1 | M2 and M2T for physical-time support | Versioned contract, documented limits and reproducible implementations |
| M4 | Reproducible experimental benchmark | M1; usable specimen metadata | Published baseline reproduction and frozen evaluation protocol |
| M5 | Twenty executable formulations | M3; screened source dossiers | Twenty complete formulations meeting admission and verification gates |
| M6 | Evidence-driven public atlas | Incremental from M1; M3/M4 for complete evidence views | Source, capability and result provenance visible on the website |
| M7 | Paper and archived research release | M4–M6; independent scientific review | Reproducible results, final manuscript and archived release |

Literature screening, data curation and prior-work analysis can proceed alongside M1–M3. M4 may start with a reviewed subset; it need not wait for twenty models. Publish useful software increments throughout, with provisional status visible. Software deployment does not close a research gate.

## 5. M0 — establish the baseline

- [ ] **BASE-01:** Capture a pinned baseline manifest: source commit, model hashes, schema/compiler version, toolchain, checks and known limitations.
- [ ] **BASE-02:** Reconcile `docs/STATUS.md`, catalogue statuses and website wording with actual evidence. Keep operational deployment status separate from scientific release readiness.
- [ ] **BASE-03:** Define machine-readable review and evidence records, with schema validation and stable IDs. Proposed locations: `catalogue/reviews/`, `catalogue/evidence/` and `docs/decisions/`; create these when their first records are implemented.
- [ ] **BASE-04:** Turn the first work package in section 13 into repository issues, with leads and reviewers. Do not assign tasks to either maintainer without agreement.

**Acceptance:** a reader can identify what executes, which claims are supported, how to reproduce the baseline and which work remains. Counts distinguish discovery records, admitted formulations and executable definitions.

## 6. M1 — review and verify the five current models

Prepare one source dossier per formulation. Each dossier must contain the exact original source/variant, persistent URL, complete governing equations, stress/strain conventions, state definitions, parameter units and ranges, initialization, domain restrictions, and all corrections or regularizations. Link every implemented equation to its source or label it as a project numerical choice.

| Work item | Formulation | Review and verification focus |
| --- | --- | --- |
| REV-01 | Linear isotropic elasticity | Independent analytical tensor response, shear convention and control-path solutions |
| REV-02 | Nonassociated perfect-plastic Drucker–Prager | Yield/flow definitions, compression and extension, elastic/plastic transition, unloading and apex regularization |
| REV-03 | Modified Cam Clay | Pressure-dependent stiffness, hardening, consolidation initialization, loading/unloading and critical-state response |
| REV-04 | von Wolffersdorff sand hypoplasticity | Original-paper factors and tensor invariants, sign conversions, density/stress limits and reference parameter examples |
| REV-05 | Hypoplasticity + IGS | Original overlay and history evolution, small-strain stiffness, reversal and cyclic response, comparison with the base law |

- [ ] **REV-06:** Specify independent reference cases and their provenance. Use analytical results where available and independently sourced implementations or published numerical results otherwise; check reuse terms and exact variants.
- [ ] **REV-07:** Add step-refinement studies, rotational covariance checks, domain/failure cases and failed-increment rollback checks appropriate to each law. Do not interpret fixed-frame covariance as finite-rotation objectivity.
- [ ] **REV-08:** Record reviewer, date, tested revision, evidence and unresolved discrepancies. Fix disagreements or retain a lower status with an explicit reason.

**Acceptance:** all five dossiers and evidence records are complete, with review independent of the original transcription. If no suitable independent reference exists, document the gap and keep that model below the reviewed gate. Existing IGS draft status is not promoted solely because CI passes.

## 7. M2 — SANISAND-2004 and the six-model proof

The candidate source is already linked in the [catalogue](catalogue/manifest.json). Pin the exact formulation and its initialization before implementing it; do not mix later SANISAND variants into the 2004 model without separate identities.

- [ ] **SAN-01:** Extract the full three-dimensional equations, bounding/dilatancy surfaces, backstress and fabric evolution, reversal memory, parameter conventions and admissible starting states.
- [ ] **SAN-02:** Write a capability gap analysis against the existing DSL and 24-scalar state limit. Determine which history operations are actually required from the source before designing generic events.
- [ ] **SAN-03:** Specify trial versus committed state, event detection and ordering, reversal updates, initialization, substep behaviour and rollback. Define any event-location tolerance and the derivative policy at nonsmooth transitions.
- [ ] **SAN-04:** Implement the smallest generic extensions needed by the extracted equations, with matching Python/native/Wasm semantics. Document the design decision and migration implications.
- [ ] **SAN-05:** Transcribe SANISAND declaratively, including source locators and declared parameter/state constraints.
- [ ] **SAN-06:** Verify monotonic compression/extension, unloading/reloading, reversal and representative cyclic paths against an independent matching reference. Record parameter sets and tolerances per case.
- [ ] **SAN-07:** Demonstrate unchanged results for the existing five models within predefined numerical tolerances.

**Acceptance:** all six formulations meet their review gates and execute through the common engine without model-specific mathematical escape hatches. History and initialization semantics are explicit and tested under substepping and rollback. A paper figure or website curve alone cannot close this milestone.

### Additional near-term target — Terracotta (M2T)

**Temporal design progress:** [The physical-time integration draft](docs/TEMPORAL_INTEGRATION.md) records the current-engine gap, proposed equation/time contracts, timed controls, rollback semantics, analytical acceptance cases and TIME-01–06 implementation packages. The draft is delivered; TC-02/TC-03 remain open pending source extraction and contract validation. An [experimental physical-time ODE subset](docs/TIME_ODE_API.md) now passes analytical native/Wasm checks using separate synthetic fixtures. An [experimental ordered timed driver](docs/TIMED_SCHEDULES.md) now supports mixed component controls, holds and algebraic observables, verified against analytical Maxwell/Kelvin–Voigt cases in native/Wasm. A [separate Figure 1 research draft](docs/models/terracotta-2024-transcription.md) now adds signed axisymmetric kinematics and five author-RHS reference histories in native/Wasm. Full journal/source reconciliation, independent review, mixed-control/creep references and browser execution remain outstanding. These engine checks do not close TC-02/TC-03. The [author-source audit](docs/models/terracotta-2024-source-audit.md) records core requirements and unresolved discrepancies; TC-01 is not closed.

Target the original **Terracotta / Terra Cotta model by Max Wiebicke and Itai Einav (2024)**, [A simple hydrodynamic model for clay](https://doi.org/10.1016/j.jmps.2024.105789), with the [author reference implementation](https://github.com/MaxWiebicke/Terracotta-pq). The [source and implementation brief](docs/models/terracotta-2024.md) pins the reference revision and open questions. It remains a browser candidate with a separate axisymmetric research executable; it is not independently reviewed or a full 3D atlas model.

- [ ] **TC-01:** Extract the published triaxial-invariant equations, energy/stress contributions, solid-fraction and mesoscopic-temperature evolution, parameters, units and initialization. Reconcile the journal version against the pinned author code and record differences.
- [ ] **TC-02:** Design physical time, step duration and strain/stress-rate inputs in the schema and generic solver. Establish dimensional checks for all additional quantities; do not reinterpret normalized path fraction as elapsed seconds.
- [ ] **TC-03:** Specify rate changes, finite-duration holds, creep and relaxation controls, initial internal-state requirements and rollback. Determine the required internal-variable domain restrictions from the source.
- [ ] **TC-04:** Implement the original triaxial formulation declaratively with an explicitly restricted capability label. Decide how this scope fits the initial 3D release requirement; do not silently infer a full tensor law or count a restricted implementation toward the twenty-model 3D gate.
- [ ] **TC-05:** Reproduce author reference cases for monotonic loading, at least two physical loading rates, a rate change, relaxation and creep. Pin source code, parameters, durations and comparison tolerances. Seek independent equation/numerical review and preserve existing model regressions.
- [ ] **TC-06:** Add timed protocol/parameter presets and source links to the browser only once the native/Wasm execution evidence passes. Choose compatible clay data for later experimental comparison; do not treat Karlsruhe sand as clay validation.

**Acceptance:** a source-complete dossier, versioned physical-time contract and executable declarative original variant reproduce the pinned reference cases, including nontrivial evolution during a zero-strain-rate hold where the source predicts it. Native and Wasm agree, units/initialization are explicit and the displayed kinematic scope is accurate. SANISAND's six-model gate remains separate. Later tensorial generalizations or fault-friction variants require distinct source review and model identity.

## 8. M3 — freeze the supported representation and numerical API

- [ ] **REP-01:** Separate document/schema version, expression-language version, model revision and engine version. Define compatibility rules, migration fixtures and result hash semantics.
- [ ] **REP-02:** Specify supported kinematics, stress measures, zero-spin assumption, tensor bases, units and differentiation rules. Reject unsupported capabilities clearly rather than accepting partially meaningful inputs.
- [ ] **REP-03:** Finalize reusable initialization and history contracts proven by M2. Use M2T to specify physical-time dependence before freezing that part of v1; retain its unsupported status until implemented and verified. Keep vectors, fourth-order anisotropy and cycle-count drivers unsupported until source-complete models justify them.
- [ ] **NUM-01:** Expose a material update API returning committed state, convergence diagnostics and a documented algorithmic tangent. Distinguish an AD residual Jacobian from the tangent of the complete integrated update.
- [ ] **NUM-02:** Verify tangents against independent perturbations over smooth elastic/plastic/rate regimes. Declare behaviour at yield switches and history events; do not promise a unique derivative where one does not exist.
- [ ] **NUM-03:** Make integration tolerances, maximum iterations, substepping and failure limits configurable and include them in run provenance. Add refinement evidence before changing defaults.
- [ ] **NUM-04:** Extend drivers to replay ordered recorded paths, including reversals and mixed controls. Specify units, independent variable, interpolation and path termination; never sort a cyclic history by strain.
- [ ] **REP-04:** Publish schema v1 documentation, examples, capability matrix and migration guidance only after these contracts stabilize.

**Acceptance:** documented versioned interfaces reproduce the six-model evidence suite natively and in Wasm. New schemas validate both structure and semantics. Unsupported model families remain discoverable as candidates without implying execution support.

## 9. M4 — experimental benchmark and controlled calibration

### Data and applicability

- [ ] **DATA-01:** Audit the seventeen existing imports against original headers and representative rows. Record channel definitions, signs, units, uncertainty, warnings, raw/member checksums and transformation version.
- [ ] **DATA-02:** Extract specimen preparation, material identity, density/void ratio, consolidation history, stress state, drainage and loading controls from original metadata/publications. Keep unavailable fields explicitly missing; TMU void ratios are not inferred without evidence.
- [ ] **DATA-03:** Implement cyclic sand and kaolin importers only with reviewed channel mappings and specimen metadata. Report eligible and ineligible test counts with reasons.
- [ ] **DATA-04:** Define a model–experiment applicability matrix. Numerical execution does not imply applicability, and parameters cannot be shared across sand/clay materials without justification.

### Published baselines before fitting

- [ ] **BENCH-01:** Select a complete published model/parameter/material example that matches an available implementation and dataset. Freeze its source, initial state, protocol, output channels and numerical settings.
- [ ] **BENCH-02:** Reproduce the published calculation within declared precision or document discrepancies. The existing transfer of extension parameters to the base law remains a separate demonstration.
- [ ] **BENCH-03:** Publish one end-to-end benchmark command that fetches permitted data, verifies hashes, normalizes, executes, computes errors and generates figures/tables without manual editing.

### Controlled study

- [ ] **CAL-01:** Freeze whole-test calibration and evaluation IDs before optimization, stratified by relevant pressure, density and loading conditions. Keep all samples of a test together; record how previously inspected tests were used and avoid claiming blind evaluation of them.
- [ ] **CAL-02:** Predefine tunable versus fixed parameters, bounds, initialization parameters, objective channels/scales, optimizer, seeds, stopping conditions, budgets and treatment of solver failures.
- [ ] **CAL-03:** Implement calibration on the frozen calibration subset. Record every candidate evaluation and failure, not only the selected parameter vector.
- [ ] **CAL-04:** Evaluate the locked parameter set on the evaluation subset. Any retuning after inspection creates a new study revision and requires a fresh evaluation strategy.
- [ ] **CAL-05:** Report curve errors on declared sampling grids, relevant physical features, sensitivity/identifiability and parameter uncertainty. Preserve path order, prohibit extrapolation and avoid weighting results by recording density.

**Acceptance:** at least one source-matched published baseline is reproduced and a controlled study is fully reproducible. All results identify model, parameters, experiment, protocol, solver settings, hashes, eligibility and failures. Unit tests remain distinct from scientific error thresholds. No universal ranking is inferred from one material or test family.

## 10. M5 — expand toward twenty executable formulations

Screen and source-pin the shortlist before treating it as a release commitment. The following waves prioritize representational value and compatible data; they are provisional implementation order, not claims that these candidates are already complete or suitable.

| Wave | Candidate formulations | Prerequisite or admission question |
| --- | --- | --- |
| A | Original Cam Clay; NorSand-1993; clay hypoplasticity-2005 | Exact source variants, complete state laws and appropriate sand/clay benchmarks |
| B | Manzari–Dafalias-1997; S-CLAY1; clay hypoplasticity-2013 | Proven history semantics and any necessary anisotropic representation |
| C | Mohr–Coulomb; Tresca; Lade–Duncan; Matsuoka–Nakai-based formulation | Complete constitutive closures; generic nonsmooth/edge/apex treatment where required |
| D | Duncan–Chang-1970; source-pinned sand barodesy; ISA extension; HCA-2005 | Complete 3D loading/unloading laws or new history/cycle-count capabilities supported by sources |

SANISAND is delivered through M2; Terracotta is prioritized separately through M2T. These waves account for the other fourteen original candidates. The discovery catalogue now has thirty-one entries while the executable release target remains twenty; freeze the final selection after source/capability review, without silently dropping an existing candidate. A criterion alone, an unspecified family, an unsupported cycle-averaged law or an inaccessible source does not count toward twenty executable formulations.

The [SoilModels coverage record](catalogue/discovery/soilmodels-2026-10-30.json) maps all thirteen main directory listings to candidates or existing formulations. Ten candidates were added, with family/version ambiguities recorded explicitly. Discovery does not change the twenty-formulation release target. Screen these additions before assigning implementation waves: PM4Sand/PM4Silt need version and dimensional-scope review; EMC needs hardening and nonsmooth integration; the interface model needs traction/slip and in-plane stresses; multilaminate plasticity needs plane quadrature and per-plane history; thermal cycles and VIBE need thermal/hydraulic inputs, with VIBE also requiring physical time; generalized IGS needs a pinned host-law pairing; clay barodesy and clay hypoplasticity-2014 need separate source dossiers.

- [ ] **LIT-01:** Screen and deduplicate the fifty discovery records, then perform backward/forward citation tracing and targeted searches across the charter's families. Preserve queries, dates, source access and exclusion reasons.
- [ ] **LIT-02:** Maintain a publication-to-formulation lineage graph linking originals, corrections, extensions and competing implementations.
- [ ] **ATLAS-01:** Select each implementation from an admitted source dossier, with an applicability target and a clear reason it adds scientific or representational coverage.
- [ ] **ATLAS-02:** Apply the M1 review process and M3 compatibility suite to every added formulation. Extend the capability matrix and browser provenance together.
- [ ] **ATLAS-03:** Replace or defer unsuitable candidates through a recorded decision. Explain count/scope changes rather than padding the release with parameter variants.

**Acceptance:** twenty distinct complete formulations have persistent sources, declarative definitions, initialization, capability declarations, numerical evidence and independent review. Each has either an applicable experimental comparison or an explicit reason that comparison is absent. Do not claim that all twenty have been experimentally validated.

## 11. M6 — make the website an evidence browser

- [ ] **WEB-01:** Give each formulation a stable shareable URL with source links, variant/lineage, status, review evidence, assumptions, parameters, initial-state requirements and known limitations.
- [ ] **WEB-02:** Generate catalogue and detail pages from canonical records so hyperlinks, revisions and statuses cannot drift into a separate manually maintained database.
- [ ] **WEB-03:** Expose reproducible protocol presets and source-backed parameter sets, visibly distinguished from illustrative defaults. Include engine/schema/model revisions in exported runs.
- [ ] **WEB-04:** Add applicable benchmark overlays and evidence summaries with provenance, failures, numerical settings and calibration/evaluation labels. Host measurements only when reuse terms permit; otherwise retain source links and local loading.
- [ ] **WEB-05:** Support comparisons under identical declared conditions, while flagging incompatible materials, state assumptions or protocols. Avoid an unexplained aggregate leaderboard.
- [ ] **WEB-06:** Check keyboard/mobile use, chart units, import compatibility, stale-asset detection, cancellation and resource limits. Verify deployment beneath the GitHub Pages project path.

**Acceptance:** a reader can travel from a plotted curve to the exact formulation, source equations, parameters, initialization, protocol and evidence used to generate it. Pages deployment continues to depend on native and Wasm checks. Website availability remains separate from scientific review status.

## 12. M7 — paper, reproducibility package and research release

- [ ] **PAPER-01:** Prepare a source-backed prior-work comparison covering constitutive DSLs/code generation, material-point verification tools, calibration systems and model/data repositories. Assess novelty before making a novelty claim.
- [ ] **PAPER-02:** Freeze study questions and analysis around faithful representation, reproducibility, numerical robustness and applicability-dependent experimental performance. Document what the study cannot answer.
- [ ] **PAPER-03:** Generate all quantitative tables and scientific figures from versioned result manifests, including failed cases and uncertainty. Keep the manuscript synchronized with the actual release scope.
- [ ] **PAPER-04:** Have equation transcriptions, numerical evidence, data mappings and scientific conclusions independently reviewed. Resolve or disclose every material discrepancy.
- [ ] **REL-01:** Produce a clean-checkout reproduction guide, pinned toolchain/dependency versions, hashes, executable definitions, parameter/protocol/data manifests, review evidence and a test/benchmark report.
- [ ] **REL-02:** Audit source/data reuse permissions, citation metadata, author contributions and release contents. Existing authors are Benjy Marks and François Guillard; contribution statements and affiliations require their input.
- [ ] **REL-03:** Tag and archive the accepted release, obtain an archival identifier when available, and update the paper and website to reference it. Agree journal/venue and submission separately; the roadmap does not authorize submission or contacting third parties.

**Acceptance:** a new researcher can reproduce the reported results from a pinned source snapshot and permitted data, with no undocumented manual adjustment. The final paper's claims match that snapshot. Describe coverage with a search cutoff and inclusion boundaries rather than claiming all possible models have been collected.

## 13. Next work package

Start with these bounded tasks; they prepare the six-model milestone without prematurely implementing another large batch.

1. **BASE-01–03:** Pin the baseline and define the review/evidence record structure.
2. **REV-01:** Complete elasticity as the first end-to-end dossier and independent analytical reference example.
3. **REV-02–03:** Review Drucker–Prager and Modified Cam Clay, exercising the same admission workflow on plasticity.
4. **REV-04–05:** Review both hypoplastic formulations, with IGS reversal evidence before status promotion.
5. **SAN-01–02:** Extract SANISAND and publish the capability gap analysis; then implement only the demonstrated missing semantics.
6. **TC-01–03:** Start the Terracotta source dossier and physical-time/hold-driver design as near-term work, then implement and verify the original variant through TC-04–06.
7. **DATA-01–02 / BENCH-01:** Audit current imports and select the first source-matched published baseline alongside model review.

The first checkpoint is a reviewed elasticity dossier plus a reusable evidence record and reproducible analytical case. The next checkpoint is the complete five-model review pack and source-complete SANISAND and Terracotta designs. Neither checkpoint is complete at the date of this roadmap.

## 14. Tracking and scope decisions

Maintain this file as the milestone-level plan, repository issues as task-level tracking, and evidence manifests as the record of completed work. Update checkboxes only when acceptance evidence is linked. Record changed priorities, replaced formulations, schema extensions and study revisions in decision records.

Track progress through admitted/source-complete/executable/reviewed formulations, reproduced reference cases, eligible experiments, baseline reproductions, study completion and reproducibility status. Do not use paper counts, lines of code or passing CI alone as measures of scientific completion.

Keep finite-strain/finite-rotation mechanics, finite elements, boundary-value solvers, unsaturated/coupled processes, rock damage, general time-dependent families and nonlocal execution outside the initial engine release unless a documented scope decision adds them with corresponding sources and tests. Terracotta's physical-time, creep and relaxation work is the explicit near-term exception in M2T; it does not imply general support for those other families. Continue discovering and cataloguing them with honest capability labels.
