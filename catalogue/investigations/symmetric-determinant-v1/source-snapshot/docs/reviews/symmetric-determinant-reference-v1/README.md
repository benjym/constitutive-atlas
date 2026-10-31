# Independent symmetric Mandel determinant references v1

Task REF-robust-symmetric-determinant-v1, 2026-10-31. Scope: generic determinant and 38-direction Jet references, independent of Atlas/material evaluation. The worker stages this directory privately for coordinator integration into `docs/reviews/symmetric-determinant-reference-v1/`. No shared code, builds, compiled execution, material rates or scientific admission.

## Prospective identity and policy

`prospective-freeze.json` SHA256 `7122803d372c9784f501f6575a07ad8263f7a65a7f54ad20da90555349da8ad1` was created and sent to the coordinator **before reference evaluation or compiled observation**. `freeze.py` records 78 literal cases, six Mandel values each and a6x38seed matrix, plus precision/convergence/rounding/failure policy. The clay actual inputs pin `catalogue/investigations/clay2005-rates-v3/protocol.json`; no source vector or support label is changed.

All finite tokens mean the exact binary64 value obtained by parsing the literal, reconstructed through integer ratios. Coordinates are xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Intentional `NaN`, `Infinity`, `-Infinity` tokens are strings representing invalid numeric inputs for the future primitive harness; they are never nonstandard JSON numeric constants. Signed zero input tokens are retained. Invalid handling must test the primitive itself rather than report a harness parser rejection as primitive evidence.

`cases.json` is the compact harness input: literal values/seeds and frozen expected status, primal and38derivatives, including hexadecimal expected finite binary64 values. `references.json` retains full Decimal estimates, convergence differences, exact Cartesian radical-field components and rounding certificates. Expectations are not fitted to any production result.

Success means every input and all228seed scalars are finite, the exact mathematical determinant and all38exact cofactor directional contractions round to finite binary64, nearest with ties even, and every rounded zero has positive-zero bits. The derivative is of the exact real determinant evaluated at the actual input, then independently rounded; it is not the derivative of a discontinuous floating-point rounding map. On rejection the caller's complete output must remain unchanged. False expectations therefore contain null values plus `unchanged_output:true`; null is not a numerical oracle. A later harness must initialize distinctive primal and all38derivative sentinels and verify all remain unchanged, not only status or primal.

Acceptance is exact expected status and exact hexadecimal primal/all38derivative equality. No ULP or relative relaxation is supplied. Final finite underflow to zero succeeds with canonical+0; final rounded overflow in either primal or any derivative rejects. Overflow of an intermediate expression alone must not force rejection when the exact final result is finite.

## Independent calculations and certification

`reference.py` imports only the Python standard library. Its main calculation reconstructs a Cartesian matrix with off-diagonals u/sqrt(2), computes an ordinary3x3cofactor determinant, and computes each direction as the full Cartesian cofactor:direction contraction. It uses Decimal160/320digits, with a frozen scaled convergence threshold1e-120 over the primal and all38directions. Exact rational midpoint cases do not trust a decimal approximation to settle a tie.

A separate exact calculation maps each Cartesian off-diagonal to `(u/2)*sqrt(2)` and performs generic matrix/cofactor operations in Fraction pairs a+b*sqrt(2). It does not import Atlas or implement the coordinator's signed-bigint midpoint-comparison algorithm. Pure rational components use exact rational nearest-even conversion. Irrational components enclose sqrt(2) between consecutive rational multiples of10^-512 obtained from integer square root. Both enclosure endpoints must round identically; otherwise the reference remains unresolved and the packet retains a failure. No unresolved component occurred.

`verify_rounding.py` independently checks the claimed rounded result against exact rational binary64 rounding cells. It does not rely on the host conversion merely because it returned a float. Rational lower/upper cell boundaries come from exact adjacent-float ratios; boundary equality is permitted only for even significands. Overflow starts at the exact halfway boundary2^1024-2^970. For irrational components both rational enclosing endpoints must lie in the certified cell. The sqrt(2) bracket is checked by exact squaring. This certifies every supplied result component, including rational midpoint cases and overflow components; it is stronger than agreement of two decimal precisions.

The Decimal route and exact Cartesian field route share the mathematical determinant/cofactor definition. They are two implementations, not independent scientific model derivations. This is a mathematical primitive with no paper-specific constitutive assumptions.

## Results and coverage

All34finite-input cases pass the160/320convergence policy; their1326components are resolved and their rounding cells verified. Of these1026components are rational and300use the irrational enclosure. There are32successful primitive cases and2output-overflow rejections. There are44nonfinite rejections: six individual input positions and one isolated poison in each of38seed columns. Some poisons occur in off-diagonal directions whose cofactor vanishes at the identity; the finite-seed contract still requires rejection. All finite accepted cases exercise every seed column, including basis, zero and mixed directions.

