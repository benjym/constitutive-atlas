# Constitutive Atlas browser distribution

This directory contains the static material laboratory in the main GitHub repository. The authoritative model definitions, compiler, C++ engine, tests, data tools and manuscript live in the parent research workspace.

Run `python3 tools/build_web.py` from that workspace after native/Wasm tests. It copies this UI, the compiled engine and canonical catalogue into `dist/`. The catalogue hash in the runtime and browser metadata must agree. GitHub Actions publishes `dist/` to GitHub Pages after native and Wasm verification. All asset URLs are relative to support the `/constitutive-atlas/` project path. Source references, model JSON definitions, and schemas are bundled; raw measurements are excluded. The optional Sites publication helper also packages `dist/` using `.openai/hosting.json`.

The [public GitHub Pages laboratory](https://benjym.github.io/constitutive-atlas/) is an experimental research preview. Five models are executable; the 21-entry catalogue includes research candidates. No raw Wichtmann measurements are distributed in this site, and no model is described as independently source-reviewed or experimentally validated.

For Sites publication, use a separate Sites checkout and copy this directory plus the freshly generated `dist/` into it. Do not initialize another Git repository inside `web/`. The pre-migration Sites history is preserved locally in `.local/sites-source.git` at the research repository root.

## Developer build and local preview

Requires Emscripten (tested with 6.0.8). From the repository root:

```sh
EM_CACHE="$PWD/.cache/emscripten" emcmake cmake -S . -B build-wasm -DCMAKE_BUILD_TYPE=Release
EM_CACHE="$PWD/.cache/emscripten" cmake --build build-wasm --parallel 2
node tools/test_wasm.mjs
python3 tools/build_web.py
python3 -m http.server 8765 --bind 127.0.0.1 --directory web/dist
```

Open <http://127.0.0.1:8765> for development. The native build must exist before running the parity check. Packaging rejects stale model definitions.

## Experimental overlays

Load one or more original Wichtmann `TMD*.dat` / `TMU*.dat` files after extracting the provider archives, or normalized Atlas experiment JSON. The selector switches tests; **Show experimental data** toggles measured points without rerunning the solver. Clear removes the loaded collection from the application. No file is uploaded. Other original formats require a reviewed importer. See [data reuse review](../docs/DATA_REUSE.md); measurements are excluded from the public build pending permission.

Run `node tools/test_experiments.mjs` from the repository root to verify browser import mappings and visibility semantics.
