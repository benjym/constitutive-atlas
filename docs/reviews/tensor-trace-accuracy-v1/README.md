# Three-term tensor trace accuracy design

Task `NUM-trace-cancellation-design`; owner `review_igs97`; 2026-10-31. Source-only proposal and executable Python specification. No shared arithmetic changes, compilation, compiled execution or scientific admission. The frozen negative sand study remains unchanged.

## Observed problem and current mapping

`cpp/include/atlas/tensor.hpp:97` evaluates trace as `(xx+yy)+zz`. Its Jet addition (`:23`) repeats the same operation in every derivative column. The actual binary64 input `[500,1e-130,-500]` therefore returns0. The exact-input real trace rounds to `1e-130`; with e=.75 the sand void expression returns `-1.7500000000000002e-130`. This is a generic arithmetic defect, not a constitutive-law correction.

`atlas/dsl.py:77–78` uses Python built-in `sum`; on the inspected Python3.14.7 it preserves this witness. Its result cannot define a cross-version numerical contract. `atlas/dsl.py:244–269` emits ordinary `trace(...)`; `dev` also calls trace (`tensor.hpp:98`, `dsl.py:81–82`). Repairing the shared trace changes all dependent models, including their deviatoric projections. Existing frozen sources/results must remain replayable by the separate archive lane. Do not silently re-assess historical studies against the changed arithmetic.

## Proposed bounded contract

For three **actual binary64 diagonal inputs**, return the nearest binary64 value of their exact real sum, round-to-nearest/ties-to-even. Reject nonfinite inputs and a final sum that rounds outside finite binary64. Finite final sums must not fail solely because a particular addition ordering overflows. No arbitrary-length summation, dot-product repair, model-ID branch or new physical parameter is proposed.

Canonicalize exact zero to **positive zero**, including three negative zeros and exact cancellation. Every nonzero subnormal exact sum is supported. Any finite binary64 sum is an integer multiple of the smallest subnormal; sums of three inputs cannot produce an exact nonzero magnitude below that quantum. Preserve actual values; do not normalize or clip inputs.

A checked API should fill a local candidate and commit output only on complete success. Suggested overloads are `sum3_checked(double,double,double,double&)` and `trace_checked(Sym<double>,double&)`, plus a Jet overload. A same-sign final overflow is a numerical failure, not a plausible large finite answer. A direct `trace(Sym<T>)` compatibility wrapper can return a nonfinite sentinel on failure so existing generated finite checks reject it; or the compiler can use an `or_mark` form consistently. Root must review all direct and nested `dev` uses before choosing failure plumbing. Preserve lazy `select`: an unselected trace expression must remain unevaluated.

`sum3_checked` checks its three operands. The tensor wrapper should explicitly choose and document whether it checks all six tensor components/seeds (recommended consistent full-tensor finite validation) or only the three accessed diagonals. The mathematical value and derivative ignore off-diagonal components; do not turn an off-diagonal finite seed into a trace derivative.

## Minimal fast path and rare exact fallback

