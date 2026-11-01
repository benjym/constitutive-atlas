# Constitutive complexity and predictive capability paper plan

Planning date: 30 October 2026.

The first follow-through after the collection expansion comprises a [paper-side source reconciliation](study/source_reconciliation_2026-10-31.md), updated VW96/IGS annotations and a [proposed Ottawa cyclic protocol](study/ottawa_cyclic_protocol.md) with a reproducible metadata map. Remaining tasks are source-document and specimen/control review, exact model admission and a development pilot before the cyclic study can be frozen.

The [31 October collection refresh](study/collection_refresh_2026-10-31.md) updates the evidence and task priorities after the atlas expansion. Reconcile the newly available original-source reviews first, assess the SANISAND research policies separately from constitutive identities, and scope an Ottawa F65 cyclic panel alongside the existing KFS and second-sand work. The refresh does not change the study's admission rules or final-evaluation reservations.

Development progress is recorded in [DEVELOPMENT.md](DEVELOPMENT.md). The local data audit, competing-source metadata, six scoped model annotations, three-model pressure/density pilots, matched-count calibration-design contrast, recorded-order sensitivity diagnostic and fixed-parameter compression sensitivity are implemented under `paper/`. Generated manuscript tables now include the compression initialization/convention comparison. They support M1 and M2 below; the frozen study and later milestones remain open. Independent scientific review, additional admitted formulations and broader experimental evidence are still required.

## Scientific objective

Determine which constitutive ingredients improve geomechanical prediction, under which loading conditions, and at what calibration cost. The intended audience is researchers developing, calibrating, and selecting constitutive models.

Working manuscript title: **What does constitutive complexity buy? Predictive capability and calibration requirements across geomechanical models.** The final title should name the benchmark material domain if the predictive study concentrates on sand.

The paper will combine a systematic survey of a future 50+ formulation collection with a controlled computational benchmark of a smaller, scientifically comparable subset. Its contributions are a traceable map of mechanisms and calibration requirements, evidence about predictive benefit versus complexity, and a reproducible comparison protocol. The number of models supports these contributions; it is not the scientific conclusion.

This is a systematic model survey and computational benchmark. Reserve the term meta-analysis for any later synthesis that actually combines compatible effect estimates from independent studies.

## Relationship to the current draft

The original representation, solver, verification and published-parameter transfer draft is preserved in `article/implementation-note.tex`. Its demonstration remains development evidence.

`article/main.tex` now organizes the working paper around scientific questions, comparison methods and generated development results. Counts, tables and the calibration-design figure regenerate from source-pinned annotations and frozen run records. This is a development manuscript; independent review, the broader survey, study freeze and final evaluation remain open. The 50+ collection is a future survey target. Regenerate final coverage counts from a frozen release manifest rather than adopting a changing repository count.

## Research questions and primary outcomes

| Question | Comparison | Main evidence |
| --- | --- | --- |
| RQ1 Which mechanisms and calibration requirements distinguish the collection? | All admitted survey formulations | Capability matrix, parameter roles, state dimensions, and lineage |
| RQ2 When does additional complexity improve prediction? | Comparable models under the same calibration information | Held-out error versus independent fitted constants, state complexity, and calibration cost |
| RQ3 Which calibration experiments improve transfer? | Nested data packages for each eligible model | Prediction versus data curves and parameter and prediction uncertainty |
| RQ4 Do extensions improve their intended behaviours? | Reviewed parent and extension pairs | Paired changes in target feature error, other responses, calibration effort, and failure rate |
| RQ5 Which experiments distinguish apparently equivalent models? | Models with similar calibration fit | Loading paths with disagreement exceeding plausible parameter uncertainty |

RQ1 to RQ3 form the core paper. RQ4 is included when credible pairs are available. RQ5 is an exploratory extension unless the core study leaves enough experimental coverage and analysis capacity. Do not make five complete studies prerequisites for one paper.

Hypotheses to test include diminishing returns from extra complexity under conventional loading, greater benefit from memory or fabric mechanisms under reversal, and improved transfer from complementary calibration test types. Contradictory or null findings remain publishable outcomes. Do not write these hypotheses as anticipated conclusions.

