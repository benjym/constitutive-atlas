# Complete whole-test calibration objective

`atlas.study_objective` and `tools/score_study_objective.py` implement a complete
saved-candidate scorer for CAL-02/05. This is reusable software, not a scientific
study freeze, optimizer, new fit or replacement for historical scores.

The [objective schema](../schemas/study-objective-v0.1.schema.json) requires an ID,
exact allocation byte hash, one calibration package, metric identity, channel SI
units/scales/weights, equal-whole-test aggregation and rejection of the entire
candidate on any failure. The semantic validator also validates the allocation
against its exact reservation-policy identity before response access.

Supported channels are q and p in Pa, and volumetric_strain in dimensionless units.
Scales and channel weights must be positive finite numbers; weights are normalized
once across channels. No unit conversion or model-dependent inference occurs.
For each test, compute the weighted mean of channel scaled MSE using
[ordered piecewise-linear residual integration](ORDERED_METRICS.md). The objective
is the arithmetic mean across complete whole tests. Row count and strain travel
do not weight one test against another. Holds retain the axial-travel metric's
zero-weight limitation; physical-time scoring needs a separate declared contract.

Both observations and predictions must contain exactly the selected calibration
IDs, with no evaluation, reserved, unknown or missing tests. Each observation
bundle has `units` and `rows`; each prediction bundle has `units`, `status` and
`points`. Units maps exactly match policy channels. Rows and points follow the
ordered metric contract, including exact observation indices and axial coordinates.
A failed, truncated, reordered or nonfinite prediction rejects the entire candidate
with a named test/channel error. No success-prefix score or finite penalty is
invented. A future optimizer must retain these failures and explicitly define its
search behavior; this scorer does not implement an optimizer's failure log.

```sh
python3 -B tools/score_study_objective.py \
  --policy objective.json --allocation allocation.json \
  --reservations reservation-policy.json \
  --observations observations.json --predictions candidate.json \
  --output new-result.json
python3 -B -m unittest tests.test_study_objective tests.test_curve_metrics tests.test_study_allocation -v
```

The CLI strictly rejects duplicate JSON keys and nonfinite serialized numbers.
It checks metadata before opening either response bundle, reads only explicitly
supplied files and follows no experiment paths. Successful reports include all
per-test/channel metrics, normalized weights and SHA-256 of the five exact inputs.
Failure exits nonzero without creating a result; existing outputs are never
overwritten. A result does not bind a model executable, parameter vector, material
preparation or solver process status beyond the supplied prediction bundle. A
study runner must establish that provenance and candidate identity separately.

The eight synthetic test groups construct all metadata and responses locally.
They check a closed-form two-test/two-channel objective of 11/24, invariance to
redundant sampling, failed-test exclusion attempts, ordering/completion/numeric
errors, unit/policy identity, pre-response metadata rejection, exact input hashes,
strict JSON and exclusive CLI output. No real measurement file, native/Wasm build
or material simulation is needed. The schema describes structure; runtime checks
supply cross-file and finite-arithmetic constraints. Independent JSON Schema engine
validation is not claimed here.

The existing allocation/parameter contracts and all historical results remain
unchanged. CAL-01/02/05 remain open for prospective scientific choices, initialization,
model/data provenance, optimizer and budgets, physical features and uncertainty.
