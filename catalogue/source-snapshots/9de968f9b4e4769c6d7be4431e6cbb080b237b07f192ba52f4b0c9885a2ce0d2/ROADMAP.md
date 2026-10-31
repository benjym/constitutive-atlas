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
| Catalogue | Thirty-two discovery entries, including the near-term Terracotta candidate and SoilModels coverage; 34 distinct publications excluded from the original fifty Crossref results; targeted source review started | Reviewed admission, exact variants and literature coverage accounting |
| Representation | Restricted expressions, dimensional/shape checks, Python interpretation, C++ generation | Equation-level provenance, history/event semantics, richer initialization and version migration |
| Numerics | AD residual Jacobians, implicit/rate integration, substepping, rollback, five axisymmetric drivers | Independent references, public update tangent, configurable tolerances and recorded-path replay |
| Data | Seventeen normalized Wichtmann tests; five early-strain drained transfer demonstrations | Preparation metadata, missing initial states, broader importers and controlled evaluation |
| Delivery | Native/Wasm checks, automatic Linux CI, manual macOS checks, public GitHub Pages deployment | Evidence-backed model pages and a scientific release package |
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

- [x] **BASE-01:** Capture a pinned baseline manifest: source commit, model hashes, schema/compiler source identity, toolchain, checks and known limitations. The [complete clean-export baseline](catalogue/baselines/2026-10-30-r3/manifest.json) passes all fifteen ordered checks; [run history](catalogue/baselines/README.md) retains two failed attempts and [reproduction instructions](docs/SOFTWARE_BASELINE.md) describe the fresh native/Wasm build. This is software verification, not independent scientific review.
- [ ] **BASE-02:** Reconcile `docs/STATUS.md`, catalogue statuses and website wording with actual evidence. Keep operational deployment status separate from scientific release readiness.
- [x] **BASE-03:** Define machine-readable review and evidence records, with schema validation and stable IDs. The [record contract](docs/EVIDENCE_RECORDS.md), numerical/review schemas, hashed [elasticity evidence](catalogue/evidence/linear-elastic-analytical-v1.json) and [pending review](catalogue/reviews/linear-elastic-source-v1.json) are implemented. Integrity and current-definition checks are separate; no model is automatically promoted. Experimental scope choices now use [decision records](docs/decisions/0001-sanisand-parent-reset-research.md).
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

The [elasticity dossier](docs/models/linear-elastic.md) and [29-case analytical report](catalogue/evidence/reports/linear-elastic-analytical-v1.json) now provide the first source mapping and numerical evidence example. All 29 native cases pass, and the rebuilt public catalogue passes native/Wasm parity. REV-01 remains open for independent review; the automated oracle does not supply independent authorship.

The [plasticity investigation](docs/PLASTICITY_VERIFICATION.md) adds 19 Drucker–Prager and 20 MCC comparisons, source-scope notes, increment diagnostics and revision-pinned failed-outcome evidence. DP passes 18/19, with a shear/apex rollback limitation. MCC passes 19/20: the retained full-step comparison differs after automatic subdivision, while the matching two-half-step scalar reference agrees; both isotropic refinement studies pass. REV-02/REV-03 and independent review remain open. The later [declarative DP apex correction](docs/models/drucker-prager-apex.md) resolves the observed shear/apex failure and passes 73 analytical cases, now a native regression gate, with a passing v2 evidence record and pending v2 review. Earlier failed reports remain immutable. The [MCC dossier](docs/models/modified-cam-clay.md) now contains the full equation/state/parameter and initialization contract plus a general scalar reduction. Its passing v2 evidence covers 57 cases, including wet/dry plastic tensor increments and exact accepted-partition replay; raw unpartitioned comparisons remain explicit. The 57-case suite is a native regression gate. Independent review remains pending. The [VW96 base-law dossier](docs/models/hypoplastic-sand-vw96.md), hashed source-image inventory and passing v2 evidence add 229 Cartesian-rate, oblique covariance, independently refined RK4 path and rollback checks. The initial failed reversal-reference convergence report is retained. Full original-paper and independent review remain open; REV-04/REV-05 are not closed by the base-law checks.

The [IGS draft dossier](docs/models/hypoplastic-sand-igs97.md) now separates the continuous history/overlay law from numerical caps and external projection algorithms. Its initial 303-case investigation passes all 295 instantaneous/covariance/rollback checks and four histories, while retaining four failed history checks. Cyclic native history discrepancy and RK4 reference convergence remain open; REV-05 is not complete.