## Scope and model admission

### Broad survey

Survey 50+ distinct, source-pinned formulations across the supported atlas domains. Keep publications, formulations, implementation variants, and parameter sets as separate entities. Record exact parent relationships; a parameter set or numerical integration scheme is not another constitutive formulation. Count a failure criterion only as a criterion unless stiffness, flow, and evolution laws define a complete model.

Use the research charter's search and screening protocol and the paper's [development search and screening records](study/survey_protocol.md). The eight-theme pilot and assisted title decisions now exercise that process; they do not complete the survey. Publish search dates, inclusion and exclusion rules, unavailable-source decisions, and counts. The executable subset may be biased toward accessible sources and the language's capabilities; describe that selection explicitly. An atlas census does not establish the prevalence of a model in engineering practice or the completeness of the literature.

### Focused predictive benchmark

Provisional primary domain: saturated sand under monotonic drained and undrained loading, followed by unloading and cyclic loading where supported. Start with Karlsruhe fine sand because an ingestion path exists. Add a second independently documented sand dataset if feasible; without it, conclusions concern loading and state transfer on the tested material, not generalization across sands.

Aim for approximately 8 to 15 benchmark formulations spanning useful baselines, distinct families, and parent–extension pairs. This is a workload estimate, not a quota. Choose the subset by domain overlap, source review, usable data, and independent numerical evidence before examining comparative performance. Do not force clay, rock, rate-dependent, or cycle-averaged models into a sand leaderboard. Use separate task panels for later domains.

Admission to the predictive benchmark requires a pinned formulation and source locators, reviewed equations and conventions, initialization rules, a declared applicability domain, analytical or refinement checks, and an independent reference comparison where available. Record absence of independent reference evidence as a qualification. Apply admission criteria before fitting; retain all failures of admitted models in the results.

## Survey metadata

Store a paper-specific annotation table keyed to authoritative atlas model IDs; do not create competing model definitions. Every literature-derived annotation needs a source locator and review status.

| Category | Required fields |
| --- | --- |
| Identity | Model ID, exact variant, publication, year, parent IDs, source and review status |
| Applicability | Material, drainage or coupling assumptions, kinematics, rate dependence, pressure and state restrictions |
| Framework | Mathematical family, yield and flow structure where relevant, evolution and memory mechanisms |
| Mechanisms | Dilatancy, critical state, fabric, small-strain response, reversal memory, bonding, damage, viscosity as applicable |
| Material constants | Total declared, independent fitted, measured or externally fixed, constrained or derived; physical roles, units, bounds and sources |
| State | Scalar and tensor variables, independent components, initialization measurements and preparation history |
| Calibration | Required test types, recommended sequence, specialized measurements, assumed or fitted initial states |
| Evidence | Claimed capabilities, experimentally demonstrated capabilities, benchmarked capabilities, and known limitations |

Count independent state components consistently with constraints and symmetry, separately from implementation storage size. Treat numerical tolerances and regularization settings separately from material constants. Record estimated initial-state quantities as fitted nuisance quantities rather than hiding them from the calibration burden. Do not equate parameters solely because their symbols match.

## Experimental and calibration protocol

### Data audit and evaluation units

The [curated-data feasibility audit](study/data_feasibility.md) now checks minimum fields in the shared public collection without admitting it to the benchmark. The immediate KFS characterization/compression evidence and unassigned provider series are recorded in [kfs_characterization.json](study/kfs_characterization.json). Resolve these same-material inputs before treating unrelated compression curves as calibration evidence.

Before fitting, audit material identity, preparation, consolidation history, initial effective stress, density or void ratio, strain and stress conventions, drainage, loading control, and channel uncertainty. Resolve missing TMU initial void ratios from original evidence or exclude those tests from analyses requiring them. Record missingness explicitly.

Define admissible intervals before looking at model errors. Account for specimen nonuniformity and localization when using large-strain measurements to judge a homogeneous material-point law. Preserve loading order and reversal history. Use phase-aware resampling for cyclic data and uniform strain grids only on suitable monotonic segments.

