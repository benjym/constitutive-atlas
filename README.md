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
cmake --build build --parallel 1
ctest --test-dir build --output-on-failure
```

For the browser build, see [web/README.md](web/README.md) (Node.js 24 and Emscripten required).

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
- [Delivery ledger template](docs/ingestion/DELIVERY_TEMPLATE.md) — copy to `docs/ingestion/<model-id>/DELIVERY.md`; track `[ ]` unstarted, `[-]` working/blocked and `[X]` verified complete with evidence.
- [Agent instructions](AGENTS.md) and [source-packet template](docs/ingestion/TEMPLATE.md) — ownership, coordination and the source-ingestion subtask.
- [Models](models/) and [schemas](schemas/) — authoritative definitions and file formats.
- [Architecture](docs/ARCHITECTURE.md) — engine design, mathematical language and conventions.
- [Formulation contract](docs/FORMULATION_CONTRACT.md) — explicit equation, kinematic and stress-output semantics; v0.3 schema and migration.
- [Experimental data](docs/DATA_REUSE.md) — sources, attribution and reuse terms.
- [Literature screening](docs/LITERATURE_SCREENING.md) — discovery and review process.
- [Working manuscript](paper/article/main.tex) and [research charter](docs/RESEARCH_CHARTER.md).

By [Benjy Marks](https://github.com/benjym) and [François Guillard](https://github.com/Franzzzzzzzz).

Original code and model definitions are [MIT licensed](LICENSE). Publications, third-party implementations and experimental data retain their own terms.
