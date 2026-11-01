# Source-root feasibility of the bounded one-third retry

Bounded independent review of the four original frozen failed external increments, before revised compiled observations. **All four have admissible source-root continuations under the proposed actual binary64 `de/3`, `de-left` partition and dyadic children, without increasing depth14 or max_substeps20000.** This is source-root feasibility, not proof that the generic Newton implementation finds these roots. The original native study remains FAIL; no gate is changed, and no E5 approval is given.

| Frozen path | Accepted retry leaves | Maximum depth | Including discarded first-attempt work | Final D (Pa), binary continuation |
|---|---:|---:|---:|---:|
| loose-max-crossing-16 | 13 | 12 | 22 | 100978.85748025909 |
| loose-max-crossing-32 | 12 | 11 | 22 | 100112.73657735012 |
| loose-max-crossing-64 | 11 | 10 | 21 | 100112.73657735027 |
| loose-max-crossing-128 | 10 | 9 | 20 | 100112.73657734998 |

The analysis extracts the first failed raw request from each retained native path and uses its exact stored binary64 strain components and incoming state. It uses independently derived scalar branch-root equations from source Eq15, including the small nonzero lateral stress-per-modulus term induced by the stored drained radial strain. Each node tries unloading, primary, then postfailure roots under the exact strict/closed history and strength branch conditions; only a node with no branch root is bisected. Every accepted leaf is additionally checked against the source-compliance oracle, branch reconstruction and history constraint. The scalar root calculation uses 240 bisections; it does not model the engine's 45-iteration Newton budget or line search.

Two continuations are retained: continuous Decimal stress/history, and binary64-encoded stress with the source maximum history rounded upward when necessary. The latter is a feasible state encoding witness, not a prediction of engine output or permission for solver projection. Both have identical partitions and branches. Independently repeating at Decimal100 and160 preserves every leaf load, depth and branch, with final-state differences below1e-60Pa (the encoded states agree exactly). All encoded leaf source residuals/p_ref are at most1.371e-16, below the unchanged2e-10 policy. All paths visit unloading and primary; no postfailure branch is needed.

The actual non-dyadic split has zero axial exact-real defect and negative radial defects of3.3881317890172014e-21,1.6940658945086007e-21,8.470329472543003e-22,4.235164736271502e-22 respectively. Rounded child recomposition equals each incoming binary64 component. These defects are disclosed, not silently treated as exact real conservation. Actual leaf wire tensors are retained as hexadecimal floats; nominal fractions sum to1 at the working precision. No component underflow occurs in these four inputs.

Reproduce from repository root:

```sh
python3 docs/ingestion/duncan-chang-1970/material-v1/independent-review/execution-v1/native-failure/analytical-partition-v1/analyze.py
python3 docs/ingestion/duncan-chang-1970/material-v1/independent-review/execution-v1/native-failure/analytical-partition-v1/check_precision.py
```

`results.json` retains every accepted source leaf, no-root node depth, modulus-equation error, compliance residual and input binding. `precision-check.json` retains the repeated-precision comparison. `receipt.json` binds this review and its exact inputs. No compiled calls, material engine updates, builds, implementation changes or shared-evidence mutations were performed. The smallest next step is separately reviewed generic retry implementation and a new frozen full native/Wasm study with all original scientific gates intact; source feasibility alone cannot close that work.
