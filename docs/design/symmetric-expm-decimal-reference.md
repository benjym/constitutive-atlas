# Independent symmetric exponential Decimal reference

This packet supplies mathematical operator evidence, not a production kernel or model admission. The barodesy requirement is its original body Eq3 and footnote5, printed366, [Medicus & Fellin2017](https://doi.org/10.1007/s11440-016-0458-4): tensor/matrix exponential, not componentwise scalar exp. No source PDF, text or renders are bundled.

## Inputs, outputs and independence

`tools/reference_symmetric_expm.py` imports only Python stdlib. It imports no Atlas DSL, compiler, tensor, production solver, model, NumPy/SciPy, author program or native/Wasm module. Public `oracle(values, precision)` accepts six actual finite binary64 floats in orthonormal Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. Integers/Boolean/wrong shape/nonfinite values are rejected by this corpus interface, independently of any future production language coercion policy.

Every input is converted with Decimal.from_float; shear entries are divided by Decimal(2).sqrt() at each working precision. Thus the target is the mathematical Cartesian tensor corresponding to the supplied binary64 Mandel components and exact sqrt2 conversion. Floating-point rotation construction does not imply exact original eigenvalues. Exact Mandel Frobenius<=64 is the corpus support policy, not the exponential's mathematical domain. Production computed-boundary roundoff is a separate implementation decision.

The output is six value components and a6×6Jacobian: rows are output Mandel components, columns are the six unit input Mandel directions. This is the full Fréchet derivative restricted to symmetric tensors; no tangent seeds are omitted. The corpus retains160-digit Decimal strings plus rounded binary64 oracle values/Jacobian for production comparisons. Invalid-case tokens keep NaN/Infinity out of JSON numeric fields. Large derivative-seed overflow, production finite-intermediate failure handling and rollback belong to the parent implementation tests, not this reference corpus.

## Independent recurrence

Scale Cartesian A by powers of two until ||B||infinity<=1/8, independently of the proposed production Horner18threshold/order. For each direction, scale H by the same factor. Starting T0=I and U0=0, compute forward terms

`Tk=Tk−1 B/k`, `Uk=(Uk−1 B+Tk−1 H)/k`.

Accumulate the value and all six directional sums. Stop when all current value/directional terms remain below10^(−(precision−25)) for three successive terms. A4096-term cap rejects nonconvergence; it is not a fixed polynomial order. Undo each scaling with Xnew=X² and Lnew=XL+LX. Output shear mapping uses the symmetric average of the two Cartesian entries at the final mapping. This is an independent forward recurrence with adaptive term termination, not the production Horner polynomial or a borrowed production AD evaluation.

The study uses100and160digits. Every value and Jacobian component records the absolute precision-pair difference; norm-scaled maxima use max(1,maxabs(reference channel)). These are empirical precision-refinement diagnostics, not rigorous error bounds or guarantees for binary64 implementations. For the44retained cases, maximum normalized value difference is4.179e−82 and Jacobian difference6.783e−82. At most63terms and9scalings were needed. No assumption about a resolved convergence order is made from two precisions.

## Corpus and checks

44valid cases include zero; positive/negative isotropic tensors; mixed distinct, double and nearly double spectra through a single binary64 ulp; pure off-diagonal shear; oblique rotations and reflections of actual rounded tensors; safe large mixed signs; and nextafter below/at/above powers-of-two scaling thresholds0.5through64subject to support. The first point above64is a separate invalid case, with nonfinite/wrong-shape/Boolean categories.

Seven Python groups check:

1. Complete44case retained reproduction, input hashes, full six-by-six shape and componentwise100/160precision agreement.
2. expm(cI)=exp(c)I and L(cI,H)=exp(c)H for all six independent H, including c=0.
3. Independently evaluated analytic divided differences for actual binary64 diagonal entries, including equal and nearly equal eigenvalues; this checks the differentiated recurrence without a common matrix-series derivative implementation.
4. Pure shear Cartesian closed form from scalar cosh/sinh identities.
5. Fréchet self-adjointness in the Mandel inner product for every corpus case.
6. Secondary rounded rotation covariance of values and full Jacobian, with an allowance for actual rounded input/construction differences; no false exact-spectrum claim.
7. Explicit support/type/shape/nonfinite/precision rejection.

All7groups passed via Python only. Exact source/physical-model verification, production derivatives under arbitrary seed magnitude, native/Wasm ABI behavior and scientific/public admission are not claimed.

## Reproduction and parent integration

From the staged packet root or after installing only whitelist files:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m tools.reference_symmetric_expm --output /private/tmp/expm-reference-check.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_reference_symmetric_expm.py' -v
```

The first command must reproduce the retained JSON byte for byte when script bytes and Python Decimal semantics match; metadata pins the exact script bytes. The test compares regenerated parsed corpus and analytic invariants. Parent production tests should consume the rounded oracle values/Jacobian, check all36entries with absolute-plus-relative tolerances, and separately compare native/Python/Wasm status and failure semantics. Hash/input/oracle provenance should stay attached to retained production results. Do not call backend parity an independent mathematical oracle.
