# Explicit stress-scope metadata — bounded implementation

Completed 1 November 2026. This implements the metadata foundation of the existing [total-stress design](../total-stress-profile-v1/README.md), after the [Python](../effective-replay-scope-v1/README.md) and [browser](../browser-effective-overlay-scope-v1/README.md) effective-measurement guards.

`atlas.stress.stress_binding` returns detached metadata from a validated definition. `stress_scope` resolves the generated field:

| Definition | Resolved scope |
| --- | --- |
| Legacy incremental 0.1 | effective, by the existing documented contract |
| Legacy timed 0.2 with stress observable | unspecified; no total/effective or Cauchy measure inferred |
| Timed definition without stress | none |
| Explicit 0.3 stress binding | declared effective or total |
| Missing/malformed 0.3 binding | error |

Generated C++ `Model` gains `StressScope stress_scope`. The enum includes `unspecified` in addition to the design's proposed none/effective/total: legacy timed observables need an honest representation distinct from no stress. An omitted aggregate field defaults to unspecified. All nine generated-catalogue CMake dependency lists include the new helper. `stress_offset` keeps its existing observable-only meaning; incremental state stress does not become an observable offset.

The accessor does not validate a complete model or authorize an execution profile. Incremental total-stress definitions still fail the unchanged semantic validator. No current model bytes, catalogue JSON, numerical functions, API versions, result serializers, pore semantics, browser execution capability or scientific status change.

## Evidence

The [prospective freeze](freeze.json) precedes native configuration/build/execution. The single `atlas_scope_metadata_tests` target was built serially with `--parallel 1`; the [run receipt](run-receipt.json) verifies seven exact scope/offset cases using the ordinary generated models and solver/recorded/schedule headers. It evaluates no material model. Source/generated hashes were checked against [pre-build pins](pre-build.json) immediately before execution. Raw configure/build/run output and binary hash are retained; no binary is distributed.

Five new Python groups cover declared/legacy scopes, detached binding, malformed metadata, unchanged total-profile rejection and exact old/new generation. For both the nine-model public catalogue and seven synthetic fixtures, complete JSON bytes match the archived prior compiler and every generated numerical function is byte-identical. Removing only the three additive metadata constructs also restores the entire prior header exactly. Frozen determinant header checks retain their old expected files and compare the same numerical bytes with the additive scope tokens removed.

The final focused command passes 31 tests:

```sh
python3 -B -m unittest tests.test_stress_scope tests.test_formulation tests.test_normalized_determinant_dsl tests.test_atlas.LanguageTests -v
```

[Retained failures](retained-failures.json) record the initial migration metadata assertion and two failures from an inadvertently broad selection that invoked the stale local eight-model solver. That incidental run supplied no evidence for this implementation and captured no process receipts; the overall turn is not claimed to have zero material calls. Neither old numerical gates nor model equations were adjusted. Subsequent commands explicitly select the language-only class.

[Previous sources](previous-sources.json) retain exact original compiler, CMake and modified regression-test bytes. Existing scientific receipts are unchanged. This packet does not claim fresh whole-project, Wasm, visual browser or hosted verification.

## Reproduce the metadata target

Choose a fresh private destination:

```sh
python3 -B docs/reviews/stress-scope-metadata-v1/prepare.py /private/tmp/atlas-scope-reproduction
cmake -S /private/tmp/atlas-scope-reproduction -B /private/tmp/atlas-scope-reproduction/build -DCMAKE_BUILD_TYPE=Release
cmake --build /private/tmp/atlas-scope-reproduction/build --target atlas_scope_metadata_tests --parallel 1
/private/tmp/atlas-scope-reproduction/build/atlas_scope_metadata_tests
```

The preparer only generates synthetic definitions, CMake configuration and source pins; it never invokes a compiler or material evaluator. Source copies are private inputs, not additions to the public atlas.

## Next bounded slice

Implement and freeze the scope-aware native laboratory response contract, including explicit unavailable pore-pressure channels, and effective-only legacy API guards. Keep all existing controller arithmetic and old effective response bytes. Do not activate total incremental validation or install Tresca until recorded contracts, browser labels/exports/imports and their independent source/reference/backend gates also pass. The existing Tresca transcription remains the target; no repeat transcription or calibration expansion is required.
