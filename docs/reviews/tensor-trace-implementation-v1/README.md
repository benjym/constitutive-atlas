# Generic exact trace: staged C++ candidate

Task `NUM-trace-cancellation-candidate`; owner `review_igs97`; 2026-10-31. This is a source-only candidate for the [reviewed design](../tensor-trace-accuracy-v1/README.md). No shared files have been changed, no C++ has been compiled or executed and no model equations, thresholds, admission or historical evidence have changed.

## Deliverable and integration boundary

`trace_accuracy_candidate.hpp` contains the bounded three-term helper and checked scalar/Jet tensor wrappers. It includes only C++ standard headers, has no Atlas-type dependency, no heap allocation, no arbitrary-length API and no material branches. Structural wrapper templates are instantiated only for the existing Sym<double>/Sym<Jet> layout. Static assertions require six tensor components and38 Jet directions.

The coordinator may copy this exact header to `cpp/include/atlas/trace_accuracy_candidate.hpp` and apply `tensor-integration.patch` **after archival**. The zero-context patch requires exact baseline bytes (and `--unidiff-zero` if applied with git apply). Its prior tensor header is pinned in `reviewed-inputs.json`; it adds only the include, public `trace_checked` forwarding and replacement compatibility `trace`. `dev` retains its existing source and obtains the repaired trace through that forwarding. Compiler trace emission and lazy `select` remain unchanged. The candidate version string is `trace-three-binary64-certified-eft-fixed34-v1-candidate`.

All six scalar tensor components must be finite. For a Jet, every primal and every seed in all six components/38 columns must be finite, including unused off-diagonal values/seeds. A local candidate is committed only after every result is successful. Nonfinite input or final primal/derivative overflow leaves destination bits unchanged. Compatibility trace returns a nonfinite scalar or a Jet with NaN primal; existing whole-value finite checks must reject it. There is no sticky failure state.

The returned value is nearest-even of the exact real sum of three supplied binary64 diagonals. The analytic Jet action independently sums supplied diagonal seed triples by the same rule. This differentiates the real linear trace map, not rounded branch logic. Off-diagonal seed contributions are zero; their finiteness is still checked. Exact-zero primal and seeds canonicalize positive zero. Finite final results are supported even when a naive intermediate addition overflows.

## Candidate algorithm and assumptions

The two-TwoSum exact-result shortcut handles sparse unit/zero seed directions. Two further TwoSum operations produce the exact expansion h+low+tail. Return h when both residuals vanish or their maximum magnitude is strictly less than one quarter the smaller adjacent binary64 spacing; otherwise use the exact fixed34word fallback. See the design packet for the rounding certificate proof.

The fallback decodes three finite doubles into positive/negative integer magnitudes in units2^-1074, adds shifted53bit significands with explicit uint64 carry, subtracts magnitudes with borrow and rounds once with exact guard/sticky/tie-even logic. Three finite inputs require at most2100bits;34uint64 words supply2176bits. Input exponent2047 is rejected before decoding. Shifts are explicitly separated when offsets are zero; there is no shift by64 or signed-integer overflow. No final infinity is returned as a valid result. Exact midpoint overflow rejects; below-midpoint sums can round to DBL_MAX.

C++20, eight-byte IEEE binary64,53bit significands, ordinary binary64 expression evaluation (`FLT_EVAL_METHOD==0`), gradual underflow and masked floating exceptions are required. `__FAST_MATH__` and nonzero `__FINITE_MATH_ONLY__` are rejected at preprocessing. Build with no unsafe reassociation/finite-math-only/excess-precision options. A runtime rounding mode other than FE_TONEAREST skips EFT and uses the integer fallback, still producing nearest-even bits. The scalar API checks the rounding mode once; the tensor wrapper checks once and shares it across primal/seed calls. The code does not change the caller's rounding mode. Ordinary arithmetic may set floating exception flags, including underflow/overflow in a failed EFT attempt; preserving exception flags is not promised. FTZ/DAZ modes are outside the candidate support contract and must be excluded/tested by the build/runtime study.

No performance claim is made. The fast path avoids fixed-word work for many cases and sparse seeds, but the worst case requires39 scalar fallbacks. Each fallback uses bounded local arrays; no heap/bignum library is required. Solver throughput, Wasm stack use and fallback frequency need measurement before selecting this as the final production algorithm. Do not replace the rounding contract with an unreviewed compensated final addition to improve timing.

## Probe and source checks

`trace_probe.cpp` is independent of constitutive models. It exports `atlas_trace_selftest()` for Wasm and provides a native main. It emits97 original fixture records, all38 nontrivial derivative result bits, test counts and failure labels. It checks:

- Scalar97case exact results/rejections and rejected-output nonmutation.
- Full-six scalar nonfinite validation, sentinel failures and recovery.
- Primal cancellation and all38 signed cancellation derivatives.
- Six diagonal/shear basis directions.
- Every component/seed-column nonfinite rejection and whole-Jet nonmutation/recovery.
- Final primal/derivative overflow, finite intermediate overflow with valid final results, subnormal seed, positive-zero canonicalization and recovery.
- Alternate ambient rounding mode where runtime permits it, restoring the original mode afterward.

Compile with `ATLAS_TRACE_INTEGRATED` only after applying the routing patch. That mode also checks actual Atlas trace, nested dev rejection and the compiler-equivalent lazy ternary. The probe then uses the installed header through tensor.hpp, avoiding a second copy from the staging directory. Without that macro it tests only the staged candidate against the existing Atlas types. A full generated-DSL context study is still needed; the ternary check alone does not establish schema/compiler integration.

`trace_fixtures.hpp` is mechanically generated from the independent97case Fraction corpus retained in the design packet. It stores actual input and expected binary64 bits, not decimal approximations. `generate_fixtures.py --check --corpus CORPUS` verifies this transport. `check_source.py` independently derives exact results with Fraction and mirrors the fixed-limb transcription;97 fixture cases,12,000 seeded random triples and12,276 exponent/alignment cases pass. Its mirror tests do not execute or certify the C++ implementation, compiler behavior, UB absence or runtime performance. `source-checks.json` records those bounds honestly.

```sh
python3 -B check_source.py
python3 -B generate_fixtures.py --check --corpus /path/to/constitutive-atlas/docs/reviews/tensor-trace-accuracy-v1/corpus.json
```

## Coordinator-only next checks

Before observing compiled results, freeze this header/probe/fixture source and exact acceptance policy, then build one explicit native probe and one Wasm probe serially. Do not tune exact-bit criteria after observations. Run a persistent same-instance pair of selftests and independently validate complete fixture/seed outputs, descriptor/version, raw receipts and artifact/source hashes. Native executable exit status must bind its JSON failure count; Wasm runner must require exact keys/types/counts rather than trusting a success label. Retain raw output before parsing.

A candidate compile command (not run by this agent) is `c++ -std=c++20 -O2 -I /path/to/repo/cpp/include trace_probe.cpp -o /private/tmp/atlas-trace-probe`; after integration add `-DATLAS_TRACE_INTEGRATED`. Use ordinary IEEE options and retain actual commands/toolchain versions. A Wasm build needs a modularized/no-entry CABI target and exported runtime ccall; root owns exact flags/receipts. Also test generated direct trace/dev/lazy DSL contexts and broader engine regressions with archives preserving their original sources.

The original failed sand study remains failed. A separately named follow-up may test unchanged constitutive equations against repaired engine bytes, with no model-specific bypass or relaxed thresholds. Full constitutive AD, finite integration and scientific admission remain separate.
