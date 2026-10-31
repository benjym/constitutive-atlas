# Tresca pressure/deviator correction — source and references

A separately identified private draft now expresses the same BK2022v1/project-BE law using pressure/deviator arithmetic and an equivalent plastic-strain residual row. It passes normal v0.3 validation and C++ source generation. **No candidate material evaluation, compiled build, installation or numerical qualification is claimed.** The original failed native/Wasm study and strict-initial-membership discrepancy remain unchanged.

[model.json](model.json) preserves every original parameter, state component, default/example, physical formulation, source hyperlink, domain, initialization requirement and exact initial-check expression. Only its distinct algorithm identity/description, derived expressions and residual representation change. Full persistent sigma6/ep6 remains. This is an algorithm variant, not another constitutive family. The source remains [BK2022v1](https://arxiv.org/abs/2207.12719v1); finite BE integration and the conditioning are separately project-derived.

## Why this addresses the diagnosed arithmetic

The [failed study](../../../catalogue/investigations/tresca-rounded-backends-v1/README.md) adds a small elastic deviatoric change to a 2^60 Pa hydrostatic parent, losing it before return classification and plastic-history update. The new proposal first computes `D=dev(sigma_n)+2mu*dev(de)` and its pressure-invariant projection, computes plastic change from the deviatoric correction, then recombines mean stress for the returned stress. No physical state, source parameter range or required history is reduced.

[DERIVATION.md](DERIVATION.md) proves `R(T)=mI+R(D)` and the block residual transformation `rp_new=rp_old−C_inverse(rσ_old)`. For fixed material parameters, all 38 current/parent/loading derivative columns transform by the same invertible row operation. The exact roots, full stress/plastic-strain solution and temporal law are unchanged; finite floating solver behavior still requires requalification.

## Independent evidence

The unchanged six-plane high-precision reference implementation supplies the old residuals and full updates. Two independently expressed routes check the new residuals: the compliance row operation and current state/seed minus the independently computed full update/direction. Original stress residual rows, returned states, returned-state derivatives, all 61 cases and all 12 history rows/committed bits are preserved from the frozen original references. The known source-invalid rounded parent remains marked invalid.

- 28,692 row-transformation component checks per precision pass the unchanged 1e-55 gate; maximum error 3.08e-177 at 200 digits and 1.77e-257 at 280 digits.
- 57,384 saved transformed residual components independently match current-minus-update data; maximum normalized error 6.52e-73.
- 1,464 full update components from independent split-tensor projection match original updates across both precisions, maximum normalized error 3.56e-73.
- Cross-precision agreement covers 58,713 numeric fields, maximum normalized difference 3.34e-166. All original update/history values and stress rows remain unchanged.
- 33 focused source/evidence/activation/archive tests pass, including exact Fraction block-row identities, deterministic compressed-byte replay and jointly corrupted value/seed residual rejection.

## Retained reference-precision failure

The first `transform.py` attempts applied compliance to already 73 digit-formatted old residual strings. At the 2^-80 stiffness scale, cancellation amplified their truncation to 8.65e-51, failing the frozen 1e-55 gate at both precisions. Those scripts, hashes, raw process receipts and failures are retained.

`full-precision-amendment-freeze.json` records the separate `transform_full_precision.py` correction before its checks: recompute the same independent old residuals at their original 200/280 digit working precision, apply the same row operation before formatting, and preserve the original update/history data. No candidate observation, error-budget relaxation, input deletion or output replacement was used. The failed serialized-output conversion is not retrospectively reported as a pass.

## Reproduce and next gate

```sh
python3 -B docs/reviews/tresca-pressure-split-v1/verify.py
python3 -B -m unittest tests.test_tresca_pressure_split
python3 -B docs/reviews/tresca-pressure-split-v1/transform_full_precision.py --precision 200 --output /private/tmp/tresca-split-reference-replay.json.gz
```

Use a fresh output path. `propose.py` and transformation scripts refuse overwriting evidence. `source-pins.json`, both prospective freezes, source-validation hashes and `manifest.json` bind this delivery. All work stays outside executable model directories; no raw source PDF is distributed.

The pressure/deviator correction and independent equivalent references are ready for a separately frozen compiled study. Strict initial-yield membership remains a separate requirement; [the follow-up note](NEXT_INITIAL_MEMBERSHIP.md) identifies a generic exact-predicate route requiring proof and tests. No tolerance, clipping or source-domain restriction is introduced here. Do not promote/install the draft on the strength of algebraic/source checks alone.
