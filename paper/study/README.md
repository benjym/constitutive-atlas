# Development study inputs

These records support the early paper work while atlas formulations and schemas change. None is the frozen scientific release manifest.

| File | Responsibility |
| --- | --- |
| `datasets.json` | Local experimental coverage, provider discoveries, missing evidence and next acquisition tasks |
| `related_work.json`, `positioning.md` | Targeted primary-source positioning check, access limits and consequences for the paper; not a systematic search |
| `survey_protocol.json`, `survey_protocol.md` | Broad discovery scope, separate publication/formulation identities, screening rules and remaining search gates |
| `survey_searches.json`, `survey_legacy_quality.json` | Pinned eight-theme metadata pilot and preserved evidence of the earlier search-quality problem |
| `survey_screening.json` | Source-located assisted title decisions; no full-text formulation admission or independent review |
| `survey_full_text_screening.json` | Assisted full-text publication decisions, including supplementary-route criterion sources without an atlas formulation or verified DOI; separate from the Crossref pilot queue |
| `calibration_information.json`, `information_protocol.md` | Fixed/fitted information audit of pinned development configurations and decisions required for a common-information benchmark |
| `data_feasibility.md`, `kfs_characterization.json` | Curated-data feasibility interpretation and source-pinned KFS index/compression discovery; not benchmark admission |
| `experiment_metadata.json` | Source-located supplemental initial state and series context, without rewriting normalized measurements |
| `terracotta_normalization.md` | Derived normalization redundancy, scope and independent-review limitations |
| `hca_normalization.md` | Conditional scalar reference/history reparameterization and a counterexample across the amplitude cap; not a full HCA implementation or dimension count |
| `interface_protocol.md` | Development requirements for traction–slip tasks, stiffness units, thickness mappings, roughness and initialization; no interface benchmark admission |
| `model_annotations.json` | Scientific interpretation of exact formulation snapshots, parameter roles, mechanisms and evidence status |
| `source_formulations/` | Partial primary-source reviews keyed to atlas IDs, including formulations without executable definitions; separate from implementation annotations and admission counts |
| `pilot.json` | Original pressure-development splits, fitting choices, fixed information, numerical controls and budgets |
| `pilot_density.json` | Density-development calibration packages with explicitly separate acquisition-order evaluation |
| `pilot_matched.json` | Equal three-test pressure/density contrast, evaluation cohorts and declared weighting sensitivity |
| `reservations.json` | Development and reserved-final roles, prior exposure and release constraints |
| `development_sources.json` | Pinned mixed archives and the permitted development members |
| `compression_sources.json` | Pinned OE archives with only OE1/OE12 permitted for development extraction |
| `compression_protocol.json` | Source-pinned positive-stress start precedents, first-loading strain-coordinate diagnostics and unresolved initialization gates |
| `compression_sensitivity.json` | Fixed-baseline stress-initialization, strain-coordinate and numerical-resolution development scenarios; no calibration or scenario selection |
| `metadata_conflicts.json` | Competing initial-state source claims and unresolved interpretation |
| `replay_sensitivity.json` | Fixed-parameter, paired initial-state scenarios and numerical refinements |

## Adding a formulation

Source review can precede executable transcription. Store these early records in `source_formulations/`, with the exact variant, discovery route, access limitations, claim-level page locators and unresolved questions. The first example is [the original NorSand source review](source_formulations/norsand-1993.json). A source-only record needs no invented definition hash, state layout or parameter count. Its existence does not admit a formulation to the survey or benchmark, and it does not increase the implementation-annotation count in the manuscript. Link an eventual implementation annotation after its actual definition and conventions have been reviewed; retain the source evidence.

The [HCA source review](source_formulations/hca-sand-2005.json) tests a different evolution coordinate and the distinction between a formulation and its companion calculation. The [interface review](source_formulations/hypoplastic-interface-2016.json) adds traction–slip, thickness and apparatus requirements. These remain partial assisted reviews. `validate_study.py` checks source-review identity, access provenance, claim locators and local snapshot hashes when available; it does not certify the science. Local source PDFs live under ignored `paper/results/sources/` and are not bundled by a Git checkout. Re-download the recorded URL and compare SHA256 before continuing a source review on another machine. A missing PDF is an access gap; a mismatching PDF is rejected. The HCA bibliographic snapshot is also required for its identifier cross-check.

Identify the exact variant and parent relationship before annotating it. Keep publications, formulations, numerical implementations and calibrated material sets distinct. Record the definition path and hash that were examined, along with source locations. A changed hash requests review of the annotation; it does not imply the scientific interpretation necessarily changed.

