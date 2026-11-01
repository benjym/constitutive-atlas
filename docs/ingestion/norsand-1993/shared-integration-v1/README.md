# Controlled-path shared integration v1

Coordinator task `INT-controlled-path-profile-v1`, 2026-11-01. This installs the separately reviewed generic v0.3 controlled-path profile, without migrating existing model definitions or adding a model-specific runtime kernel.

`integration-freeze-v2.json` identifies the current implementation, schema/contract, dedicated generator/CMake target, tests, exact draft NorSand candidate and named example. V1 remains immutable. The candidate bytes deliberately retain their prior draft/staged metadata; admission has not been inferred.

## Verification

- `generated-identity.json`: all three generated controlled-path C++/metadata files equal the accepted e2-v3 v6 bytes exactly. The current required compilation headers are unchanged; `header-identity.json` also lists unrelated shared solver/recorded/linearization drift, which this target does not include.
- `legacy-generation.json`: all13 public definitions generate byte-identical output before/after the generic hooks. Existing model JSON is untouched.
- `unit-results-v2.json`:25 relevant Python checks pass, with3 opt-in native state-contract checks skipped. New analytical scalar/tensor/curved, full-context rollback/recovery, complete inputs, named example and legacy-API rejection checks run. The original migration-test failure is retained; the test now selects the profile-specific generated header and still requires exact equivalence.
- `preservation.json`:179 previously resolvable source/archive-map bindings redirected to exact-byte snapshots. `routing-repair-v2/preservation.json`:9 further bindings preserved before routing/test fixes.
- `check_preserved_bindings.py`:3336 previously resolvable bindings from the original exact inventory remain valid;220 pre-existing unresolved bindings are retained as failures, not repinned. This does not repair or approve those unrelated records.

```sh
python3 -B -m unittest tests.test_controlled_path tests.test_formulation tests.test_state_contract -q
python3 -B docs/ingestion/norsand-1993/shared-integration-v1/check_preserved_bindings.py
python3 -B tools/generate_controlled_path.py --output /private/tmp/atlas-path-generated models/research/norsand/norsand-jefferies-1993-active-axial.json
```

The new `cmake/controlled-path` native/Wasm target is queued behind the currently claimed serial build slot. Its generated material code equals the already qualified source, but a fresh build of this durable target is not yet claimed as tested. No E5 approval, main-atlas selection, packaged browser or live deployment is asserted here.

## Retained failures and boundaries

The first preservation plan found stale document pins and stopped before sidecar writes. A second attempt extended sidecars but failed its final verification; the next pass verified179 planned bindings. No previously resolvable source binding regressed. Exact failed scripts, original inventories and failure summaries are retained. The unmodified general scanner subsequently encountered concurrent absolute `/private/tmp/.../source-archive-map.json` references outside this repository and failed; the routing-repair copy ignores unsupported absolute/parent-traversal references and the full preservation check instead rechecks the original exact inventory directly.

All source copyrighted PDF/text/images remain private. Original-source algebra, independent high-precision references,58requests per compiled backend, exact parity and separate bounded compiled review remain in immutable `../e2-v3/` and `../supplied-original-v2/`. They qualify a bounded original active monotonic drained axial law, not broad parameter validity, experiments, elasticity/cyclic/3D behavior, FE integration or public delivery.
