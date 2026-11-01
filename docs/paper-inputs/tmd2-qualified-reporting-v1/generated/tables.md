# TMD2 qualified reporting: paper tables

Descriptive calibration-campaign errors; no held-out validation, model ranking or experimental-validation claim. Strain errors below are percentage points (fraction ×100), and stress errors are kPa (Pa ÷1000).

| Caller intervals | Saved points | q RMSE (kPa) | q MAE (kPa) | q max abs. (kPa) | trace-volume RMSE (pp) | trace-volume MAE (pp) | trace-volume max abs. (pp) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 400 | 401 | 23.5369 | 16.5073 | 54.156 | 0.207738 | 0.174208 | 0.452851 |
| 800 | 801 | 23.5406 | 16.5093 | 54.1679 | 0.207739 | 0.174213 | 0.452841 |
| 1600 | 1601 | 23.5417 | 16.5099 | 54.1712 | 0.20774 | 0.17422 | 0.452803 |

## Saved path-pair refinement

These are saved path-pair differences against frozen assessor limits, not physical integration-error bounds or an observed convergence order.

| Path pair | Channel | Maximum difference | Frozen limit | Unit | Difference / limit |
| --- | --- | --- | --- | --- | --- |
| tmd2-400 → tmd2-800 | q | 0.0169391 | 0.632714 | kPa | 0.0267721 |
| tmd2-400 → tmd2-800 | volumetric_strain | 6.87084e-05 | 0.017716 | percentage points | 0.00387833 |
| tmd2-800 → tmd2-1600 | q | 0.00561394 | 0.632714 | kPa | 0.0088728 |
| tmd2-800 → tmd2-1600 | volumetric_strain | 5.74396e-05 | 0.017716 | percentage points | 0.00324225 |

## Retained historical failures

The earlier ordinary laboratory API rejected all three 25% requests with zero points. Those rejections are distinct from the qualified research-range paths tabulated above. A separate saved-receipt exit23 witness passed the historical assessor; the corrected process-status guard rejects it. Neither is discarded or turned into a numerical-accuracy pass.

## Mandatory scientific qualifications

- Exact historical decks/version/strain/output conversion unverified
- No internal-stage physical-history-ball/domain proof
- Project continuations and finite-step integration remain distinct from printed law
- No general IGS/host scientific admission, cyclic validation, M1/M4 or REV-04/05 completion
- No held-out validation, uncertainty or ranking
- Original measurement redistribution permission unresolved
- Reduced portable receipt shares frozen inputs and prior raw numerical archive; private dependency durability not inferred

Source/review identities and full-precision values are in reporting.json. All table values are rounded for presentation; raw measurements are excluded.