Start with plain descriptions when a mechanism does not fit an existing term. Extend the vocabulary after several real cases establish a useful distinction. Unknown values must remain unknown rather than being recorded as zero. Keep claimed capabilities separate from reviewed equations, numerical checks and experimental evidence.

Classify every declared constant by its role. Record fitted quantities separately in the study configuration. A constitutive coefficient, a gauge or normalization convention, an integration tolerance, and a fitted specimen state are different inputs even if all appear as numbers in a model definition. Count independently adjustable material quantities only after reviewing constraints and parameterization.

State counts need a declared kinematic scope. The six version-2 annotation records distinguish stored stress, internal fields, bookkeeping, transient multipliers and independent output components within an explicit kinematic scope. The axisymmetric Terracotta case has four scalar internal states, algebraic stress and null full-3D counts. Independent material dimensions remain unknown; a normalization upper bound does not establish identifiability. They do not prescribe how to count every future model. Algebraic stress, constrained tensors, axisymmetric invariants, history events and physical-time fields require explicit interpretations. Document these before comparing dimensions across formulations.

Independent review fields stay empty until a reviewer other than the annotator has actually reviewed the evidence. Passing the input validator does not review the science or change model admission status.

## Adding experimental evidence

Inventory downloaded files separately from sources discovered through provider pages. Preserve original archive and member hashes. Associate metadata with exact test IDs; a range of densities on a provider page is not an initial void ratio for an individual specimen.

For supplemental values, record source, table or equation location, units, reported precision, transformations, and review status. Distinguish nominal protocol values from measured initial observations. Do not interpret printed decimal precision as measurement uncertainty. Source defaults for preparation or geometry need qualifiers when specimen-level deviations have not been checked.

The current pilots intentionally use development drained tests. The reservation was recorded before extracting the additional development members; reserved responses remain excluded from paper commands. Keep related specimens or preparation batches together where independence cannot be justified. Density bands do not establish independent batches.

## Updating a development run

Change and validate the configuration before running. Keep old configurations or their complete copies with the outputs. Use a new output directory and retain failed trials and termination reasons. Never choose parameters, bounds or optimizer starts using the development evaluation score while describing that score as independent of tuning.

When a new atlas representation arrives, update the adapter or add a scoped adapter. The paper analysis consumes loading coordinates, observable channels, run status and provenance; it should not infer them by reaching into an unfamiliar internal-state layout.

## Density-development comparison

`pilot_density.json` keeps the original one-test C1 and three-pressure C2 packages, then adds two 200 kPa tests from other density bands in C_density. Evaluation tests are disjoint from every calibration package. C_density changes both count and density coverage relative to C2, so this nested comparison estimates their combined value. A matched-count design is needed to attribute a change specifically to test diversity.

Calibration uses uniform-strain resampling of monotonic ramps. Evaluation uses the recorded acquisition order for all six tests, with trapezoidal endpoint errors weighted by absolute axial-strain travel. These evaluation aggregates cannot be compared numerically with the earlier pilot's uniform-strain aggregates. The file's measured initial void ratio and effective stress are used in both calibration and evaluation; the original-table void-ratio interpretation is an explicitly separate development sensitivity scenario. That decision preserves the measurements without claiming to resolve the source disagreement.

The density groups, partial hypoplastic calibration, inherited literature constants, optimizer starts and exploratory bounds do not establish an equal-information model ranking or independent-material generalization. Search variability is not experimental or parameter uncertainty.

The matched-count development contrast in `pilot_matched.json` keeps three calibration tests in each package: TMD2/3/4 span pressure at the loosest density band, while TMD3/8/13 span density at nominally 200 kPa. The six current evaluation tests are disjoint from both. This asks whether a three-test laboratory budget is better spent on pressure or density coverage for the declared tasks. It changes the kind of coverage rather than attributing a result to diversity in general, and it does not equalize specimen-preparation effort. The new protocol was recorded before fitting its density3 package, after inspecting the nested development pilot; do not present it as a preregistered final hypothesis.


Its reference package `pressure3` is TMD2/3/4 and its alternative `density3` is TMD3/8/13. Paired changes are alternative minus reference; negative error changes favor density3. Three descriptive evaluation cohorts partition all six evaluation tests: loose (TMD1/5), intermediate (TMD7/9), and higher density (TMD12/14). These are not independently verified preparation batches.

Primary evaluation gives equal weight to stress and volume scaled MSE. Declared stress-weight sensitivity uses 0.25, 0.50 and 0.75 with the fitted parameters held fixed; it tests evaluation aggregation, not recalibration under another objective. The report retains paired test errors, cohort aggregates, completion and same-seed search diagnostics. Missing or failed scheduled cases do not disappear from the contrast. Search seeds are not experimental replicates or posterior draws. Concurrent development runs do not support comparative runtime claims.
