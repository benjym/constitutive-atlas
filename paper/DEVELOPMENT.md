# Paper development while the atlas evolves

## Current work package

The [source reconciliation](study/source_reconciliation_2026-10-31.md) now updates the VW96/IGS annotations against the shared original-source reviews, preserves original-versus-default host distinctions, links the passing IGS v2 numerical record alongside failed v1, and separates the two SANISAND numerical policies from constitutive identities. All remain subject to independent scientific review. Historical pilot configurations and material/state counts are unchanged.

The [Ottawa cyclic design](study/ottawa_cyclic_protocol.md) specifies control and conditioning tracks, calibration-information packages, outcomes and admission order. Its [metadata inventory](study/ottawa_cyclic_inventory.json) maps 91 records to 55 source-file blocks and conservatively locks phases and raw/processed records within two campaign split blocks. This is not a specimen count or final split. The new metadata-only inventory command and split guard open no response assets; cyclic calibration and final role assignments remain pending source/control review.

The [31 October collection refresh](study/collection_refresh_2026-10-31.md) records 32 catalogue entries, eight public/research definition files and 628 public experimental records, with distinct counting units and pinned inputs. It updates source-review and model–data pairing priorities without promoting candidates or running new calibrations.

The early work package implements the data inventory, scientific annotations, and a small calibration pilot proposed in the paper discussion. These are development tools and evidence for designing the later study. The broad survey and controlled paper described in [PLAN.md](PLAN.md) remain future work.

## Work that survives schema changes

The scientific protocol can mature before the executable representation stabilizes. Prioritize these deliverables:

| Work now | Deliverable | Treatment when the atlas changes |
| --- | --- | --- |
| Define the comparison questions | Pressure, density and loading-path transfer; calibration-information cost; parent–extension comparisons | Keep the question; revise admission criteria explicitly |
| Review model mechanisms and lineage | Source-located scientific annotations with unknown and not-applicable values | Review affected annotations against definition hashes |
| Inventory experiments | Controls, observables, initial state, preparation, uncertainty, source versions and reuse terms | Preserve source evidence independently of atlas field names |
| Design calibration packages and metrics | Whole-test splits, fixed physical scales, failure reporting and information budgets | Version the study protocol separately from model schema |
| Exercise a small pilot | Recoverable runs, optimizer diagnostics and numerical checks | Replace the adapter and rerun; retain old snapshots |
| Draft the manuscript | Motivation, questions, comparison methods, figure specifications and limitations | Leave counts, rankings and quantitative conclusions unfilled |

Do not freeze a universal parameter/state taxonomy yet. Distinguish paper, formulation, implementation and parameter set; record unsupported capabilities explicitly. Count material constants, fitted constants, persistent internal state and supplied initial/history information separately. Parameter counts alone do not measure calibration difficulty. Rate dependence, algebraic stress, tensor fabric, finite strains and coupled variables are useful tests of the emerging representation rather than reasons to force every model into the current adapter.

The narrow paper-facing contract is: model identity and implementation hash; declared capabilities; explicit parameters and initialization; prescribed controls; observable histories; completion/failure records; and provenance. Translation from the evolving atlas belongs in an adapter. Unsupported requests should fail explicitly. Avoid building another general constitutive engine inside `paper/`.

Defer population percentages, broad model rankings, inferential comparisons across families and final benchmark conclusions until the eligible collection and evidence review are sufficiently complete. Development plots may change freely; a confirmatory protocol should be frozen only after the pilot has resolved its design decisions.

The scientific annotations and experiment inventory have their own small, versioned paper records. They refer to stable model and test IDs and retain source locators. They do not extend or freeze the executable model schema. Only `analysis/atlas_adapter.py` interprets the current native catalogue, state layout, and solver output; a changed representation should be handled there or through another explicit adapter.

### Immediate priorities with a small collection

1. **Review the scientific descriptions already available.** For each exact formulation, document mechanisms, parameter roles, initial-state requirements and source evidence. Use the next substantially different model to challenge the annotation vocabulary. Preserve the distinction between unknown, not applicable and unsupported; do not assign a capability from a family name alone. A few carefully reviewed examples are more useful now than preliminary percentages of the atlas.
2. **Settle the calibration-information and data questions.** Account for every measured, literature-fixed, fitted and assumed input, including initial stress and history. Resolve the compression initialization gate below before adding compression to a fit. The deliverable is a feasible laboratory-information comparison, rather than another parameter sweep on the same shear curves.
3. **Complete one end-to-end development comparison.** Demonstrate initialization, calibration, separate whole-test prediction, numerical refinement, explicit failure reporting and generated manuscript outputs on a small comparable subset. Use it to choose objectives and estimate workload. Current pilots exercise this pipeline; independent scientific review and fair information accounting remain open.

Write the motivation, research questions, source-review procedure and comparison methods alongside this work. Keep the final survey results, model-selection conclusions and population-level claims for a sufficiently complete, reviewed collection. More models should extend the evidence, rather than force the paper to change its central question.

### Source review before executable transcription

Publication screening also needs records for sources that do not establish a complete law. The [assisted full-text ledger](study/survey_full_text_screening.json) records a criterion decision from a foundational author-publication route and an unresolved HCA variant from an atlas-seed route, with primary-source hashes and page locators. Neither contributes a formulation or benchmark admission or alters the bounded Crossref pilot's counts. These records test the survey's inclusion boundary without extending the executable atlas schema. Citation follow-up and independent review remain open.

