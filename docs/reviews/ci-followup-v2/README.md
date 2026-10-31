# CI follow-up: recorded fixtures and historical source contexts

Repair for [run 41243306056](https://github.com/benjym/constitutive-atlas/actions/runs/41243306056),
testing `6517d642cb897a9c6513d8df55074cac6c418c70`. Work and verification use an
isolated archive of that commit, excluding unrelated active research/browser work.
Original hosted failures and later local failures are retained alongside this note.

## Changes and preserved claims

- The recorded API test derives the complete model list from actual checked model
  definitions rather than expecting five entries. It explicitly supplies the
  illustrative state for each model, respecting the four v0.3 additions' contract.
  It still checks direct-increment equivalence and restart for every model.
- The legacy replay comparison independently verifies the current catalogue hash
  before comparing retained physical behavior. The historical hash remains in the
  retained response. The existing `1e-9` floating comparison now applies when either
  JSON operand is a float, including integer-encoded physical values. Discrete
  integer values remain exact; the opt-in historical exact mode remains unchanged.
- The original sand source report embeds `sys.version`: its original adapter
  therefore rejects a different Python patch/build string. Hosted Python was
  3.14.10 and the original report records 3.14.7. A distinct
  `catalogue/source-replays/source-rates-runtime-v2/` capsule retains every original
  source byte and adds one adapter. Every numerical/report field except runtime
  metadata must still match exactly, and all 11 original test groups still run.
  The outer result records the actual interpreter. Original capsule, output and
  report remain unchanged; no identical-environment/output claim is made for v2.
  Replay errors now include exit status, interpreter and underlying stderr.
- The barodesy finite studies require their original compiler/kernel source hashes.
  The workflow now uses `tools/run_historical_barodesy.py` to materialize the
  explicitly pinned trusted finite-study archive and build its original engine
  with a separately identified minimal CMake driver. One explicit target is built
  serially for native, then Wasm. Original isotropic and wider collectors and
  assessors run unchanged, including raw-transport and persistent-recovery checks.
  Reports are explicitly **historical regression**, not current-engine finite-path
  qualification. Existing current native/Wasm rate, AD, hydro and public-model
  checks remain required, as do all deployment dependencies.

No constitutive equation, model definition, numerical reference, tolerance or
scientific admission gate is changed. This repair does not migrate existing models.

## Reproduction

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
python -B tools/build_ci_targets.py build
PYTHONDONTWRITEBYTECODE=1 ctest --test-dir build --output-on-failure
ATLAS_RECORDED_SOLVER="$PWD/build/atlas_solver" python -B -m unittest tests.test_recorded_api tests.test_recorded_restarts -v
python -B tools/run_historical_barodesy.py --directory /tmp/atlas-historical-barodesy-fresh
```

The last command requires the pinned Emscripten 6.0.8 tools and Node on PATH, and a
fresh destination. On a read-only SDK installation, set `EM_CACHE` to a writable
copy of the installed SDK cache. The first local link failed at the system cache
lock; that failure is retained. The successful run uses a separate temporary cache.

All nine native CTest groups passed in 454.93 seconds, including 1193 Python tests
with 19 existing skips. The 74 recorded-path tests pass on both local Python 3.12
and3.14; 19 isolated focused checks, 15 Python 3.12 checks and 18 shared-checkout
checks pass. Frozen historical native/Wasm assessments pass for 45 isotropic and
48 wider trajectories, and the later current hydro/clay-2014 Wasm stages pass.
All 514 frozen source inputs remain unchanged. Exact outcomes and limits are in
`verification.json`; raw reports/transports are retained compressed under
`historical/` and `remaining-wasm/`. `original-source-bindings.json` identifies
exact-byte archives of each edited prior source.

Hosted Python 3.14.10 and a fresh remote workflow are not claimed by local
verification. No commit, push or remote run is performed.