The basic evaluation unit is a whole physical test, with replicate specimens and related preparation batches identified. Do not split adjacent recorded samples between calibration and validation. Use test or material blocks for uncertainty estimates; thousands of samples along one curve are not thousands of independent observations.

### Frozen splits and data packages

Reserve a final evaluation pool before tuning objectives, optimizers, parameter bounds, or model selection. Use development tests for those choices. Within the development data, use grouped validation to finalize the protocol. Record that publicly available experiments constitute a frozen held-out evaluation, not genuinely undisclosed blind data.

Construct feasible nested calibration packages from the remaining tests:

| Package | Information supplied | Intended question |
| --- | --- | --- |
| C1 | One declared drained triaxial test | What can a minimal programme constrain? |
| C2 | Additional drained tests across pressure and density | Does state coverage improve transfer? |
| C3 | Add compression and unloading tests | Does complementary stiffness and compression information help? |
| C4 | Add undrained tests | Does pore-pressure information improve prediction? |
| C5 | Add cyclic tests | Does reversal information constrain memory and accumulation? |

Freeze actual test IDs and counts after the audit. Every package uses the same untouched final evaluation pool, whose members never migrate into a later calibration package. Where data permit, repeat package construction using prespecified alternative test subsets to separate test-selection effects from information volume. Never create an impossible package solely to preserve this table.

Label evaluation tasks separately: interpolation within observed states; transfer to held-out pressure or density; transfer to a different loading path; and transfer to another material after a separately declared calibration programme. Holding out a material without recalibration answers a different question and should not be mixed with ordinary parameter transfer within one material.

### Calibration controls

Use one material parameter set per model, material, and calibration package across specimen states. Specimen-specific initialization follows measured preparation and state information. Reproduce a source-published parameter baseline before optimization where one exists; it is a separate track from controlled calibration.

Freeze parameter transformations, bounds, constraints, measured constants, state initialization, objective channels, scales, weighting, algorithms, seeds, stopping rules, and budgets. Use a common baseline optimizer and multistart protocol, with a declared alternative or larger-budget sensitivity study on a representative subset. Report both evaluation counts and wall time; neither alone establishes equal opportunity across models. Label optimization that reaches a budget limit without convincing convergence.

The primary comparison holds calibration information constant. A secondary data-rich comparison can assess each formulation under its recommended experimental programme, but must expose the extra information supplied. Estimate run counts and compute cost from the pilot before fixing full-study replication.

### Metrics and uncertainty

Report separate errors for stress, volumetric strain, and pore-pressure response, using task-specific channels. Add prespecified feature errors such as peak stress ratio, dilation onset, unloading stiffness, cyclic accumulation, and cycles to a declared liquefaction threshold. Define thresholds and treatment of unreached or censored events before running the study.

Choose channel scales from physical reference quantities or documented measurement uncertainty. Freeze them before final evaluation, document the weighting hierarchy across points, channels, tests and tasks, and report sensitivity to reasonable alternatives. Keep physical-unit errors alongside normalized summaries. Never normalize using the candidate model's own predicted amplitude.

Use held-out curve error and declared target-feature errors as primary outcomes within each task. Summarize paired per-test differences, variability across calibration seeds and data subsets, and uncertainty across experimental blocks when sample sizes support it. Distinguish optimizer variability from experimental variability and from parameter uncertainty; multiple optimizer seeds alone do not quantify the latter. Use parameter profiles or resampling on selected models where feasible. Avoid confident intervals from very few independent tests.

Report declared, fitted, and effectively constrained parameter counts separately. Sensitivity rank depends on scaling, parameterization and data; it is a diagnostic, not an intrinsic complexity score. Prediction uncertainty can remain small despite uncertain individual parameters.

### Numerical failures and computational cost

Distinguish outside-domain tasks, absent data, unimplemented controls, calibration failures, and attempted integration failures. For attempted tasks, show completion rate and conditional accuracy together, including paired completed-test comparisons. Do not silently drop failures or invent an arbitrary penalty as the sole ranking rule.

