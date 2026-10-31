# Barodesy 2017 bounded isotropic finite-update study

This bounded common-engine study now retains actual native and WebAssembly runs. The protocol unit tests use synthetic transcripts; the evidence tests independently replay the scalar solution and audit raw responses without executing binaries. Model, independent reference and prior runtime evidence are unchanged. The selected body law remains a research fragment with no public admission.

## Independent target and matrix

The independently derived scalar compression solution in `tools.barodesy2017_isotropic_reference.py` is replayed afresh, including the correction for the actual rounded initial void ratio. The ideal NCL relation uses p, whereas critical density in the body law uses 2p. Ideal p=p0 exp(v/lambda) and 1+e=(1+e0) exp(-v) alone do not define the rounded-initial stress oracle. Reference derivation and source locators remain in `docs/reviews/barodesy2017-isotropic-reference.md` and the pinned implementation checklist. The primary manuscript SHA256 is bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15; no PDF is bundled.

Nine paths cover London, Dresden and Weald parameters at 25, 100 and 400 kPa. Each has three positive isotropic compression segments ending at volumetric strains .005, .015 and .03. Each is run at rate tolerances 1e-4/1e-6/1e-8 with one caller partition, plus 1e-4/1e-8 with seven partitions: 45 trajectories and 459 actual update calls per backend. Every returned caller point is independently compared, checked for finite positive pressure and supported e>=0, isotropy and exact zero shear. The exact exponential volume relation is checked numerically with the declared volume budget; no algebraic volume preservation is claimed.

The common rate solver uses explicit midpoint with step doubling. This packet does not test constitutive AD or an implicit material tangent. It covers zero-spin isotropic compression only: no reversal, off-NCL general path, nonisotropic trajectory, boundary saturation, experiment, or broad model admission.

## Predeclared numerical gates

Stress error is divided by original p0; e error is absolute. Bounds are 5e-3, 3e-4 and 2e-5 at the three tolerances. Volume bounds are .01 times those bounds plus 1e-14. These deliberately predeclared empirical acceptance budgets are not rigorous error bounds. Refinement is assessed separately for stress and e from original segment endpoint maxima: successive tighter errors <=.65 times previous plus twice the reference floor, and tight <=.35 coarse plus twice that floor. Floors are 1e-7 Pa and 1e-14 e. Tight one-versus-seven caller partition discrepancy must be <=.35 loose discrepancy plus twice the floor. No formal convergence order is assumed. Backend state parity budget is 5e-11 in stress/p0 and absolute e. A valid synthetic bias regression independently passes each backend's budgets yet fails parity; other regressions independently exercise refinement and partition shrink.

## Protocol and transaction checks

The collector sends all actual returned states forward. Every request/response binds the explicit parameter, strain, initial state, complete integration settings, selected single-model runtime descriptor and canonical catalogue hash. Fresh Python reference and literal source dependency hashes are checked before assessment. Finite vectors, numeric types, integer counters, substep fractions and complete successful coverage are required. Source code pins and binary SHA receipts record identity; they do not prove which source built an executable without a separate build receipt.

Budget failure is requested with max_substeps=3 and must retain positive partial diagnostic coverage while exactly rolling back the parent state. Both actual backends meet this gate: two accepted substeps cover 1/64 of the parent increment before budget failure, and the returned state equals the original parent exactly. An invalid initial e=-.1 must reject before accepted progress and preserve the parent. A zero increment must preserve its parent exactly. All three are followed by the same independently validated successful control. Native CLI calls are separate processes; those recoveries establish repeated API behavior, not process persistence. The Wasm collector uses one live module for all 459 calls and the three probes/recoveries. Python reassessment and native binding remain required after collection.

## Retained results

The [integration packet](../../catalogue/investigations/barodesy2017-integration-v1/manifest.json) binds both unmodified reports, 466 raw transport rows per backend, collection-time source copies, the build receipt and fresh assessment. At tolerances 1e-4/1e-6/1e-8, worst stress/p0 errors are 1.030e-5/4.747e-7/2.145e-8; worst absolute void errors are 1.646e-8/1.028e-9/3.756e-11. Maximum native/Wasm state difference is 2.911e-16 in the declared scaled norm. All refinement, partition and recovery gates pass. Independent review tightened paired dyadic substep/depth/budget checks and requires native-report binding for a full Wasm CLI assessment; the original reports pass this stronger reassessment without recollection or altered numerical gates.

Both Release builds ran serially with one job on the local machine. No remote CI result or reproducible-build claim is made. The common source/model/compiler and public catalogue are unchanged.

## Reproduction

Run from repository root. The `atlas_barodesy_solver` target reuses `atlas_barodesy_models`; it is declared in the authoritative CMake file. Select the build directories and build one target at a time with `--parallel 1`. No new generator ownership or automatic execution is introduced.

```sh
python3 -B -m unittest discover -s tests -p test_barodesy2017_integration_study.py -v
python3 -m tools.barodesy2017_integration_study --solver BUILD/atlas_barodesy_solver --output OUT/native.json
node tools/test_barodesy2017_paths_wasm.mjs --native-report OUT/native.json --wasm WASM/barodesy-isotropic.js --output OUT/wasm.json
python3 -m tools.barodesy2017_integration_study --report OUT/wasm.json --native-report OUT/native.json --output OUT/wasm-assessed.json
```

The collectors save raw intermediate transcripts before validation so failed runs remain inspectable. The current verifier intentionally requires literal current source pins and a fresh independent reference replay. It is a local exact-source replay, not a portable historical reassessment mode; archival receipts must preserve these exact bytes before future source evolution. The stored assessment field is recomputed, never trusted.

## Opaque transport retention

Native and Wasm collectors append a companion `.transport.jsonl` before parsing any engine response, including the descriptor. A complete run has 466 rows: one descriptor, 459 path updates and six probe/recovery updates. Native rows retain argv, request, raw stdout/stderr and exit status; timeout rows retain available partial transport and exception. Wasm rows retain C ABI function, argument types/strings, request and raw returned text; thrown calls retain the exception. Malformed output and wrong exit status therefore remain inspectable even when no parsed report can be saved. Protocol and review tests include mocked native malformed/status/timeout/descriptor checks. The actual persistent Wasm run and independent transport audit verify raw response correspondence for the full matrix. [Independent review](barodesy2017-finite-independent-review.md) records the diagnostic/CLI hardening and limits. Numerical gates are unchanged.

The raw transport auditor `tools.barodesy2017_transport.audit` checks all descriptor/update/probe/recovery rows against parsed requests and responses, native exit codes/arguments and Wasm ABI arguments. It supplements, and does not replace, numerical reassessment. Retained replay checks source and report identity; binary hashes are not verified against executable bytes during no-execution evidence tests.
