# Stored-Mandel independent spectral references v1

2026-10-31; REF-symmetric-spectral-stored-mandel-v1. This is a precompiled-observation reference freeze, not an Atlas primitive, constitutive kernel, floating acceptance policy or scientific admission. No Atlas modules, supplied author code, candidate Jacobi algorithm or compiled artifact was imported/executed. Work was staged privately; shared code is unchanged.

## Exact input identity and output layout

`inputs.json` is authoritative:48 tensors, each six literal binary64 hex Mandel values `(xx,yy,zz,sqrt(2)xy,sqrt(2)yz,sqrt(2)xz)`, and38 six-component seed directions. The first6 directions are coordinate basis;32 are nontrivial mixed binary64 directions. Each binary64 is converted by `Decimal.from_float(float.fromhex(literal))`, preserving its exact stored value. Cartesian shear is that exact value divided by mathematical sqrt(2), approximated at the declared Decimal precision. The same conversion applies to seeds. Intended pre-encoding rotations are never used as the reference tensor. Rational rotation matrices only constructed some frozen binary64 inputs; the actual encoded rotated repeated pair generally splits and receives derivatives for its actual simple spectrum.

`reference-p360.json.gz` is the canonical reference; `reference-p280.json.gz` is the independent precision-repeat record. Both contain decimal strings printed with73 significant digits, even for outputs outside binary64 range. Top-level `seeds_mandel_hex` is38x6. `cases[*].input` contains `id` and `mandel_hex`. Its `reference` contains:

- `eigenvalues`:3 descending values; `method` identifies exact diagonal versus characteristic cubic.
- `selected.max/mid/min`: `status`, and for an isolated selected eigenvalue, `normalized_gap`, Cartesian3x3 `projector`, and38 `directions`, each with scalar `eigenvalue` derivative and Cartesian3x3 `projector` derivative.
- `pair_sums.upper/lower`: value and status;38 scalar derivatives when the complementary extreme is isolated.
- `maximum_internal_normalized_residual`: construction diagnostic.

A repeated selected eigenvalue is explicitly `repeated-selected-no-classical-derivative`. Repeated-complement pair sums use the corresponding explicit no-classical-derivative status. Value references remain present at all repeated/hydrostatic inputs. A repeated complementary pair remains supported for the isolated individual projector and pair sum. No physically valid input is discarded to simplify differentiation.

Projector matrices and their directional derivatives are Cartesian, not Mandel. A collector maps shear components by multiplying Cartesian off-diagonals by mathematical sqrt(2). Frobenius error norms must count both symmetric off-diagonal entries. `normalized_gap` is a reference mathematical diagnostic, not an adopted solver gap threshold.

## Independent method

For non-diagonal A, scale by its largest absolute Cartesian entry. Center B by m=trace(B)/3, giving C=B-mI. Set q=trace(C²)/6 and r=det(C)/2. Its eigenvalues x solve the project-derived characteristic cubic `x³-3qx-2r=0`. Stationary points are±sqrt(q); the three real roots of a symmetric tensor lie in `[-2sqrt(q),-sqrt(q)]`, `[-sqrt(q),sqrt(q)]`, `[sqrt(q),2sqrt(q)]`. Sign-checked bisection uses each interval, then restores center/scale. The iteration budget is4*precision and normalized interval stopping width is10^-(precision-18). Unresolved stationary/end-point signs or budget exhaustion are reported in top-level `unresolved`; there are none in final runs. This is not a rigorous directed-rounding interval implementation.

For simple selected lambda_i, the polynomial projector is the product `(A-lambda_j I)(A-lambda_k I)/((lambda_i-lambda_j)(lambda_i-lambda_k))`. Exact diagonal coordinate projectors avoid artificial polynomial roundoff in mixed-scale diagonal cases. Derivatives use `Dlambda=tr(PH)` and spectral divided-gap formulas, combining an exactly repeated complementary pair through `I-P`; they do not differentiate bisection or a numerical eigenvector algorithm. Pair-sum derivatives use `tr((I-Pisolated)H)`.

Checks use eigenrelation, projector idempotence/trace, differentiated idempotence/trace, and differentiated eigenrelation for all directions. The scalar cubic and spectral formulas are elementary project derivations. [NIST DLMF1.11(iii)](https://dlmf.nist.gov/1.11#iii) provides polynomial-root background; [Python Decimal documentation](https://docs.python.org/3/library/decimal.html) documents arithmetic/context and exact float conversion. Neither is borrowed executable solver code. Mathematical projector derivations and exact Cartesian checks are independently retained in the preceding symmetric-spectral analytical audit.

## Frozen adequacy check and results

`check.py` records the unchanged internal criterion1e-60 for norm-scaled dual-precision differences and construction residuals. This checks reference adequacy; it does not set the candidate's acceptance/gap policy. Eigenvalue/pair differences scale with the tensor spectral magnitude, including tiny tensors; derivatives of values scale with seed magnitude; projector errors use scale1; projector derivative differences scale with max(1,reference derivative magnitude). Exact zero tensors have scale1.

Final280/360-digit runs cover48 tensors and38 columns, compare54,543 numerical fields, and have zero unresolved tensors or failed checks. Maximum normalized difference is4.24033e-110; maximum construction residuals are8.43544e-110 at280 digits and8.79666e-190 at360 digits. `check-results.json` retains full values and source hashes. Agreement is strong internal convergence evidence, not a rigorous root/separation certificate.

Corpus coverage includes zero/hydrostatic/negative/distinct diagonal tensors; both exact repeated complementary pairs; generic dense tensors; binary64-encoded dense rational rotations; both signs and scaling by2^±400; diagonal and dense subnormal inputs; maximum finite diagonal entries; mixed diagonal `(1e300,1,-1e300)`; upper/lower gaps2^-8,2^-24,2^-40,2^-48, plus rounded rotated gaps; finite inputs with true eigenvalue or pair-sum overflow. Mathematical derivatives may exceed binary64 range, especially at subnormal gaps. Their Decimal references are retained; the parent owns prospective checked failure/range policy.

## Reproduction and retained failures

From this directory:

```
python3 generate.py 280 > reference-p280.json
python3 generate.py 360 > reference-p360.json
python3 check.py > reproduced-check.json
```

`check.py` also reads the shipped gzip records directly when uncompressed names are absent. gzip members have deterministic mtime0. Input bytes and generator/check/reference hashes are pinned in manifest/check results. Reproducing literal reference bytes additionally depends on the standard-library Decimal implementation; the numerical checks are the intended cross-runtime reproducibility assessment.

Two failed attempts remain under `retained-failures/` with their original generators/reports/reference bytes (JSON compressed losslessly). Initial general polynomial handling of a huge diagonal amplified tiny projector normalization errors into spurious derivatives. Exact diagonal projectors fixed that defect. Subsequent140/200-digit arithmetic was insufficient to control absolute near-zero derivative cancellation in2^-400-scaled encoded nearly repeated tensors. The criterion was retained; precision increased to280/360. No candidate results had been observed. Neither failure was relabeled as a physical domain restriction. Full original uncompressed staging also remains outside this portable packet.

## Limits and next step

These are finite-input mathematical references only. They do not exercise malformed input, all-column NaN/Inf rejection, transactional/sticky failure, lazy branch execution, solver rollback, MC return classification or native/Wasm agreement. Boundary/source tangent choices remain as previously audited. The parent must freeze numerical accuracy, convergence/gap classification, range diagnostics and runtime failure policies before observing any compiled candidate. Actual stored Mandel matrices are used throughout; no claim of exact intended rational spectra survives encoding. Source histories and failed studies are preserved.
