# Recorded scope document boundary

`web/recorded-document.mjs` supplies pure `parseRecordedDocument(text, catalogue)`,
`createRecordedDocument(specification, result, catalogue)` and
`recordedDocumentCSV(specification, result, catalogue)`. This implements the
recorded document portion of the [total-stress consumer design](../total-stress-profile-v1/README.md).
It is not connected to the live recorded view or packaging yet. No engine call,
model activation, material run, build, deployment or scientific admission occurs.

## Contract

The caller provides a trusted compiled catalogue from the matching build.
Raw requests can be legacy0.1 or explicitly scoped0.2. Exports use the matching
`experimental-recorded-replay-export-0.1` or `experimental-recorded-replay-export-0.2`
closed envelope with exactly `schema_version`, `catalogue_hash`, `specification`
and `result`. Scope is required in a0.2 specification and checked against its
selected canonical model. Catalogue/model/version mismatches and malformed
parameter/state vectors reject. Modern scoped model0.3 requests require explicit
initial state, as in the dedicated execution adapter. An export always requires
a verified result; raw requests have none. Imports return
`{specification, result, stress_scope}`; they do not execute or restart a run.

Result validation reuses the dedicated scoped response verifier, including
settings, wires, full state, complete success or retained failure prefixes.
Legacy requests are restricted to effective state stress; their results must use
legacy API0.1 without a stress descriptor. A detached validation view applies the
documented legacy effective meaning to the strict checker; returned documents
retain their original request/API/envelope versions. No automatic migration or
engine fallback occurs. Export objects are detached copies. Full persistent
state is retained in JSON, including history beyond the six stress components.
The module checks consumer metadata, not scientific equations or model admission.

Scoped CSVs use `effective_stress_*_Pa` or `total_stress_*_Pa` component names,
plus `stress_scope`, `pore_pressure_availability` and `pore_pressure_change_Pa`.
Recorded replay supplies no pore reconstruction: availability is `unavailable`
and its value is blank for both scopes. This states a replay-interface limit;
it does not decide whether the constitutive model has a pore law. No drainage
meaning is inferred. CSV contains plotted channels and diagnostics, not full
restart state. Numeric channels must be finite. Legacy CSV formatting is retained
exactly, including its effective component headers and existing column order.

## Verification

```sh
python3 -B -m unittest tests.test_recorded_document tests.test_recorded_scope_execution tests.test_recorded_scope -q
node tools/test_recorded.mjs
```

Eight focused tests pass. The new Node harness consumes all16 saved native
responses from `recorded-scope-native-v1` without executing a solver. It checks
request/envelope round trips, scope-specific CSV values/headers, blank pore
values, full extra-history retention, detached exports, effective legacy
compatibility, total legacy rejection and187 rejection assertions. Inputs remain
unchanged. Rejections include envelope/request/API disagreement, stale scope,
catalogue/model mismatch, extra fields, null/corrupted results, malformed vectors
and an integer literal that cannot be represented exactly in binary64. The
existing recorded contract suite also passes with zero native/Wasm pairs.
These saved-data tests do not establish actual browser/Wasm integration.

## Next bounded delivery

Connect the recorded view, worker routing, scope-aware plot/summary labels and
this document boundary together, include their module dependencies in packaging,
and qualify the new engine exports in a prospectively frozen serial Wasm/browser
gate. Laboratory labels, pore plots and laboratory documents also remain part of
the wider total-stress interface gate. Keep production total-profile activation
and the existing Tresca candidate separate until those consumers are coherent.
