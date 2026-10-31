# CI portability and preserved evidence repair

This repair addresses failed [run 41233149000](https://github.com/benjym/constitutive-atlas/actions/runs/41233149000), after website commit `14e1631`. The original failure counts and case names remain in `original-failure-summary.json`. Earlier CI also failed exact numerical replay; the Methods page did not introduce those numerical differences.

## Changes

- Use Node's operating-system temporary directory for the browser loading wire fixture.
- Resolve historical source and model assertions against their original hash-pinned bytes. Add content-addressed snapshots and archive bindings, preserving original reports, receipts and prior archive-map bytes. The approved Drucker–Prager domain change is verified separately from its historical definition.
- Derive screening publication identity from the actual publication graph and screening records instead of a fixed count.
- Give the synthetic archived optimizer accounting test its exact original project Python sources, checked against their original code hashes. This fixture contains no private observations, parameter data or binaries and does not require the untracked `paper/` tree.
- Suppress bytecode generation so source packet inventories do not gain cache files.
- Build serially with one explicit CMake target per command.

## Runtime policy

The retained exact JSON, decimal argument and finite-difference references reproduce with macOS arm64 and Python 3.14. Python 3.12 differs even on macOS for the source-rate capsule replay. Required native and full Wasm reference jobs therefore use `macos-26` and Python 3.14. Their numerical tests are unchanged; no tolerance, reference output, constitutive model, kernel or admission policy is relaxed.

Linux remains required for native tests, the portable Python suite, browser/native Wasm parity and the packaged website. `tools/ci_exact_replays.json` explicitly enumerates 31 runtime-bound test IDs. The Linux runner records those as skipped, rejects unknown or duplicate policy IDs, and retains all other discovered tests. Every listed test still runs unchanged in the required full macOS suite. Deployment requires both native matrix entries, the full Wasm job and the Linux Wasm job.

## Verification

Verification uses a clean `git archive` of `71910d2` with only the repair files overlaid. It excludes the private/untracked `paper/` tree. Before the build and test run, 509 source and fixture hashes were frozen; they were rechecked against both the clean build snapshot and working checkout without differences.

The build uses Python 3.14 and Release CMake configuration, then `python tools/build_ci_targets.py build`. Each of its 19 native target builds is sequential and uses `--parallel 1`. Full verification uses `PYTHONDONTWRITEBYTECODE=1 ctest --test-dir build --output-on-failure`. All nine groups passed in 461.29 seconds, including 1,192 Python tests with 19 existing skips. Results are recorded in `verification.json` and `ctest-summary.txt`. All 54 affected original source/archive-map pins also resolve successfully.

Additional checks passed: 56 focused evidence/repair tests, 25 CI/web tests, 42 numerical reference tests, three source-rate replay tests, workflow YAML parsing and `git diff --check`. The browser loading check passed 101 current native/Wasm model/protocol pairs, 90 same-instance import/export replays and failed-prefix recovery. An earlier attempt correctly rejected a stale native binary against a current Wasm catalogue; its failed local report was retained separately.

Local verification does not claim a fresh Linux execution, a rebuilt full Wasm matrix or a completed hosted GitHub run. Those remain remote confirmation steps. The original failed run, original archived numerical reports and source identities are retained.
