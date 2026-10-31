# Explicit total-Cauchy incremental profile activation

The semantic validator now accepts `state/sigma/cauchy` with explicit `effective` or `total` scope. Every other supported profile restriction remains: first persistent symmetric Pa stress, full initialization, declared spatial tensor semantics, fixed frame, infinitesimal strain, Mandel representation and compression-positive signs. Legacy v0.1 migration still cannot be relabelled total. Physical-time scope profiles remain unchanged.

This completes the validation portion of the [total-stress design](../total-stress-profile-v1/README.md), after the separately delivered native, recorded/laboratory consumer and effective-experiment guard gates. It changes no schema, compiler, numerical kernel, model definition, source-derived constitutive condition or solver tolerance. New total runs require scoped APIs; legacy APIs remain effective-only. The test-only scope substitution/loader patch is removed: the isolated synthetic elastic transport fixture now passes ordinary validation and generation.

## Evidence

`freeze.json` predates the change and observations. Four effective/total residual/rate combinations validate; 22 malformed bindings/profile/state/initialization variants reject. Legacy migration rejection and the existing timed effective/total/no-stress matrix remain tested. The archived validator is imported with its schema-resource root explicitly set to the repository; original bytes are unmodified.

The unchanged [BK2022v1 Tresca proposal](../tresca-declarative-v1/model.json) passes ordinary loading and full C++ source generation, retaining explicit total stress, sigma6/ep6, source-ideal initial checks, parameter domain and lazy spectral expressions. The exact previous validator still rejects that same proposal for the previously documented effective-only restriction. This is code generation, not material execution or a numerical accuracy claim. The proposal stays outside executable model directories.

Using the frozen prior validator versus the changed validator with the same unchanged compiler, all nine public models generate byte-identical complete `models.json` and `models.hpp` files. `observations.json` records their hashes and the candidate generation hashes. The focused suite ran 49 tests: 46 passed, three optional native checks skipped. No compiled process, native/Wasm build, material evaluation, deployment or scientific admission occurred.

The first regression run hit two harness resource errors because an archived module calculated its schema root inside the content-addressed directory. `retained-harness-failure.json` records the observed errors and correction; no material output or acceptance tolerance was involved.

Exact previous sources and sidecar bytes are preserved in `previous-sources.json` and `archive-changes.json`. Additive archive maps bind old documents to old bytes; historical reports are not rewritten to claim support they did not have. Proposed mappings for five uncommitted packets owned by another chat are retained in `deferred-untracked-archive-maps.json` for that integration owner; those original files were left untouched. Historical source-check scripts asserting the old rejection must run against their pinned source context, not be rewritten as present success.

## Next bounded task

Use the existing Tresca source/certificates/proposal to construct an independent rounded-Mandel reference corpus before observing this candidate's numerical outputs. Freeze actual binary64 tensor inputs and parameters, projection branch/boundary policy, full sigma/ep history, KKT certificates, noncoaxial/sheared/rotated and repeated-spectrum cases, all 38 state/previous/loading derivative columns, finite-input rejection and same-instance rollback/recovery. Preserve the strict source-ideal initial-yield policy; specify rounded numerical boundary behavior separately without silently relaxing it.

Only after those references and acceptance policies are reviewed should a distinct serial native/Wasm candidate qualification run or any executable installation occur. This activation adds no public model and supplies no Wichtmann applicability claim.
