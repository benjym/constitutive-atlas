# Clay2005 determinant input rounding diagnostic v1

Task REV-clay2005-determinant-input-rounding-v1; 2026-10-31. Source-only follow-up to the independently converged [boundary precision study](../boundary-precision-v1/README.md). This packet quantifies how rounding the normalized tensor changes a determinant factor before an accurate determinant primitive receives it. It does not evaluate the Atlas interpreter, primitive implementation, compiled artifacts, complete Y/source rates or a new material path. No reference, domain, support classification, original budget or gate changes.

## Prospective identity and exact inputs

`prospective-freeze.json` SHA256 `46f9d41004960f82311171c48e1e4720f2e188eadc244ac323548a9c0b9a5265` was created and communicated to the coordinator **before this diagnostic evaluation**. It pins the existing eleven actual binary64 stress inputs, the prior source study/results, original frozen protocol/model, the additive source correction and inspected tensor/trace implementation files. It records actual stress literal/hex/integer ratios,160/320digit precision and relative determinant convergence<=1e-120 for every route, plus the source/failure limitations. The scripts use standard-library Fraction/Decimal only, with no Atlas imports or source-oracle execution. Inputs are never replaced by an ideal rotation or spectrum.

The eleven cases are the five retained finite-only parity failures and six predeclared controls from the earlier source packet. The old tiny-positive/scaled-positive-1.0 duplicate physical tensors retain both identities. Source and dynamic files are pinned as contextual inspection receipts, not interpreted as source equations. A current-source change causes the diagnostic script to reject until a separate identity is prepared; do not edit the receipt to bypass this check.

## Source homogeneity and interpretation

