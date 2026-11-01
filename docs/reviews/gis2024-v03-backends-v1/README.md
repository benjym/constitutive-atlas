# GIS2024 v0.3 isolated backend qualification

NUM-gis2024-v03-backends-v1, 1 November 2026. **Native, Wasm and full-state parity
pass the unchanged prospective gates** for the selected research artifact.
This closes isolated backend qualification, not scientific admission, arbitrary
boundary support, public installation or experimental validation.

## Frozen identity and controls

The [candidate/input/policy freeze](../gis2024-v03-research-freeze-v1/README.md)
binds the distinctly named v0.3 HP/extracted-ASBS+GIS pairing of
[Mugele, Stutz & Mašín (2024)](https://doi.org/10.1016/j.compgeo.2024.106480).
All14persistent components are carried: sigma6,e,h6,Omega. The
[source/formulation packet](../../ingestion/hypoplastic-generalized-igs-2024/README.md)
records equation locators, paper hyperlinks, preparation and domain limitations.
No model equation, tolerance, acceptance gate or original evidence was changed.

`execution-freeze.json` pins the driver, independent assessor, normal source
staging, native transport and20passing synthetic preflight tests before builds.
The saved-reference audit recomputes32channel differences from retained16/32/64
RK grids and checks source/dependency/input identities; no ODE is rerun.
After native acceptance, `parity-freeze.json` pins five additional synthetic
corruption tests and the full-state comparator before Wasm build/observations.
Synthetic interpolated fixtures test assessors only; they are not model evidence.

## Actual execution and result

| Check | Native | Wasm |
| --- | --- | --- |
| Four paths, five tolerance/partition settings | 20 complete trajectories | 20 complete trajectories |
| Base caller updates, own state carried | 204 | 204 |
| Same-context plus fresh-context restart suffix updates | 272 | 272 |
| Negative/zero/late-budget probes | 9 pass | 9 pass |
| Immediate valid recovery in persistent context | 9 pass | 9 pass |
| Raw descriptor/call receipts | 516 | 516 |

Each backend makes495material C-API calls (476trajectory/restart, one clean
control, nine probes and nine recoveries), plus21descriptor calls. All raw
responses are written before parsing/assessment. No reference history is injected.
At each trajectory's first original endpoint, both restart suffixes use the
backend's complete captured14state and reproduce the original suffix exactly.
The late-budget failure reports accepted internal work and returns all incoming
history unchanged. Zero increment returns the exact full state. All declared
source-domain failures and malformed state/parameter requests reject.

The independent saved-output assessor checks literal request and settings echoes,
canonical catalogue identity, ordered full coverage, raw receipt binding,
independent selected-domain checks at every returned point, all14endpoint
accuracy, exact density closure, temporal and caller-partition refinement,
rollback, persistent recovery and fresh-process/module restart. It imports the
independent Cartesian instantaneous oracle, not Atlas/compiler/solver code, and
performs no constitutive integration. It does not expose every internal stage.

Both volume-error maxima are3.3307e-16. Parity covers493returned states and their
incoming histories; malformed response envelopes are checked separately. The
maximum scaled native/Wasm full-state difference is1.2474e-16 under the unchanged
1e-7bound. Stress is scaled by each request's p_scale, memory by R, scalars by1;
this is not a relative stress error. See separate assessments for every trajectory.

## Persistent native transport and builds

The usual native CLI starts a new process per request. `runner.cpp` therefore
provides a **test-only** line entrypoint around the unmodified production
`atlas_describe` and `atlas_integrate_with_settings` functions. It includes
`cpp/main.cpp` with its CLI main renamed; no material equation, solver operation
or state projection is implemented in the runner. The staged CMake change only
selects this entrypoint for the existing atlas_solver target. `native-stage.json`
binds original/staged CMake and runner hashes. Production repository CMake/C++
files are unchanged. Native fresh-context checks launch separate runner processes.

Wasm uses the normal cpp/main.cpp/atlas_solver Emscripten target and its existing
C ABI. `wasm_line.mjs` keeps one live module per process and instantiates fresh
modules in separate processes for restart checks. Each context's PID, request
line, raw response and stderr log is retained.

Native and Wasm each build serially, one explicit atlas_solver target with
--parallel1. Toolchain/build/source/artifact receipts are retained. The initial
Wasm link failed because sandbox permissions denied the normal Homebrew
Emscripten cache lock. Its exact failure is preserved in `wasm-build.json`.
The identical target then linked successfully with ordinary toolchain cache
access; no source, settings or numerical gate changed. This was a build failure,
not an omitted numerical outcome. Binaries remain private; their hashes and
compile/link flags are recorded in `build-artifacts.json`.

## Saved-only reproduction

```sh
python3 docs/reviews/gis2024-v03-backends-v1/verify.py
```

The verifier checks original freezes and final packet hashes, safely unpacks
native/wasm evidence into temporary directories, rebinds all1032raw receipts,
replays each unchanged backend assessor and full-state parity, and repeats the
saved-reference audit. It never runs a binary or integrates a model.
Raw receipts, full results, partial checkpoints, stderr logs and per-backend
assessments are inside the two evidence archives. Small standalone assessment
files support review without extracting them.

To deliberately rerun, stage a new exclusive directory with `stage.py`, build
one explicit target serially, and invoke `driver.py` with backend/executable/new
output directory. An independent assessor is a mandatory separate step; driver
exit0 alone means transport completion. Preserve every failed report. Wasm must
not run before native qualification. The original frozen policy remains binding.

## Next bounded task and limits

Freeze mixed-catalogue compatibility for the ten existing public drafts plus this
new research definition, retaining explicit history initialization and scope.
Only after compatibility and a separately reviewed browser/preparation plan should
local draft installation be considered. No push/deployment is authorized here.
No unreviewed default should be presented as a source-prepared specimen.

The selected host, f=0, rate independence, effective stress, zero spin and
small-strain restrictions remain. Strict computed-memory-norm boundary rejection,
representability/suppression limits, ASBS singular neighborhoods, wider parameter
and loading coverage, complete-update tangents, author-release/license/algorithm
reconciliation and independent scientific review remain open. This bounded
numerical pass does not admit the entire GIS family or validate Wichtmann data.
