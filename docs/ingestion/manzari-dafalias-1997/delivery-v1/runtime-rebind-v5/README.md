# MD1997 control-runtime rebind v5

Task `QUAL-md1997-control-runtime-rebind-v5`, source-only preparation. No build, compiled material call, model/reference/settings/tolerance edit or approval occurred. This packet binds exact582-file control-fix source receipt SHA `4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8` at `/private/tmp/atlas-control-partition-v1/source` to the **unchanged** frozen resolution-study-v4 numerical work. The prior578source, v4 packet, old rebinds and failed reports remain immutable.

The material wrapper delegates `resolution-study-v4/run_native.py` directly. Its raw report retains the original v4 requests/policy/manifest/model identities and must be checked with the original v4 source/parity checkers. It never executes v4's old578source preflight/wrapper. Instead `runtime-binding.json`, strict current preflight and a separately supplied coordinator build receipt establish new runtime identity. This is an additive identity receipt, not a claim that the v4 original source receipt describes the new artifact.

| Study | Preserved evidence/gates | New identity only |
|---|---|---|
| Full MD | All35cases,14paths,2048/4096 grids/checkpoints, BOTH coarse/fine accuracy gates, refinement, replay/covariance, AD/FD/partition/branch, special/rollback/recovery and public defaults | Strict582source/build/artifact wrapper and separate runtime binding |
| Ordinary | All16cases/parameters/model hashes/settings/initial states, expected outcomes, GIS exact failure and every original check | v7 runner report/receipt path; policy identity/sourcehash |
| Original coarse diagnostic | Exact execution-v3 drained-dense-compression-128 parameters/settings/initial/133controls/bits | One-path operational completion/finite fullstate diagnostic, explicitly no full128/512 or source-pass claim |

`check_rebind.py` proves the ordinary runner has only two identity/path substitutions and policy only identity/sourcehash changes. It verifies all582source files and all pinned historical manifests, including the full v4 requests/checkers. `comparisons.json` and `full-freeze.json` retain exact equality/hash evidence. Existing historical policy purpose wording remains unchanged as provenance; it is not a new source/build correspondence claim.

## External coordinator build receipt

Before any delegation, all wrappers require `--build-receipt <file>`. The coordinator supplies a new receipt based on actual serial build logs, with these fields (additional build provenance fields are allowed):

```
identity: md1997-control-runtime-build-receipt-v5
source_freeze_sha256: 4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8
source_directory: /private/tmp/atlas-control-partition-v1/source
source_files: 582
backend: native OR wasm
artifact_path: absolute native solver OR Wasm JS module path
artifact_sha256: SHA256 of that exact file
catalogue_path: absolute generated normal16-model models.json path
generated_catalogue_sha256: f38da28fd2857e03e1def0c2ed70dc2a5b999984ef087360b324c933a2da3a99
build_log_path: absolute retained actual build log path
build_log_sha256: SHA256 of that exact log
wasm_path: absolute sibling .wasm path (Wasm only)
wasm_sha256: SHA256 of payload (Wasm only)
```

Paths/hashes are checked against actual bytes; no stub receipt or inferred old build correspondence is accepted. The normal16model catalogue stays unchanged because scientific model records and compiler are unchanged; the capability's separate two-model fixture catalogue is insufficient. A receipt is coordinator provenance, not independent approval or a proof derived from filename alone. The reviewer must verify actual source/build correspondence and numerical evidence. The wrapper copies the exact external receipt into the new output and binds its hash. Keep build logs, catalogue and artifacts at their recorded paths for saved read-only verification.

## Commands after separate prospective review and coordinator build

Use fresh evidence/check paths throughout. Run native results before Wasm under the coordinator's serial execution ownership. `<R>` is this packet and `<V4>` is the unchanged sibling resolution-study-v4.

```
python3 -B <R>/preflight.py
python3 -B <R>/run_coarse.py --solver <native> --build-receipt <native-receipt> --output <new-coarse-native>
python3 -B <R>/check_coarse.py <new-coarse-native> --output <new-coarse-native-checks.json>
python3 -B <R>/run_md.py --solver <native> --build-receipt <native-receipt> --output <new-md-native>
python3 -B <R>/check_binding.py <new-md-native> --study md --output <new-md-native-binding-checks.json>
python3 -B <V4>/check_reports.py <new-md-native>/report.json --output <new-md-native-source-checks.json>
python3 -B <R>/run_ordinary.py --solver <native> --build-receipt <native-receipt> --output <new-ordinary-native>
python3 -B <R>/check_binding.py <new-ordinary-native> --study ordinary --output <new-ordinary-native-binding-checks.json>
```

Repeat the same wrappers with `--wasm-engine <module>` and a Wasm receipt into distinct new directories; run each unchanged source checker separately, then mandatory paired v4 check:

```
python3 -B <V4>/check_parity.py <new-md-native>/report.json <new-md-wasm>/report.json --output <new-md-parity-checks.json>
```

Do not use `--case` for a full qualification claim. MD diagnostic subsets can be retained but saved full-study binding verification rejects them. Ordinary selection is forbidden. Coarse wrapper selects exactly one frozen old case and emits no special-suite claim. `check_coarse.py` verifies133finite14state/6strain rows, exact coordinates/bits, initial state/zero strain and complete raw request/response linkage. No old source gate is removed or reinterpreted by that diagnostic.

## Retention and readiness limits

Preserve runtime-binding.json, copied external receipt, complete raw gzipJSONL requests/responses/stdout/stderr, control wires, worker stderr, raw reports, actual process logs and every checker failure. Wrapper records delegate command/hash/exit and report hash; it does not turn a delegated process exit0 into numerical acceptance. Saved binding verification rereads current582source, original request/checker identities, complete case order, artifact/payload/catalogue/log bytes and copied external receipt. Numerical source and parity checks remain separately mandatory. Full ordinary checks run unchanged, including the exact predeclared GIS failure.

Source-only preparation verifies Python AST syntax, exact fork semantics/hash closure and invalid external receipt rejection. Mock receipt tests are explicitly negative and execute no solver/engine. There is no new actual pass or scientific approval. Separate prospective review, coordinator current build receipt and actual native/Wasm evidence with independent review remain required. Shared app/profile/browser/release work remains outside this packet.
