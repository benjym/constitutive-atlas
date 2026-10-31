# Normalized determinant expression integration

The prospectively frozen study **passes all 1,953 calls per backend**: 1,935 material evaluations and 18 history evaluations on native and WebAssembly. All expected closed response shapes, statuses, scalar bits, applicable 38-column derivative bits and transaction metadata match exactly. Complete decoded native/Wasm responses agree. There are 726 immediate material rejection/recovery pairs and six history good/bad/recover triplets.

The 55 synthetic schema v0.3 definitions exercise nine contexts: equations, derived expressions, domain checks, initial checks, observables, increment-reset guards and values, state scales and observable scales. Eight direct/outer-trace paths retain all 98 independently certified primitive inputs and seed/reference literals. An independent rational trace-first composition tests cancellation before the normalized determinant. Eager evaluation retains failures; unselected lazy branches skip them. Seed/derivative rejection, initial-check disabling and dispatch skipping are explicit fixtures. See [the frozen contract](CONTRACT.md) for exact scope and output limits.

The [assessment](assessment.json), opaque raw journals, execution receipts, build commands and verbatim CMake configuration are retained. Native and Wasm builds ran serially with one explicit target, `--parallel 1` and `EMCC_CORES=1`. Both builds and transports completed successfully; no acceptance policy, case or budget changed after observation. The freeze contains 159 source/reference/harness files and excludes caches and bytecode.

The [isolated source replay](isolated-generator-replay.json) reconstructs only the frozen files in a fresh tree and regenerates all 64 output files exactly with an isolated Python interpreter. This checks source/protocol portability; it does not rebuild or execute compiled artifacts or replay raw numerical gates. `verify_study.py` separately reopens recorded artifact bytes for hash verification and reassesses both raw journals under the current frozen source bindings. Artifact paths are temporary and may eventually disappear; their receipts remain retained.

The [registration checkpoint](REGISTRATION.md) retains 45 passing source-level tests. Ten formerly live compiler/DSL/history bindings were archived before registration. The [expanded source audit](../../source-replays/dsl-identity-v6/postchange-source-audit.json) retains seven pre-existing unresolved bindings; this work does not claim to repair them. Earlier numerical failures and reference budgets remain intact.

This is a finite software conformance study, not a performance measurement, complete constitutive-law verification, finite-path integration study, experimental validation or scientific admission. No production model was added or promoted and no website was deployed. Next is the distinct original-stress clay2005 normalized-determinant candidate, retaining all 120 ordered requests and unchanged source/parity budgets.

Reproduction from the repository root:

```sh
python3 -B catalogue/investigations/normalized-determinant-expressions-v1/verify_study.py
python3 -B catalogue/investigations/normalized-determinant-expressions-v1/replay_sources.py
```
