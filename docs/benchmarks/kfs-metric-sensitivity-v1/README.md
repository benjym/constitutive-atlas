# KFS saved-prediction metric sensitivity — v1

The six aggregate errors change by only **0.029–0.073%** under exact
piecewise-linear residual integration. The sign of every within-model
density-minus-pressure contrast is unchanged. This is a retrospective reporting
diagnostic at locked parameters, not a new calibration or scientific admission.

## Frozen scope

[Policy](policy.json) was frozen before the first diagnostic execution;
[freeze receipt](freeze.json) binds its exact bytes, assessor and synthetic tests.
It selects all 36 previously selected predictions from the existing budget96 run:
three archived formulations, two calibration packages and six previously exposed
development evaluation tests. Calibration/evaluation roles, inherited VW96 inputs
and exact historical definitions are checked using the shared allocation and
parameter policies before saved response-file access. Reserved observations are
not opened. No parameter selection, fitting, material call or build occurs.

Initialization stays exactly as saved: file effective stress and void ratio.
The TMD12–14 source disagreement remains unresolved; these results cannot establish
a physically preferred initialization. The window retains acquisition rows from
zero through the first crossing of 2% axial strain, excluding the crossing row.
It never takes a later return below the boundary or extrapolates a boundary value.

The only change is the [metric](../../ORDERED_METRICS.md). Stress error is scaled
by initial mean effective pressure and volumetric strain by 0.01. Root mean scaled
MSE gives equal weights to channels within each test and to each of the six tests.

## Results

| Archived formulation | Calibration package | Endpoint trapezoid | Linear residual integral | Change |
| --- | --- | ---: | ---: | ---: |
| linear-elastic | pressure3 | 0.667924634 | 0.667731535 | -0.0289% |
| linear-elastic | density3 | 1.126857936 | 1.126530119 | -0.0291% |
| drucker-prager | pressure3 | 0.411328756 | 0.411142123 | -0.0454% |
| drucker-prager | density3 | 0.334724637 | 0.334480522 | -0.0729% |
| hypoplastic-sand-vw96 | pressure3 | 0.169110278 | 0.169042679 | -0.0400% |
| hypoplastic-sand-vw96 | density3 | 0.129421246 | 0.129344363 | -0.0594% |

| Within-model density3 minus pressure3 | Endpoint trapezoid | Linear residual integral |
| --- | ---: | ---: |
| linear-elastic | +0.458933302 | +0.458798584 |
| drucker-prager | -0.076604119 | -0.076661600 |
| hypoplastic-sand-vw96 | -0.039689033 | -0.039698316 |

Negative contrasts favor density3 for this declared development objective;
positive contrasts favor pressure3. These are within-model contrasts. Differing
inherited material information, applicability and archived implementation limits
prevent interpreting the rows as a fair cross-model ranking. No confidence
intervals or independent-material inference are supplied.

Lower scores are expected from the quadrature change. For endpoint residuals
a,b and travel w, endpoint-trapezoid MSE minus exact linear-residual MSE has
segment numerator `w*(a-b)^2/6`. The diagnostic verifies this identity for all 72
test/channel comparisons, along with the original saved score, full observation
coverage, exact coordinates and locked selected-fit parameters. The frozen
arithmetic comparison tolerance is relative 1e-12/absolute 1e-15 in scaled MSE.
This checks arithmetic reconstruction; it is not a scientific acceptance bound.
A reduced score therefore does not mean the model prediction improved.

[Detailed results](results.json) contain aggregate/per-test errors, identity
checks and hashes, with no measured response arrays or predicted curves. The
[execution receipt](execution.json), [stdout](execution.stdout) and
[stderr](execution.stderr) retain the successful first run. Historical report,
code, fits and manuscript remain unchanged.

## Reproduction and stopping point

Requires the existing private/local budget96 report and six normalized snapshots.
The exact report and data hashes are listed in the policy; this packet does not
download or redistribute them. Run from the repository root with a fresh output:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/benchmarks/kfs-metric-sensitivity-v1/assess.py --output /private/tmp/kfs-metric-sensitivity-replay.json
python3 -m unittest discover -s tests -p test_kfs_metric_sensitivity.py -v
```

Seven new synthetic tests pass, covering analytical aggregate/gap reconstruction,
first-crossing behavior, changed selected parameters, duplicate/missing/extra
predictions, failed/truncated predictions, corrupt historical scores and metadata
gating before a missing report could be read. With the shared metric tests,
19 tests pass; [log](tests.log). Reproduction preserves exclusive output creation.

This closes only the bounded metric-sensitivity task. CAL-02 remains open for a
scientifically justified complete prospective study policy; CAL-05 remains open
for physical features, sensitivity/identifiability and uncertainty. No claim of
blind evaluation, current-engine equivalence or scientific admission is added.
The next study decision is a source-based initialization policy with explicitly
qualified scenarios, before selecting any new fit or evaluation campaign.