Compare runtimes on declared hardware and builds at verified numerical accuracy. Record tolerances, refinement behaviour, substeps, iterations and failures. The shared engine reduces implementation differences but may favour some equation forms; numerical cost and robustness describe the tested implementation and solver combination. Common tolerances alone do not guarantee comparable numerical error.

## Analysis and figure plan

| Output | Content | Scientific purpose |
| --- | --- | --- |
| Figure 1 | Model lineage with a mechanism and evidence matrix | Explain the collection and its benchmark subset |
| Figure 2 | Parameter roles, independent fitted counts, state components, and required test types | Describe practical complexity without reducing it to one number |
| Figure 3 | Held-out error versus fitted constants, with calibration cost and completion rate | Identify task-specific Pareto frontiers |
| Figure 4 | Held-out error versus calibration package, with variability | Quantify the value of additional experimental information |
| Figure 5 | Paired parent–extension changes in target and other errors | Test the benefit and cost of added mechanisms |
| Figure 6 if supported | Behavioural similarity and loading paths that separate models | Suggest discriminating experiments |
| Table 1 | Benchmark model identities, intended domains, and evidence status | Establish comparable scope |
| Table 2 | Materials, preparation, test coverage, splits, and missing data | Establish the experimental basis |
| Table 3 | Task-specific accuracy, calibration requirements, completion and cost | Provide a usable scorecard |

Reduce or combine figures after the pilot to avoid repeating evidence. Pareto status should be accompanied by uncertainty and sensitivity, not treated as a definitive ordering. Use selected response curves to explain mechanisms behind aggregate results.

For parent–extension pairs, compare independently recalibrated performance and, where mathematically legitimate, a controlled reduction of the extension. Independent recalibration estimates achievable performance; reduction examines a mechanism under a controlled parameter mapping. Related models are not independent samples. Descriptive comparisons and paired results take priority over a regression across many correlated model variants; any cross-model statistical analysis must address lineage and limited independent families.

For behavioural similarity, freeze path sets, observables and scaling. Compare predictions across plausible calibrated parameter sets. Clustering indicates response similarity under the tested paths, not a new universal taxonomy. Synthetic disagreement identifies candidate experiments; measured outcomes are needed to decide which prediction is better.

## Manuscript structure

1. **Introduction:** the unresolved choice between predictive capability and calibration burden; research questions and contribution relative to existing surveys, calibration tools and benchmarks.
2. **Collection and constitutive complexity:** search and admission, lineage, taxonomy, parameter roles and state representation.
3. **Benchmark methods:** model verification, materials and tests, initialization, splits, calibration controls, metrics, uncertainty and failure accounting.
4. **Results:** collection structure; task-specific complexity frontiers; calibration-data curves; supported extension comparisons; optional behavioural discrimination.
5. **Discussion:** mechanisms supported by evidence, implications for laboratory programmes and new model development, selection bias, identifiability, implementation effects, and domain limits.
6. **Conclusions:** answers to the research questions at the scope supported by the data.
7. **Availability:** pinned model, data and solver manifests, code, archival outputs and data access instructions.

Move detailed expression-language rules, numerical algorithms, verification cases, full model cards, calibration bounds, individual response curves and supplementary sensitivity studies to appendices or supplementary material. Keep enough implementation detail in the main text to assess fairness and numerical accuracy. A material-point study does not establish boundary-value predictive accuracy.

## Paper implementation

Keep paper-specific scripts and future study configurations under `paper/`; organization and the current demonstration command are described in `README.md`. Shared engine and model development remain outside this directory.

Build only after each protocol decision is settled:

1. `study/` manifests for survey annotations, benchmark admission, experiments, splits, parameter bounds, calibration packages, seeds, solver settings, objectives and analysis versions.
2. A validation command that checks IDs and hashes, complete metadata, split disjointness, related-test grouping, and applicability records before expensive runs.
3. Calibration orchestration around shared atlas APIs with restartable, uniquely identified runs and explicit success or failure records.
4. Prediction orchestration that uses frozen fitted parameters without consulting evaluation responses during fitting.
5. Analysis modules producing machine-readable per-test metrics, uncertainty summaries, cost records and figure inputs.
6. Figure and LaTeX table generators that consume result records and preserve links to run manifests.

