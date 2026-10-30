# Constitutive Atlas browser distribution

This directory contains the static material laboratory in the main GitHub repository. The authoritative model definitions, compiler, C++ engine, tests, data tools and manuscript live in the parent research workspace.

Run `python3 tools/build_web.py` from that workspace after native/Wasm tests. It copies this UI, the compiled engine and canonical catalogue into `dist/`. The catalogue hash in the runtime and browser metadata must agree. The publication helper packages `dist/` using `.openai/hosting.json`.

This is an experimental private software preview. Five models are executable; the 20-entry catalogue includes research candidates. No raw Wichtmann measurements are distributed in this site, and no model is described as independently source-reviewed or experimentally validated.

For Sites publication, use a separate Sites checkout and copy this directory plus the freshly generated `dist/` into it. Do not initialize another Git repository inside `web/`. The pre-migration Sites history is preserved locally in `.local/sites-source.git` at the research repository root.
