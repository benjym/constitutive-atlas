# Maxwell main-atlas transport contract

This bounded E7 prerequisite implements [the browser contract](../../../../web/maxwell-atlas-contract.mjs), not a standalone page or production constitutive kernel. It supports all four existing named histories with explicit SI physical time, parameters, six initial stresses/strains/rates and every hold/rate control. Fixed settings match the retained qualified schedules; broad input bounds do not establish a material/computational envelope.

The transport checks the exact model/catalogue, complete echoed request/settings, sample/event order, six-component state/strain/rate/observable histories, initial and transition continuity, and componentwise unresolved stress-control transition rates. Export/import binds exact package provenance and reconstructed ABI arguments. Replay compares every returned deterministic field, including channels absent from plots. This validates structure and identity; arbitrary finite result values still require actual engine replay/reference qualification.

## Checks

```sh
node --test tests/test_maxwell_atlas_contract.mjs tests/test_sls_laboratory_contract.mjs tests/test_timed_route.mjs
```

All 14 test groups pass in [restart-inclusive regression output](tests-restarts.log), including eight new Maxwell groups. The saved successful fixed-policy fixtures cover six schedule cases plus two complete-state endpoint restarts at start times 4s and 8s, two repetitions, both backends: 32 responses. The deliberately coarse-policy cases and original failed budget schedules remain rejected. Tests also cover all four unchanged source presets, full ABI encoding, strict JSON, mutated inputs/outputs/provenance/requests and complete replay. [Initial output](tests-initial.log) is retained; the subsequent change additionally rejects sparse direct-call tensor arrays. [Input identities](inputs.json) pin implementation, source presets, original wire responses and current common ABI inspected.

No native/Wasm artifact was built or executed. No scientific scope, admission entry, web discovery, shared router, builder, CI or deployment changed. Independent review is required before integration. Next: main-laboratory worker/controller, exact-identity standard packaging, fresh serial current-source native/Wasm qualification and actual browser exercise; E7/E8 remain open.

Independent review found permissive unknown result/point fields and sparse direct-call strain-rate holes. Both are now rejected, with added mutation tests; prior test outputs remain retained. Review closure must bind the corrected bytes.

The reviewer also identified missing transaction-file restart fixtures. Added all eight successful saved restart calls; nonzero start times and complete restart strains/rates are now exercised durably. No new material calls were made.
