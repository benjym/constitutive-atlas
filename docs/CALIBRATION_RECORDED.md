# Recorded-path calibration runner

`atlas.calibration_recorded.run_recorded_search` connects the
[bounded search](CALIBRATION_SEARCH.md) to `prepare_replay` and the existing native
`execute_recorded` API. It accepts decoded model, experiment, per-test configuration,
allocation/reservation, objective and search records plus an explicitly selected
solver, its SHA-256, a compiled catalogue and a **new** output directory.

Before material execution it validates exact calibration-package coverage, complete
parameter inventory and bounds, observation units/order/travel, explicit preparation,
source void-ratio overrides and the selected model's identity and parameter order
in the compiled catalogue. It checks executable bytes and compares one native
`--describe` response to that catalogue. It does not build or discover a solver.
The library supports existing validated incremental definitions; newly authored
model records still require v0.3. Physical-time and non-drained protocols remain
unsupported by this recorded experiment adapter.

Every candidate and whole test starts with a new replay request made from its fixed
configuration. No state is carried from another candidate/test, and initialization
parameters are not fitted by this adapter. All test configurations must explicitly
contain the same search seed parameter vector; candidate values replace that vector
without changing history, initial strain or solver/control settings.

Predictions use signed axial-minus-mean-radial q and mean stress p from the returned
stress tensor, and volumetric strain relative to the declared initial strain. If
volume is scored, the first measured volume must be zero; no offset is inferred.
Sampling coordinates are the prescribed observation coordinates, including
reversals/duplicates, with the native control tolerance checked at each returned
point. Measured radial stress is replayed as a constraint; this is a conditional
comparison, not an independent apparatus classification or model applicability
judgment. It does not sort, interpolate, downsample or extrapolate observations.

The runner writes `freeze.json` and metadata, then a directory for every attempted
candidate. Each contains the prepared request/provenance and returned response for
each attempted test, followed by its assessment. Failed native prefixes remain on
disk and never receive an objective. A test failure stops that candidate; later
tests are not executed. Expected native failure/timeout rejects the candidate;
transport or identity corruption is fatal and stops the search. Every attempt
consumes search budget, but this is not a cap on internal substeps/material trials.
Their limits and per-process timeout are separately declared.

Writes use exclusive creation and flush/fsync; existing output is rejected. An
assessment-write failure propagates before the next candidate. A final result and
file-hash manifest identify a completed run, including a completed search with no
feasible candidate or a recorded fatal adapter error. Interrupted/failed persistence
can leave an incomplete directory; resume and certified crash recovery are not
implemented. Keep real measurement-bearing run directories private unless reuse
rights are established.

The freeze records the complete decoded configuration, canonical value hashes,
selected source-file hashes and executable identity. It does **not** recover
original input-file bytes or a complete transitive source/build closure. A production
study must additionally bind those source receipts and its accepted study design.
The existing native helper checks process returncode against status before returning;
this wrapper retains its parsed response, not raw material-process stdout/stderr or
command receipts. Metadata stdout/stderr and errors are retained. Those limitations
are explicit; this is not a new portable archival release or scientific signature.

The [three-candidate elastic smoke study](benchmarks/calibration-elastic-smoke-v1/README.md)
uses the existing traceable executable with no rebuild. It freezes expectations
before three native calls, recovers analytical E=30MPa, and retains every request,
response and assessment. Its saved-only replay reconstructs the complete search
result without executing the solver. Synthetic tests also cover persistence errors,
failed prefixes, identity/order/completion corruption, incorrect inputs and fresh
preparation. No real-data fitting campaign or historical result changes accompany
this implementation. Prospective scientific study choices remain open.

```sh
python3 -B -m unittest tests.test_calibration_recorded tests.test_calibration_search tests.test_study_objective tests.test_curve_metrics tests.test_study_allocation -v
python3 -B docs/benchmarks/calibration-elastic-smoke-v1/verify.py
```
