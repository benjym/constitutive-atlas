# Exact Mandel determinant core v1 — results

The prospectively frozen primitive study **passes**. All 124 ordered calls per backend match the independent expected status and binary64 bits, including every one of the 38 derivative columns. Complete native/Wasm responses agree. All 46 rejected Jet calls preserve the complete sentinel output, and each immediate baseline recovery succeeds in the same process/module. Python primal results also match every independent expectation.

The corpus contains 78 independent fixtures: 32 accepted Jet cases, 44 nonfinite-input/seed rejections and two final-output overflow rejections. Forty-six added recoveries give 78 accepted Jet calls and 46 rejected calls per backend. The separate scalar primitive can succeed when only Jet seeds or derivatives are invalid; its status and bits are assessed independently. Canonical positive zero, subnormal ties, normal-binade ties, irrational cancellation, mixed scales, huge rank-one cancellation and exact directional cancellation are included.

Before any compilation or execution, `prospective-freeze.json` pinned 32 source/reference/harness files; `source-snapshot/` preserves their exact bytes. Builds used ordinary Release flags, one explicit target at a time, `--parallel 1` and `EMCC_CORES=1`. No contraction override was used. Actual toolchain/configure/build output, artifact hashes, opaque raw responses and execution receipts are retained in this directory. Both builds and all collection commands succeeded on their first attempt in this study.

The coordinator independently regenerated the reference report and its 1,326 exact rounding-cell checks, obtaining identical JSON to the reviewed packet. Seven unit tests pass, including all frozen Python primal cases and deliberate corruption of each of the 39 Jet output components, rejected output, status types and signed zero. The independent review retained its initial probe-harness failure, found two structural API type/arity gaps, and confirmed their fixes before the compiled freeze; its 1,524 source-only probes pass. These are distinct evidence scopes.

Reproduce from the repository root:

```sh
python3 -B -m unittest discover -s tests -p test_symmetric_determinant.py -v
python3 -B catalogue/investigations/symmetric-determinant-v1/verify_study.py
```

The verifier validates all retained file hashes and frozen snapshots, then replays assessment against the current hash-matched source and retained native/Wasm artifacts. Build artifacts reside under `/private/tmp/atlas-symmetric-determinant-{native,wasm}-v1/`; rebuilding requires a distinct fresh study identity rather than overwriting receipts. Future changes to frozen root source require an explicit archived-source replay before these historical receipts can be revalidated.

This completes the numerical core study only. The operation is **not yet registered in the expression language or used by a model**. Dimension typing, executed-expression failure handling, trace/AD routing and a new complete clay2005 rate study remain open. The original model's 109 cases, failed results, independent accuracy budgets and parity gate are unchanged. No finite-integration, experimental-validation, scientific-admission or performance claim follows. Local runnable count remains eight; the hosted website remains five.
