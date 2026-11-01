# Runnable two-component power creep

The new declarative research identity is
[`power-creep-itasca900-both-active-ode`](../../../../models/research/power-creep/power-creep-itasca900-both-active-ode.json).
It runs through the unchanged common C++/Wasm physical-time engine. The source's
**both-components-active** option is implemented; threshold switching remains
outside this identity. Parameters are illustrative, not a salt calibration.

The [local interactive demo](http://127.0.0.1:8768/) offers relaxation, stress-held
creep, editable coefficients, physical duration, plotted stress/strain and a full
JSON download. It is separate from the public strain-path laboratory and has not
been deployed. The server binds only loopback and serves only the named demo and
engine resources.

## Run it

The qualified artifacts currently reside in
`/private/tmp/atlas-power-creep-execution-v1/`. The browser server was left running
at port8768. To restart it:

```sh
python3 tools/serve_power_creep.py \
  --build /private/tmp/atlas-power-creep-execution-v1/wasm \
  --catalogue docs/ingestion/power-creep-itasca900/execution-v1/frozen/generated/models.json \
  --port 8768
```

The server checks the generated catalogue against the current isolated model
before starting. The page checks each response's catalogue identity. Downloads
include model/module/Wasm hashes and the full explicit timed API request.

Run a timed JSON example from the repository root:

```sh
python3 -m atlas.cli run \
  docs/ingestion/power-creep-itasca900/execution-v1/examples/creep.json \
  --solver /private/tmp/atlas-power-creep-execution-v1/native/atlas_power_creep_solver \
  --output /private/tmp/power-creep-result.json
```

Replace `creep.json` with `relaxation.json` for a strain hold. CLI output includes
the complete original specification and can be supplied to the same command for
replay. The [saved creep specification/result](examples/creep-result.json) replays
exactly, including full state and diagnostics. Browser downloads instead contain
an explicit `atlas_run_schedule` request; [the browser replay receipt](browser-report.json)
records the equivalent native command and physical parity.

To build from the current checkout, use the new opt-in isolated target:

```sh
cmake -S . -B build-power-creep-native -DCMAKE_BUILD_TYPE=Release
cmake --build build-power-creep-native --target atlas_power_creep_solver --parallel 1

emcmake cmake -S . -B build-power-creep-wasm -DCMAKE_BUILD_TYPE=Release
cmake --build build-power-creep-wasm --target atlas_power_creep_solver --parallel 1
python3 tools/serve_power_creep.py --build build-power-creep-wasm --port 8768
```

Run native and Wasm builds serially. The root target is excluded from default
builds. It generates only `models/research/power-creep/*.json`; it does not
replace the public catalogue. If the installed Emscripten cache is read-only,
copy it to task-owned writable storage and set `EM_CACHE` to that directory,
with `EMCC_CORES=1`. The retained successful cache retry used
`/private/tmp/atlas-power-creep-execution-v1/emcache`. No protection was disabled.

For exact-source reproduction, replace `-S .` with
`-S docs/ingestion/power-creep-itasca900/execution-v1/frozen` and pass
`--catalogue docs/ingestion/power-creep-itasca900/execution-v1/frozen/generated/models.json`
to the demo server. This is the minimal project actually qualified here. The
root target was separately configuration-checked; it uses the same compiler,
model and common engine source.

## Definition and numerical choices

The [prospective plan](PLAN.md) records the source decisions before compilation:
Eq.(2)'s deviator projection, elastic volume, both active mechanisms, explicit
normalization `b_i=A_i*p_ref^n_i`, and the continuous zero-stress extension for
`n_i>=1`. The full explicit v0.3 formulation binds an effective Cauchy stress
observable only for an uncoupled zero-pore-pressure, small-strain, fixed-frame,
zero-spin host. No large-rotation or vendor finite-step equivalence is claimed.

State is exactly six persistent Mandel stresses. No void ratio or hidden strain
history was added. Timed schedules separately accumulate strain and solve stress
controls. All examples supply the state, parameters, time and initial rate
explicitly. `initialization.json` records typed initialization. `time_scale`
affects only the creep-rate observable's numerical scale, not evolution.

Direct time updates use the existing adaptive midpoint integrator. Mixed-control
schedules use the existing backward-Euler/step-doubling Newton solver. Their
local error estimates are not global accuracy guarantees. The two example files
retain ordinary illustrative settings; the qualification study separately fixes
stricter settings and analytical endpoint budgets.

## Verification and retained failures

- Full model structural, dimensional and semantic validation passes; typed
  initialization and both example schedule contracts pass.
- Nine interpreter source-rate/replay cases pass against independent Cartesian
  references, including shear, zero stress, sign reversal and noninteger powers.
- The original [native study v1](native-report.json) is **failed:22/27**. Three
  direct-update checks missed the0.06Pa global budget by about0.006–0.024Pa;
  two schedule checks missed the15Pa budget by about3.4–4.6Pa. All original
  inputs, assessor, raw observations and failures are retained.
- A separately frozen [refinement v2](refinement-v2/PLAN.md) tightens only temporal
  tolerances by100. It preserves all physical inputs, equations, references,
  accuracy budgets and limits. [Native27/27](refinement-v2/native-report.json)
  and [Wasm27/27 plus parity](refinement-v2/wasm-report.json) pass. Wasm runs all
  calls in one instance, including failures followed by recovery and replay.
- Checks include exact mixed linear/cubic relaxation, constant-rate loading,
  nonlinear stress-held creep with a general tensor, hydrostatic behavior,
  Newton loading from the origin, invalid duration/exponent/state rejection,
  and full state/clock rollback after accepted partial work.
- One serial native target builds successfully. The first serial Wasm attempt
  failed while locking the installed Emscripten cache. Original logs remain;
  a retry using a writable private cache succeeds. No equations or gates changed.
- Both timed CLI examples complete10s. Saved-specification replay is exactly
  equal. The [actual browser receipt](browser-report.json) records relaxation,
  creep, JSON export, native replay of all22exported points and exact engine
  hashes. In the browser,10s relaxation takes q from0.3000 to0.1436MPa;
  stress hold keeps q at0.3000MPa and accumulates0.6270%axial strain.

Reapply frozen gates without rebuilding:

```sh
python3 tools/power_creep_refined_study.py verify-freeze
python3 tools/power_creep_refined_study.py assess \
  --output docs/ingestion/power-creep-itasca900/execution-v1/refinement-v2/native
python3 tools/power_creep_refined_study.py assess \
  --output docs/ingestion/power-creep-itasca900/execution-v1/refinement-v2/wasm \
  --native docs/ingestion/power-creep-itasca900/execution-v1/refinement-v2/native
```

For new observations, choose a fresh output directory; do not overwrite the
retained receipts. `tools/power_creep_study.py` collects native API calls and
assesses independent references; `tools/collect_power_creep_wasm.mjs` uses the
same frozen requests in one module instance. `power_creep_refined_study.py`
selects the separately frozen refined study without changing the original tool.
The [freeze](freeze.json), [revised freeze](refinement-v2/freeze.json) and final
`manifest.json` bind exact source, reference, artifacts and results.

## Remaining scope

The draft is executable and technically qualified for these bounded cases. The
original thresholded family, crossing/equality policies, sublinear exponents,
finite rotation, pore-pressure coupling, source-specific calibration, vendor
algorithm reproduction, independent scientific review and experimental admission
remain open. The original [ingestion source gaps](../README.md) remain unchanged.
Public website integration of generic timed controls is a separate task; this
local demo adds no draft to the ordinary strain-path selector.

Owned additions: the model directory, four dedicated tools, standalone
`web/power-creep.html`, additive CMake target, this execution packet and its board
row. Shared compiler/schema/material algorithms are unchanged. Concurrent
Maxwell/Burgers work and unrelated files are preserved. No commit, push, public
hosting or deployment was performed.
