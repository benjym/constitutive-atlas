# Constitutive Atlas

A declarative geomechanics model database, C++20 material-point engine, reproducible experiment pipeline, and WebAssembly laboratory.

**[Open the browser laboratory →](https://benjym.github.io/constitutive-atlas/)** · [Model catalogue](https://benjym.github.io/constitutive-atlas/#catalogue) · [Methods & evidence](https://benjym.github.io/constitutive-atlas/#methods)

Authors and maintainers: [Benjy Marks](https://github.com/benjym) and [François Guillard](https://github.com/Franzzzzzzzz).

**This is an initial research implementation, not the completed atlas or a validated engineering package.** Five models execute; the 21-entry catalogue includes sixteen research candidates. SANISAND, the full literature review, controlled calibration/held-out validation, and the final paper remain outstanding. See the [detailed roadmap](ROADMAP.md), [project status](docs/STATUS.md) and [research charter](docs/RESEARCH_CHARTER.md).

## Build and test

Requires Python 3.10+, CMake 3.20+, and a C++20 compiler. The compiler and runtime have no Python/numerical dependencies.

```sh
python3 -m atlas.cli validate
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel 2
ctest --test-dir build --output-on-failure
```

Tests check analytical elastic paths, yield consistency, hardening/unloading, step refinement, initial-state failure/rollback, tensor conventions, interpreter/generated agreement, AD Jacobians, fixed-frame covariance, and data transformations. Source review and numerical verification are separate from experimental validity.

```sh
./build/atlas_solver --list
./build/atlas_solver --describe
python3 -m atlas.cli run benchmarks/elastic-example.json --output artifacts/elastic-run.json
python3 -m atlas.cli database artifacts/atlas.sqlite
```

The authoritative definitions are in [models](models/). [JSON schemas](schemas/) cover model, experiment and run documents. [Architecture](docs/ARCHITECTURE.md) describes the mathematical language and conventions. The [temporal integration design draft](docs/TEMPORAL_INTEGRATION.md) sets out the physical-time extension for Terracotta and its implementation gates. An [experimental v0.2 ODE update](docs/TIME_ODE_API.md) now runs analytical native/Wasm fixtures; an [experimental timed driver](docs/TIMED_SCHEDULES.md) adds mixed component controls, holds and algebraic outputs. Terracotta execution and timed browser controls remain outstanding.

## Browser laboratory

The public website is deployed to [GitHub Pages](https://benjym.github.io/constitutive-atlas/). The verification workflow builds the Emscripten engine, runs native/Wasm parity checks, and uploads only `web/dist`. Deployment from `main` waits for both native CI platforms and the Wasm job to pass; pull requests only build and test. You can also trigger it manually from Actions.

Model source hyperlinks are required in each executable definition and displayed in the laboratory and catalogue. Candidate entries link to discovery references pending review. Each executable card also links to its downloadable JSON definition; the [model schema](https://benjym.github.io/constitutive-atlas/schemas/model.schema.json) is published alongside it.

[Launch the laboratory](https://benjym.github.io/constitutive-atlas/) to edit parameters and initial states, run five loading protocols, inspect model equations and sources, overlay experiments, and import/export reproducible runs. The C++ engine runs in your browser through WebAssembly; no installation or solver server is required.

The laboratory supports built-in experimental tests: select a test, and its processed measurements load automatically. No archive download, extraction or upload is required. **Show measurements** toggles the overlay; **Use initial state & protocol** explicitly applies available initial stresses, void ratio and drainage conditions while preserving material constants and loading history. Local-file comparison remains available under **Compare your own measurements**. Public builds currently include 522 records with 3,094,470 observations from 19 of the 30 screened candidates: OPARA, ten GEOLAB material workbooks, Finnish clay, rockfills, Castlegate, Hurley 3DXRD and four LEAP campaigns. The catalogue separates 49 normalized triaxial overlays, 401 native measurement series and 72 summary tables/populations. Record counts are not independent specimen counts. Each record retains source attribution, its CC BY 4.0 or ODC Attribution 1.0 terms, and interpretation warnings. The 17 original Wichtmann tests remain local-preview only; their public release is pending the evidence recorded in the [data reuse review](docs/DATA_REUSE.md).

The separate [public-source registry](data/public_sources.json) pins original file hashes, licences and attribution. Committed gzip JSON in `data/curated/` retains full reviewed channels and native worksheet observations; the website builds a smaller plot view without sampling. These measurements retain their source licences and are not relicensed under the software's MIT licence. Rebuilding from originals requires optional readers:

```sh
python3 -m pip install '.[data]'
python3 tools/ingest_public_data.py --download
python3 tools/build_web.py
```

The ordinary website build is offline with respect to these curated sources and requires no HDF5, spreadsheet or MATLAB readers. Search the measurement catalogue by material, protocol or ID. Native-source records provide separate X/Y channel selectors and source units; they do not apply simulation initial conditions. GEOLAB principal stresses with unspecified total/effective meaning are archived as reported; effective mean stress and initial state are not inferred. Missing optional channels remain missing. The [30-candidate survey](docs/dataset-survey-2026-10-30.json) tracks every ingestion decision and the eleven remaining access/licence holds, including the user-requested 4TU pause.

Developer build and local preview instructions are in [web/README.md](web/README.md).

## Original experimental data

The source registry [data/sources.json](data/sources.json) pins two original Wichtmann archives. Raw and normalized files are excluded from Git and the hosted site. Source access and redistribution terms are separate questions.

```sh
python3 tools/fetch_data.py
python3 -m atlas.cli ingest data/raw/KFS-TMD1-5.zip
python3 -m atlas.cli ingest data/raw/KFS-TMU-all.zip
python3 -m atlas.cli benchmark benchmarks/kfs-drained.json --output artifacts/kfs-drained.json
```

This imports five drained and twelve undrained triaxial experiments. TMU initial void ratios require source extraction before comparison. The five drained comparisons transfer published KFS hypoplastic constants to the base law over the first 2% strain; they are explicitly a **demonstration**, with no optimization or held-out validation claim. Every result retains input/data/model/solver hashes. Failure and data-interpretation warnings are retained.

## Working manuscript

The editable LaTeX project is [paper/article/main.tex](paper/article/main.tex). The current PDF is generated at `output/pdf/constitutive-atlas-working-draft.pdf`; it is a five-page methods draft with real preliminary results and explicit limitations, not a submission-ready article. Numerical figures/tables are generated, not manually entered.

After generating the benchmark report, install matplotlib if necessary, then:

```sh
python3 tools/paper_results.py
cd paper/article
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

Open `paper/article` in Codex for the source editor and live PDF preview. Original experiments must be downloaded to regenerate the figure; they are not distributed with the source.

## Literature discovery

```sh
python3 -m atlas.cli discover --query 'soil constitutive hypoplasticity critical state model' --rows 50 --output catalogue/discovery/new-search.json
```

Discovery preserves query/cursor/retrieval metadata and raw Crossref responses. It refuses to overwrite evidence. Existing batches contain 50 unscreened search results across soil and rock queries, not 50 admitted models. Use the screening ledger and research charter before promoting a record. The 21 catalogue entries, including the near-term [Terracotta target](docs/models/terracotta-2024.md), are a working shortlist, not a frozen reviewed release manifest.

Original code and original definitions are MIT licensed. Referenced publications, implementations and data retain their own terms.
