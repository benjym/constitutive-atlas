# Constitutive Atlas

Explore geomechanical models and compare their response with laboratory measurements. A C++20 material-point engine runs directly in your browser through WebAssembly.

**[Open the laboratory →](https://benjym.github.io/constitutive-atlas/)** · [Model catalogue](https://benjym.github.io/constitutive-atlas/#catalogue)

- Adjust model parameters and loading conditions with live response plots.
- Compare with built-in measurements or load your own files locally.
- Inspect equations, source references and data attribution; export reproducible runs.

**Research software.** Model coverage, source review and experimental validation are ongoing. See the [project status](docs/STATUS.md) and [roadmap](ROADMAP.md) for current capabilities and limitations.

## Build and test

Requires Python 3.10+, CMake 3.20+ and a C++20 compiler.

```sh
python3 -m atlas.cli validate
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --target atlas_solver --parallel 1
cmake --build build --target atlas_numerical_tests --parallel 1
python3 -B tools/check_current_numerical_ci.py --build build --output build/current-numerics
```

For the browser build, see [web/README.md](web/README.md) (Node.js 24 and Emscripten required).

## Continuous integration

**Fast CI** validates today's model definitions and browser contracts. On code changes and pushes to `main`, it runs the current ordinary catalogue on native and Wasm, compares the histories within tolerance, and runs targeted checks against independent numerical references. For a model with no named example, the sweep uses the default drained test. Dedicated schedule and material-point engines have their own targeted tests in the same workflow. The schedule regressions use representative cases from the independent references; the manual studies retain the full matrices.

**Publish Pages** reuses the tested ordinary Wasm engine from Fast CI, builds the other engines needed by the site, and smoke-tests the package in Chromium before deploying that artifact.

For exact historical reproduction, manually run **Historical research replays** or **Controlled physical time research replay**. Both use the archived source revision, with its original checks and checksums. The original broader study commands are in the [retired workflow at its last revision](https://github.com/benjym/constitutive-atlas/blob/41122c0a478372d589496e41310dd62f5bdc5425/.github/workflows/qualification.yml). Run the independent package studies with **Publish Pages → replay_studies** (no deploy), or locally by building the site without `--package-checks-only`.

## Published benchmark

Reproduce the fixed Karlsruhe fine sand TMD2 calculation locally (Python, CMake, C++20 and Matplotlib):

```sh
python3 -m pip install -e '.[benchmark]'
python3 tools/benchmark_tmd2.py --output /private/tmp/tmd2-local-reproduction
```

The command downloads the pinned source data, builds the archived Atlas solver serially, runs three resolutions and generates the figure, error table and receipts. [Benchmark guide and limitations](docs/benchmarks/kfs-tmd2-portable-v1/README.md). Original measurements remain local; their public redistribution terms are unresolved.

## Documentation

- [Live implementation board](IMPLEMENTATION_PLAN.md) — task status, owners, bounded scope and handoffs.
- [Full model-delivery checklist](docs/MODEL_DELIVERY_CHECKLIST.md) — E0–E8, from source acquisition and schema to solver qualification, independent agent review and the live atlas.
- [New-model agent assignment](docs/ingestion/AGENT_ASSIGNMENT_TEMPLATE.md) — copyable brief, stage outputs, integration responsibilities and handoff format.
- [Delivery ledger template](docs/ingestion/DELIVERY_TEMPLATE.md) — copy to `docs/ingestion/<model-id>/DELIVERY.md`; track `[ ]` unstarted, `[-]` working/blocked and `[X]` verified complete with evidence.
- [Agent instructions](AGENTS.md) and [source-packet template](docs/ingestion/TEMPLATE.md) — ownership, coordination and the source-ingestion subtask.
- [Models](models/) and [schemas](schemas/) — authoritative definitions and file formats.
- [Architecture](docs/ARCHITECTURE.md) — engine design, mathematical language and conventions.
- [Formulation contract](docs/FORMULATION_CONTRACT.md) — explicit equation, kinematic and stress-output semantics; v0.3 schema and migration.
- [Experimental data](docs/DATA_REUSE.md) — sources, attribution and reuse terms.
- [Local storage](docs/STORAGE.md) — artifact consolidation, evidence preservation and disk usage.
- [Literature screening](docs/LITERATURE_SCREENING.md) — discovery and review process.
- [Working manuscript](paper/article/main.tex) and [research charter](docs/RESEARCH_CHARTER.md).

By [Benjy Marks](https://github.com/benjym) and [François Guillard](https://github.com/Franzzzzzzzz).

Original code and model definitions are [MIT licensed](LICENSE). Publications, third-party implementations and experimental data retain their own terms.
