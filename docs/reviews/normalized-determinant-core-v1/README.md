# Normalized determinant core: independent source review v1

Task REV-normalized-determinant-core-v1. Reviewer sanisand_loading_source, 2026-10-31. **No blocking arithmetic defect found in the inspected source.** This is a prospective source review, not compiled verification, an independent numerical oracle, performance qualification or a model-admission decision. No builds, compiled artifacts or supplied author code were executed. The independent fixture/reference worker owns the mathematical reference corpus; this review does not derive that corpus from implementation results.

## Exact inspected bytes

[manifest.json](manifest.json) pins four snapshots under reviewed-sources/: new C++ normalized_determinant.hpp, new Python normalized_determinant.py, and the reused C++/Python determinant cores. The snapshots have their repository-relative paths. Mutable work-board/AGENTS bytes are not numerical dependencies. Findings apply to these bytes; source edits require a new/additive review identity. The prospective contract inspected was docs/NORMALIZED_DETERMINANT.md: exact original stored Mandel inputs, exact nonzero trace, nearest-even final primal/directional values, canonical +0 and transactional rejection.

## Quotient, sign and rounding reasoning

Let P=a+b*sqrt(2), T=xx+yy+zz computed as exact dyadics. The primal construction uses numerator P and denominator T^3; the checked entry rejects exact T=0 before construction. `quotient` negates both numerator coefficients and denominator if the denominator is negative. Consequently the positive-denominator invariant holds for every valid checked call, including negative T. Direct helper calls with zero/negative denominator do not silently succeed: `rounded` rejects nonpositive denominators. The helper is not advertised as a public validation substitute.

For denominator d>0 and dyadic rounding boundary y, `compare_to` computes sign(a-y*d+b*sqrt(2)). Subtraction/multiplication are exact, including when y*d does not fit binary64. Reused `radical_sign` first separates equal-sign or zero coefficients. For opposite signs, comparing a^2 and 2*b^2 determines the radical's sign, multiplied by sign(a). This avoids incorrect squaring of two unknown-sign sides. With rational/dyadic nonzero a,b, exact cancellation a+b*sqrt(2)=0 cannot occur; the zero comparison still behaves correctly. Python's reused comparator has the same sign logic with arbitrary rational coefficients, so dividing by exact T^3 before calling it does not require the quotient coefficients to remain dyadic.

The rounding implementation takes the sign of the exact radical before making its magnitude positive. A zero numerator returns +0 only after the denominator check; it cannot accept 0/0. The overflow boundary is midpoint(maxfinite, conceptual2^1024). Equality rejects: at that tie the conceptual upper significand is even, so nearest-even overflows. This implements final-range rejection rather than rejecting an intermediate P or T cube.

Every candidate cell is certified with exact lower/upper midpoint comparisons and the candidate's low significand bit. Zero has no negative lower boundary because the searched magnitude is nonnegative. At the minimum-subnormal half-way point, zero is even and correctly selected; sign is applied only for a nonzero bit pattern, yielding canonical +0 for either underflow sign. Normal/subnormal and power-of-two transitions are covered by midpoint arithmetic on exact adjacent values rather than a constant-ULP approximation.

The floating guide only proposes one of five cells. Any catastrophic cancellation, overflow, underflow, negative approximation or inaccurate sqrt(2) guide cannot certify a wrong cell. If no candidate is certified, the bounded integer-bit binary search covers all positive finite binary64 encodings, finds the lower representable neighbor, and performs a final exact midpoint/tie decision. The earlier overflow check ensures that the chosen upper neighbor cannot be infinity. The uint64 bit-index arithmetic stays below maxfinite+2, well below uint64 range; lower-neighbor subtraction is guarded.

## Degree, trace and AD reasoning

For stored Mandel components x,y,z,u,v,w, the reused polynomial is

`P = xyz - (x*v*v+y*w*w+z*u*u)/2 + (u*v*w/2)*sqrt(2)`.

These are the exact Cartesian determinant terms because the physical off-diagonals are u/sqrt(2),v/sqrt(2),w/sqrt(2). Its six gradient entries are the exact partial derivatives, including the half-radical off-diagonal cross terms. No normalized component, rounded sqrt(2) coefficient or rounded cofactor is used in the exact computation.

For each of38 stored seed columns E, code forms the exact directional determinant derivative DP as the sum of six gradient-times-seed radicals and DT from the three diagonal seeds. It forms `(DP*T-3*P*DT)/T^4`. The T^4 denominator is positive for nonzero T; the numerator retains the sign of T in its first term. This is the quotient rule at the original stored primal, not the derivative of a rounded normalized matrix or of the rounding map. Primal and each seed column are independently rounded once from their exact expressions. A finite primal therefore does not permit a nonfinite/overflowing derivative.

The structural static assertions require six stored tensor components and exactly38 derivative slots on both the result and source component type. All six primals and all228 input seed entries are explicitly finite-checked before trace/polynomial work; no zero cofactor/zero seed optimization skips validation. The actual calculation iterates all38 columns. A different double/Jet layout must fail compilation rather than silently shorten the derivative loop. This review establishes the loop/formula by inspection; it does not establish a compiled template instantiation or ABI.

An exact trace may overflow binary64 or be much smaller than rounded summation would preserve. Exact Dyadic addition retains it. A finite binary64 exact sum cannot lie strictly between zero and2^-1074; hence an exact nonzero trace never underflows this integer representation. Its cube/fourth power and P may exceed or fall below binary64 range without early range rejection. Mixed magnitudes are handled by exponent alignment and arbitrary limb vectors, preserving cancellations. Python uses exact Fractions before quotient rounding, with the same property.

