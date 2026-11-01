# Public Dense/Loose400 regression runner — prospective source delivery

Scope: CI-lade-public-presets-v1, implementation by /root/lade_interface_review. This is new code awaiting a separate source review, not an extension of this run's earlier interface acceptance. No material call, build, browser run or new numerical result has been produced here. Existing scientific/source acceptance gates and bounds remain unchanged.

After exact scientific qualification, E5 and guarded packaging have passed, invoke from repository root:

```sh
node tools/test_implicit_path_public_presets.mjs BUILD OUTPUT IDENTITY
```

BUILD is a qualified build containing lade-domain.mjs, lade-domain.wasm and generated/models.json, or a guarded engine-implicit-path package directory containing the same artifact names and models.json. IDENTITY is the guarded package identity.json. OUTPUT is a new report filename; OUTPUT.raw and OUTPUT.status.json must also be absent. The runner refuses to overwrite earlier observations. A failed check exits nonzero and retains incremental report/status and any child raw manifest/stdout/stderr, including timed-out or crashed calls.

Before artifacts are called, the tool verifies POLICY.json dependency hashes, exact source-reference bounds, canonical model bytes, full four-model catalogue ordering, guarded identity and actual loader/Wasm hashes. It checks atlas_describe against the complete catalogue, then runs exactly dense and loose source presets at protocol1, target.005,400 increments,0 cycles and the unchanged contract's fixed eight settings. Each first/recomputed replay call must pass complete verifyResult, succeed and meet the original three source final-reference bounds. Full export/import uses stringifyRun to preserve signed zero. Recomputed replay uses verifyReplay, which excludes only elapsed_ms.

All four material calls use the unchanged frozen fused-linear-v1/wasm-bounded-v1 createBoundedModule. Its worker supports only three material APIs and cannot call atlas_describe. A new metadata-only companion worker and the existing boundedCall wrapper therefore perform atlas_describe with the same 120000ms startup-inclusive cap, artifact hashes, exit/signal/error inspection, raw streams and manifest. This companion rejects every API other than atlas_describe. No frozen runner/worker/transport file was edited.

Pure verification (does not import an executable engine or invoke run):

```sh
node docs/ingestion/lade-duncan-1975/atlas-integration-v1/public-ci-v1/check_pure.mjs
```

Results and exact new/source dependencies are retained in pure-results.json, POLICY.json and SOURCE_FREEZE.json. SOURCE_FREEZE omits itself to avoid a self-hash. No full native saved-response equality is claimed; this runner presently uses the unchanged independent scalar source references. Scientific full-campaign qualification, compiled execution approval, actual browser qualification and publishing remain separate gates. The smallest next action is independent review of these exact new files, then coordinator-authorized invocation against the eventual guarded artifacts.
