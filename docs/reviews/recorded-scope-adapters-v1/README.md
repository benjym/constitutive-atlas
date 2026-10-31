# Scoped recorded execution adapters

Completed 1 November 2026. Separate Python and JavaScript adapters now connect the [native recorded0.2 endpoints](../recorded-scope-native-v1/README.md). Existing0.1 adapters and the browser view remain unchanged. No public model, production total-profile activation or deployment is added.

## Use and identity

Python `atlas.recorded_scope_execution.execute_scoped_recorded(spec, catalogue, solver, timeout=60)` takes the scope-aware0.2 request and a caller-frozen compiled catalogue. It checks model ID/scope/state binding, parameter-vector lengths/bounds and initial-state dimensions before invoking a process. Model0.3 requires explicit state. It queries `--describe` and compares the full decoded catalogue and parameter order before the material request. Only `--mode recorded --recorded-stress-scope ...` is used. Timeout is finite and at most60seconds per process; no build, fitting, specimen preparation or legacy fallback occurs.

JavaScript `web/recorded-scope-execution.mjs` exports `runScopedRecorded(engine, spec, catalogue)`. It clones inputs, validates the same metadata, compares `atlas_describe` including parameter order and calls only `atlas_replay_recorded_scope` or `atlas_replay_recorded_scope_with_restarts`. Missing exports and old responses throw without fallback. The current browser view does not call this module yet.

Both modules export response verifiers for saved-only replay. They require:

- Version0.2, a closed exact stress descriptor, expected catalogue hash/model, controls/knots/initial-strain wire and complete resolved parameter/initial vectors.
- Exact material/control settings and optional restart policy, with bounded nonnegative restart accounting.
- Complete successful point counts and coordinates, finite state/strain dimensions, initial point identity and final-state identity; or a legitimate failed prefix whose final state/strain equal its last committed point. A pre-initial-point versioned failure can retain only the supplied initial state with failed_knot=-1. Unversioned/legacy engine errors are exceptions, not accepted scoped output.

These are contract/identity checks. The supplied catalogue must come from the validated compiler/build; descriptor equality does not independently validate source equations or establish a complete binary/source build provenance chain. Production total incremental validation is still disabled. The test catalogue contains the already documented restricted synthetic total-elastic fixture, not a new atlas model. No new constitutive tolerance or numerical controller policy is introduced.

## Verification

The new response suite uses all16retained scoped outputs from the native gate. Python and JavaScript accept each and reject25copied corruptions covering version/scope/descriptor/catalogue/model/wire, state/parameters/settings, boolean confusion, extra policy fields, restart counts, truncation, coordinates, final state and failure prefix. Input objects remain unchanged. Mocked transport checks prove scope rejection before calls, descriptor and parameter-order rejection before material requests, exit-status checks and missing-export/old-engine no-fallback behavior.

[freeze.json](freeze.json) selects exactly three existing native cases before observations: effective mixed reversal, one-trial-budget failed prefix with restart policy, and synthetic total mixed reversal. The existing native binary is SHA-bound; no rebuild ran. Three metadata calls and three material requests reproduce the exact prior saved responses. Six raw process receipts retain commands, wire-file contents, exits, stdout/stderr and binary identity. JavaScript validates and routes the returned native responses using a ccall test double; this is not actual Wasm execution/parity or a browser rollout.

[Saved replay](verify.py) reconstructs transport/request identity and response acceptance without any process calls. Four copied receipt corruptions reject. Nineteen focused tests pass:

```sh
python3 -B docs/reviews/recorded-scope-adapters-v1/verify.py
python3 -B -m unittest tests.test_recorded_scope_execution tests.test_recorded_scope_adapter_evidence tests.test_recorded_scope_native tests.test_recorded_scope tests.test_recorded_api.RecordedRunContractTests tests.test_laboratory_scope_contract -q
```

The [native summary](summary.json), [pre-execution freeze](pre-execution.json), returned responses and raw receipts are retained. The exact previous request-status document is preserved through [previous-sources.json](previous-sources.json); earlier native references/receipts and gates are unchanged.

## Stop and next dependency

Next implement browser scope identity, labels, mechanical protocol descriptions, unavailable pore channels and CSV/JSON import/export together, selecting the new laboratory/recorded APIs with no fallback. Freeze native/Wasm/browser comparison and legacy regression gates before observing compiled results. Keep production total activation and the existing Tresca transcription's source/reference/backend gates separate. This adapter slice makes no scientific promotion, push or deployment.