The [IGS endpoint-defect correction](docs/models/hypoplastic-sand-igs97.md#endpoint-defect-correction-and-v2-evidence) resolves the analytically confirmed small-cycle error. All 303 checks now pass with unchanged tolerances and analytical-stage history for collinear RK4 references; full-state refinement remains for noncollinear paths. Native/Wasm crossing and cyclic regressions supplement the preserved failed v1 evidence. Independent review and REV-05 remain open.

**Acceptance:** all five dossiers and evidence records are complete, with review independent of the original transcription. If no suitable independent reference exists, document the gap and keep that model below the reviewed gate. Existing IGS draft status is not promoted solely because CI passes.

## 7. M2 — SANISAND-2004 and the six-model proof

The candidate source is already linked in the [catalogue](catalogue/manifest.json). Pin the exact formulation and its initialization before implementing it; do not mix later SANISAND variants into the 2004 model without separate identities.

- [ ] **SAN-01:** Extract the full three-dimensional equations, bounding/dilatancy surfaces, backstress and fabric evolution, reversal memory, parameter conventions and admissible starting states.
- [ ] **SAN-02:** Write a capability gap analysis against the DSL and state capacity (originally 24 scalar components). Determine which history operations are actually required from the source before designing generic events.
- [ ] **SAN-03:** Specify trial versus committed state, event detection and ordering, reversal updates, initialization, substep behaviour and rollback. Define any event-location tolerance and the derivative policy at nonsmooth transitions.
- [ ] **SAN-04:** Implement the smallest generic extensions needed by the extracted equations, with matching Python/native/Wasm semantics. Document the design decision and migration implications.
- [ ] **SAN-05:** Transcribe SANISAND declaratively, including source locators and declared parameter/state constraints.
- [ ] **SAN-06:** Verify monotonic compression/extension, unloading/reloading, reversal and representative cyclic paths against an independent matching reference. Record parameter sets and tolerances per case.
- [ ] **SAN-07:** Demonstrate unchanged results for the existing five models within predefined numerical tolerances.

The [SANISAND source brief](docs/models/sanisand-2004.md), [pinned OpenSees inventory](catalogue/source-audits/sanisand-2004-opensees.json) and [provisional capability analysis](docs/SANISAND_CAPABILITIES.md) identify a 25-component persistent layout (26 with a multiplier), missing tensor square and unresolved reversal transaction scope. Synthetic capacity/type probes are reproducible. Original-paper extraction and numerical-variant reconciliation remain incomplete; SAN-01–04 are not closed and no executable candidate is added.

The [symmetric tensor-square primitive](docs/TENSOR_SQUARE.md) now resolves the demonstrated algebraic gap, with dimensional/type checks, Cartesian references, all native AD columns and a generated Python/native/Wasm fixture. Existing five-model references continue to pass. The [state-capacity extension](docs/STATE_CAPACITY.md) also accommodates 32 state components and all six mixed controls. Reversal transactions, complete original-paper extraction and the rest of SAN-04–07 remain open.

The [experimental parent-increment reset contract](docs/PARENT_INCREMENT_RESETS.md) now supplies typed simultaneous memory assignments from a committed parent, frozen internal trials and exact rollback. Python/native/Wasm synthetic checks cover reversals, cutbacks, internal threshold crossing, caller partition effects, invalid values and outer mixed controls. The [verification record](catalogue/investigations/parent-reset-v1.json) pins its source and outcomes. This implements one explicit engine scope; canonical SANISAND policy, full original-paper extraction, initialization and independent reference execution remain open.

A [source-conventions audit](docs/models/sanisand-2004-conventions.md) now adds tested engineering-shear/unit/tangent conversions and 87 Cartesian comparisons of 18 unchanged selected OpenSees state/tensor functions. The [revision-pinned report](catalogue/investigations/sanisand-source-functions-v1.json) documents a unit-dependent low-pressure correction and other variant-specific limits. This advances SAN-01/02/06 source reconciliation; complete original-paper extraction, full reference integration and canonical transcription remain open.

An [initialization/transaction source contract](docs/models/sanisand-2004-initialization.md) now records stage-dependent parameter mutation, shared stage/copy effects, preparation strain origins, recorder trial/committed distinctions and reset omissions. Its [twelve pending full-reference scenarios](catalogue/source-audits/sanisand-2004-initialization.json) advance SAN-01/03/06 extraction without claiming runtime characterization or closing those tasks.

The [integration source contract](docs/models/sanisand-2004-integration.md) now maps all eleven declared scheme codes and identifies stage-density, tolerance, subdivision, fallback and status-reporting differences. Its ten runtime scenarios remain pending; scheme names and zero API return codes do not establish a source-matched reference solution. SAN-01/03/06 stay open.

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

SANISAND is delivered through M2; Terracotta is prioritized separately through M2T. These waves account for the other fourteen original candidates. The discovery catalogue now has thirty-two entries while the executable release target remains twenty; freeze the final selection after source/capability review, without silently dropping an existing candidate. A criterion alone, an unspecified family, an unsupported cycle-averaged law or an inaccessible source does not count toward twenty executable formulations.

The [SoilModels coverage record](catalogue/discovery/soilmodels-2026-10-30.json) maps all thirteen main directory listings to candidates or existing formulations. Ten candidates were added, with family/version ambiguities recorded explicitly. Discovery does not change the twenty-formulation release target. Screen these additions before assigning implementation waves: PM4Sand/PM4Silt need version and dimensional-scope review; EMC needs hardening and nonsmooth integration; the interface model needs traction/slip and in-plane stresses; multilaminate plasticity needs plane quadrature and per-plane history; thermal cycles and VIBE need thermal/hydraulic inputs, with VIBE also requiring physical time; generalized IGS needs a pinned host-law pairing; clay barodesy and clay hypoplasticity-2014 need separate source dossiers.

Author-source screening on 2026-10-31 identifies a separate PM4Sand3D 1.0 release (Kippen, Boulanger & Ziotopoulou; author page cites May 2026, downloaded vendor manual says June). The [version dossier](docs/models/pm4sand-versions.md) and [lineage record](catalogue/discovery/pm4sand-2026-10-31.json) distinguish it from the selected plane-strain PM4Sand2D 3.3 candidate. The [partial manual audit](docs/models/pm4sand3d-1.0-manual.md) now pins both vendor PDFs and identifies lagged zone/subzone integration requirements. Full equations, author-edition equivalence and reference execution remain open. Catalogue counts stay at 32 total, 27 candidates; this does not count toward twenty verified formulations.

- [ ] **LIT-01:** Initial metadata screening and DOI deduplication are recorded in the [screening report](docs/LITERATURE_SCREENING.md): all 34 distinct publications in the original fifty results were outside scope. The SQLite export preserves decisions and all raw-source occurrences alongside lineage records, with evidence validation before export. Continue targeted searches and backward/forward citation tracing across the charter's families; complete full-text screening and independent review. Preserve queries, dates, source access and exclusion reasons.
- [ ] **LIT-02:** Maintain a publication-to-formulation lineage graph linking originals, corrections, extensions and competing implementations. The [initial publication graph](docs/PUBLICATION_LINEAGE.md) now records nine hypoplasticity publications, seven sourced relations and the existing von Wolffersdorff formulation binding; broader source coverage, version/equation reconciliation and independent review remain open.
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

A standalone publication browser now exposes the canonical graph with title/author/DOI/year search, version and formulation filters, correction notices, source locators and shareable publication links. Model source panels link to bound publications. The regular Pages packaging includes these assets; local static browser checks cover the initial graph without running the solver. WEB-01/02 remain open for complete per-formulation evidence, assumptions, parameter and review pages; deployment verification of this addition is pending.

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

The first checkpoint is a reviewed elasticity dossier plus a reusable evidence record and reproducible analytical case. The next checkpoint is the complete five-model review pack and source-complete SANISAND and Terracotta designs. BASE-01/BASE-03 and the elasticity dossier/analytical evidence are implemented. Neither independently reviewed checkpoint is complete at the date of this roadmap.

## 14. Tracking and scope decisions

Maintain this file as the milestone-level plan, repository issues as task-level tracking, and evidence manifests as the record of completed work. Update checkboxes only when acceptance evidence is linked. Record changed priorities, replaced formulations, schema extensions and study revisions in decision records.

Track progress through admitted/source-complete/executable/reviewed formulations, reproduced reference cases, eligible experiments, baseline reproductions, study completion and reproducibility status. Do not use paper counts, lines of code or passing CI alone as measures of scientific completion.

Keep finite-strain/finite-rotation mechanics, finite elements, boundary-value solvers, unsaturated/coupled processes, rock damage, general time-dependent families and nonlocal execution outside the initial engine release unless a documented scope decision adds them with corresponding sources and tests. Terracotta's physical-time, creep and relaxation work is the explicit near-term exception in M2T; it does not imply general support for those other families. Continue discovering and cataloguing them with honest capability labels.

### Original papers received — 2026-10-31

The [four-paper receipt](catalogue/source-audits/original-papers-2026-10-31.json) pins user-supplied SANISAND-2004, VW96, IGS97 and Wu–Bauer 1994 PDFs without redistributing them. All title pages are verified. The [SANISAND original-paper dossier](docs/models/sanisand-2004-original.md) maps equations, Table 1 and triaxial reductions, distinguishes current-void-ratio elasticity from OpenSees, and flags the apparent missing bulk modulus in printed Eq. (20). VW96/IGS97 equation reconciliation and Wu–Bauer extraction remain pending. SAN-01 remains open for initialization, domains and independent review; no executable count or validation claim changes.

### IGS original-source reconciliation — 2026-10-31

The [IGS97 original-paper review](docs/models/hypoplastic-sand-igs97-original.md) confirms the continuous overlay, identifies the seven-parameter host as `beta=1`, pins Table I, and separates history overshoot/reset and spin transport from Atlas numerical choices. A new [Python-only source-equation report](catalogue/investigations/igs-original-rates-v1.json) passes 576 Cartesian fourth-order versus interpreter comparisons. Complete preparation-path reproduction, native/reference integration, original VW96 reconciliation and independent review remain open; REV-04/REV-05 are not closed.

### VW96 original-source reconciliation — 2026-10-31

The [original VW96 review](docs/models/hypoplastic-sand-vw96-original.md) directly maps Eqs. (40)–(46), the isotropic limit and the published continuity law to the existing transcription. The eight-parameter host is confirmed; its Hochstetten Table I uses `beta=1.5`, distinct from the IGS97 specialization and current illustrative defaults. Independent review, full derivation/domain studies and source-specific benchmark reproduction remain open under REV-04. No model equations or defaults change.

### SANISAND original algebra — 2026-10-31

A [33-term source fragment](catalogue/source-audits/sanisand-2004-original-equations.json) now type-checks the original on-cone elasticity, surfaces, flow, hardening, fabric and loading equations in the existing DSL. Five [Python test groups](tests/test_sanisand_original.py) verify source identities, Cartesian tensor algebra, active yield consistency, triaxial limits, pressure-unit covariance, unloading/dilation, softening and undefined-state rejection. The [record](catalogue/investigations/sanisand-original-algebra-v1.json) pins this evidence. SAN-05 remains open: infinite-hardening initialization, yield entry, reversal events and the finite-step algorithm are deliberately not supplied by this fragment. Native builds/executable tests are held again following the latest Cortex report; no compilation was used for this investigation.

### SANISAND infinite-hardening products — 2026-10-31

The [derived finite-product formulation](docs/models/sanisand-2004-hardening-limit.md) avoids separately evaluating divergent `h` and `Kp` and supplies a one-sided zero-distance limit when the hardening numerator is positive. The [typed fragment](catalogue/source-audits/sanisand-2004-hardening-limit.json) and four Python test groups cover 120 finite-distance equivalence cases, zero-limit yield consistency, pressure scaling, overflow avoidance and explicit rejection of unresolved limits. This advances singular-limit analysis in SAN-01/03/05 without selecting reversal events or closing integration/reference gates. Independent review remains pending; no arbitrary cap is introduced.

### Cautious native SANISAND check — 2026-10-31

Following renewed user authorization, one standalone C++20 file compiled at `-O0` and ran successfully: 12 on-cone loading/unloading and zero/positive reversal-distance cases, 2,280 value checks and 6,840 strain-derivative checks. The [generator](tools/prepare_sanisand_native.py) prepares the fixture without compiling it; the [record](catalogue/investigations/sanisand-native-algebra-v1.json) pins inputs, compiler, tolerances and results. This supersedes the blanket native hold for cautious individual checks. The full OpenSees build remains deferred. SAN-05 still requires initialization, events and finite integration; these derivatives are strain columns of instantaneous algebra, not an algorithmic tangent.

### SANISAND elastic entry — 2026-10-31

An [exact elastic-path derivation and first-yield reference](docs/models/sanisand-2004-elastic-entry.md) now advances SAN-03/05. It retains current-density elasticity and explicitly inferred volume closure, with configurable signed event bracketing, a convexity argument and declared domain failures. Six new Python research test groups cover independent RK4 refinement, an analytical yield point, composition, rotation, units and unloading; all 15 SANISAND groups pass in the [record](catalogue/investigations/sanisand-elastic-entry-v1.json). Production common-engine integration, initialization, reversal memory, plastic continuation and independent review remain open; executable model counts are unchanged.

### SANISAND common-solver research material — 2026-10-31

A [26-component fixed-memory backward-Euler research definition](docs/models/sanisand-2004-fixed-memory-be.md) now executes original tensor equations through the existing common compiler/C++ solver without model-specific engine code. One small standalone native build passes 336 compression, extension and general-shear increments; interpreted residual checks and step-halving refinement pass in the [retained evidence](catalogue/investigations/sanisand-fixed-memory-be-v1/manifest.json). Four new Python groups establish source-rate consistency and research scope; all 19 SANISAND groups pass. Original cone-normal reversal and OpenSees parent trial-direction tests differ; this draft deliberately freezes memory and supports only the initial loading branch. SAN-03/05/06 remain open for original memory-event rules, yield splitting, rollback, independent reference histories and complete admission; public model counts are unchanged.

### SANISAND history domains and rollback — 2026-10-31

The research material now rejects nondeviatoric histories explicitly. A [seven-case native transaction investigation](catalogue/investigations/sanisand-transactions-v1/manifest.json) verifies pre-solve rejection of all three history fields, successful and zero trials, full parent restoration after two accepted substeps followed by failure, and exact repeated-trial equality. All 21 SANISAND Python groups pass. The original 336 native trajectories remain historical and pass interpreted checks under the strengthened domain. This advances SAN-03/05 rollback/domain coverage; reversal-memory events and full admission remain open.

### SANISAND parent-reset research variant — 2026-10-31

A [separate project variant](docs/models/sanisand-2004-parent-reset-be.md) now exercises existing generic parent resets with the complete tensor residuals. The [native evidence](catalogue/investigations/sanisand-parent-reset-v1/manifest.json) passes 896 cyclic increments, 18 cyclic resets, six zero trials and six failures restoring pre-reset memory after accepted internal work; 224 monotonic states match the retained fixed-memory run. Cyclic step-halving refinement and all 26 SANISAND Python groups pass. [Decision 0001](docs/decisions/0001-sanisand-parent-reset-research.md) explicitly separates this parent trial-direction policy from the original cone-normal rule and from full OpenSees equivalence. SAN-03/05/06 remain open for canonical events, independent references, mixed controls and Wasm; no public admission/count changes.

### SANISAND mixed-control research evidence — 2026-10-31

The unchanged common control solver now passes [898 native research cases](catalogue/investigations/sanisand-mixed-controls-v1/manifest.json): 896 cyclic increments under fixed-radial-stress or prescribed-q/zero-volume controls plus two independently derived elastic cases. Every controlled result matches direct material replay from the same parent; interpreted preparation/residuals, 18 resets, control constraints and endpoint refinement pass. All 30 SANISAND Python groups pass. The [dossier](docs/models/sanisand-2004-mixed-controls.md) separates control tolerance from material residuals and records scope. This advances SAN-03/05/06 and NUM-01/02/04 without supplying canonical source events, a complete-update tangent, failed-outer-control semantics or Wasm parity.

### Accepted-update linearization — 2026-10-31

An [experimental C++ update-linearization API](docs/UPDATE_LINEARIZATION.md) now differentiates the full accepted material update, including parent preparation, implicit residual solves and midpoint substeps, with partition/branches fixed. It preserves material success separately from tangent availability. A small native investigation, reproduced from the repository preparation command, passes 720 complete-update finite-difference and 228 independent analytical entries across the five public models, SANISAND research loading/reversal and synthetic reset/cutback cases; two native status assertions and 20 related Python groups pass in the [record](catalogue/investigations/update-tangent-v1/manifest.json). [Decision 0002](docs/decisions/0002-fixed-partition-linearization.md) defines local derivative scope. NUM-01/02 remain open for C/Wasm access, broader nonsmooth/time/control semantics, capacity and regression verification.

### Native update-linearization JSON interface — 2026-10-31

The [experimental C ABI/CLI endpoint](docs/UPDATE_LINEARIZATION_API.md) exposes accepted state and optional tangent with separate success flags, explicit Mandel layout, fixed-partition/branch policy and request provenance. Two small standalone builds and separate serial captures completed normally. All 21 API cases pass, including exact parity with eleven retained C++ matrices, singular-derivative success, rollback, malformed requests and unchanged integrate behavior. All 24 related Python groups pass in the [record](catalogue/investigations/linearization-api-v1/manifest.json). NUM-01/02 remain open for Wasm/browser execution, broader numerical regression and the existing time/control/nonsmooth derivative gates. No large external build or push was performed.

### Tangent directions and rotations — 2026-10-31

A [native follow-up](docs/TANGENT_GEOMETRY.md) reuses the verified binary for 49 serial requests, with no compilation. Seven directional sequences (288 state comparisons) pass the finest-step `1e-5` criterion; one coarse SANISAND discrepancy decreases about fourfold with each halving. Six same-partition rotations pass; IGS changes adaptive partition and remains a diagnostic, with explicit componentwise-controller limitations. All 29 related Python groups pass in the [record](catalogue/investigations/tangent-geometry-v1/manifest.json). This advances NUM-02 without closing native/Wasm, broader numerical regression, or NUM-03 configuration/provenance gates.

### Configurable incremental integration — 2026-10-31

The [shared incremental settings contract](docs/INCREMENTAL_SETTINGS.md) now exposes residual/rate tolerances, iteration/depth/substep limits and Newton backtracking through C++, additive C APIs and opt-in CLI provenance. Tangent replay and all material trials in laboratory protocols receive the chosen settings. Nominal substep caps are now exact, fixing previous boundary overshoot; other defaults are retained. Thirty settings cases and 21 unchanged default API responses pass, with synthetic rate/root/tangent refinement. The existing five-model native numerical program and all 33 related Python groups pass in the [record](catalogue/investigations/incremental-settings-v1/manifest.json). Small standalone builds completed normally. NUM-03 remains open for outer-control settings, global budgets, website use and native/Wasm verification; no large build or push occurred.

### Public browser numerical controls — 2026-10-31

The [laboratory settings integration](docs/BROWSER_NUMERICS.md) adds six numerical controls, exact engine-setting checks and export/import provenance with explicit legacy defaults. An isolated unoptimized Wasm/native build passes 17 new protocol/tangent/status pairs and the existing 25 protocol, four rollback, two rate and six IGS history checks; six related Python groups and pure JS validation pass. Browser checks verify custom replay, legacy defaults, invalid-input blocking and Reset. An existing missing `result-note` response target is restored and regression-checked. The [record](catalogue/investigations/browser-numerics-v1/manifest.json) pins evidence and toolchain limits. Public-model Wasm access advances NUM-01/02/03 and WEB-03/06; research/timed catalogues, complete release gates and hosted deployment remain open. CI is updated locally; nothing was pushed.

### Parallel source audits and Wu–Bauer extraction — 2026-10-31

Three bounded AI source audits of SANISAND-2004, VW96 and IGS97 support the existing core transcriptions in their inspected scope and record source conflicts and remaining domain/integration gaps in the [audit ledger](catalogue/source-audits/parallel-original-reviews-2026-10-31.json). They do not replace independent scientific review. The [Wu–Bauer original-paper dossier](docs/models/wu-bauer-1994-original.md) and typed instantaneous source fragment close its access gap, preserve unresolved printed sign/calibration conflicts, and provide independent Cartesian/axisymmetric algebra checks. Source identity/provenance is linked into the publication database; no public formulation is admitted. Source-path reproduction, domain decisions and the REV gates remain open. No native build or hosted publication was used for these audits.

### Ordered recorded-path engine — 2026-10-31

An [experimental JSON/Python/C++ recorded-path contract](docs/RECORDED_PATHS.md) now preserves ordered reversals and duplicate observations, with six general linear strain/stress constraints, explicit initial strain, immutable-parent stress-root trials, restart and accepted-prefix failure semantics. The reduced solve keeps prescribed strains fixed during all stress-root probes. Small serial native checks and contract tests are recorded in the [investigation](catalogue/investigations/recorded-path-v1/manifest.json), including the initial failed IGS root attempt. This advances NUM-04 and transaction coverage; C ABI/CLI consumption, Wasm/browser access, path-density studies and full experimental replay remain open. No source model is admitted or scientific-review gate closed.


### Native recorded-path JSON bridge — 2026-10-31

The [recorded replay interface](docs/RECORDED_PATHS.md#native-json-replay-command) now accepts a closed JSON run request through `atlas.cli replay`, validates it, and executes an additive C ABI via the native CLI. Temporary wire files support the full 5,001-knot contract without argument-size limits. Responses preserve exact requests, request hashes, resolved numerical settings and accepted-prefix failure semantics. The [evidence](catalogue/investigations/recorded-replay-api-v1/manifest.json) retains 16 native responses and 46 unchanged existing-command comparisons, plus analytical controls, all-five-model restart/direct replay, invalid wire and command tests. One small serial native target build completed normally. NUM-04 remains open for Wasm/browser access, path-density studies and full experimental replay. No source-review or scientific-validation gate is closed.


### Browser ordered recorded replay — 2026-10-31

The source-linked **Recorded paths** view imports the recorded-run contract, executes it in a cancellable Wasm worker, plots all six Mandel stress/strain components by ordered coordinate, and exports full requests/results or committed observations. Sixteen fresh public native/Wasm pairs pass, including the 5,001-record bound and three failure branches. Seventeen existing settings/tangent pairs and the 25 protocol, four rollback, two rate and six IGS history regressions pass. Browser file import, component selection, sources and failure-prefix export/native replay equality are retained in the [record](catalogue/investigations/recorded-browser-v1/manifest.json). The small unoptimized Wasm build completed normally. NUM-04 advances without closing path-density studies, source-matched nonlinear references or full experimental replay. Measurement overlays/conversion remain separate, and nothing was deployed.


### Recorded caller-path refinement — 2026-10-31

An [explicit refinement-study contract and command](docs/RECORDED_REFINEMENT.md) now preserve original observations while inserting declared piecewise-linear target knots, independently of internal material tolerances. Two native studies retain 60 runs (54 successful, six failed), including mixed controls, all three shears, reversals/duplicates and separate plastic loading/unloading cases. Comparisons distinguish persistent state from increment-local multipliers; failed finest levels are never replaced by selected successful levels. The [record](catalogue/investigations/recorded-refinement-v1/manifest.json) includes full responses, corruption checks, analytical elasticity, table and figure. Coarse IGS97 and plastic Drucker–Prager failures remain explicit; plastic Cam-Clay still changes by about 4.43 kPa at the finest pair. This advances NUM-03/04 with resolution evidence without declaring convergence, fixing numerical defaults, closing scientific-review gates or replacing full experimental replay. No new compilation or deployment occurred.


### Recorded resolution mechanisms and continuous reference — 2026-10-31

The [resolution diagnosis](docs/RECORDED_RESOLUTION_DIAGNOSIS.md) separates the six retained coarse failures into IGS97 initial-history depth exhaustion and Drucker–Prager singular apex seeds. Three serial native material calls confirm the predicted IGS depth thresholds at unchanged tolerances. An exact piecewise isotropic reduction of the declared continuous Cam-Clay equations now compares loading, yield entry, unloading, duplicates and reloading against the retained path. Factor 64 reduces maximum pressure/pc error from 4.50 to 2.26 kPa; tightening factor-32 residual tolerance to `1e-12` changes no output. The [evidence](catalogue/investigations/recorded-resolution-diagnosis-v1/manifest.json) preserves requests, responses, diagnostic scripts and limits. This advances NUM-03/04 and project-equation analytical coverage; generic mixed-control globalization, accuracy-controlled implicit integration, source-matched references and experimental replay remain open. No solver/model defaults, public admission status, compilation or deployment changed.


### Bounded mixed-control restarts — 2026-10-31

The [opt-in recorded control restart](docs/RECORDED_RESTARTS.md) searches only the feasible strain nullspace after a singular finite reduced Jacobian. Every exploratory material call starts from the immutable parent and consumes the existing global trial budget; a failed search preserves the committed prefix. The additive C/Wasm endpoint, CLI flag, closed JSON schemas and Python/browser modules preserve explicit policy/provenance while legacy responses remain unchanged. All three previously failing coarse Drucker–Prager paths now complete under the enabled policy, with independent scalar return/density checks. The [record](catalogue/investigations/recorded-restarts-v1/manifest.json) retains enabled/disabled runs, bounded-search/budget failures, synthetic persistent-history checks and native/Wasm parity. This advances NUM-03/04 without claiming general root convergence, continuous stress control, constitutive accuracy control, source-matched validation or experimental replay. Small serial builds completed normally; no defaults changed and nothing was deployed.


### Ordered experimental replay bridge and parallel source queue (2026-10-31)

The [normalized drained replay bridge](docs/EXPERIMENT_REPLAY.md) connects explicit p/q and axial-strain observations to the ordered common solver without sorting, trimming or deduplicating. All parameters/history are named explicitly, source/configuration/model/request hashes are retained, and conflicting source void ratio requires an explicit override explanation. The synthetic elastic fixture verifies stress, volume and density at every observation; a local illustrative KFS-TMD1 pipeline replay completes all 421 observations without publishing permission-held measurements. This advances NUM-04/BENCH-03 infrastructure; reviewed physical mappings, initialization, applicable published parameter baselines, experimental comparisons and the full BENCH gates remain open.

The [parallel source-work queue](docs/reviews/parallel-source-queue.md) records bounded Terracotta, PM4Sand and remaining SoilModels triage. It identifies exact source/variant and capability gaps before implementation. Near-term independent packets are PM4Sand3D flow algebra, its state/lagged-history inventory, Terracotta initialization and boundary/creep evidence, and clay/generalized-IGS source acquisition. These AI technical reviews do not close independent scientific review or increase executable-model counts. Native verification remains serial; no reference DLL or external Fortran build was run for this milestone.


### PM4Sand3D flow and typed initialization recipes (2026-10-31)

The [PM4Sand3D flow fragment](docs/models/pm4sand3d-1.0-flow.md) adds Eqs.35–37 to the pinned surface algebra, with supplied D, typed terms, independent Cartesian/rotation/triaxial checks and explicit Section2/algorithm discrepancies. It supplies no full state/history update or new executable model. Next work remains the complete state/event/lagged-history and initialization inventory.

The [experimental initialization contract](docs/INITIALIZATION_RECIPES.md) separates typed guarded initialization from constitutive integration. A source-linked Terracotta Figure1 recipe resolves the positive stable root from explicit total stress/phi/Tm/rates, validates model domain and initial-history checks, and exports hashed fields for the common timed driver. Independent forward/inverse algebra, parameter changes, signed shear, a second tensor-state model, one-sided native rate jumps and exact zero-rate temperature decay are checked. This advances REP-03/TC-03 infrastructure and closes the fixed-default-pressure initialization gap; general nonlinear/browser initialization, full source review and independent Terracotta creep remain open. Model counts and scientific review statuses are unchanged.

The [combined investigation](catalogue/investigations/initialization-and-pm4-flow-v1/manifest.json) retains the passing 34-test run, hashes and native Terracotta boundary/decay response using the existing matching research binary. No new native build was required.


### Prepared Terracotta creep and PM4Sand3D history inventory (2026-10-31)

The [Terracotta creep reference](docs/TERRACOTTA_CREEP_REFERENCE.md) adds separate scalar Figure1 algebra, RK4 preparation/hold refinement and midpoint cross-checks without the Atlas interpreter, native integrator or disputed author mixed-control residual. Nine native runs cover compression/extension/isotropic preparation and three tolerances; all non-roundoff state/strain/rate/elastic-stress channels improve, with complete matrix/diagnostic/provenance validation. It advances TC-05 numerical evidence; frozen preparation, positive-Tm inversion, external author-matched histories, scientific source review, new-case Wasm and clay validation remain explicit limits.

The [PM4Sand3D inventory](docs/models/pm4sand3d-1.0-history.md) records 30 source-located field groups and caller-step phases, separating physical history, lagged coefficients, caches, preparation flags and host/subzone workspace. Raw named tensor storage alone totals54 slots; larger allocation scenarios are documentary ledgers, not a proven minimal state count or permission to raise engine capacity. Alias, initialization/sign, fabric-product and update-order conflicts remain open. Next schema work must define typed lifetime/transaction/context semantics before a full source-matched model update.

### 2026-10-31 — Prepared Terracotta creep across native/Wasm

All nine frozen-preparation creep requests now pass native/Wasm C-ABI parity and independent scalar-reference assessment for each backend. Retained evidence, corruption regressions and CI commands are linked in [the creep study](docs/TERRACOTTA_CREEP_REFERENCE.md#nativewasm-prepared-creep-verification). Existing builds were reused locally. This closes the Wasm gap for this bounded study; full journal reconciliation, external experimental comparisons, scientific review, browser creep interaction and full-3D model admission remain open.

### 2026-10-31 — History and transaction design

The [experimental history contract](docs/HISTORY_TRANSACTIONS.md) turns the PM4Sand3D inventory into explicit storage classes, immutable ordered phase snapshots, atomic reset/advance/rollback, caller-step lag and restart lineage. Its [machine-readable example](proposals/pm4sand3d-history-contract.json) is deliberately non-loadable, retains 19 source blockers and leaves every PM4 update phase disabled. Eight acceptance gates specify separate Python validation/interpreter work, transaction fixtures, legacy compatibility, source resolution and eventual native/Wasm evidence. No runtime API or 32-component capacity change is made.

### 2026-10-31 — SANISAND event decision review

The [source-located decision packet](docs/reviews/sanisand-2004-decision.md) separates the original continuous law, pinned OpenSees policies and the two Atlas research algorithms for initialization, first yield, reversal, zero-distance hardening and rollback. The paper-local cone-normal and parent trial-direction guards demonstrably differ at an existing retained peak. Canonical reset semantics remain open pending the referenced loading-process source and distinguishing Python fixtures; no public model or review status changes.

### 2026-10-31 — HCA recording and accumulation contract

The [HCA-2005 contract draft](docs/reviews/hca-2005-contract.md) specifies one recording cycle and one accumulation block, source-located amplitude/history equations, companion-law handoffs and per-cycle evolution. It preserves conflicting recording-filter rules and the full 9D versus symmetric 6D polarization-initialization issue. Next independent checks are sampled-loop amplitudes and scalar history composition; a general cycle-count API, full closure and executable admission remain open. No source document was redistributed and no build was run.

### 2026-10-31 — Typed Python history reference and SANISAND event fixtures

The [experimental history reference](docs/HISTORY_REFERENCE.md) implements a separate versioned program/snapshot contract with scalar/symmetric-tensor SI checking, immutable phase bindings, simultaneous writes, preparation ancestry, strict negative guards, finite intermediate arithmetic and full-parent rollback. Fourteen arithmetic regression groups cover preparation/modes/lag/clock, late failure, serialization, repeated candidates, invalid inputs and budgets. This advances HIST-G2/G3 without changing legacy model semantics, native APIs or capacity. Source-blocked PM4 updates, host reductions, coupled solver adapters and native/Wasm parity remain open.

The [SANISAND event fixtures](docs/SANISAND_EVENT_FIXTURES.md) retain portable Python-only entry brackets, an independent constant-volume analytical entry, peak/oblique guard decisions and regular zero-distance hardening comparisons with dependency/input hashes. Four fixture groups pass; frozen-state selection is explicitly not a sequential trajectory or partition-convergence result. Canonical loading-process/event semantics, plastic continuation and source-matched external histories remain open.

### 2026-10-31 — Legacy snapshot bridge and HCA arithmetic diagnostics

The [legacy snapshot bridge](docs/HISTORY_LEGACY_BRIDGE.md) preserves existing full-integrator reset semantics rather than translating dimensional/eager legacy expressions into the new phase language. Seventeen bridge/callback groups cover complete state/strain transport, parameter wire-order identity, all five public layout roundtrips, copied original-parent calls, restart, trial failure and binary/request echoes. Four small serial native cases cover rate, residual, cutbacks and late rollback. The stale fixture binary was rejected, then one single-job `atlas_time_solver` target rebuild completed normally. No C++ API/model/default changes were made. Native/Wasm phased-history integration, timed/coupled adapters, host reductions and source-blocked PM4 updates remain open.

The [HCA diagnostics](docs/HCA_DIAGNOSTICS.md) implement sampled-loop farthest-pair/projection amplitudes and fixed-amplitude scalar history only. Seventeen tests include independent Cartesian/Mandel covariance, harmonic/rank oracles, sampling refinement, composition and high-precision extreme-range checks; source-bound evidence retains errors and policies. Intermediate overflow/underflow is handled without rejecting representable final increments. This does not implement polarization, stress/density evolution, companion handoff or a cycle-count constitutive solver; both documented source conflicts remain unresolved.

### 2026-10-31 — Shared phased-history runtime and parallel source acquisition

The [experimental C++/Wasm history runtime](docs/HISTORY_RUNTIME.md) compiles the separate typed phase contract and verifies 23 arithmetic cases against Python through the native CLI and real Wasm C ABI. Canonical sorted wire layouts bind positional values to the program hash independently of JSON key order. Review also closed Boolean-arithmetic inference and non-binary64 integer restart ambiguities in the new contract; the legacy model DSL is unchanged. Checks cover finite executed intermediates, lazy branches, preparation/restart, strict guards, late rollback, modes and counter exhaustion. Small serial native/Wasm builds completed normally. This advances generic runtime infrastructure toward HIST-G8 without closing its PM4 source/model gates, coupled controls, internal subdivisions, host reductions or durable lineage. No executable-model count or scientific-review flag changes.

Parallel primary-source packets now pin [2013 clay hypoplasticity and the separate 2014 dependency](docs/reviews/clay-2013-2014-source-packet.md), [generalized IGS2024 with its exact HP+ASBS host](docs/models/hypoplastic-generalized-igs-2024-source.md), and the [1986 SANISAND loading-process access gap](docs/reviews/sanisand-1986-loading-process.md). Next bounded source tasks are independent clay rate/Cartesian oracles and GIS/host-action fragments. The 2014 and 1986 full texts remain unacquired; neither is replaced by a related paper. No copyrighted source document or reference code is bundled.

### 2026-10-31 — Clay2013 and supplied-host GIS source-rate algebra

The [clay2013 source-rate fragment](docs/models/clay2013-source-rate.md) now represents the complete zero-spin instantaneous stress/density law with explicit parameters and units. Independent Cartesian fourth-order contractions and180-digit invariant/limit fixtures verify the reduced Mandel algebra. A scale-free invariant quotient and double deviator projection before normalization resolve near-isotropic cancellation; comparisons use actual supplied binary64 values. Six rate groups and five Decimal/integrity groups cover isotropic loading/unloading, noncoaxial rates/rotation, homogeneity, source sign/units, limits and conservative-domain rejection. Coupled integration, initial-state/ASBS policy, singular-boundary treatment, final-version reconciliation and source-matched paths remain open.

The [supplied-host GIS2024 fragment](docs/models/gis-2024-supplied-host-rates.md) adds typed continuous h/Omega/stress rates with explicit E,m,C,S,f, independently checked Cartesian covariance/sign/branch algebra and zero-direction continuation. Nine groups pin40 random cases, full symmetric memory, reversal limits, independent gamma_Omega and the nested exponent. A reviewed convex Eq39 rewrite preserves k=1 at large-modulus fully mobilized loading. Full HP/extracted-ASBS host actions, preparation, coupling and integration remain open. Candidate source links are exported in the database/browser catalogue; executable statuses/counts are unchanged. These Python-only algebra checks do not supply native/Wasm model or experimental validation.


### 2026-10-31 — Coupled clay research target and exact trajectories

The [isolated clay research target](docs/models/clay2013-research-integration.md) now uses the common schema/compiler/engine for stress6+e. An independent Decimal closed form verifies33 isotropic loading/unloading/reversal trajectories at three density scales, tolerance refinement and caller partitioning. Native and real-C-ABI Wasm matrices cover115 paired updates, with transactional domain/budget failure and persistent-module recovery probes. Numerical stress weighting is explicit and separate from the fixed source reference pressure. Code, source and retained evidence are pinned; the candidate remains non-executable in the public atlas.

The [initialization review](docs/reviews/clay2013-initialization-policy.md) records an outward ASBS-rate witness, ruling out a universal hard ASBS stage barrier while leaving physical outside-ASBS initialization unverified. Next clay gates are nonisotropic finite paths, boundary arithmetic, source-matched preparation/experimental comparisons and scientific review. In parallel the selected HP/extracted-ASBS host-action packet for GIS is ready for integration and independent root review; full GIS material coupling remains open. These steps advance the shared engine and source database; catalogue-wide coverage, the paper and public model admission remain unfinished.


### 2026-10-31 — Full GIS rate schema, nonisotropic clay paths and parallel queue

The [isolated HP/extracted-ASBS+GIS research definition](docs/models/gis2024-research-rates.md) now represents all14 continuous states in the existing schema/compiler. Independent Cartesian/dense host and full-rate references match38 instantaneous cases through Python, native C++ and real-C-ABI Wasm. Source/sign, spherical precision and positive-factor/suppression underflow reviews are retained. A second boundary review found and resolved an inconsistent tolerance shell: the full pairing now requires computed norm(h)<=R with no projection. Finite coupled GIS histories, integration/stage/rollback policy, physical preparation and scientific/experimental admission remain open; public executable counts do not change.

The [clay nonisotropic study](docs/CLAY2013_CARTESIAN_PATH_REFERENCE.md) extends finite-path evidence to two full-tensor paths and rotated companions, at three tolerances:12 trajectories/36 explicit updates per backend. Independent Cartesian RK4 grids and a64-step review support refinement; Wasm states are actually chained and independently reassessed. The reviewed comparator now checks pinned source/code receipts and fresh complete reference replay, rejecting forged endpoint/statistical evidence. These successful paths do not close nonisotropic failure recovery, partition/boundary/parameter sweeps, physical initialization, published/experimental comparisons or scientific review.

The refreshed [parallel source queue](docs/reviews/parallel-source-queue.md) accounts for all27 candidates. Independent source-ready batches are PM4Sand3D old/new chronology, HCA filter/polarization reconciliation and Wu–Bauer AppendixI lineage closure; the latter is outside the32-entry catalogue count. First new-identity acquisition priorities are clay barodesy2017, exact ISA2020 and NorSand1993. Source-only agents stage isolated packets; shared schema/solver integration and cautious native builds remain serial. The paper and public admission gates remain unfinished.


### 2026-10-31 — PM4Sand3D old/new chronology reconciliation

The [bounded manual review](docs/reviews/pm4sand3d-1.0-order-reconciliation.md) now distinguishes shared caller-step D/Kp lag from later zone candidates, anchor snapshots, fabric updates and final publication. It records the printed Eq27 strict versus Eq47 nonstrict previous-anchor condition and the zero true-anchor denominator after coincident initialization/reset; apparent-anchor construction and the evaluated branch remain unresolved. Retained synthetic ordering witnesses illustrate consequences without selecting a PM4 algorithm or exercising the runtime. Exact source/code pairing, reversal-stage operands, late fabric/anchor read edges and update/initialization branches must be resolved before an executable history kernel; storage/runtime changes do not close these source gates.

### 2026-10-31 — GIS interior finite paths and next source packets

The [GIS coupled research integration](docs/models/gis2024-research-integration.md) now retains20trajectories/204updates per native and Wasm backend against independent Cartesian RK4 references, tolerance/caller-partition refinement, exact volume checks, full-state rollback after partial progress and persistent Wasm recovery transcripts. Corruption checks reject invalid intermediate memory, altered diagnostics/settings, missing matrices and broken chains. Memory-origin/saturation/boundary integration, wider paths, physical preparation and experimental/scientific review remain open; no public admission follows.

Exact primary PDFs for [clay barodesy2017](docs/reviews/barodesy-clay-2017-source-packet.md) and [ISA2020](docs/models/hypoplastic-isa-2020-original.md) are acquired privately and source-linked in the catalogue. Independent [barodesy algebra review](docs/reviews/barodesy2017-independent-review.md) supports an explicitly named body-law regular-domain zero-spin research variant while retaining the body/appendix discrepancy. The next shared capability is a [dimensionless symmetric matrix exponential with full derivatives](docs/design/symmetric-expm-contract.md), followed by source-declared branches and instantaneous body-law checks. The operator design is not an implemented or validated kernel. ISA printed-equation/host/hardening ambiguities remain explicit; no silent repair is selected.

Three parallel acquisition reviews are delivered: [NorSand1993 access gap](docs/reviews/norsand-1993-source-packet.md), [clay2014 anisotropy manuscript](docs/models/hypoplastic-clay-2014-original.md) and [PM4Silt v1 manual/release](docs/reviews/pm4silt-v1-source.md). Clay anisotropic-action and PM4Silt in-plane algebra checks are retained; a printed clay IGS normalization conflict is asserted as an unresolved source discrepancy, not repaired. NorSand still requires original equation images. One integration owner handles shared code and serial native builds; no later-version substitution is made. The full atlas, public model coverage, paper and experimental programme remain unfinished.

### 2026-10-31 — Checked symmetric exponential

The [dimensionless symmetric matrix exponential](docs/SYMMETRIC_EXPM.md) is implemented in Python and generated C++ with all-six-direction Fréchet derivatives, sticky checked failures and transactional history/material rollback. Independent100/160digit reference evidence covers44matrices and full6×6Jacobians through native and Wasm,29context checks and23invalid probes with persistent Wasm recovery. The implementation support is computed Frobenius<=64; no exact boundary-invariance or small-mode relative-accuracy guarantee is claimed. Historical source receipts are preserved through bound [immutable source archives](docs/IMMUTABLE_SOURCE_ARCHIVES.md), not rewritten to current hashes.

Next is the [source-located barodesy body-law implementation checklist](docs/models/barodesy2017-implementation-checklist.md): an isolated seven-state zero-spin instantaneous research fragment and independent Cartesian rate oracle, followed by finite-path studies. Body/appendix critical-void-ratio differences, numerical branches and zero-loading tangent policy remain explicit. No public model is promoted; catalogue coverage, experimental validation and manuscript/release gates remain open.


### 2026-10-31 — Stable scalar logarithm and parallel implementation lanes

The [checked scalar log1p operator](docs/SCALAR_LOG1P.md) now supports stable near-hydrostatic Barodesy algebra through the shared Python/C++ DSL and transactional history compiler. Independent500/650digit evidence covers38binary64inputs, all38Jetchannels,6×38schema derivatives,27contexts and10invalid cases per backend, including persistent Wasm recovery. Native/Wasm discrepancies stay within the predeclared four-step componentwise budget; signed zero and lost subnormals are checked explicitly. Historical source receipts remain immutable through additional bound archives.

Parallel agents stage independent references, source/model fragments and review/testing packets; one integration owner serializes shared-code edits and native/Wasm builds. The Barodesy seven-state body-law zero-spin draft matches111independent Python instantaneous-rate cases. Its native/Wasm rates, constitutive derivative checks and finite paths still require integration and review; neither the public executable catalogue nor scientific admission is expanded here.


### 2026-10-31 — Barodesy instantaneous rates and regular material derivatives

The [isolated seven-state Barodesy body-law implementation](docs/models/barodesy2017-research-rates.md) now runs through the shared schema/compiler. Fresh independent Cartesian80/140/160digit exponential references verify111canonical rates, three support scales and16rejection/recovery cases in native C++ and persistent Wasm. A review-found invariant determinant cancellation is fixed by a declared normalized Cartesian64-epsilon interior guard; tests retain indefinite and ill-conditioned witnesses. Exact zero channels, void closure and component stress envelopes supplement the primal norm budget.

All21regular7x13 material Jacobians match independently refined differences and analytical void/homogeneity/rotation/density/pressure-scaling identities in both backends;20invalid/recovery pairs include exact zero and hydrostatic derivative exclusions. Worst final scaled finite-difference discrepancy is below6.2e-11 against the fixed2e-8 budget. Raw/partial reports, source bindings, build receipts and corruption tests are retained; original historical evidence remains immutable.

The [isotropic reference and study design](docs/reviews/barodesy2017-isotropic-reference.md) prepares nine NCL compression paths, explicitly measuring rounded-initial-state corrections and separating reversal/off-NCL scalar diagnostics. Next are hydrostatic derivative-limit review and actual common-engine finite paths with refinement, partitioning and rollback. Near-hydrostatic/zero tangents, general spin, source differences, physical preparation, experimental/scientific review and public admission remain open. Catalogue-wide source completion, the website release and paper remain unfinished.