Every run must record model and implementation hashes, solver build and settings, data and transformation hashes, initialization, calibration package, objective, bounds, seed, algorithm, budget, termination status and elapsed time. Archive selected parameter sets and their selection rule. Failed and partial runs remain auditable. Keep future dependency requirements under `paper/` and document a clean reproduction command when the pipeline exists.

## Milestones and completion gates

| Milestone | Deliverable | Completion condition |
| --- | --- | --- |
| M1 Survey and data audit | Annotation template, admission list, test inventory and gap report | Exact variants and usable test metadata are known; provisional sand scope can be justified |
| M2 Pilot protocol | Frozen development pilot on roughly 3 to 5 contrasting formulations | Baselines reproduced, initialization reviewed, meaningful held-out tasks and cost estimates demonstrated |
| M3 Study freeze | Versioned manifests, primary outcomes and analysis rules | Models, data, splits, budgets, metrics and failure handling fixed before final evaluation |
| M4 Core runs | Calibration and evaluation results for the admitted subset | All scheduled runs accounted for, numerical accuracy checked, missing or failed cases explained |
| M5 Scientific analysis | Survey plus complexity and data-requirement results | Primary conclusions survive declared weighting, calibration and numerical sensitivity checks or are narrowed accordingly |
| M6 Manuscript and release | Rewritten article, supplement and reproducibility package | Figures regenerate, numbers trace to runs, claims match evidence, source review and release checks complete |

Initial M1/M2 artifacts now exist, including the development pressure/density comparison and budget sensitivity. Matched-count pressure-versus-density packages have also been exercised. The next decisions are calibration-information fairness, independent review of formulations and initialization, and experimental metadata and loading-path gaps. M1/M2 are not closed by a passing software check or successful pilot run. Include a parent–extension pair only when both formulations pass admission. SANISAND and IGS are candidates subject to those checks. Pilot changes are recorded before the final study freeze.

The core paper does not wait for every surveyed model to pass every protocol. If cyclic data or verification remain insufficient, narrow the predictive claims to monotonic and unloading behaviour and report cyclic coverage as a survey gap. If a second material is unavailable, state the material-specific scope in the title and conclusions. Broader mechanisms and experiments can support subsequent papers.

## Related work to verify and position

The [targeted positioning audit](study/positioning.md) now records primary-source checks in [a structured ledger](study/related_work.json), including targeted methods review of local full-text copies of the closest fine-sand and dataset-design studies. It confirms substantial overlap in benchmarking, automatic calibration and calibration-data design. The paper must demonstrate its intended mechanism/information comparisons rather than claim those general topics as new. Complete protocol comparison, independent review and broader literature screening remain open. The [information protocol](study/information_protocol.md) defines the remaining calibration-information decisions before the study freeze.

Maintain a source-reviewed comparison of the intended contribution against existing capabilities before claiming novelty. These are starting references, not a completed literature review:

- [Lade, Overview of Constitutive Models for Soils](https://doi.org/10.1061/40786(165)1): model features, calibration requirements and model selection.
- [D'Onza et al., 2011, Benchmark of constitutive models for unsaturated soils](https://eprints.gla.ac.uk/56619/): collaborative model comparison including an undisclosed experimental test.
- [Machaček et al., 2023, Automatic Parameter Calibration of Two Advanced Constitutive Models](https://doi.org/10.1007/978-3-031-12851-6_14): automated calibration of hypoplasticity and SANISAND.
- [Zeng et al., 2026, Data strategies for automatic calibration of soil constitutive models](https://doi.org/10.1016/j.compgeo.2026.108009): calibration dataset composition and weighting for SANISAND-F.
- [MFront and TFEL](https://thelfer.github.io/tfel/web/behaviours.html), [SoilModels](https://soilmodels.com/) and [numgeo](https://www.numgeo.de/): relevant constitutive infrastructure, implementations and calibration workflows.

The atlas's intended distinction is the combination of source-traceable breadth, controlled comparisons across formulations, and evidence connecting constitutive mechanisms to prediction and calibration requirements. Establish that distinction through the completed review and results.
