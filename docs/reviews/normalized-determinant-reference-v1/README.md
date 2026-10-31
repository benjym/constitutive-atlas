# Independent normalized determinant references v1

Task REF-normalized-determinant-v1; 2026-10-31. This source-only packet supplies independent expectations for `normalized_determinant(A)` and its38directional derivatives on **original exact binary64 Mandel inputs**. No Atlas imports, new implementation/core execution, compiled builds/calls, author-code execution, material rates or model admission. Old reference packets and gates remain untouched.

## Freeze and format

`prospective-freeze.json` SHA256 `7d4ed3c8d83e97bbc9a902e32b1a74b93b8328197cfd8c6a28de48f1fb84c384` was written and sent to the coordinator before evaluating these references. It pins only the prospective [generic numerical contract](../../NORMALIZED_DETERMINANT.md) and prior independent determinant **input** freeze. It does not pin/import the new implementation, which is under separate independent review.

There are98unique fixtures: the prior78actual-input/seed tensors and20new normalized-contract cases. Prior determinant output values/statuses are **not** reused; the new function has different failure semantics and derivatives. Prefix `prior/` and `prior-determinant-*` tags identify inherited inputs, not inherited normalized-determinant claims. For example, a determinant-overflow input can now succeed because its normalized ratio is finite; prior determinant midpoint tags need not remain midpoint cases for the ratio.

`cases.json` is the compact adapter fixture. Each row has:

- `id`, `values` six literal strings in Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz, and `seeds` six rows by38literal columns.
- `primal_expectation`: `ok:true,hex` for a scalar success, or `ok:false,reason` for a scalar rejection. A seed-only or derivative-only failure does not imply scalar rejection.
- `expectation`: full-Jet `ok:true,value_hex,derivatives_hex[38]` with finite numeric values also retained, or `ok:false,reason,unchanged_output:true`. Null rejection values are not numerical references.

Intentional `NaN`, `Infinity`, `-Infinity` tokens are strings, not invalid JSON numbers. The future harness must construct those invalid primitive numeric inputs and distinguish a primitive rejection from parser rejection. All normal finite literals first parse to binary64, then exact integer ratios. Exact expected hexadecimal bits are required; every successful rounded zero must be+0. A rejection must preserve the caller's entire distinctive primal/38derivative sentinel output.

## Mathematical calculation and certification

Write T for the exact real sum of the stored three diagonals, P for the Cartesian determinant and E for one stored seed direction. The source-independent mathematical operation is P/T³, and the directional derivative is `(cofactor(A):E*T-3*P*trace(E))/T^4`. The exact trace need not fit binary64. Exactly zero trace rejects even if P=0. No sign/SPD or magnitude gate is imposed. Each primal and derivative is independently rounded once at its exact value; differentiate the real ratio, not the binary64 rounding map or a rounded normalized tensor.

`reference.py` copies the earlier worker's independent standard-library Cartesian scaffold into this new packet; it never edits/imports the old packet or the production implementation. Its Decimal route reconstructs Cartesian off-diagonals by dividing exact Mandel inputs by high-precision sqrt(2), computes a3x3cofactor determinant and the full cofactor:seed contraction. The trace is constructed from the exact rational sum before Decimal conversion, avoiding false trace-zero results due to intermediate cancellation. The quotient and quotient derivative are calculated at640and960digits.

The predeclared convergence gate is max_i |a_i-b_i|/max(1,|a_i|,|b_i|)<=1e-200. Exact zero components have a **prospectively declared exact-algebraic branch**: the independent exact Cartesian radical field must prove both rational/radical coefficients zero; the convergence comparison then uses exact0 for that component. Raw Decimal residuals remain in `references.json`. This is important for tiny isotropic inputs: subtracting approximate large derivative terms can leave a numerical residual even though the exact derivative is zero. It is not a post-observation tolerance relaxation or arbitrary ignoring of nonconvergence. Every nonzero component must meet the original convergence gate. All50full finite-input/nonzero-trace cases pass; maximum reported nonzero/corrected scaled difference is about5.06e-639. There are593exact-zero component branches.

The separate exact calculation uses ordinary Cartesian matrix/cofactor operations in Fraction pairs a+b*sqrt(2). It divides each coefficient by the exact Fraction trace powers, including negative T³, without rounding intermediate determinant, trace, powers or cofactors. Thus the same field represents exact normalized primal and exact directional derivative, although coefficients are general rational numbers rather than only dyadics.

For irrational components, exact integer square root gives rational bounds of width10^-512 around sqrt(2). The scaled/shifted rational interval must have identical nearest-even binary64 endpoint results. Pure rational components use exact rational rounding. `verify_rounding.py` separately checks all claimed endpoints/results against exact rational binary64 rounding cells and parity, including the exact overflow threshold2^1024-2^970. This certifies the supplied corpus's correct rounding without trusting a Decimal approximation to select a midpoint side. No unresolved bound occurred. The512digit bound is not claimed sufficient for every possible binary64 tensor/seed combination; a production exact comparison must not depend on that empirical precision.

## Outcomes and distinct scalar/Jet failures

The independent results are:

| Fixture outcome | Count |
|---|---:|
| Unique fixtures |98|
| Scalar successes / rejections |85 /13|
| Full-Jet successes / rejections |45 /53|
| Nonfinite primal rejections |6|
| Nonfinite seed rejections |38|
| Exact trace-zero rejections |4|
| Final primal overflow rejections |3|
| Finite primal with final derivative overflow |2|

All1988distinct evaluated primal/directional components are certified:1644rational and344irrational. The count includes a primal certificate for each nonzero-trace/finite-primal input even when seeds are invalid; for the50fully finite cases it additionally includes all38directional certificates. The full-row repeated primal certificate is checked for identity and not counted twice.

Important explicit cases include:

- The original five clay boundary tensors plus shear-near control, regular/indefinite/rank-deficient tensors, signed zeros, mixed scales and rounded-covariance witnesses. Actual rounded tensors remain independent inputs; no false exact covariance identity is imposed.
- Maximum finite isotropic tensors of either sign: exact trace and determinant overflow binary64 individually, but the normalized primal is RNE(1/27), hex `0x1.2f684bda12f68p-5`, and all derivatives are exact+0. Minimum-subnormal isotropic tensors give the same finite result and zero derivatives despite determinant/trace-cube underflow in naive arithmetic.
- `[minsub,minsub,2minsub,0,0,0]`: scalar1/32succeeds but basis seed directions overflow the final Jet derivative. The same primal with all-zero seeds succeeds as a full Jet. Rejecting merely because the tensor is tiny would violate the contract.
- `[1,-1,2^-500,0,0,0]`: finite scalar `-0x1.0000000000000p+1000`, but a final derivative overflows. With2^-600instead the final scalar itself overflows and both APIs reject.
- Exact trace cancellation `[maxFinite,minsub,-maxFinite,...]`, where the exact trace is minsub and the final ratio overflows; and `[2^500,-2^500,1,...]`, whose final ratio and38directions are finite despite an unrepresentable naive determinant.
- Trace-zero with nonzero determinant and trace-zero with determinant0; both reject, independently of rank or positive/negative stress interpretation.
- Three normalized rational midpoint cases, plus underflow-to-canonical-zero and subnormal outputs. Exact rational certificates, not input-origin tags, identify normalized midpoint behavior.
- All38individual seed poison columns, including directions whose mathematical coefficient vanishes. Every stored seed must be finite. Both scalar and Jet expectations are supplied so a harness cannot accidentally count seed rejection as scalar failure.
- Two homogeneous directional fixtures with every seed equal to+Aor-A. All38derivatives are proved exactly zero at the regular and sensitive oblique stored tensors, using the real degree-zero identity rather than rounded normalized components.

## Recovery and driver adaptation

The baseline is `prior/regular/sphere`; both its scalar and full-Jet evaluations are certified successful. This packet contains98unique rows only. The coordinator should append an identical baseline request **immediately after each of53Jet rejections**, preserving its literal values, all228seed values and exact expected output. That gives151prospective Jet requests. If scalar transport is a separate stream, it can similarly recover after the13scalar rejections under an explicit separate request sequence. Do not turn repeated recoveries into additional independent reference cases.

A driver must verify status, all expected hexadecimal bits or all unchanged sentinels, exact row identity/order, persistent instance recovery, and raw evidence/build/source bindings. The adapter may change request encoding/API plumbing without changing mathematical expectations. Unknown-status or partial-output handling cannot be treated as an accepted rejection. No compiled observation has occurred in producing this packet.

## Independent proof requirements and limitations

The prospective implementation contract remains under independent code review. At minimum it must retain exact original-input trace and determinant/cofactor numerators; normalize a negative scalar denominator without changing the quotient; compare a radical quotient against a dyadic rounding boundary by exact cross multiplication; establish signs before integer squaring; cover normal/subnormal/overflow midpoints and canonical zero; and validate all input/seed finiteness before final assignment. The derivative numerator is degree4 counting the seed, so integer capacity/shift reasoning must cover a larger intermediate exponent span than the cubic primitive. All result fields must remain unchanged on failure. Intermediate overflow/underflow in ordinary floating arithmetic cannot be a rejection reason if the exact final results are finite.

The Decimal and exact-field routes share the mathematical Cartesian/cofactor definition; they are independent implementations, not a formal external proof of that definition. The rounding-cell audit supplies bounded exact certificates for these fixtures. It does not prove all-input implementation correctness, bound runtime/memory use or establish whole-law source-rate accuracy. No kernel, Python interpreter or native/Wasm output was used to choose expectations. Correct arithmetic here cannot imply a clay support theorem, complete material tangents, finite integration, calibrated preparation, experiment agreement or scientific admission.

## Reproduction

Standard Python3only, no PDF, author code, external library or network required. With PACKET the absolute installed directory, from the repository root:

```sh
python3 -B "$PACKET/reference.py" --packet "$PACKET" --root "$PWD" --output /private/tmp/fresh-normalized-determinant-references.json
python3 -B "$PACKET/verify_rounding.py" --packet "$PACKET" --output /private/tmp/fresh-normalized-determinant-rounding-checks.json
```

Outputs must be fresh. `freeze.py` can reproduce input selection into a separate fresh file; never overwrite the original prospective freeze. `manifest.json` pins the worker packet, including compact cases and the rich calculation/certificates. There were no unresolved references or failed convergence gates. No old source or numerical evidence was changed.
