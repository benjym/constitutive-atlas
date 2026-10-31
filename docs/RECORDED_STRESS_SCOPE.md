# Scope-aware recorded request contract

The separate [recorded-run 0.2 schema](../schemas/recorded-run-v0.2.schema.json) defines explicit stress identity for ordered mechanical replay. This is a pure request/codec foundation. [Native 0.2 responses and restart exports](reviews/recorded-scope-native-v1/README.md) are implemented behind explicit scope selection. [Dedicated Python/JavaScript execution adapters](reviews/recorded-scope-adapters-v1/README.md) now connect the scoped endpoints with strict identity checks. Browser rendering/import/export remains unconnected. The public atlas still has nine executable models and the production incremental validator still rejects total stress.

## Request

Use `version: "experimental-recorded-run-0.2"` and required `stress_scope: "effective"` or `"total"`. All existing model/path/parameter/initial-state/control/material/restart settings retain their meanings. The nested path remains `experimental-recorded-path-0.1`: its coordinate orders the path, its stress targets are absolute projections in Pa, and its strain targets are dimensionless. No time, pore-pressure, preparation or drainage meaning is inferred.

The object remains closed. The old 0.1 schema is unchanged and does not accept the new scope field. Scope is required even for all-strain paths because the result's state stress must have an explicit meaning. This is an API request version, not a constitutive model schema migration.

Python `atlas.recorded_scope` provides:

- `validate_scoped_recorded_run(spec)` for the closed request plus the existing path/settings/integer-transport checks.
- `validate_scoped_recorded_model(spec, model)` for model ID, explicit scope/binding and a first persistent incremental Cauchy sigma6 field in Pa.
- `scoped_recorded_wire(spec, model)` for unchanged ordered numeric controls/knots after the metadata check.

JavaScript [recorded-scope.mjs](../web/recorded-scope.mjs) supplies `validateScopedRecordedRun`, `validateScopedRecordedModel` and `scopedRecordedWire` with the same contract. Inputs are not mutated, sorted, interpolated or reinitialized. The model metadata checker is not a full semantic model validator or an engine capability check. Those remain mandatory before future execution; accepting metadata for a synthetic total binding does not enable that model in production.

Legacy incremental model0.1 retains its documented effective Cauchy state contract. Modern model0.3 must bind state sigma/Cauchy to the declared effective/total scope and use the strain-path profile. Timed, observable, unknown/missing-scope, temporary and incompatible state bindings reject. Legacy unscoped timed outputs cannot acquire a guessed scope.

## Verification and current boundary

```sh
python3 -B -m unittest tests.test_recorded_scope tests.test_recorded_api.RecordedRunContractTests -v
node tools/test_recorded.mjs
```

Eight focused Python tests pass. The new cross-language corpus has28cases: all nine current effective models, two explicit effective/total metadata cases, and17 negative cases for scope, version, closed fields, model identity/binding, time/state roles, ordering and settings. Accepted paths produce exactly the old mechanical wire, including reversal ordering and restart policy. Inputs retain exact values/structure. Nonfinite and nonrepresentable integer inputs reject.

The existing Python `execute_recorded` and JavaScript `runRecorded` remain strictly0.1. Separate scoped execution is provided by `atlas.recorded_scope_execution.execute_scoped_recorded` and `web/recorded-scope-execution.mjs` `runScopedRecorded`, using a caller-frozen compiled catalogue and metadata preflight. Tests prove every accepted0.2 request is rejected by those adapters before subprocess/ccall. The existing JavaScript recorded contract suite passes with zero native/Wasm pairs requested. No build, material run, live browser rollout, prior evidence rewrite or model promotion occurs in this task.

## Native status and next execution gate

The [native gate](reviews/recorded-scope-native-v1/README.md) implements scoped endpoints with and without restarts, the required scope/model match, response0.2 stress descriptor and effective-only legacy guards. Exact legacy comparisons, synthetic total analytical paths, restart policies and failure prefixes pass its prospective serial gate. This does not enable total models in the production validator or browser.

The [dedicated adapters](reviews/recorded-scope-adapters-v1/README.md) now enforce response version/stress/catalogue/request/settings/restart identity and complete success or retained failure prefixes, with no legacy fallback. Three explicit native requests reproduce the prior saved outputs exactly; browser-side checks use returned native data, not a newly built Wasm engine.

Next connect browser scope labels, CSV/JSON import/export and the new engine APIs together under a frozen native/Wasm/browser gate. Keep the current browser view on its effective-only legacy contract until that gate passes. Browser support still precedes production total-profile activation and the existing Tresca transcription's source/reference/backend checks.
