# Prospective resolution study v4

Task `QUAL-md1997-resolution-study-v4`; source-only preparation, no compiled observation or approval. The coordinator clarified the fine resolution to4096 **before any observation** because the existing runtime accepts at most5001 explicit controls. The exact earlier2048/8192 preparation is preserved in `blocked-8192-v1/`, including its original manifest and request SHA `2534aa9809a637b18fe85953f2afff8845ba6f39125ba3caab443d0d9c7fa880`. Those files were originally generated at this directory level; after relocation their relative-path scripts are provenance only and must not be executed. Eight fine axis requests exceed the unchanged runtime limit. No split-control adapter or runtime modification is used.

The active request SHA is `dc02829df6c1e1b3500781bb5c3c7dc6728897a64b2cd50bd56ef60d99a89d10`. Old128/512 requests, policies, reports, failures and source records remain untouched. `parent-inputs.json` pins exact parent bytes. `source-freeze.json` is an exact copy of the coordinator's578-file receipt SHA `126d9bc3a221b6e0098c769eee267306d5be3d03f2b02725c824a6063243aa44`. Runtime/source/model/reference/tolerances/public defaults are unchanged.

| Item | Original execution-v3/parity-v6 | Active v4 |
|---|---|---|
| Eight axis and six interior paths | uniform128/512 plus every exact reference checkpoint | uniform2048/4096 plus the identical checkpoints |
| Both coarse and fine source accuracy | every checkpoint stress/alpha/e/radial gate mandatory | identical gates for **both** resolutions |
| Refinement | fine512 versus coarse128; normalized floor1e-5 | fine4096 versus coarse2048; identical comparison/floor |
| Restart/covariance/AD parent | first interior512 | first interior4096 |
| Restart index | before increment256 | before increment2048; same midpoint-index convention, including checkpoint insertions |
| Hydrostatic, elastic cycle, public defaults |512 hydro;128 per elastic leg;.01/100 public | entire cases byte-semantically identical |
| Special requests | zero/hold, invalid/recovery, forced rollback, AD/FD | identical numerical requests; only AD parent identifier retargeted |
| Native/Wasm transports | execution-v3 | both files byte-identical |
| Source checker | execution-v3 gates | only fine/coarse ID selectors and result identity changed |
| Parity checker | parity-v6 gates | local request path/hash and policy/result identity changed only |

`changes.json` lists every source-text substitution in preparation/checkers. `comparisons.json` proves that all other case metadata, reference values, parameters, initialization, settings and special requests are identical, grids contain every checkpoint, binary64 control bits are exact, all active axis requests fit the existing limit, and all35 cases remain. All14 material paths still have two resolutions. Restart/covariance retain every fine grid point. Covariance increments retain the original rotation operation order. A subsequent pass at fine resolution cannot excuse any coarse source failure or refinement failure.

The motivation is the coordinator's independent source-BE truncation finding, which reproduced old compiled512 behavior rather than suggesting a tolerance change. **Independent cross-path source-BE resolution justification and separate prospective review remain prerequisites to execution.** This packet does not assert those external prerequisites are complete. Old native FD partition mismatch and other failures remain recorded in their original studies; the branch/partition/AD gates here remain unchanged and may fail again.

## Source-only reproduction

Run `python3 -B check_preparation.py` from this directory or using its full path. It compares exact fork substitutions and all case semantics without importing a production kernel. `python3 -B preflight.py` verifies the manifest, immutable parent inputs and all578 source files, including control-count limits. Python AST parsing passed. Both checkers were run only against the preserved empty mock report and rejected it with exit1; `mock-checks.json` retains commands/stdout/stderr and expected rejection, while `mock-empty-*-checks.json` retain every failed gate. These are negative harness checks, never backend evidence.

`prepare.py` is the deterministic request generator, inherited apart from declared substitutions. **Do not rerun it over this frozen study:** its original behavior rewrites requests and a top-level manifest. Regeneration belongs in a fresh separately identified directory; the final handoff manifest additionally hashes all source-only checks and the blocked8192 preparation recursively.

## Coordinator execution after prerequisites

Use fresh output directories and exact build receipts showing correspondence to the578-file source. The wrapper performs source/parent/manifest preflight, delegates unchanged transport and writes `runtime-binding.json` with artifact/report hashes. Do not substitute an old engine or infer correspondence solely from a filename.

```
python3 -B <study>/run_study.py --solver <new-native-solver> --output <new-native-evidence>
python3 -B <study>/check_reports.py <new-native-evidence>/report.json --output <new-native-checks.json>
python3 -B <study>/run_study.py --wasm-engine <new-wasm-module> --output <new-wasm-evidence>
python3 -B <study>/check_reports.py <new-wasm-evidence>/report.json --output <new-wasm-checks.json>
python3 -B <study>/check_parity.py <new-native-evidence>/report.json <new-wasm-evidence>/report.json --output <new-parity-checks.json>
```

Coordinator runs serially; no build commands or runtime changes are part of this task. No case selector may be used for a claim of complete qualification. Keep full reports, every gzipJSONL request/response/raw stdout/stderr, controls files, worker stderr, runtime bindings, checker outputs and process exit statuses, including all failures. Native chain collection uses a fresh CLI process per increment; Wasm uses one persistent module, as before. Larger grids increase process count and raw retention, without changing those boundaries. A separate agent must review exact actual evidence before acceptance.

The smallest next action is independent prospective review plus the independent cross-path resolution justification, then coordinator-owned execution with the existing corrected native/Wasm builds and exact build receipts. No scientific approval, current numerical pass or live delivery is claimed by this preparation.
