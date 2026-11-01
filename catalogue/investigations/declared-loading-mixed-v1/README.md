# Repaired eleven-model engine: bounded compatibility qualification

Task **NUM-declared-loading-mixed-rollout-v1**, coordinating parent, 1 November 2026. This closes mixed-catalogue/default-run qualification only; packaging, actual-browser checks, deployment and scientific admission remain separate.

The [v0.3 finite-loading repair](../declared-loading-boundary-v2/README.md) now has a fresh native and Wasm **normal `atlas_solver` target** built from all eleven unchanged top-level definitions. Each fresh backend exactly matches its own qualified pre-repair backend over twelve fixed requests, excluding only elapsed time. Full-response native/Wasm parity also passes. No model equations, defaults, integration controls, source/review statuses or numerical gates were changed.

## Prospective scope and baselines

[Literal requests](requests.json) retain ten ordinary drained defaults, the already qualified small GIS example and the unchanged ordinary GIS default. Their full state, parameters, numerical settings and exact control bits come from the earlier [actual packaged-producer check](../../../docs/reviews/gis2024-browser-closure-v1/observations/gis-closure-package-results.json). The [policy](policy.json) pins that document and defines acceptance before candidate builds.

Both original [artifact identities](baseline-artifacts.json) were checked against the previous [eleven-model qualification](../../../docs/reviews/gis2024-mixed-catalogue-v1/README.md). The old native executable uses the historical test transport wrapper, which delegates the explicit command-line requests to the unchanged production CLI. The new native executable is the normal production target. Old and new Wasm use the normal exported production C ABI. Baselines were collected before compiling either candidate. These are software regression references, not independent constitutive truth.

The exact committed revision and111build-input checksums are in [source pins](source-pins.json). Both candidates were configured with the repository's normal CMake project in clean, separate temporary directories. Only `atlas_solver` was built with `--parallel 1`; native qualification passed before the Wasm build started. All pinned inputs were rechecked after collection. Both generated headers/catalogues equal the frozen expected files; [generated/artifact checks](generated-artifact-checks.json) retain hashes and actual compile/link flags.

## Results

| Request group | Per backend | Result |
| --- | --- | --- |
| Ten prior ordinary defaults |10runs,101points each |Pass; exact same-backend complete-response compatibility |
| Explicit small GIS example |1run,9full14-state points |Pass; exact same-backend compatibility |
| Ordinary GIS 1%/100step/depth14default |1failed run,initial full14-state point retained |Original failure preserved exactly |
| Total retained points |1,020 |All full-state point arrays, stress/strain outputs, settings, loading bits and failure prefixes compared |

Same-backend comparison recursively requires exact parsed response equality after removing only `elapsed_ms`. Cross-backend comparison requires identical structure, strings, booleans and null fields; numeric scalars use the frozen `1e-7*max(1,abs(native),abs(wasm))` regression tolerance. This is a compatibility policy, not a stress-accuracy or scientific error bound. Complete raw responses remain in backend observation files; CLI exit1for the deliberately failed GIS run is retained by the collector and is not discarded.

The frozen assessor rejects four controlled corruptions: changed history component, changed control bits, false GIS success and missing point. It accepts the declared elapsed-only control. No new acceptance condition was selected after candidate observations. Source/fixture metadata, collectors, assessor and literal baselines were [frozen before building](prospective-freeze.json). Backend receipts capture all commands/artifact hashes; observation stderr is empty.

## Saved-only verification

```sh
python3 -B catalogue/investigations/declared-loading-mixed-v1/verify.py
```

This checks retained file hashes and original source bindings, then assesses saved observations without building or executing artifacts. Successful compatibility still reports the ordinary GIS default as failed. Historical scientific/model studies remain separate and unchanged. Backend runners refuse to overwrite existing evidence directories.

## Portability correction

The original prospective freeze is retained literally and records an incidental ignored assessor bytecode cache. [Portable freeze](portable-freeze.json) preserves every source, policy, baseline and collector hash while excluding only that cache from required file availability. Final manifest/replay verification requires no bytecode. The earlier repaired-evaluator packet has the same additive [portability supplement](../declared-loading-boundary-v2/PORTABILITY.md); its original committed manifest and numerical acceptance remain unchanged. Both replays were checked with caches absent.

## Remaining delivery gate

The isolated repaired-evaluator study retains the direct invalid-loading rejection proof. This mixed study establishes compatibility of the normal engine under the twelve fixed requests; it does not rerun all five protocols, all original constitutive references, tangents or experimental studies. The ordinary GIS failure remains an open limitation. No fit or setting adjustment is justified here.

Next package these exact qualified Wasm artifacts in a fresh local website directory and verify catalogue identity, source/review disclosure, named/default loading and import/reset behavior. The existing website assets still contain the earlier engine. Keep source/scientific gates and the failed default visible; do not claim a new model or scientific release. Hosted deployment needs a new explicit instruction.
