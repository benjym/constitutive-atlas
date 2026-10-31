# Barodesy sand 2015: exact-volume rate study v2

Research-only source-rate packet, dated 2026-10-31. This distinct revision preserves the complete v1 packet and independent audit. It does not change model admission, the shared compiler, or a native material kernel. No compiled execution was performed for this packet.

## Identity and source mapping

The physical formulation remains Kolymbas, *Introduction to barodesy* (2015), [DOI 10.1680/geot.14.P.151](https://doi.org/10.1680/geot.14.P.151), publisher PDF SHA-256 `4d4511bdbb6014c19460bf0c5d7e2072c2c606fa8a5b49db180fc99d0da149da`. Printed p54 Eq9 supplies the matrix exponential direction; p55 Eq20 the void rate; p55 Eq23 the stiffness scalar; p56 Eqs26–27 the critical density; p56 Eq31 the stress rate. The parent source packet retains the source trace typo and other source qualifications. Private PDFs are excluded.

The seven parameters, state, derived equations, domain, source entries and integration declaration are byte-equivalent JSON values to v1. Only the draft ID/name/description differ. Compression-positive Atlas stress and stretching are converted to the source tension-positive Cartesian tensors; the returned stress rate is converted back. Atlas Mandel order is `[xx, yy, zz, sqrt(2)*xy, sqrt(2)*yz, sqrt(2)*xz]`. State is stress6 followed by void ratio. Zero spin is supplied; there is no additional history or reset. Zero loading has the declared continuous zero-rate extension, without a material-AD claim.

The illustrative defaults come from the separately pinned 2019 [DOI 10.1002/nag.2984](https://doi.org/10.1002/nag.2984) fixture, Table1 (author-upload PDF6, printed p5), SHA-256 `71d1f54b8f67259970aff33a26b807597ca2cf648b0ae49182db2e7bb4cea4eb`; c4 is converted from 465 kPa to 465000 Pa. These values are not established as the exact 2015 calibration or experimental validation.

## Distinct ideal and operational contracts

`reference.ideal_source_rate` independently evaluates the source in Cartesian matrices using Decimal arithmetic and a forward exponential series. It accepts mathematically positive-definite nonzero stress and source density conditions within the explicit parameter envelope. It does not call the operational validator. Its finite-precision stress results and determinant classification are numerical diagnostics, not a certified ideal arithmetic oracle for arbitrary near-singular states. The 80/120-digit agreement is empirical; no rigorous full-rate error bound is claimed.

`support.validate` separately defines the bounded Python binary64 operational domain used for paired DSL comparisons. It enforces the retained parameter bounds, e−emin >=1e−8, e<=3, scaled stress norm in [1e−10,1e10], normalized leading stress minors >64 ulp(1), nonzero loading norm >=1e−140 and norm<=1000, positive rounded B and ec−emin, and exponential argument norm<=64. These are project support choices, not new physical constitutive restrictions. They keep intermediate arithmetic away from obvious overflow, norm underflow, singular denominators and roundoff-scale minors. The 64-ulp margin is not a proof of compiler-independent positive-definiteness classification. The rounded critical-density check deliberately rejects representational collapse rather than clipping it.

The dimensionless exponential argument has the source bound |c1| exp(c2 sqrt(3)) <=2 exp(1.5 sqrt(3)) <26.88 within the selected parameter envelope, below the generic norm64 support. This justifies exponential support for this envelope, not every source parameter choice. Operational boundary classifications remain floating-point computations and are not proved equivalent across Python, native and Wasm implementations.

## Exact actual-input volume and retained findings

`reference.exact_volume` sums the actual binary64 loading diagonals using Fraction and multiplies exactly by the actual binary64 value of 1+e interpreted as the rational expression `1 + Fraction(e)`. No rounded intermediate trace, product or fixed Decimal precision determines the void rate. Converting the final Fraction to float supplies the nearest binary64 result; exact rational numerator/denominator and terminating Decimal values are retained. Tests cover cancellation, subnormal values and a halfway rounding case.

Both original audit findings are retained in `counterexamples.json` with their historical bytes pinned. For loading `[500,1e-130,-500,0,0,0]` and e=.75, the exact-volume result rounds to `-1.7500000000000002e-130`. The original finite-precision false zero is corrected in the v2 reference and this request is an additional operational-valid case. The rounded critical-density witness remains ideal-source evaluable with positive critical-density gap, but is explicitly outside operational binary64 support. It is an additional numeric domain rejection, not a changed source law.

All 37 original valid input documents and 19 original invalid documents remain identical. All 37 original 120-digit-oracle binary64 seven-rate vectors remain identical. Numerical-only operational rejections can be ideal-source accepted; `reference.json` records both decisions instead of mislabelling them physical source violations.

## Checks and frozen next study

The retained `python-report.json` records 38 valid comparisons and 20 operational rejections, maximum scaled stress discrepancy `7.603988223053184e-16`. Eleven test groups pass. The checks include fresh exact reference replay, ancestor hashes, unchanged v1 inputs/equations/results, independent Cartesian actions, source scalar-diagonal exponential action, retained orientation cases, strict types, nonmutation and corruption probes. `provenance.json` pins every ancestor packet file and observed runtime bytes; ancestor pins are actively checked. Observed runtime hashes are receipts, not a claim of validated future compiler behavior.

From this directory, with a repository checkout available:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 reference.py --check reference.json
PYTHONPATH=/path/to/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 check.py --output /private/tmp/barodesy-v2-fresh-report.json
ATLAS_REVIEW_REPO=/path/to/constitutive-atlas PYTHONPATH=/path/to/constitutive-atlas PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_rate_study.py
```

Use a fresh output path. Python version is recorded. Current Python summation behavior does not establish equivalent compiled trace behavior.

`protocol.json` freezes stress accuracy at scaled error <=2e−12 and void accuracy at four ulp of the exact-rational rounded result, with exact zero when the reference is zero. The smallest proposed persistent compiled corpus is 71 raw rows per backend: descriptor +38 valid +16 numeric invalid/recovery pairs. The four remaining invalids are Python structural/type cases and are explicitly mapped. The compiled collection must bind source/model/protocol/reference, artifact and transport bytes, retain raw responses before parsing, and check recovery in the same process/instance. The cancellation case may fail naive compiled trace summation; retain such failure without relaxing its gate or introducing a model-ID bypass. No compiled outcome is predicted here.

Finite-step integration, material AD, arbitrary parameter/domain support, zero-stress continuation, finite-spin objectivity and experimental/scientific validation remain separate gates. A rate evaluation is a trial function of supplied state/loading; it neither commits nor mutates state. A future integrator must keep rejected trials transactional and supply objective kinematics explicitly. This packet supplies no finite-update or temporal error claim.
