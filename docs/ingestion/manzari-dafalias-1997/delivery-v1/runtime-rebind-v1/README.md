# Corrected generic runtime rebind v1

QUAL-md1997-runtime-rebind-v1. Scope: identity-only prospective MD/ordinary qualification binding. Own this directory and ../ordinary-regression-v6/ only. No shared source, original evidence, model, reference, numerical policy, build or compiled artifact was changed/executed. Source-only checks do not approve model/capability or predict passing results.

Active source is the exact coordinator receipt copied byte-for-byte to source-freeze.json: SHA-256 126d9bc3a221b6e0098c769eee267306d5be3d03f2b02725c824a6063243aa44, 578 files under /private/tmp/atlas-predictor-constraints-v1/source. Old source-v2 remains separately identified and its observed failures remain failures. check_rebind.py records the actual source delta and compares all ordinary cases/numeric gates exactly. full-freeze.json pins unchanged execution-v3/parity-v6 dependencies, original requests/references/model and old identity receipts as well as the new ordinary manifest; manifest.json pins this wrapper packet. Source-freeze lists every corrected source file, not just solver.

preflight.py verifies full-freeze receipts, its own manifest and every 578 source hash without calling a material engine. run_md.py then delegates unchanged execution-v3/run_native.py for either native or persistent Wasm transport and adds runtime-binding.json beside saved output. That binding explicitly records corrected source receipt, unchanged delegate command, artifact hash and report hash. It does not prove compilation correspondence; the coordinator must supply exact source/toolchain/generated/binary build receipts. All previous main-checker AND parity-v6 gates are still required; the wrapper changes no solver settings, reference, request or acceptance check.

Coordinator after prospective independent review and serial execution handoff:

```sh
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v1/preflight.py
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v1/run_md.py --solver <qualified-corrected-native> --output <new-md-native-dir>
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/runtime-rebind-v1/run_md.py --wasm-engine <qualified-corrected-atlas.js> --output <new-md-wasm-dir>
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/execution-v3/check_reports.py <new-md-native-dir>/report.json <new-md-wasm-dir>/report.json --output <new-main-check.json>
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/parity-v6/check.py <new-md-native-dir>/report.json <new-md-wasm-dir>/report.json --output <new-parity-check.json>
```

Run unchanged 16-case ordinary policy through ../ordinary-regression-v6/run.py on both exact corrected artifacts; its README provides commands. Before source-only acceptance, run check_rebind.py --output <new-file> and compare saved comparisons.json; policy cases/gates must be identical and source delta exactly solver + 2 new standalone fixture files. All MD execution/parity material request bytes stay identical. Use fresh output paths; preserve failures and malformed raw transport responses. A partial diagnostic --case is never full qualification. Current entire atlas/dedicated/browser/live release remains outside this study.