The [NorSand source record](study/source_formulations/norsand-1993.json) exercises scientific annotation of a catalogue candidate before an executable definition exists. It records the atlas-seed discovery route separately from the bibliographic search pilot, exact-variant scope, page-level evidence and calibration-information dependencies. It retains unknown dimensions and pending admission and independent review. Web-extracted primary text was accessible, but direct PDF download returned HTTP 403; no local source hash or visually verified equation transcription is claimed.

Source-only records remain separate from the six implementation annotations used by the current manuscript generator. This allows source review to progress while the executable schema evolves. The next review should challenge a different mechanism or initialization requirement, rather than duplicate the same family merely to increase the count.

The [HCA review](study/source_formulations/hca-sand-2005.json) now supplies that contrast, with a hash-pinned author manuscript and a Crossref identifier check. It motivates separate accounting for companion calculations and measured versus computed loading information. Source-only records remain outside manuscript implementation counts and all benchmark admission. Integrity checks are integrated into study validation; independent review and complete equation audits remain open.

All 16 HCA manuscript pages have now received an assisted text screening, with additional visual checks of pages 11–12. This advances publication screening while leaving the linked equation audit partial. The decision remains `unresolved_variant`: journal-version reconciliation and companion-law pinning precede an exact formulation identity. The source also exposes limits worth retaining in the paper's task design: yield-surface encounters require special treatment, multiple-source amplitude combination is approximate, and polarization calibration calls for loading information beyond conventional axial cycles. No independent dimension or performance ranking follows from these observations.

