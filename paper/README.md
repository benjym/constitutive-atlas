# Constitutive Atlas paper

The planned paper asks which constitutive ingredients improve prediction, under which loading conditions, and at what calibration cost. Start with [the paper plan](PLAN.md) for the scientific questions, study design, proposed figures, and milestones.

The study assumes a future collection of 50+ source-pinned formulations. This is a planning target, not a count of currently verified models. The [LaTeX manuscript](article/main.tex) now develops the scientific questions, comparison methods and explicitly labelled development evidence. The original software and transfer-demonstration draft is preserved in [implementation-note.tex](article/implementation-note.tex). [The development work package](DEVELOPMENT.md) records what can be done while model representations evolve.

The [dataset information hunt](study/dataset_information_hunt.md) identifies recovered metadata and the remaining questions that affect benchmark use. The [methods download log](study/dataset_methods_downloads.json) records the bounded LEAP-2022/GEOLAB retrieval, local paths and source hashes. [Clarification requests](study/dataset_clarification_questions.json) are retained on hold; contacting people or submitting copy requests is not authorized. The [torsion phase correspondence](study/torsion_acquisition_correspondence.json), [torsion processing formulas](study/torsion_processing_formulas.json), [torsion workbook extraction](study/torsion_workbook_metadata.json), [Ottawa source metadata](study/ottawa_source_metadata.json) and [Hostun source conflicts](study/hostun_source_metadata.json) preserve source hashes and unresolved mappings.

The [LEAP-2022 methods review](study/leap2022_methods_review.md) processes the additional downloads: state timing, static-shear preloading, apparatus compliance, plotting conventions and source conflicts. Its [54-row state transcription](study/leap2022_specimen_metadata.json) retains nominal-condition filename candidates without granting benchmark admission. Regenerate with `python3 paper/scripts/extract_leap2022_metadata.py`; it reads no raw response CSVs.

The [development assumption register](study/assumption_proposal.md) records the approved core A01-A07; optional scenarios B01-B02 remain pending. The [DSS core configuration](study/leap2022_core_development.json) prepares32 byte-verified source/header contracts and four initial-stress scenarios per candidate. It retains one campaign dependency block and grants no benchmark admission. The [approved compression configuration](study/compression_sensitivity_approved_core.json) adds the same initial-stress scenarios to the existing fixed-parameter diagnostic, preserving earlier runs and configurations. No contacts are authorized.

The [approved-core progress report](study/approved_core_progress.md) records the32-file header audit and192 successful fixed-parameter compression replays. Simple-shear adapter admission remains a separate implementation gate.

The [source reconciliation](study/source_reconciliation_2026-10-31.md) and [Ottawa cyclic panel design](study/ottawa_cyclic_protocol.md) carry the latest collection expansion into the paper. Regenerate the source/phase metadata map with `python3 paper/scripts/inventory_ottawa_cyclic.py`; this command opens no response assets.

Start with the work-package table in `DEVELOPMENT.md`: scientific annotations, experimental evidence, protocol design and small pilots can proceed independently of schema changes. The executable density extension now declares acquisition-order evaluation and file-based initialization; a separate fixed-parameter diagnostic quantifies initial-state source sensitivity. Reserved final responses are excluded from development commands by `study/reservations.json`.