Use binary64 operations with nearest-even rounding, gradual underflow, no excess precision and no fast-math/reassociation. Knuth TwoSum gives an error-free two-term expansion when its operations are finite; the prototype checks every intermediate. General EFT context is described by [Rump, Ogita and Oishi, Fast High Precision Summation](https://www.tuhh.de/ti3/paper/rump/RuOgOi08.pdf), Introduction and Section3. This packet does not claim to implement that paper's full algorithms.

1. TwoSum(a,b)=(s,e), TwoSum(s,c)=(t,f). If e=f=0, t is exact and can return immediately, canonicalizing zero. This cheaply handles zero/unit derivative seeds.
2. Otherwise TwoSum(e,f)=(q,low), TwoSum(t,q)=(h,tail). The exact real sum is **h+low+tail**.
3. If low=tail=0, return exact h. Otherwise compute the smaller adjacent finite spacing at h. If both neighbors are finite and `max(abs(low),abs(tail)) < spacing/4`, return h. The exact correction magnitude is at most twice that maximum, strictly less than half either spacing; h is therefore the unique nearest float. Neighbor spacings are powers of two, so multiplying by1/4 is exact or underflows conservatively to zero. The strict inequality deliberately avoids midpoint cases.
4. On any nonfinite EFT intermediate, uncertified rounding, zero/subnormal rounding ambiguity or edge-range ambiguity, use a **three-term exact fallback**. Do not return an arbitrary compensated sum without either a rounding certificate or exact fallback.

The fallback decodes each finite binary64 into a signed integer coefficient of2^-1074. For exponent bits E=0, coefficient is the fraction bits; for1<=E<=2046 it is `(2^52+fraction) << (E-1)`. Add positive and negative magnitudes exactly, subtract once, then round the magnitude once by retained53bits and exact guard/remainder/tie-even logic. Reconstruct binary64 bits, canonicalize zero and reject a rounded exponent2047. No floating intermediate overflow is possible in this path.

A finite input coefficient needs at most2098bits; the sum of three magnitudes needs at most2100bits. Thus33uint64 limbs suffice;34 is a conservative implementation allocation. Use bounded local arrays, shifts, carry/borrow and bit inspection, with no heap allocation or big-integer dependency. `prototype.py` uses Python integers as a readable specification of these fixed operations, not a proposed C++ dependency. This is a bounded3sum fallback, not a general superaccumulator library. [Neal2015](https://arxiv.org/abs/1505.05571), abstract and introductory superaccumulator description, supplies primary context for exact accumulation then rounding; this packet's small fixed3term layout is independently derived and is not copied author code.

A simpler opposite-sign ordering or `long double` alone does not establish this contract. Native extended precision is not available identically in Wasm; a small residual may be arbitrarily far below the largest term. Python `math.fsum([DBL_MAX,DBL_MAX,-DBL_MAX])` raises intermediate overflow on the inspected runtime despite its finite exact result. Neither built-in sum nor bare fsum is the portable full-range reference. The Python DSL can use the same three-term specification, or fsum on a proved-safe range plus the exact fallback for exceptional ranges; verify against the same corpus.

## Jet derivative contract

Trace is real-linear. For each of the38 Jet directions, compute the nearest-even exact-input sum of the **three supplied diagonal seed coefficients**, using the same scalar helper independently of the primal value. This is the analytic derivative of the real trace map applied to supplied seed directions, rounded once; it is not a derivative of the discontinuous rounded bit-program. Do not differentiate the EFT certificate, permutation or bit-decoding branches.

Independent diagonal basis directions have derivative1; off-diagonal basis directions have derivative0. Arbitrary seed triples, including cancellation and subnormals, must obey the same summation contract. Check all38 columns, including index37. Finite primal plus any nonfinite or final-overflow derivative must reject the entire candidate Jet, leaving an existing destination unchanged. A failure followed by a valid call must recover with no sticky state. Exact-zero derivatives canonicalize positive zero. The prototype raises before returning a partial Jet; future C++ tests must check destination nonmutation explicitly.

## Retained checks and cost limits

`fixtures.py` obtains independent exact sums with `Fraction.from_float` and rounds through Fraction.__float__. It does not call the prototype's decoder or rounder. `corpus.json` retains97 permutation cases,85finite results and12 final-overflow rejections, including cancellation, huge/tiny mixtures, half-even ties, below/at overflow midpoint, subnormals, normal/subnormal boundary and signed zeros. Hex inputs/results and exact rational numerator/denominator make it portable without decimal parsing ambiguity. Nonfinite/type cases are explicit tests, not silently coerced numeric records.

Eight test groups pass: corpus replay,12,000 deterministic random bit-triples, all38 cancelling Jet columns, six diagonal/shear seed identities, derivative overflow in index37, nonfinite/Boolean inputs and seeds, signed zero, and the historical witness. All finite prototype results match independent Fraction bit-for-bit. These tests and the mathematical decomposition support this design, but **no compiled implementation has been verified**.

The certificate substantially reduces fallback use in the retained random diagnostic:495/12000triples require fallback, compared with11999/12000for an exact-additions-only shortcut. This distribution is not a solver benchmark and does not establish interactive performance. The adversarial corpus intentionally reaches fallback frequently. Full Jets can require up to39 scalar helper calls. Root should first measure actual rate/AD/integration workloads, count fallback frequency and compare the bounded expansion path with a reviewed3partial implementation. Keep exact contract fixed if optimizing. A complete34word calculation for every column is not recommended as the unconditional hot path.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -v test_design
```

## Smallest implementation and study

Archive old shared tensor/DSL bytes first. Implement the generic three-term helper and scalar/Jet trace plumbing only; keep unrelated sums/operators unchanged. Add a separate operator probe with the97cases, complete38seed checks, invalid derivative/primal rejection and same-instance recovery. Freeze inputs, exact references, signed-zero/failure policy, compiler configuration, generated schema contexts and artifact receipts before collection. Require bitwise scalar/column agreement on native/Wasm/Python and descriptor/version binding, not an absolute error floor hiding tiny residuals. Exercise direct DSL trace, nested dev, lazy branch and ordinary rate contexts.

The old failed sand study remains failed. A new separately identified source/engine study can rerun the unchanged constitutive definition and policy with new engine hashes, preserving raw evidence for both. Passing the repair does not imply finite-path, AD of the sand law, physical or scientific admission.
