# Hill fresh-build behavioral qualifiers

Task CI-hill-abaqus2025-v1; source specialist `/root/hill_source`, 2026-11-02. This additive CI harness reads the original frozen policy, 31-case / 41-increment Decimal corpus, negative requests and original assessor without modifying them. [frozen-inputs.json](frozen-inputs.json) binds these exact inputs and the source oracle. Both tools verify the model source hash against the frozen references.

From the repository root, after the coordinator builds each explicit target serially:

```sh
python3 -B tools/test_hill_native.py --solver /absolute/path/atlas_hill_solver --output /absolute/path/ci-results/hill-native
node tools/test_hill_wasm.mjs --module /absolute/path/hill.mjs --output /absolute/path/ci-results/hill-wasm
```

The module path must refer to the fresh generated Emscripten module with a default asynchronous factory. Its matching Wasm binary must remain beside it, as required by that factory. Use distinct native/Wasm output directories. No hashes of a different toolchain's fresh binaries are required to equal the original reviewed binaries. Each run records actual artifact/input hashes; the production package independently retains the scientifically reviewed Wasm bytes. These qualifiers do not change scientific approval identity or establish a wider parameter/loading envelope.

Every frozen case runs twice, including all six Mandel directions, shear sign reversals, hydrostatic/zero/unload/nonproportional paths, coefficient variants and the public preset. Complete per-backend response replay must be exact. All seven output components are assessed against original limits: stress `0.01 Pa + 1e-10*abs(reference)` and multiplier `1e-9`. Native invokes the immutable original assessor; JavaScript explicitly reproduces its row/initial/parameter/strain/replay/component gates with additional finite-number checks. This standalone qualifier does not add a native/Wasm parity claim; the original paired study remains unchanged.

Five frozen negative requests must reject. Four parameter-bound failures return no state because they fail before a state response exists. The outside-yield initial state returns the complete unchanged state. A deliberately distinct material failure using settings `1e-11,1e-6,1,0,1,0` must return `ok:false` and the full incoming seven-component parent. Valid same-instance Wasm recovery (and stateless native request recovery) must equal the baseline exactly after every negative request and the material failure. No missing state is accepted for the actual material failure.

Output consists of raw responses/calls, incremental corpus rows, negative and rollback observations, assessments and a final report. Raw observations are written before their corresponding scientific assertions; failed runs retain diagnostics. Final `report.json` is produced only after all gates pass. Output is confined to the caller's directory, with explicit rejection of an output directory inside reviewed `execution-v1`, including symlink aliases. Qualifiers never regenerate references or write to source/reviewed evidence.

Worker verification: Python AST parse and `node --check` succeeded. No compiled artifact was executed or built by this worker. The coordinator owns actual fresh-build execution and CI integration; results must be recorded in the caller-supplied directories.
