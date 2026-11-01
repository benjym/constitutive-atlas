# Independent saved diagnostic and prospective Decimal study review

The saved diagnostic is authentic within the hash-bound source/build/process archive and confirms the expected native failure. The proposed generic Decimal study is accepted as a bounded prospective design. Neither finding establishes a passing native fixture or complete AD correctness.

The reviewed actual manifest is `07170ea87de97c23330b3e6a138e4312ac88acbc4cee650dfb4437cb09d9f8ba`. The 932-member archive has safe, unique regular members, all matching the receipt. All 594 source files match their freeze; only the logging insertion changes the prior source, and its removal recovers the exact accepted fixture. Public process/raw/freeze/runner bytes match their archived counterparts. All 6,821 tool files retain their identities. Three serial commands return exactly 0, 0, 1: configure, build one target, then the expected failing fixture. Raw streams, process identities, environment and postchecks match. No artifact was called by this reviewer.

The first retained failure is row0, column8 (alpha_yy), level0, h=5e-11. Native AD is -235.38608480040432, FD is -235.37722881883383, and the error .008855981570491167 exceeds the unchanged budget .00706158254401213. Both residual operands and FD are bit-identical to the frozen source-only analysis. Full state, direction and scales match. The instrumentation leaves arithmetic, state, steps and gates unchanged.

## Independent mathematical assessment

Both observed residuals lie in magnitude binade [32768,65536), whose binary64 spacing is 2^-37. Their difference is an integer multiple of that spacing; division by the exact stored 2h gives a secant lattice. The independent Fraction calculation encloses the entire possible original acceptance interval around the logged native AD, including a conservative 1e-12 enclosure for rounding. There is no lattice point in that interval. The nearest possible h secant has error at least .00885598157047132 versus budget at most .00706158254401213. The exact recorded subtraction/division reproduces native FD.

This proves a **conditional limitation of the binary64 endpoint secant at this observed entry**, rather than an excuse to drop its gate. The h binade condition is observed. The h/2 lattice proof is conditional because the native fixture stopped at level0; it is not an observed level1 result. The proof is centered on logged native AD and does not assume that AD is mathematically correct. A separate publication-derived analytic calculation using direct 3x3 contractions and exact binary64 input values is stable at Decimal70/110 within 1e-60 and gives -235.38608480001029947..., differing from native AD by 3.9402e-10. Author v1 uses ideal decimal input literals and gives -235.3860848000169; that small input-semantics difference explains the slightly different reported delta. Both are far below the failed secant error. One-entry agreement cannot certify the full Jacobian.

## Prospective proposal decision

Exact analysis-v2 manifest `012df6fdb9799457a30c94ce2cc6e4bdfae54eedd835044e7678218ae4d4b315` and PLAN SHA `5aa7e15207cd06b5d09c6282514c35e1ba2be93918da5dcb58b9589006be7949` are accepted as a bounded design, with no blocking finding. The saved v2 binding is independently recomputed without executing its author script. The proposal changes the full14 reference arithmetic under a distinct identity and keeps all392 AD and196 convergence comparisons, original steps/tolerances, rank13 checks, covariance and prior15 fixtures. Both historical failure profiles remain required strict negatives.

The design preserves exact rounded binary64 endpoint locations and original nominal 2h denominator. Its Decimal primitive arithmetic is a mathematical residual reference, not binary64 emulation. Literal/default decoding must follow exact compiler binary64 values. Generic DSL agreement tests numerical differentiation/code generation against the declared equations; it does not replace independent publication-law verification. These distinctions are explicit in the proposal.

The coordinator may assign a NEW implementation scope. Before any new native AD observation, require independent generic evaluator tests (including rational and tensor oracles, lazy branches and malformed inputs), fixed Decimal80/120 precision checks, all56 endpoint identities and28 secant vectors frozen, and a separate evaluator/reference/corpus/strict transport review. The proposed native export must run unchanged rank13/rotation/prior15 checks and cannot report overall acceptance until external comparison passes. No production DSL/compiler/runtime/model/CMake change or gate waiver is accepted here.

## Reproduction and retained outcome

Run from repository root, unoptimized, without bytecode:

```sh
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python3 -B docs/investigations/control-partition-derivative-v1/native-fixture-fd-diagnostic-actual-review-v1/check_actual.py
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python3 -B docs/investigations/control-partition-derivative-v1/native-fixture-fd-diagnostic-actual-review-v1/lattice_review.py
PYTHONOPTIMIZE=0 PYTHONDONTWRITEBYTECODE=1 python3 -B docs/investigations/control-partition-derivative-v1/native-fixture-fd-diagnostic-actual-review-v1/check_plan.py
```

The saved results contain 8,405 actual-closure checks, the exact-rational lattice/direct analytic checks, and 33 proposal/input-binding checks. All pass as review checks. The underlying positive native numerical fixture remains FAIL; no suite/E5/model-admission/browser acceptance follows. Review builds and compiled calls: zero. Original source analysis, diagnostic, failed CI and author proposal bytes remain unchanged. Smallest next action: separately claim the bounded generic evaluator/reference implementation and commission its independent review before new compiled collection.
