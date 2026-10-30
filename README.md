# Constitutive Atlas

A declarative geomechanics model database, C++20 material-point engine, reproducible experiment pipeline, and WebAssembly laboratory.

Authors and maintainers: [Benjy Marks](https://github.com/benjym) and [François Guillard](https://github.com/Franzzzzzzzz).

**This is an initial research implementation, not the completed atlas or a validated engineering package.** Five models execute; the 20-entry catalogue includes fifteen research candidates. SANISAND, the full literature review, controlled calibration/held-out validation, and the final paper remain outstanding. See [project status](docs/STATUS.md) and the [research charter](docs/RESEARCH_CHARTER.md).

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

The authoritative definitions are in [models](models/). [JSON schemas](schemas/) cover model, experiment and run documents. [Architecture](docs/ARCHITECTURE.md) describes the mathematical language and conventions.

## Browser laboratory

The public website is deployed to [GitHub Pages](https://benjym.github.io/constitutive-atlas/). The verification workflow builds the Emscripten engine, runs native/Wasm parity checks, and uploads only `web/dist`. Deployment from `main` waits for both native CI platforms and the Wasm job to pass; pull requests only build and test. You can also trigger it manually from Actions.

Model source hyperlinks are required in each executable definition and displayed in the laboratory and catalogue. Candidate entries link to discovery references pending review. Each executable card also links to its downloadable JSON definition; the [model schema](https://benjym.github.io/constitutive-atlas/schemas/model.schema.json) is published alongside it.

Requires Emscripten; tested here with 6.0.8. Use a workspace-local cache when the installed SDK directory is not writable.

```sh
EM_CACHE="$PWD/.cache/emscripten" emcmake cmake -S . -B build-wasm -DCMAKE_BUILD_TYPE=Release
EM_CACHE="$PWD/.cache/emscripten" cmake --build build-wasm --parallel 2
node tools/test_wasm.mjs
python3 tools/build_web.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory web/dist
```

Open <http://127.0.0.1:8765>. The app runs the generated C++ engine in a Worker, supports cancellation, parameter/state editing, five laboratory protocols, model/source inspection, experimental overlays, and reproducible run import/export. No solver server is required. The browser catalogue hash must match the Wasm build; packaging rejects stale definitions.

The [private preview](https://geomechanics-constitutive-atlas.creamyjoy12.chatgpt.site) requires its owner's ChatGPT sign-in and is managed through the Sites project recorded in `web/.openai/hosting.json`. Publishing does not establish a scientific release or make the site public. Rebuild and use the Sites workflow from a separate Sites checkout for future deployments; see [browser distribution instructions](web/README.md). The authoritative source repository is [benjym/constitutive-atlas](https://github.com/benjym/constitutive-atlas).

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

Discovery preserves query/cursor/retrieval metadata and raw Crossref responses. It refuses to overwrite evidence. Existing batches contain 50 unscreened search results across soil and rock queries, not 50 admitted models. Use the screening ledger and research charter before promoting a record. The first 20 candidate entries are a working shortlist, not a frozen reviewed release manifest.

Original code and original definitions are MIT licensed. Referenced publications, implementations and data retain their own terms.