The immediate priorities are scientific/source review, explicit calibration-information accounting and one defensible end-to-end development comparison. See [the priorities and schema revision rules](DEVELOPMENT.md#immediate-priorities-with-a-small-collection). The schema can evolve behind the paper adapter; scientific changes require review and new run identities.

The matched-count design in `study/pilot_matched.json` compares three pressure-spanning with three density-spanning calibration tests. Its paired report includes individual tests, descriptive cohorts, evaluation-weight sensitivity and search-start diagnostics. Commands and interpretation limits are recorded in `DEVELOPMENT.md`.

The [positioning audit](study/positioning.md) records the closest literature precedents and source access. The [information protocol](study/information_protocol.md) specifies the decisions needed before a common-information benchmark; `study/calibration_information.json` records fixed and fitted inputs in the current development configurations. Validation checks those partitions and configuration hashes without changing the archived fits.

The [survey search and screening protocol](study/survey_protocol.md) now has a pinned eight-theme bibliographic pilot and source-located assisted title decisions. Publication deduplication is separate from formulation identity and benchmark admission. Run `python3 paper/scripts/audit_survey_discovery.py` to audit the saved retrieval and screening links; further full-text and search work remains open.

The [compression sensitivity study](DEVELOPMENT.md#fixed-parameter-compression-sensitivity) now separates assumed initial lateral stress, strain mapping and numerical refinement on two selected first-loading records. It retains 144 fixed-parameter development replays and an audited curve figure. The results expose initialization and convention sensitivity; they do not select a physical assumption or admit compression to the primary benchmark.

## Repository organization

Keep paper-specific code, configurations, analysis, and manuscript assets under `paper/`. Reuse the shared atlas APIs and solver; reusable model implementations, experiment ingestion, and solver improvements remain in their existing repository locations.

| Path | Purpose |
| --- | --- |
| `PLAN.md` | Scientific scope, protocols, manuscript outline, and completion gates |
| `article/` | Editable LaTeX manuscript and generated figure and table inputs |
| `scripts/` | Paper-specific orchestration and figure and table generation |
| `study/` | Development inventory, scientific annotations, and explicit pilot configuration; later frozen manifests |
| `analysis/` | Paper-specific analysis and an adapter for current atlas interfaces |
| `tests/` | Scientific controls, inverse-problem checks, and native adapter verification |
| `results/` | Ignored local audit reports, calibration outputs, figures, and provenance |

Keep raw experiments in the existing data store and reference them by ID and hash. Do not maintain tracked duplicate measurements or constitutive definitions in the paper directory. Ignored run snapshots retain exact inputs for recovery while the shared worktree evolves.

Commit study manifests, source code, and dependency specifications. `paper/.gitignore` excludes generated results and caches; the current generated manuscript images and table are also ignored. An archival release should include the reviewed manifests and the outputs needed to reproduce the published claims, subject to data reuse terms.

## Run the development work package

The data audit, calibration and tests use Python 3.10+ standard-library modules. Plotting requires matplotlib, declared in `requirements.txt`. Fetch and ingest the two existing source archives and build `build/atlas_solver` using the repository instructions first. The adapter rejects compiled models that differ from their current definitions.

```sh
python3 paper/scripts/validate_study.py
python3 paper/scripts/audit_data.py
python3 paper/scripts/audit_public_feasibility.py
python3 -m unittest discover -s paper/tests -v
python3 paper/scripts/run_pilot.py --output paper/results/pilot-frozen96
python3 paper/scripts/run_pilot.py --max-evaluations 384 --output paper/results/pilot-frozen384 --solver paper/results/pilot-frozen96/solver/atlas_solver --model-dir paper/results/pilot-frozen96/models
python3 paper/scripts/report_pilot.py --comparison paper/results/pilot-frozen384/report.json
```

Each run executes its archived solver and model snapshot, so concurrent atlas changes do not alter it. The sensitivity command reuses the baseline snapshot to preserve identical inputs across budgets. For deliberate reruns, use new output directories and pass the resulting `report.json` files with `--report` and `--comparison` to the reporting command. Incomplete runs retain a journal; no command overwrites an existing calibration directory. The final command writes a generated Markdown report, JSON summary and two diagnostic figures to `paper/results/diagnostics/`.

These runs develop the protocol on already inspected tests. They do not establish a final evaluation set, a model ranking, or independent equation review. See `DEVELOPMENT.md` for initialization assumptions, partial calibration, optimizer limits, data gaps, and the decisions needed before a controlled study.

The public feasibility audit uses the shared curated loader and writes `results/public-feasibility/report.json` and `.md`. It checks minimum field availability and preserves warnings; it does not admit data to the benchmark. See [the interpretation and next data decisions](study/data_feasibility.md). It rejects reserved or unassigned KFS IDs before loading curated response assets.

## Regenerate the scientific manuscript

After producing the matched-count reports, contrasts and fixed-parameter compression sensitivity report described in `DEVELOPMENT.md`, run:

```sh
python3 paper/scripts/generate_manuscript_inputs.py
```

The generator checks annotation hashes and frozen run inputs, recomputes the paired contrasts, and writes tables, a figure and a provenance manifest under ignored `article/generated/`. The compression table also checks archived baseline constants and full scenario coverage; `--compression-report PATH` selects a deliberate rerun. It does not recalibrate models. Compile `article/main.tex` twice from `paper/article/`, or use the LaTeX editor. The local PDF preview is `results/manuscript-preview/main.pdf`; generated inputs require the pinned local run records and are not yet an archival release.

The manuscript's NorSand and HCA source examples use the provisional records under `study/source_formulations/`. The generator validates their publication identities and adds review files and available source snapshots to its provenance manifest. These examples remain outside the implementation table and benchmark; their access and review limitations stay in the source records.

The bibliographic screening counts also regenerate from the paper survey ledger after auditing the pinned discovery responses and publication locators. The output manifest includes the search protocol, ledger, raw responses, headers and archived retrieval inputs. These are bounded assisted screening counts, not admitted formulation counts or completed systematic-search coverage.

## Regenerate the original demonstration

From the repository root, first follow the main README to obtain and normalize the source data, build the solver, and create `artifacts/kfs-drained.json`. With matplotlib available, run:

```sh
python3 paper/scripts/generate_transfer_demo.py
```

An alternative benchmark report can be selected with `--report PATH`. The generator writes `article/results.tex` and `article/images/transfer.png`. These describe the existing published-parameter transfer demonstration and must not be relabelled as held-out validation.

Compile `article/implementation-note.tex` using the LaTeX editor or run `pdflatex -interaction=nonstopmode -halt-on-error implementation-note.tex` twice from `paper/article/`. The standalone generator previously lived at `tools/paper_results.py`.

## Analysis conventions

Run paper scripts from the repository root and resolve repository resources from the script location. Record all study inputs and solver versions in output manifests. Manuscript numbers and scientific plots must be generated from result records; do not manually enter benchmark findings into LaTeX. Keep exploratory runs separate from frozen confirmatory results, and retain failed runs.
