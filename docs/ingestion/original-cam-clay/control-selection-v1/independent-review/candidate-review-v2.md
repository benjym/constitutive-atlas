# Corrected candidate source/finite-law audit v2

Reviewer `/root/occ_selection_review`, 1 November 2026. Separate follow-up to `candidate-review-v1.md`; the rejected candidate, old checker/results and all manifests remain untouched. No compiled call, build, shared edit or E5 approval occurred.

**Accept candidate SHA-256 `36012205c441860b28c722d3177330f37d102a2028d5c3b3afce7786fd36b13a` for source/finite-law transcription and the bounded portable checks below.** Both identified implementation blockers are resolved. This is permission to proceed with the separately required numerical/backend/controller/browser gates, not a claim that those gates passed.

## Source-preserving correction

Read `candidate-v03-v2.json` and `candidate-v2-numerics.md`. The correction extracts raw diagonal differences `(a-b,b-c,c-a)` and stored Mandel shears before normalization. It reconstructs normalized deviator diagonals as `(ab-ca,bc-ab,ca-bc)/3`. Algebraically this is exactly the stored tensor's deviator divided by the normalization factor. For adjacent diagonal values, raw pairwise subtraction retains the differences that the previous rounded mean subtraction destroyed. The same construction is consistently applied to old-state projection and current-state yield evaluation.

The candidate still implements the accepted contract's endpoint pressure/volume equations, corner, zero-distortion projection and discontinuous strain-interface selection. No positive amplitude threshold, shear compliance, source branch deletion, smoothing or new operator appears. The zero-distortion flag tests exact maximum of the differences/shears; the full hold flag separately tests all input components. A rounded-to-zero scalar `rmag` does not force the hold branch while direction remains nonzero. Scalar normalization divisions avoid the previous tensor reciprocal-overflow issue for subnormal denominators.

The correction therefore changes numerical evaluation of the same law. It does not relax the source law or prospective gate. Extreme-range nonrepresentable arithmetic remains an explicit potential atomic rejection, as already disclosed. No uniform all-binary64 tangent accuracy is inferred.

## Reproduction and results

```sh
python3 -B docs/ingestion/original-cam-clay/control-selection-v1/independent-review/candidate-review-v2-check.py
```

The v2 checker is a new byte-preserving copy of the original exact-wire checker with only its candidate filename and result identity changed. It retains exact `Fraction.from_float` input/state decomposition and the independent Decimal bisection of the uneliminated finite equations. All407 cases pass the unchanged `2e-10` pressure-normalized physical gate. Maximum error is `1.6960958793760993e-14`.

| Previously critical control | Corrected error |
| --- | ---: |
| Retained naive-rotation actual stored controls | `6.106226635438361e-19` |
| Adjacent diagonals near negative hydrostatic input | `2.2452792274340584e-16` |
| Pure Mandel shear `1e-200` | `2.1426886964167784e-16` |
| Minimum binary64 subnormal pure Mandel shear | `2.1426886964167784e-16` |

The400 base corpus cases, both adjacent-diagonal tests, all4 tiny-shear cases and the retained rotated actual-wire control remain present. The exact zero cases are compared to the full original state. Output is retained in `candidate-review-results-36012205c441.json`, bound to the exact candidate and checker dependencies. The prior candidate's two failures remain in `candidate-review-results-7e528930d05e.json`; no failure was overwritten or reclassified as a pass for that old identity.

This resolves the v1 source/finite-law implementation findings. The original naive matrix rotation still fails its intended hydrostatic input identity because it supplies different stored controls; its retained failure and input-producer correction remain valid evidence. The new candidate now correctly handles those stored controls as a legitimate small nonzero distortion, rather than producing a nontraceless stress.

The earlier review's covariance decision stands: exact signed permutations, analytically preserved hydrostatic tensors and rational nondegenerate rotations with exact-wire input binding provide meaningful complementary tests at the unchanged gate. This v2 follow-up runs the407 finite-law controls, not a new independent full rotation campaign. Actual parent rotation checks, source-path convergence and native/Wasm/transaction/browser evidence must retain their own exact identities before E5 review.
