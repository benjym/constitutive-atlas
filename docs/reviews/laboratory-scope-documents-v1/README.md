# Laboratory scope documents

`web/laboratory-document.mjs` supplies pure `createLaboratoryDocument`,
`parseLaboratoryDocument` and `laboratoryDocumentCSV` functions for the planned
laboratory consumer rollout. They use the existing scoped execution validator;
there are no engine calls, live page changes or automatic version migrations.
The caller supplies a trusted compiled catalogue from the matching release.

## Scoped JSON and CSV

A scoped export has the distinct closed envelope version
`atlas-laboratory-export-0.2`, with exactly `schema_version`, `catalogue_hash`,
`specification` and `result`. The request declares `response_contract` and
`stress_scope`; the result carries the exact stress and pore-pressure descriptors.
Full initial state, parameters, loading, settings and committed point state are
retained, including void ratio/history beyond sigma. Export objects are detached.
The dedicated validator checks model/catalogue/scope/settings/loading identity,
complete success or retained failure prefix and nullable pressure semantics.

Import takes JSON text, rejects nonrepresentable integer literals and validates
the complete envelope/result before returning a detached specification for fresh
replay. It does not return an unverified cached plot or continue from a partial
state. A complete saved failure prefix, including an empty preintegration prefix
with matching metadata, remains an importable description of the original run.
Scientific validity and specimen preparation do not follow from a valid document.

CSV uses scope-specific `effective_mean_stress_Pa` or `total_mean_stress_Pa`
and signed deviatoric-stress headers, dimensionless axial/radial/volumetric strain,
`stress_scope` and `pore_pressure_availability`. `pore_pressure_change_Pa` is
numeric only for the reconstructed descriptor; it is blank when unavailable.
Null cannot be converted into a numeric zero. An overflowing derived volumetric
strain is rejected. JSON, rather than plot CSV, preserves the full history.

## Exact controls and legacy compatibility

JSON erases the sign of numeric zero. For a scoped exact-loading import, the
request's validated producer/controls bits remain authoritative. A detached copy
of the saved result restores the sign only after its loading bits match the
request and each saved numeric control equals the decoded value (positive and
negative zero compare equal). Changed nonzero values, booleans, missing controls,
wrong bits and mismatched point controls reject. The strict raw-response checker
continues to require exact binary64 signs; it is not weakened for documents.
The caller's JSON and request objects remain unchanged.

Historical envelope versions `0.1` and `0.2` remain distinct from the new named
scope envelope. They use the existing legacy import/export helpers, after
canonical-model effective-scope and request validation. Total models and new
scope fields cannot enter through those legacy paths. Legacy imports retain the
old rule that saved results are untrusted and recomputed; they do not acquire
new descriptors or scientific guarantees. Existing legacy JSON versions and CSV
headers/values, including their historical numeric pore-pressure field, remain
unchanged. No old artifact is rewritten into the new contract.

## Verification

```sh
python3 -B -m unittest tests.test_laboratory_document tests.test_laboratory_scope_execution tests.test_laboratory_scope_adapter_evidence tests.test_laboratory_scope_contract -q
node tools/test_loading.mjs
```

Seven focused Python tests pass. The new Node document harness checks11scoped
saved native/Wasm results across effective/total protocols and an exact cyclic
reversal, five actual legacy native results, detached full-state exports, partial
and empty failures, CSV availability and more than180 rejection assertions.
It rejects stale scope/model/catalogue/API/settings/vectors, malformed envelopes,
result corruption and wrong pore nullability. A deliberately tiny-target
transport fixture creates an interior negative zero, proves JSON erases it and
checks scoped and legacy exact-control round trips. Its mechanical channels are
retained data solely for document validation, not a constitutive reference for
the artificial target. Legacy CSV strings match the prior app's serialization.
The original pure loading suite also passes (1,080phase cases,9,720cyclic controls,
250ramp samples,60negative checks and11contract cases), with zero material calls.

Inputs come from the immutable `laboratory-scope-contract-v1` native receipts
and `laboratory-scope-adapter-v1` captured17-point Wasm result. The earlier
auxiliary constant-history assertion failure remains retained in that packet;
this document task neither rewrites nor reruns it. There is no build, native/Wasm
material execution, browser rollout, model migration, deployment or admission.

## Next bounded integration

Connect laboratory view/worker routing, complete examples, scope-specific
protocol/axis/accessible labels, pore-availability messages and this document
boundary together. Include dependencies and schema links in static packaging,
then qualify the actual page against the existing scoped engine. Production
total-profile activation and the existing Tresca source/reference/backend gates
remain separate. The public collection still contains nine executable definitions.
