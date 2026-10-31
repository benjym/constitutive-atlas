# Normalized determinant primitive v1: verified numerical core

**Passed:**155calls per native/Wasm backend, with exact independent primal/all38directional derivative bits, complete backend parity, immutable inputs/seeds and55immediate rejection/recovery pairs. Python primal results match the same independent certificates. This is a generic numerical core; DSL registration and complete-model use remain open.

## Frozen mathematical and executable identities

The operation is `det(A)/trace(A)^3` at the original six stored binary64 Mandel components. Its directional derivative is `(Ddet(A)[E]*T-3*det(A)*trace(E))/T^4`, with exact T. It never rounds normalized tensor components, an intermediate determinant, trace or trace cube. Exactly zero trace rejects; other finite signs and indefinite tensors are arithmetic inputs. Every final component is nearest-even rounded; rounded zero is+0. Nonfinite input/seed or final primal/derivative overflow rejects without modifying caller output.

The [contract](../../../docs/NORMALIZED_DETERMINANT.md) and [source review](../../../docs/reviews/normalized-determinant-core-v1/README.md) describe the exact dyadic/radical quotient. C++ compares its radical numerator with an exact dyadic boundary times a positive exact denominator, reusing the unchanged determinant integer/sign arithmetic. An approximate floating guide only proposes a cell; exact midpoint checks certify it, with a complete binary-search fallback. The independent review finds no blocking defect and derives conservative10499-bit comparison differences/20998-bit comparison squares. Dynamic uint32limbs retain these values; local multiplication accumulation fits uint64 exactly. These are size/correctness arguments, not performance qualification.

The [independent reference packet](../../../docs/reviews/normalized-determinant-reference-v1/README.md) froze98unique fixtures before reference evaluation. Cartesian/cofactor Decimal640/960calculations pass all50finite precision checks, including593predeclared algebraically exact-zero branches with raw residuals retained. Independent rational/irrational rounding-cell certificates resolve1988components (1644rational,344irrational) with zero unresolved results. The coordinator reproduced the complete reference, rounding-audit, limb-probe and malformed-input-probe JSON exactly before compiled observation.

The [executable freeze](prospective-freeze.json), SHA256 `a7b79e951ada1d9ae3121ab2c074768c54bf090851ac90f4b38f915634a59472`, pins53source/reference/harness files and the protocol/literal request stream. No cache or bytecode enters this closure. Two supplementary cases reverse the columns of independently certified derivative-overflow fixtures, retaining their direction vectors and forcing a late derivative failure. Every rejected Jet call is immediately followed by the same accepted baseline. All expectations and exact-bit gates were fixed before either build or compiled call.

## Observed coverage

| Measure | Result |
|---|---:|
| Independent fixtures |98 |
| Supplemental late-overflow permutations |2 |
| Calls per backend |155 |
| Accepted Jet calls, including recovery controls |100 |
| Rejected Jet calls / immediate recoveries |55 /55 |
| Derivative columns per accepted Jet |38 |
| Component/seed input mutation |0 |
| Native/Wasm/reference bit failures |0 |

The fixtures distinguish85scalar successes from45Jet successes before expansion. They include all38seed-poison columns, six nonfinite primal inputs, four exact-zero traces, three final-primal overflows and two finite-primal/derivative-overflow fixtures. Extreme cases verify that isotropic max-finite tensors succeed despite a trace/determinant outside binary64 range; minimum-subnormal isotropic tensors succeed despite a determinant/trace-cube below that range. Minimum-subnormal anisotropy distinguishes overflowing seeded derivatives from valid zero-seed evaluation. Signs, oblique actual clay boundary inputs, rank loss, mixed scales, underflow/canonical zero and trace cancellation are retained.

Native and Wasm ordinary Release builds ran serially with one explicit target and --parallel1/EMCC_CORES1. Both completed normally. Exact commands, compiler versions, artifact hashes, raw journals and actual CMake cache/compile/link configuration are retained. There was no fast-math or contraction override. All9new source/assessor tests pass; all30targeted determinant tests pass, including existing core, DSL and expression-study contracts. No fixture, budget or policy changed after observation and no numerical failure was discarded.

[assessment.json](assessment.json) contains the exact gate result. The manifest and verifier validate retained source snapshots, live source identities, opaque journals, command/build/artifact bindings and identical reassessment. The portable replay reconstructs the frozen closure in a temporary directory and must reproduce the same result without compiling or executing material binaries; it reopens artifact files only to verify their hashes. This removes ambient source/cache dependence. Temporary artifact availability remains required for those hash checks.

## Remaining work

Register the dimensionless operation through the common DSL/interpreter/compiler/history paths, preserving old hash-bound source evidence before shared edits. Freeze an executed-context/branch/AD/failure study before compiled observation. Then create a separate clay2005 candidate replacing only the homogeneous determinant factor with this operation on the original stress tensor. Retain all120prior literal requests, independent source vectors/budgets, support/recovery and parity policy. The failed normalized-H whole-rate study remains failed; primitive success does not predict complete-law accuracy.

No model definition, source domain, stress floor, clipping, fit, public catalogue, website, finite integration, complete-model tangent, experimental validation, scientific admission, push or deployment changes.

## Reproduction

From repository root:

```sh
python3 -B -m unittest discover -s tests -p 'test_*determinant*.py'
python3 -B catalogue/investigations/normalized-determinant-v1/verify_study.py
python3 -B catalogue/investigations/normalized-determinant-v1/replay.py
```

Do not rerun builders/collectors into retained paths; they require fresh outputs. A future study that changes source or gates requires a new identity.