The78cases include:

- The five actual clay boundary failure IDs and the shear-near-positive-interior control, preserving their exact literal inputs and historical duplicate physical vectors.
- Regular positive, negative, indefinite, zero, mixed-shear and spherical tensors.
- Actual rounded rotated and oblique tensors, and an exactly representable signed reflection of a regular mixed tensor.
- Uniform small/large, anisotropic and mixed-sign/mixed-scale inputs.
- Six exact rational midpoint cases: half/three-half/five-half minimum-subnormal determinants, negative half-minimum-subnormal, and positive/negative normal-binade ties. Expected primal results include canonical0, even2minimum-subnormals, and the even upper-normal result.
- Exact rank-one/rank-two and huge rank-one tensors, primal overflow, derivative-only overflow, signed zeros and minimum-subnormal seeds.
- A directional-cancellation case with finite primal2^1000 and derivative column37exactly0 although its two signed contributing terms exceed binary64 range individually.

Rounded covariance witnesses are independent actual tensors: their determinant need not equal an intended ideal rotation's determinant exactly. The signed reflection is exact in the stored representation and its primal equality is checked. AD covariance requires reflecting the seed tensors too; using the same unrelated numerical seeds does not establish directional covariance. This packet does not silently enforce a false identity for rounded rotations.

The six basis columns also expose individual Mandel gradient components. Dense seed columns are deliberately simple dyadic values, with some repeated directions; they test38storage/propagation columns but are not an exhaustive set of all possible directions. All38individual poison positions are separately tested. No general matrix-conditioning certification follows from these finite witnesses.

## Independent implementation proof requirements

The proposed exact-algebraic primitive should establish the following before relying on these examples as generic correctness evidence:

1. Derive its scalar polynomial from the Mandel-to-Cartesian map, including the irrational cross coefficient. Do not replace sqrt(2) by a rounded binary64 constant before cancellation. Show its Jet contraction equals the Cartesian cofactor:direction derivative, with all off-diagonal multiplicities correct.
2. Decode every finite normal/subnormal/signed-zero binary64 input and seed exactly; validate all six inputs and all228seed values even where a mathematical coefficient happens to vanish. No fixed precision accumulator may silently truncate the full supported exponent span.
3. Prove signed comparisons for a+b*sqrt(2), including opposite signs and exact rational equality. Squaring must be conditioned on known signs, and integer shifts/products must retain the needed magnitude. Capacity or dynamic-allocation limits must cover finite binary64 products, exponent alignment and subsequent squared comparisons, not only a typical clay scale.
4. Prove bracketing and ties-even rounding across normal binades, subnormal transitions, signed underflow zero, the largest finite/overflow midpoint and negative values. Irrational components with nonzero rational radical coefficient cannot equal a rational midpoint, but can approach it closely; the generic algorithm still needs exact comparison, not a fixed-decimal empirical tolerance. The512digit bracket certifies this corpus only, not every possible binary64 input/seed combination.
5. Compute and validate all prospective primal/derivative results before assigning output. Any bad seed or final rounded overflow must leave every output component unchanged. Ensure canonical positive zero for both exact zeros and rounded negative tiny values.
6. Verify consistent native/Wasm behavior, type/dimension contracts and AD/trace identity in a separately frozen harness. No source-domain narrowing, clipping, SPD projection or clay-specific handwritten determinant is needed or justified by these references.

Correct primitive results do not by themselves establish accurate complete clay source rates, stable Lode/density factors, finite integration, preparation or scientific admission. A later candidate/source-rate study must retain historical failures and41original source budgets, and freeze any new boundary source-accuracy gate before observing repaired compiled outputs.

## Reproduction

The packet requires Python3standard library only; no PDF, author code, Atlas imports or external network is needed. From the repository root with PACKET set to its absolute installed directory:

```sh
python3 -B "$PACKET/reference.py" --root "$PWD" --packet "$PACKET" --output /private/tmp/fresh-symmetric-determinant-references.json
python3 -B "$PACKET/verify_rounding.py" --packet "$PACKET" --output /private/tmp/fresh-symmetric-determinant-rounding-checks.json
```

Outputs must be fresh. Regenerating the input freeze is optional as a separate fresh file, never overwriting the prospective receipt. The coordinator can adapt the final harness to its API without changing `cases.json` expectations; any additional cases/policy require a distinct identity. `manifest.json` pins packet bytes. There were no unresolved references or convergence failures; no compiled observations were made.