The Python API accepts only actual int/float entries, rejecting bool and other object types, and converts finite entries to stored binary64 before taking exact Fraction values. This is compatible with a binary64-input operation. It does not promise exact arithmetic on arbitrary-size integers supplied in place of binary64 values. Overflowing integer conversion is rejected by the finite check. No Python AD API was added; derivative coverage is a separate C++ Jet path. The bounded check_python_rejection.py probe loads only the reviewed snapshots and verifies12 malformed inputs reject: wrong lengths, bool/complex/string/None components, NaN/infinities, overflowing integer, non-container and generator. Sized malformed inputs raise ValueError; objects lacking len raise TypeError. This is rejection consistent with the contract; no uniform exception-class promise was specified, so the difference is not a blocker. Results are retained in python-rejection-results.json; accepted-value references remain with the independent worker.

## Conservative integer bounds

Use M=2^1024 as a strict bound on each finite input/seed magnitude, and q=2^-1074 as a common dyadic quantum. Bounds include sign-indefinite tensors and arbitrary finite seeds, without an SPD assumption.

- T is an integer multiple of q, |T|<3M. Therefore T^4 has quantum q^4=2^-4296 and |T^4|<81M^4<2^4103.
- The rational coefficient of P has absolute value <=(1+3/2)M^3=2.5M^3; its radical coefficient <=M^3/2. Both have quantum at least q^3/2=2^-3223.
- The rational coefficient of DP is bounded by [3*(3/2)+3]*M^3=7.5M^3; the radical coefficient <=1.5M^3. This includes all six arbitrary seed contributions, with |DT|<3M.
- For N=DP*T-3*P*DT, rational coefficient magnitude <45M^4<2^4102, radical coefficient <9M^4<2^4100. Both have quantum at least q^4/2=2^-4297. The factor3 is exact binary64 and exact Dyadic.
- All finite rounding boundaries and the conceptual overflow midpoint have magnitude <2^1024 and quantum at least2^-1075. Thus boundary*T^4 has quantum at least2^-5371 and magnitude <2^5127.
- The rational comparison difference N.a-boundary*T^4 has magnitude <2^5128, quantum at least2^-5371, and therefore at most10499 magnitude bits. Squaring it yields at most20998 bits. N.b squared and doubled is smaller; the factor2 is an exponent increment. The primal cubic-denominator comparisons are bounded by these same conservative maxima.

Normalization can only reduce the limb magnitude; it cannot increase these bit spans. Exponents, exponent sums/differences, shift counts and bit lengths are conservatively within +/-22000 or22000 respectively, far below signed32 limits. A20998-bit integer needs at most657 uint32 limbs. Dynamic allocations can fail, but there is no fixed-array truncation or declared limb ceiling. This is a size/overflow argument, not a practical runtime/complexity bound.

## Reused limb arithmetic reasoning

Big values are trimmed little-endian uint32 limbs. Addition's maximum local sum is2*(2^32-1)+1<2^33, safely uint64. Subtraction is called only after magnitude ordering; b_limb+borrow<=2^32. A negative intermediate converts modulo2^64 then to uint32, which gives the intended low word; the separately computed borrow is exact. Normalization's scan is safe because a nonempty trimmed magnitude contains a nonzero limb.

For multiplication with B=2^32, the local accumulation is bounded by `(B-1)^2+(B-1)+(B-1)=B^2-1`, exactly uint64max. There is no lost carry above bit63. At row i the terminal carry slot i+len(b) has not been touched by prior rows (their furthest terminal slot is one smaller), so assignment there does not overwrite an accumulated contribution. Inner slots include earlier row carries normally. The mathematical output fits the allocated len(a)+len(b) limbs.

Shift splits n into whole limbs and rest0..31. `a[i]<<rest` and the preceding limb's high fragment occupy disjoint low/high fields in each destination limb, so OR is correct. The `rest` guard prevents shifting by32. uint32 shifts truncate the intended discarded high bits, retained in the next destination limb. Exponent-alignment differences are nonnegative before conversion to unsigned. The bounds above rule out signed-int overflow on these conversions/operations for this operation's valid inputs.

[check_limb_bounds.py](check_limb_bounds.py) implements source-faithful Python translations of these specific limb formulas, checking against Python integer arithmetic with a fixed seed, adversarial limb boundaries and a657-limb all-ones carry case. [results.json](results.json) retains7744 add,7744 subtract,7745 multiply and704 shift checks, zero failures. These tests can reveal transcription-level arithmetic mistakes, but they are not compiled evidence and do not replace the reasoning or independent exact-input normalized-determinant references.

## Transactional behavior and remaining gates

`checked` writes only to local candidate and exact scratch until the final `out=candidate`. Input/trace/range/derivative rejection leaves the caller output untouched. Allocation failure before that assignment may propagate without modifying caller output, as allowed by the contract. This assertion assumes the intended ordinary double/Jet result types; an arbitrary user-defined throwing assignment operator is outside the structural interface's demonstrated guarantee. Guide floating exceptions under a custom trapping FP environment are not part of the supported default IEEE execution contract.

No corrections or gate relaxations are requested from this review. Required next evidence: frozen independent primal/38-column bit certificates, actual serial native/Wasm compilation/execution with strict FP flags, sentinels/recovery including late-column failures, source/seed nonmutation and integer/mixed-scale edge cases. The checked function's API behavior must be tested, not only its internal rounder. DSL registration/context routing and the source-preserving whole-law study remain separate. Performance remains unqualified, especially exact binary-search fallback on cancellation/extreme dynamic ranges.

Reproduce source-only checks: `python3 -B docs/reviews/normalized-determinant-core-v1/check_limb_bounds.py` after integration, or the same script from this staged packet. No Atlas import, native library or author code is needed. Compare emitted JSON to retained results and verify manifest SHA256 values. No live source or schema was edited by this worker.