Targeted visual review of HCA manuscript pages 9, 13 and 14 now records the laboratory accumulation inventory, centrifuge accumulation inputs, companion-model inputs and case initialization separately. The ledger retains unresolved parameter dependencies and initial back-polarization. The [information protocol](study/information_protocol.md#companion-calculations-and-measured-loading-information) distinguishes conditioning on an observed cycle from predicting cycles with a companion model, and requires explicit accounting of specimen-specific adaptation. These are future task designs, not additional calibration runs or benchmark results.

The working manuscript now uses NorSand and HCA as source examples of calibration burden, with primary-publication references and explicit separation from implementation snapshots and benchmark admission. Its generator checks the cited review identities and records source-review and available local source hashes in the provenance manifest. The examples motivate task design; they do not establish performance or independent parameter counts.

The [HCA normalization audit](study/hca_normalization.md) derives a conditional reference-void-ratio transformation that preserves the scalar accumulation kernel when its coefficient and cyclic history are transformed together. Numerical identity checks cover both amplitude branches and finite history updates. A separate counterexample prevents extending a quadratic-branch amplitude rescaling across the published literal cap. This equation-level diagnostic leaves the full workflow's independent dimension and identifiability unresolved. Its derivation, scalar code and checks are pinned in the source-review record and included in manuscript provenance.

The [2016 interface source review](study/source_formulations/hypoplastic-interface-2016.json) extends the source-only examples beyond bulk sand laws. Its access and variant gaps remain explicit. The [interface development protocol](study/interface_protocol.md) records the additional experimental contract: traction–slip observations, apparatus stiffness basis, thickness mapping, surface characterization and initial state. It defines future questions without freezing the atlas schema or admitting a formulation to the sand pilot.

### Handling a schema revision

Separate representation changes from scientific changes. A field rename or serialization change requires an explicit adapter update and a check that the same controls and observations retain their meaning. A changed equation, sign convention, parameter mapping, admissible domain or initialization rule requires scientific review and a new run identity; identical model IDs do not establish equivalence.

Retain the source formulation, implementation and adapter hashes for each run. Never rewrite archived results into a new schema without retaining their original records and a documented transformation. Add annotation fields when a new formulation requires them, and record whether older entries were reviewed for that field. Do not interpret an absent field in an older record as evidence that a mechanism is absent. Freeze a specific study release only after these development decisions are settled; the wider atlas can continue evolving.

The emerging [Terracotta research transcription](../docs/models/terracotta-2024-transcription.md) is a useful representation test: stress is algebraic, its four persistent states are scalars, physical time matters, and the supported kinematics are axisymmetric. Do not infer six stored stress components or general 3D capability from this formulation. Its independent physical-parameter count also requires review of mesoscopic-temperature normalization. Version 2 of the six paper annotations now records kinematic scope, storage counts and independent output components explicitly. Unsupported full-3D counts are null. The [normalization audit](study/terracotta_normalization.md) derives and tests a coordinated rescaling of mesoscopic temperature and coefficients; it gives an upper bound of nine material combinations, not a proof of identifiability. Independent review remains open. The present pilot adapter rejects this formulation rather than guessing its initialization or controls.

## Data audit

The original KFS audit below remains distinct from the newer [curated public-data feasibility audit](study/data_feasibility.md). Run `python3 paper/scripts/audit_public_feasibility.py` for a hash-pinned inventory of the shared collection. Its field candidates are not admitted benchmark tests or verified independent specimens. [KFS characterization evidence](study/kfs_characterization.json) records the original index measurements and OE/OEC/ISO source discovery. The OE development selection and audit are recorded below; OEC/ISO responses remain unassigned.

### Compression development evidence

OE1 and OE12 were selected from published initial-density metadata before inspecting their raw responses. OE2–11 were reserved at the same time. Published figures and source constants were already accessible; this is not a blind split. Two mixed archives were pinned, and only OE1/OE12 were decompressed and normalized. The extraction ledger records member, normalized-data, source-code and reservation hashes. Reproduce into a new directory:

```sh
python3 paper/scripts/prepare_development_data.py --manifest paper/study/compression_sources.json --output paper/results/compression-development-rerun
python3 paper/scripts/audit_compression.py --data paper/results/compression-development-rerun
```

The local [compression audit](results/compression-development-v1/audit.md) preserves both loading reversals and zero-stress observations. The measured initial void ratios agree with the published table at its printed precision. The source supplies axial stress, engineering axial strain and void ratio, without radial stress or physical time. The observed volume relation is consistent within a bound based on printed decimals; that bound is not measurement uncertainty. These kinematically linked channels must not count as two independent sources of calibration information.

No constitutive calibration has been performed on these records. The zero-stress start is not directly admissible for positive-pressure hypoplasticity. A qualified positive-stress start, full stress/history initialization and replay/objective design are required. The importer retains observations and does not supply K0, zero history, a pressure floor or a guessed effective-stress tensor. Tests cover unit conversion, reversal detection across repeated controls, rounding interpretation and exclusion of reserved members before parsing.

The [compression initialization protocol](study/compression_protocol.json) records targeted review of the 2016 Section 3.1 and 2019 Section 3 simulation descriptions. Both start at 1 kPa axial stress and assume vertically mobilized intergranular strain. The reviewed passages do not supply the missing lateral stress, and their history assumption cannot be transferred to the base law without an IGS state. Their first-loading curves also supplied calibration information, so agreement there was not independent validation.

Run `python3 paper/scripts/audit_compression_protocol.py` for the local [initialization and strain-coordinate diagnostic](results/compression-protocol/report.md). It selects first-loading intervals at observed stresses above 1, 5 and 10 kPa; the latter two are analyst-selected sensitivity thresholds. No measurements are interpolated or deleted. The first observation above 1 kPa is actually 1.548 kPa in both development files. The interval ends before first unloading, with any peak holds preserved.

An exact integration of the implemented void-ratio continuity equation, driven by engineering-strain increments from that start, gives end-of-first-loading void-ratio residuals of approximately 0.00144 for OE1 and 0.0000917 for OE12. These are kinematic diagnostics, not simulated stress errors or measurement uncertainty. Constant-solid-volume height geometry instead uses the logarithmic coordinate `log((1-eps_start)/(1-eps_end))`; it gives end residuals near the source's printing precision. Switching coordinates alone does not establish finite-strain validity of the stress law. Choose and qualify that convention, full stress/history initialization and numerical sensitivity before adding compression to calibration. Zero-stress unloading/reloading remains outside this first-loading diagnostic; restarting separate branches would lose history.

### Fixed-parameter compression sensitivity

[The sensitivity configuration](study/compression_sensitivity.json) exercises two memory-free models with the baseline constants preserved in the earlier matched-count run. These are not its selected fitted parameters. Elastic constants are diagnostic choices; the hypoplastic baseline inherits compression information. Neither is an independent prediction or a controlled common-information comparison. The source case's full initialization and IGS formulation are not reproduced.

The diagnostic uses all three declared start thresholds, initial radial/axial stress ratios 0.35, 0.5 and 1.0, engineering and log-height coordinate mappings, and maximum increments 0.0005 and 0.00025. The three stress ratios are assumed scenarios, not measured K0 values or an uncertainty distribution. The ratio applies only to initial stress; subsequent radial stress evolves under zero lateral strain. First-loading observation order and repeated controls are preserved. Each numerical segment starts from the preceding committed state; any failed segment rolls back to the preceding observation. No time is inferred.

```sh
python3 paper/scripts/run_compression_sensitivity.py --output paper/results/compression-sensitivity-rerun
python3 paper/scripts/plot_compression_sensitivity.py --report paper/results/compression-sensitivity-rerun/report.json
```

The local [144-path report](results/compression-sensitivity-v1/report.md) and [curve figure](results/compression-sensitivity-v1/first-loading-sensitivity.png) retain every scenario. All 144 paths completed. A separate checksum/schedule audit verified all input snapshots, baseline parameter selections, initial stress tensors, complete observation coverage and zero lateral/shear strain control. The figure generator recomputes paired summaries and checks archived input, model and executable hashes before plotting; its provenance record pins the report, plot code and figures.

For the hypoplastic baseline at the lowest start threshold, maximum axial-stress differences across the assumed initial stresses are approximately 14.2 kPa for OE1 and 10.2 kPa for OE12. Changing coordinate mapping gives maxima of 33.1 and 5.78 kPa, respectively. The corresponding maximum differences between numerical resolutions are 6.19 and 1.42 Pa. These differences compare identical acquired observations at a fixed start, holding the other factors fixed. Both initial-state and coordinate choices therefore exceed the observed refinement differences for these scenarios. This does not identify the physically correct assumption or prove convergence. Different start thresholds have different initial points and intervals, so their results are not a paired common-interval accuracy comparison.

The elastic oracle gives the expected zero axial-stress sensitivity to initial lateral stress under prescribed zero lateral strain, while retaining coordinate sensitivity. Across all runs, numerical void-ratio continuity differs from its exact imposed-coordinate solution by less than 5.1e-11. These checks establish the scoped replay controls, not constitutive validity. Independent source/initialization review, a qualified coordinate convention and an explicit treatment of missing lateral stress remain necessary before common-information calibration. No stress-error minimization was used to choose a scenario, and no reserved responses were opened.

Run `python3 paper/scripts/audit_data.py` from the repository root after fetching and ingesting the existing source archives. The local report is `paper/results/data-audit.json`; it checks archive and member hashes and records channels, initial-state availability, loading direction, repeated samples, warnings and gaps. It does not copy full measurements into a tracked artifact.

[The source inventory](study/datasets.json) separates locally audited experiments, provider-index discoveries, and unresolved searches. The original local audit covers five drained tests and twelve undrained tests; the density and compression additions are documented separately. All five original drained tests belong to the provider's loosest TMD group. They can exercise pressure transfer, but they cannot establish density transfer or generalization across sands. The undrained set contains compression and extension; decreasing strain alone is not evidence of cycling. Initial void ratio is absent from all twelve normalized undrained records.

The original experimental paper supplies candidate undrained void ratios in Table 4. [Supplemental metadata](study/experiment_metadata.json) records the original values and source-based series context. Tables were checked against rendered author-PDF pages 5 and 6, with the PDF checksum and exact locators recorded. They are source transcriptions, not resolved initialization values: later evidence disagrees for several tests, as described below. Nominal table pressures do not replace measured initial stresses. Independent transcription review is still required.

The provider records a correction to the TMU mean-pressure values in 2018. Keep exact archive hashes and reconcile file versions before scientific use. The paper supplies default preparation, geometry and loading rates, but per-specimen deviations, measurement uncertainties, and replicate grouping still require review. The audit distinguishes missing normalized fields from available supplemental evidence; it does not certify experimental validity.

The most useful next data expansion is the remaining TMD density groups, followed by complementary compression/unloading and cyclic paths. Reserve final evaluation tests before using these additions for protocol tuning. Kaolin is a separate future clay panel and cannot serve as a second sand material. Measurement redistribution terms remain as documented in `docs/DATA_REUSE.md`.

### Density expansion and unresolved evidence

[The reservation policy](study/reservations.json) assigns 14 TMD responses to a future final evaluation pool before additional response analysis. Previously inspected tests remain development data. Published figures and literature constants were already accessible, so this is not a blind holdout. A literature parameter set calibrated on reserved tests cannot be described as independent of that pool.

`prepare_development_data.py` extracts only TMD7–9 and TMD12–14 from pinned mixed archives; member names are checked before response bytes are read. The audit and pilot reject reserved IDs. The six extracted members pass raw-member hash verification. Preparation and audit commands are:

```sh
python3 paper/scripts/prepare_development_data.py
python3 paper/scripts/audit_data.py --data-dir paper/results/development-data/normalized --source-manifest paper/study/development_sources.json --output paper/results/development-data/audit.json
```

The density configuration in `study/pilot_density.json` is an executable development design. TMD12 contains a backward axial-strain step from 0.00088277579 to 0.00087883975. The monotonic metric rejects this record; do not sort it or silently discard the step. The explicit acquisition-order evaluation protocol preserves it.

TMD12–14 file initial void ratios disagree with the original Table 3 beyond its reported precision. Their file values agree to three decimals with Table 1 of [Yeh et al., DOI 10.1002/nag.3476](https://doi.org/10.1002/nag.3476). That later table also reports different void ratios for six TMU tests. [The conflict register](study/metadata_conflicts.json) retains both source versions without declaring either an erratum. No undrained initialization should be inferred automatically from the original table. Definitions and archive versions remain unresolved.

### Recorded-order replay and initial-state sensitivity

[The replay diagnostic](study/replay_sensitivity.json) uses the earlier C2 fits without recalibration. It evaluates both file and original-table void ratios for TMD12–14, holding measured initial stress and material parameters unchanged. The native adapter chains the shared drained laboratory driver between acquisition coordinates, preserving the TMD12 reversal and repeated coordinates. Each segment uses the previous committed state; a failed segment is rolled back to the preceding observation. Maximum increments of 0.0002 and 0.0001 test numerical sensitivity. The segment driver targets its initial radial stress; the wrapper bounds drift against the original radial stress and records its maximum. No loading timing is inferred.

The separate diagnostic metric integrates endpoint squared/absolute errors with trapezoidal weights over absolute axial-strain travel. It does not sort by axial strain, extrapolate failed predictions, or treat row density as equal statistical replication. Repeated-coordinate segments have zero travel weight. This is a distinct metric from the monotonic calibration objective, not a replacement silently applied to its scores. Path weighting and control fidelity still require scientific review before a final protocol freeze.

Run into a new directory, then generate the figure:

```sh
python3 paper/scripts/run_replay_sensitivity.py --output paper/results/replay-initial-state-v2
python3 paper/scripts/plot_replay_sensitivity.py --report paper/results/replay-initial-state-v2/report.json
```

The local v2 diagnostic completed all 36 cases: three models, three tests, two initial-state interpretations and two increments. The hypoplastic response changes under the initial-state choice exceed the tested refinement differences; elastic and Drucker–Prager stress and strain histories are unchanged by the void-ratio choice. Those models do not use void ratio in their stress response. These observations motivate controlling initialization in comparisons; they do not resolve the source disagreement or establish a model ranking. Full scenario errors and numerical differences are generated in the local report and figure. Source, experiment and paper-code snapshots, the native executable, checksums and a per-case journal are retained with the run. Analytical elasticity with reversals and duplicates, rollback on failure, and agreement with a native monotonic hypoplastic path are checked by tests.

### Density-development pilot

`study/pilot_density.json` declares the initial-state policy and evaluation protocol before fitting. C1 uses one loose test at 200 kPa; C2 uses three loose tests at 100, 200 and 300 kPa; C_density adds two 200 kPa tests from other density bands. Six other development tests evaluate pressure and density transfer. C_density changes both test count and coverage; this design cannot isolate the value of diversity at fixed test count. All groups belong to Karlsruhe fine sand and do not establish transfer across materials.

Calibration retains the original monotonic uniform-strain objective. Every evaluation test uses acquisition-order replay and the same travel-weighted metric, with maximum increments of 0.0002, 0.0001 and 0.00005 for selected-fit refinement. Both stages use measured file initial stress and void ratio. File-based initialization is a declared development choice; the source discrepancy remains unresolved and its paired sensitivity is reported separately. Aggregate evaluation scores are not directly comparable with those from the earlier monotonic pressure pilot.

```sh
python3 paper/scripts/run_pilot.py --config paper/study/pilot_density.json --output paper/results/pilot-density96 --solver paper/results/pilot-frozen96/solver/atlas_solver --model-dir paper/results/pilot-frozen96/models
python3 paper/scripts/run_pilot.py --config paper/study/pilot_density.json --max-evaluations 384 --output paper/results/pilot-density384 --solver paper/results/pilot-density96/solver/atlas_solver --model-dir paper/results/pilot-density96/models
python3 paper/scripts/report_pilot.py --report paper/results/pilot-density96/report.json --comparison paper/results/pilot-density384/report.json --output paper/results/diagnostics-density
```

The 96-budget run completed 27 calibration starts, 162 start-level evaluations, 108 selected-fit refinements and 18 separate baseline evaluations. Archived solver, models, code, configurations and experiment copies passed an independent checksum and schedule audit. All 18 original C1/C2 fits reproduced the earlier pilot parameters and calibration objectives exactly, despite the explicitly changed evaluation protocol. Generalized reporting pages response curves in configured ID order and requires every scheduled evaluation test before computing an aggregate score.

The 384-budget run completed the same schedule, with unchanged scientific inputs and analysis implementation. Both budgets passed the snapshot and schedule audit. All selected evaluation paths completed at every tested refinement. Plastic starts reached the search step threshold at the larger budget; several hypoplastic starts still exhausted it. A step threshold is not proof of a global optimum. The current bounds, inherited literature constants and partial hypoplastic calibration still prevent an equal-information complexity ranking.

The generated comparison is in the local `paper/results/diagnostics-density/report.md`, with response plots split over two pages and a package/budget diagnostic. Adding the density tests lowers the partial hypoplastic development evaluation aggregate relative to C2 at both budgets, while the elastic baseline's aggregate increases. The larger search budget improves hypoplastic calibration objectives but slightly increases its evaluation aggregates. These findings support studying model-dependent information requirements and calibration-versus-transfer tradeoffs; they are not final predictive claims. C_density simultaneously adds tests and changes their coverage. Matched-count calibration designs, weighting sensitivity, reviewed additional formulations and independent source review remain further work.

## Scientific annotations

[The development annotations](study/model_annotations.json) cover the five original formulations and the restricted Terracotta Figure 1 transcription. Each record separates material constants, numerical reference scales, stress components, persistent internal state, bookkeeping and transient multipliers. It records mechanisms, lineage, initialization requirements, limitations, sources and pilot admission.

These are assisted interpretations of repository equations and linked references, with independent review explicitly outstanding. The proposed calibration information is a source-review checklist, not an experimentally established minimal test programme. Source hashes allow later changes to be detected without treating a newly edited formulation as the old annotation.

Two immediate distinctions matter: Drucker–Prager's plastic multiplier is not persistent memory, and Cam Clay's preconsolidation pressure is an initial-state/history quantity rather than another universal material constant. The current Drucker–Prager bounds allow nonnegative dilatancy, which excludes plastic contraction with the implemented sign convention. That restriction must accompany any interpretation of a fit to loose sand.

## Development pilot

[The pilot configuration](study/pilot.json) specifies all test IDs, fitted and fixed constants, exploratory bounds, objective scales, optimizer starts and budgets. It uses all five already inspected TMD tests as development data:

- C1 calibrates on TMD3.
- C2 calibrates on TMD2, TMD3 and TMD4.
- TMD1 and TMD5 are withheld from those fits to exercise pressure-transfer evaluation. They are not a blind or final scientific evaluation set.

Compare an elastic diagnostic baseline, the explicit cohesionless Drucker–Prager specialization, and a partial calibration of the base sand hypoplastic law. The hypoplastic fit varies four constants while retaining four literature constants. This extra source information prevents interpreting the pilot as an equal-information complexity leaderboard. IGS needs independent review and a history-initialization decision. Cam Clay needs a suitable material panel and consolidation evidence.

Use the first measured point for effective stress and void ratio. The loading path is a monotonic ramp through the first 2 percent axial strain, stopping at the final observed point inside that interval; it does not replay unrecorded timing or pauses. Equal-strain resampling prevents dense recording intervals dominating the objective. Exact duplicate strain values retain the last observation in record order. No curve is sorted across a reversal and no evaluation interval is shortened to accommodate an incomplete prediction.

The objective averages squared stress error divided by initial mean effective stress squared and squared volume-strain error divided by 0.01 squared, first equally across channels and then across tests. The scales are declared physical references, not estimates of measurement noise. The optimizer is a bounded coordinate pattern search in unit coordinates, with log coordinates for modulus and hardness. Seed zero starts from the stated baseline and the other two starts use seeded uniform coordinates. Each sweep tries positive and negative coordinate moves from one incumbent; unsuccessful sweeps halve the step. Budgets count complete parameter-vector evaluations and every test in a failed evaluation is retained.

The large objective assigned to failed calibration trials only supports the search. Evaluation accuracy is reported alongside explicit completion status, never through a failure penalty leaderboard. Optimizer starts measure search variability; they do not quantify parameter posterior uncertainty. Parameters are selected using calibration objective only. Evaluation observations are loaded after fitting each package.

Run the pilot and the larger-budget sensitivity check into new output directories:

```sh
python3 paper/scripts/run_pilot.py --output paper/results/pilot-frozen96
python3 paper/scripts/run_pilot.py --max-evaluations 384 --output paper/results/pilot-frozen384 --solver paper/results/pilot-frozen96/solver/atlas_solver --model-dir paper/results/pilot-frozen96/models
```

Each run preserves the effective configuration, source/data/code/solver hashes, dirty-worktree status, calibration journal, termination reasons, all start results, predictions and selected-fit step refinements. It also saves the paper code, compiled model definitions and native executable actually used, so uncommitted implementations remain recoverable. The solver and model copies are used throughout execution; changes to their original paths are reported separately as origin drift. Data and paper-code changes still stop a run. The sensitivity run explicitly reuses the baseline snapshot. Existing run directories are never overwritten. The adapter rejects a mismatch between source and compiled definitions before snapshotting. Interrupted runs preserve their journal but are not automatically resumed. These local snapshots support development auditability; a scientific release still needs the pinned shared engine sources and build environment.

Generate the diagnostic report and figures with the reporting command in [README.md](README.md). Keep all generated results local under the ignored `paper/results/` directory. A separate manuscript-input generator, described below, inserts explicitly labelled development evidence.

## Decisions before a controlled study

1. Replace the current partial hypoplastic fit with a documented calibration-information comparison; decide which measured or literature constants may be supplied to each model.
2. Resolve boundary-hitting parameters and optimizer budget sensitivity before attributing differences to constitutive mechanisms. Consider alternative optimizers and parameter profiles on development data.
3. Establish preparation, consolidation and uncertainty metadata and a grouping rule for related specimens.
4. Add density variation and genuinely different loading paths; retain a final evaluation pool excluded from protocol development.
5. Check objective-weighting sensitivity and meaningful feature errors, then freeze primary metrics. Use tests and materials as statistical units, not recording samples.
6. Complete independent equation and reference-implementation review for admitted formulations. This pilot tests the comparison machinery; it does not promote their evidence status.

## Initial pilot findings

The initial baseline and larger-budget runs exposed useful study-design issues. Increasing the search budget improved some calibration objectives without consistently improving evaluation error. Some hypoplastic fits reached exploratory bounds, while Drucker–Prager selected zero dilatancy at the tested bounds. These are reasons to examine optimization, admissible response and supplied prior information before interpreting model differences. They do not establish nonidentifiability or a superiority claim.

Selected prediction paths showed small changes under the tested step refinements. The generated report gives the actual errors, completion counts and refinement differences. This supports continuing protocol development; it does not independently verify the constitutive equations. Source snapshots and executable copies are retained with the final development runs because the shared worktree is evolving.

The later study should reuse reviewed scientific decisions and stable result records while the atlas continues to develop new model representations.


## Matched-count pressure versus density design

`study/pilot_matched.json` records a development contrast after the nested density pilot: pressure3 uses TMD2/3/4, while density3 uses TMD3/8/13. Both contain three tests, use the same fitted/fixed constants, bounds and starts within each model, and predict the same six separate development tests. This compares how to allocate a three-test calibration programme; it does not equalize preparation effort or establish a universal value of diversity.

The declared paired analysis reports all six tests and three descriptive density cohorts. Negative changes mean lower error after density3 calibration. Primary evaluation uses equal stress/volume weights. Stress weights 0.25, 0.50 and 0.75 are evaluation-only sensitivity checks, with fitted parameters fixed. Same-seed fit pairs describe optimization sensitivity, not confidence intervals. Missing or failed cases prevent complete aggregates rather than disappearing from them. The design and weights were recorded before fitting density3; prior nested-pilot exposure is explicitly disclosed.

```sh
python3 paper/scripts/run_pilot.py --config paper/study/pilot_matched.json --output paper/results/pilot-matched96 --solver paper/results/pilot-density96/solver/atlas_solver --model-dir paper/results/pilot-density96/models
python3 paper/scripts/run_pilot.py --config paper/study/pilot_matched.json --max-evaluations 384 --output paper/results/pilot-matched384 --solver paper/results/pilot-matched96/solver/atlas_solver --model-dir paper/results/pilot-matched96/models
python3 paper/scripts/report_pilot.py --report paper/results/pilot-matched96/report.json --comparison paper/results/pilot-matched384/report.json --output paper/results/diagnostics-matched
python3 paper/scripts/report_calibration_design.py --report paper/results/pilot-matched96/report.json --report paper/results/pilot-matched384/report.json --output paper/results/contrasts-matched
```

Use new output directories for deliberate reruns. The original local jobs shared the prior density run's frozen executable and model definitions and ran concurrently. Their elapsed times are diagnostic, not controlled performance comparisons. Detailed preparation, initial-state and prior-information limitations from the earlier pilots still apply.

Both budgets completed 18 calibration starts, 108 start-level evaluations, 72 selected-fit refinements and 18 baseline evaluations per run. Frozen solver, model, code, configuration and experiment copies passed checksum checks, and all scheduled prediction keys were accounted for. The nine pressure3 fits at each budget exactly reproduced the prior C2 parameters and calibration objectives. The generated paired report is in local `paper/results/contrasts-matched/report.md`; companion completion, bounds and refinement diagnostics are in `paper/results/diagnostics-matched/report.md`.

For the calibration-selected partial hypoplastic fits, density3 lowers the full evaluation aggregate at both budgets and all three declared evaluation weights. The gains concentrate in the higher-density cohort; the loose and intermediate cohorts have slightly higher primary error. All three same-seed aggregate comparisons retain that direction, but these starts are not uncertainty samples. This supports examining target-specific laboratory programmes rather than selecting a universally preferable calibration package.

Drucker–Prager's selected-fit aggregate also favors density3 at both budgets and all declared weights, while some same-seed comparisons favor pressure3. That search sensitivity limits a mechanism-based interpretation. The elastic baseline's full aggregate favors pressure3, although its higher-density cohort favors density3. Neither result establishes a cross-model ranking. Test count is now matched, but preparation cost, initial-state uncertainty, prior constants and the restricted material/loading domain remain limitations.

These computations exercise RQ3 and identify outcomes worth preserving in a later controlled study: whole-test tradeoffs, calibration-information allocation and search sensitivity. They do not close the independent source-review or broader model-admission gates. The annotation extension and scientific manuscript structure are now implemented. Independent equation and initialization review, calibration-information fairness and experimental coverage remain the next scientific gates; further sweeps alone cannot resolve them.

### Definition revision during development

The shared Drucker–Prager entry changed during the matched-count jobs. The validator detected the annotation hash mismatch. Inspection of the new equations and [local derivation](../docs/models/drucker-prager-apex.md) shows that trial-direction elimination and an explicit apex subgradient branch replace the previous deviator-direction regularization; parameter roles and state counts are unchanged. The assisted current annotation was updated with a revision history, while independent review remains pending.

The pressure, density and matched-count results above use the archived definition `9eff38d8ba9ea327d9b0590b03c966b7f5797a53f0aff9e1ecd0b923423a346e`. The newly annotated definition is `d40db28d8de98b7eb8597c90787d16d1f76bac0d145cabb9a5853e86d811650d`. Frozen binaries and model copies kept the runs consistent; they do not establish equivalence to the new revision. Retain these development comparisons as evidence for their exact implementation snapshot. Recheck the revised entry before any controlled benchmark, and do not combine revisions under one unqualified model label. Paper annotations and run identities must carry definition and implementation hashes even while stable atlas IDs persist.

## Scientific manuscript inputs

`article/main.tex` now presents the scientific questions, scoped complexity descriptions, comparison methods and development evidence. The earlier implementation draft is preserved as `article/implementation-note.tex`. Run `python3 paper/scripts/generate_manuscript_inputs.py` after generating the matched-count contrasts and compression sensitivity report to rebuild its tables and figure. The generator validates frozen input checksums and recomputes the contrasts; its output manifest distinguishes current annotation hashes from historical pilot definitions. Compression methods and the generated four-row table now expose initial-stress, coordinate and numerical effects separately. Integrity tests reject changed archived inputs, different constants presented as fixed baselines, stale summaries and missing entire threshold groups. All 62 paper tests pass. The nine-page development draft compiles with both the desktop and local compilers; rendered pages and the new table were visually checked. It remains a development manuscript, not a completed survey or final benchmark.

## Literature positioning

The [targeted audit](study/positioning.md) and [evidence ledger](study/related_work.json) distinguish full-text, abstract/indexed-text and bibliographic-only access. Local full texts of the 2019 fine-sand comparison and 2026 dataset-design study are now checksum-pinned, with targeted methods review and parameter-table visual checks. The introduction acknowledges prior benchmarking, automatic calibration and experimental-data design. This check narrows the intended contribution to source-traceable comparisons linking mechanisms, supplied information and task-specific predictions. It does not establish novelty or complete the charter's systematic screening.

The [information ledger](study/calibration_information.json) accounts for fixed inputs in all three development configurations. Its hashes and fitted/fixed partitions are checked by `validate_study.py`; no historical fits were changed. The [information protocol](study/information_protocol.md) separates the future common-information benchmark from source reproductions and recommended calibration programmes. Independent review and the experimental decisions specified there remain open.

## Broad survey discovery and screening

The [paper survey protocol](study/survey_protocol.md) now implements the research charter's distinction between discovery, publication identity, exact formulation identity and benchmark admission. The two older Crossref batches were manually flagged for search-quality problems: their query labels concern geomechanics, but returned titles are predominantly biomedical. Their bytes and quality-audit hashes are preserved.

A new, explicitly relevance-ordered and date-filtered eight-theme pilot returned 200 occurrences, with 177 normalized DOI groups and 23 repeated occurrences. Exact requests, retrieval times, cursors, HTTP headers, unmodified responses and original fetch/protocol snapshots are pinned. The auditor checks all eight batches, ordering and source identities before constructing the publication queue. It flags nine same-title groups across different identifiers for review rather than merging them or calling them different formulations.

The initial first-five-per-theme screening-method pilot records 37 assisted title decisions. Extensions cover the remaining saved soil-query titles (18 additional decisions), bounding-surface titles (19), hypoplasticity titles (eight), rock titles (20), creep titles (19), coupled titles (20), interface titles (20) and nonlocal titles (16). All 177 DOI groups now have an assisted title decision: 93 full-text retrieval candidates, 43 background/source-tracing routes, 39 unresolved cases and two provisional exclusions outside geomaterial scope. All retain exact item locators and independent review pending. No formulation is admitted from title metadata. The local discovery/screening audit passed on 2026-10-31, including the full title ledger's structure, unique publication identities, pinned response identity and publication/item locators; its generated queue now has zero groups without a title decision. All 16 focused screening-audit tests passed. This validation does not establish scientific correctness, independent review or final eligibility. No new retrieval or solver run was needed.

The rock extension retains uncertain original-versus-secondary source identities and the same-title clay pair for reconciliation. The creep extension flags near-title rock-salt publication relationships and memory-representation questions for fractional-order candidates. The coupled extension links companion formulation/evidence papers and retains the surrogate's constitutive-versus-system scope question. The interface extension records bulk, weak-plane, discrete-interface and structural-system distinctions. The nonlocal extension leaves generic-theory material scope and engineered-material eligibility open and requires review of spatial operators, length information and boundary data. Full-text source review, variants, supplementary discovery routes and final retrieval/stopping rules remain open. Completion of this bounded assisted title pass is not completed systematic discovery or 50-model coverage.

Run `python3 paper/scripts/audit_survey_discovery.py` against the pinned local retrieval. Fresh retrieval commands and the rule against blindly reusing old screening locators are in the protocol. Scientific controls test DOI normalization and punctuation, cross-query duplicates, same-title different-DOI flags, incomplete identities, raw-response preservation, changed request/response rejection, failed-fetch retention and prevention of title-only formulation/review promotion. Study validation checks the paper protocol and screening records without changing the shared atlas screening ledger.

The [gradient-rock publication note](study/source_notes/gradient-rock-2018.json) starts selected primary-article text review of one existing retrieval candidate. It is deliberately outside the atlas-linked formulation annotations and completed full-text ledger: no model ID, source-byte pin or admission is claimed. Visual equation checking, full publication review and independent review remain open. Its conditional analytic inference informs spatial-task design in the information protocol; discovery and review counts are unchanged.

The [spatial observability derivation](study/spatial_observability.md) now states the assumed operator, proves homogeneous insensitivity, derives the single-mode trade-off and a conditional two-mode inverse, and identifies conditioning limits. It concerns prescribed and observed internal fields, not a complete experimental observation map. This develops the paper's experiment-selection methods without running a solver or claiming a verified nonlocal formulation.

Public PDF retrieval for the gradient-rock note was attempted through the ResearchGate link and publisher endpoint. The web route missed its PDF cache; local retrieval first failed DNS resolution, and permitted-network requests returned HTTP 403. These access outcomes are recorded in the note. No PDF was obtained, so source-byte pinning and visual equation verification remain open; extracted-text access is not promoted to verified PDF access. These HTTP/network failures do not identify a cause of the separate app-termination issue.

The working manuscript now reports the bounded assisted title pass using generated counts. `generate_manuscript_inputs.py` audits discovery hashes and title locators before generating those macros, and includes the protocol, search manifest, screening ledger, raw responses, headers and archived retrieval inputs in its provenance manifest. A new methods table declares controls, supplied information and scored responses separately for homogeneous, interface/spatial and combined-workflow tasks. The generator completed, all 16 focused screening-audit tests passed, and the ten-page PDF compiled without LaTeX warnings after two passes. The changed screening and task-table pages were rendered and visually inspected. These changes do not add source admissions, final comparisons or new solver runs.

### User-directed material scope (2026-10-31)

The [scope addendum](study/survey_scope_decisions.json) focuses the primary survey on soils, granular media, rock and their interfaces, retaining standalone concrete/geopolymer theory as linked background. Three title decisions move from unresolved to background (current totals: 93 retrieval, 46 background, 36 unresolved, two outside scope). Original retrieval and protocol snapshots are unchanged; all independent reviews remain pending. The manuscript generator pins the addendum alongside the screening ledger.

Validation after the scope update: discovery audit passed with 177 title decisions and no missing title decisions; all 16 focused screening tests passed; manuscript inputs regenerated; the 10-page PDF compiled without layout warnings and the changed scope page was visually checked. No solver or calibration run was needed.

### Constitutive-ingredient source follow-up (2026-10-31)

The [Margolin–Trent note](study/source_notes/margolin-trent-1992.json) adds selected primary-text review and a publisher bibliographic cross-check for an unresolved rock-query identity. It separates original conference bibliography from the discovery DOI and records closure and lineage questions. The third-party OCR is not a pinned or visually verified source. Discovery counts, assisted title decisions, completed full-text counts and admissions are unchanged. This source review advances M1 without depending on the evolving atlas schema.

### Second-material feasibility follow-up (2026-10-31)

The current shared curated collection expanded to 522 records (84 labels); the refreshed field audit still finds only twelve records meeting the minimum triaxial checks. The [Hostun follow-up](study/hostun_feasibility.json) pins selected source metadata and documents why worksheet summaries cannot yet initialize the differently labelled curves. All ten drained series lack a volume channel in the curated representation. Primary experiment correspondence and independent review remain open. No solver runs, source-data edits, cross-curve joins or final KFS response access were performed.

### NorSand input-role review (2026-10-31)

The original source review now distinguishes material-input candidates, fixed empirical information, initialization constraints and the example's fitted subset. It also records the need to trace characterization evidence before assigning held-out status. This advances the common-information audit; it does not assign a verified parameter/state dimension or admit the formulation. PDF text is accessible, but local source pinning and visual equation review remain open. No solver run was needed.

### Mechanism-specific compression task (2026-10-31)

The [SANISAND publication note](study/source_notes/sanisand-lineage-2004-2008.json) separates three related publications using publisher abstracts with explicit access limits. The [conditional cone derivation](study/stress_ratio_probe.md) shows why proportional pressure loading from a strict interior state cannot activate its assumed open-cone mechanism. It distinguishes elastic density change, plastic compression and oedometer loading, and specifies a possible future task. Original equations, exact lineage and independent review remain open. No source admissions, completed full-text decisions, solver runs or ISO-response access were added.
