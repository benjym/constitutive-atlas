# Generic native/Wasm qualification harness v1

No compiled calls were executed by the harness author. Policy and request plan are prospective. Coordinator must review/freeze the complete manifest before execution. This harness does not implement a constitutive kernel: Python orchestrates only generic native CLI or generic Wasm C ABI calls, with the same materialized requests and shared report checker.

```sh
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/execution-v1/prepare.py
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/execution-v1/run_native.py --solver /absolute/path/atlas_solver --output /new/native-output
node docs/ingestion/manzari-dafalias-1997/delivery-v1/execution-v1/run_wasm.mjs --engine /absolute/path/atlas_engine.mjs --output /new/wasm-output
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/execution-v1/check_reports.py /new/native-output/report.json /new/wasm-output/report.json --output /new/checks.json
```

`--output` runner directories must not exist, preserving earlier runs. An optional repeated `--case ID` executes bounded diagnostics; full checker still marks missing cases/special tests failed. Do not use subsets to claim full qualification. Native and Wasm calls must run serially under coordinator build/execution ownership; these commands do not grant a build slot.

All direct raw responses, requests, initial state, parameters, increments, exact control bits, CLI arguments and return codes are preserved gzipJSONL per case. Report JSON contains complete normalized states, cumulative strains and coordinates. A persistent Node worker loads the chosen engine once; the Python orchestrator sends identical generic requests to either backend. Python's binary64decimal representation roundtrips exactly; control wires use explicit16hexbit encoding. Wasm worker stdout is reserved forJSONL; engine prints are directed to retainedstderr. The identity receipt binds executable/JS/Wasm hashes, model, inputs, settings, requests, policy and harnessmanifest. Native source/toolchain/compiled-model closure must additionally be provided by coordinator build receipts.

Source-only static validation: Python AST parse, Node `--check`, deterministic plan materialization, bitwire roundtrip/grid/checkpoint checks and manifest verification. These checks are not numerical/backend qualification. Any harness startup/failure should be retained under a new output path; corrections after observations require additive identities/policy review rather than overwriting evidence.