[Mašín2005, A hypoplastic constitutive model for clays](https://doi.org/10.1002/nag.416), [accepted author manuscript](https://web.natur.cuni.cz/uhigug/masin/download/MasinIJNAMG05-pp.pdf),718767bytes/26pages, SHA256 `8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3`. AppendixC76 defines normalized stress;78–79 use the homogeneous invariant ratio; pp24–25 contain the selected base equations73–85. The existing source receipt and correction were reread; this pass relies on the previous original-PDF visual review and makes no new PDF inspection claim. The p10Eq38 PLUS correction and coefficient meaning remain unchanged. Final-publisher equation equivalence is still unverified. No private PDF/text/render or author code is bundled.

With source T=-sigma, normalized H=T/tr(T)=sigma/tr(sigma) exactly. Define the mathematical factor

`d(sigma)=det(sigma)/(tr(sigma))^3`.

For a nonzero scalar c, determinant and trace-cube both acquire c³, so the ratio is unchanged. Source78's numerator I1*I2+9*I3 and denominator I3 also have degree3, hence their ratio has degree0. This is a source-preserving homogeneous identity, not a new constitutive assumption or an instruction to fit a determinant floor. Numerical normalization is a separate question: independently rounding six entries of sigma/tr(sigma) generally produces a different tensor rather than one exact scalar multiple of sigma.

The existing candidate denominator uses `determinant(H)`. An exact/correctly rounded determinant of the supplied binary64 H is therefore the determinant of that changed tensor. It cannot recover the original tensor geometry lost during six component roundings. All determinant factors here are well within the normal binary64 range, so final nearest-even rounding of their exact determinants has relative error at most about1.11e-16; that cannot account for the1e-7input drift below. This packet evaluates high-precision determinants of the actual supplied normalized tensors and does not execute or revalidate the production primitive.

## Normalization routes and results

Source inspection found that both current C++ `Sym` division and Python `Sym.__truediv__` compute **a rounded reciprocal followed by component multiplications**. They do not perform six scalar divisions. The trace primitive supplies a nearest-even exact sum of the three input diagonals. This packet independently emulates those specified roundings using exact Fraction operations followed by binary64 conversion, without invoking Atlas math.

The frozen routes are:

1. Exact stored sigma and exact trace, the target det(sigma)/(tr(sigma))³.
2. Rounded trace, but otherwise exact component divisions; this isolates trace rounding alone.
3. Each exact sigma/exact-trace component rounded once.
4. Each sigma/rounded-trace component rounded by direct scalar division.
5. The actual reciprocal/multiply route: r=RNE(1/RNE(trace)), H_i=RNE(sigma_i*r).
6. Exact power-of-two scaled K, with exact det(K)/(tr(K))³.
7. A descriptive power-of-two scalar-rounding route RNE(det(K))/(RNE(tr(K)))³, evaluated without intermediate cube underflow/overflow.

All77route comparisons across the eleven cases pass the frozen160/320digit convergence check. The table gives absolute relative factor error against the exact-original-input target, based on320digit estimates:

| Case | Once-rounded exact-trace H | Direct divisions by rounded trace | Actual reciprocal/multiply H | Power-of-two K, separately rounded scalar determinant/trace |
|---|---:|---:|---:|---:|
| tiny-positive-interior |2.56e-17|2.56e-17|2.56e-17|1.24e-17|
| margin-above |8.59e-18|8.59e-18|8.59e-18|1.29e-17|
| scaled-positive-1.0 |2.56e-17|2.56e-17|2.56e-17|1.24e-17|
| scaled-positive-1e+50 |1.29e-17|1.29e-17|3.38e-16|1.18e-16|
| oblique-tiny-positive |1.90e-7|1.16e-7|1.16e-7|6.30e-17|
| shear-near-positive-interior, control |5.55e-7|5.55e-7|5.55e-7|3.93e-17|

The other regular/control actual-H errors are at most5.11e-16. Trace-only errors are at most3.02e-16. When rounded trace equals exact trace, the true trace-only error is mathematically zero; extremely tiny nonzero residuals in the Decimal report (around1e-310–1e-320) are finite-precision reconstruction noise, not physical trace drift. Directly rounding exact-trace components still changes the two sensitive oblique geometries, so improving scalar trace accuracy alone is insufficient. The diagonal boundary inputs do not demonstrate that a general component-normalized tensor is safe.

`results.json` retains all normalized component ratios/hex values, exact and rounded trace/reciprocal,160/320determinants, signed/unsigned factor error and `target/route-1`. The last metric is the isolated relative error of a reciprocal denominator factor if all other factors were held fixed. It is not an error estimate for the coupled Y expression or the final stress-rate vector: numerator, flow, Lode, density, stiffness and their arithmetic may change too. No observed full-rate compiled outcome is consulted or predicted as a passed gate.

## Power-of-two diagnostic and generic remedy requirements

For each actual input the script chooses k from the maximum stored component's binary exponent, sets K=sigma/2^k, and asserts every K component remains exactly representable binary64 by comparing Fraction ratios. That assertion passes for all eleven inputs. Exact det(K)/(tr(K))³ equals the original source factor to the declared precision. Separately rounding only scalar det(K) and trace(K) yields factor errors<=2.65e-16 here. This is evidence that preserving the actual tensor through exact dyadic scaling avoids the demonstrated component-normalization loss. The descriptive Decimal-to-binary64 det(K) conversions are stable between160/320digits; this packet does not substitute them for the separately certified generic primitive corpus or a universal rounding proof.

A scientifically defensible next implementation can use a generic normalized determinant/homogeneous invariant ratio evaluated from the **original stored tensor**, with exact dyadic power-of-two scaling and a justified final ratio rounding strategy. Alternatively retain an unrounded/exact expansion of the normalization through the determinant. The operator should express precise input and output semantics and dimensions, rather than silently changing the ordinary determinant to infer an earlier unnormalized tensor. Rounded scalar determinant/trace results must not underflow or overflow before a representable final ratio is formed.

For arbitrary finite tensors, scaling a huge component into range can underflow a tiny nonzero component. Therefore a simple floating `ldexp` path is not universally exact. Require a representability check and a fallback that keeps exact dyadic exponents/coefficients or otherwise proves adequate precision. Do not discard tiny components, project onto SPD or restrict the clay support domain to hide the problem. The eleven exact-scaling successes are bounded examples, not an all-domain theorem.

The normalized ratio's real derivative follows the quotient rule: gradient(det)/trace³ minus3*det*gradient(trace)/trace⁴, with trace-gradient[1,1,1,0,0,0] in Mandel coordinates. Its implementation must avoid overflow/underflow/cancellation in these coupled expressions, validate all38seed columns, preserve failure atomicity and make native/Wasm trace decisions reproducible. This is a generic scalar/tensor operator requirement, not a clay-specific handwritten rate kernel. Any production DSL/compiler extension or source-preserving candidate must be separately reviewed and frozen.

Other coupled homogeneous source factors may need the same treatment. Accurate `det(H)` by itself does not establish accurate Y or source rates, and replacing only detH with a generic ratio still needs a complete prospective source-rate test. Retain all109original calls,41original source vectors/budgets and unchanged parity gates; any new boundary source-accuracy references and policy must remain prospectively frozen under a distinct study identity. No fitted tolerance, stress floor or source-domain change is proposed. Preparation, finite integration, experimental comparison and scientific admission remain open.

## Reproduction and limitations

From the repository root, set PACKET to the absolute installed packet directory:

```sh
python3 -B "$PACKET/study.py" --root "$PWD" --packet "$PACKET" --output /private/tmp/fresh-clay2005-normalization-diagnostic.json
```

The output must be fresh. `freeze.py` can reproduce the selection into a separate fresh file but must never overwrite the pre-evaluation receipt. Manifest and `checks.json` identify packet bytes, frozen source identities and77convergence checks. No evaluation/convergence failure occurred; no failed compiled source-rate result is removed or reclassified by this evidence.

Precision convergence is numerical evidence, not interval certification of all arithmetic or a full source proof. Source algebra is inherited from the pinned accepted manuscript and existing independent source review; final-publisher equivalence is unverified. Correctly rounded generic determinants, complete-model source accuracy, coupled temporal integration and scientific admission remain different claims.
