# TMD13 calibration-state sensitivity — v1

Changing the disputed TMD13 void ratio changes the calibration result under the
same archived search. This closes the bounded recalibration slice, **not the
evaluation-propagation question**. No evaluation experiment file is opened by the
fit runner and no evaluation replay occurs. These are previously exposed
development data; no blind-study claim is made.

## Frozen comparison

[Policy](policy.json), [runner](run_fit.py) and [objective assessor](assess.py) are
hash-frozen before the first fit in [freeze](freeze.json). Six fits cover the
existing base-VW96 density3 package (TMD3, TMD8, TMD13), two initialization
assumptions and the original seeds 0/17/41. Only TMD13 e0 changes, from the exact
file value 0.817760544 to original 2016 Table 3 value 0.824. All effective stresses
and the other two specimen states remain unchanged. The
[source disagreement and scenario qualifications](../../../studies/kfs-development-v1/initialization-v1/README.md)
are retained; this is not a source correction or full nominal published state.

The full archived objective and search are retained: monotonic drained loading
to the last measured point at or below 2% axial strain, 100 native increments,
101 uniform-strain objective samples, q divided by initial effective pressure,
volume strain divided by 0.01, equal channel/test MSE weights, bounded coordinate
pattern search, original transforms/bounds, 96 candidate evaluations per seed,
initial search step 0.25, minimum step 0.001 and 30 seconds per test. Decreasing
measured coordinates reject; repeated coordinates collapse to the last value.

Calibration deliberately retains the historical uniform-grid metric. The new
ordered linear-residual metric is a distinct evaluation/reporting method and is
not substituted during these fits. Four material coefficients are fitted;
n, ed0, ec0 and ei0 remain literature-fixed and p_ref is a numerical scale.
The complete partitions, units and inherited seeds retain their existing
[parameter-accounting provenance](../../../studies/kfs-development-v1/parameters-v1/README.md).
The bounds are the historical exploratory analyst choices, not newly established
scientific admissibility or identifiability bounds.

## Calibration outcomes

| Seed | Initialization | Best calibration mean scaled MSE | Failed candidates | Termination |
| --- | --- | ---: | ---: | --- |
| 0 | file_initial | 0.004803041791 | 1 | budget_limit |
| 0 | original_table_disputed_e0 | 0.005438060154 | 0 | budget_limit |
| 17 | file_initial | 0.006635948579 | 0 | budget_limit |
| 17 | original_table_disputed_e0 | 0.006784425754 | 0 | budget_limit |
| 41 | file_initial | 0.005085229368 | 0 | budget_limit |
| 41 | original_table_disputed_e0 | 0.005687831417 | 0 | budget_limit |

All six fits use the full 96 candidate budget. Every file-state control reproduces
its original complete numerical trace after removing elapsed-time fields only.
The genuine historical candidate 40/TMD8 integration failure at seed 0 is retained
and reproduced, with all three test attempts present. No failure is dropped.

Selection uses only the lowest successful calibration objective, with listed
seed order retained on ties. Both scenarios select seed 0. The selected fitted
values are:

| Parameter | Unit | File initialization | Original-table TMD13 e0 |
| --- | --- | ---: | ---: |
| phi | rad | 0.50348523241 | 0.50348523241 |
| hs | Pa | 4000000000 | 4000000000 |
| alpha | 1 | 0.1290625 | 0.14 |
| beta | 1 | 2.609375 | 2.609375 |

The selected alpha changes; the other three selected fitted values agree
numerically. All starts are budget-limited. These finite-search selections do
not establish unique parameters, a converged global optimum or a confidence
interval. A lower calibration objective does not identify which competing
source state is physically correct.

## Evidence and failure accounting

The [scalar results](results.json) retain each fit summary, all selected input
values and hashes of the full private journals. The private directory
`/private/tmp/atlas-kfs-tmd13-calibration-v1/` contains all 576 candidate records,
1728 test attempts and six catalogue descriptions. Raw predictions, responses,
commands and observation files are not redistributed.

[Saved audit](saved-audit.json) verifies 1734 process receipts, reconstructs every
test metric and candidate objective from native outputs, checks candidate/input
binding, compares each journal with its completed fit, and repeats all three
control-trace comparisons. Scalar reconstruction is exact without new native
calls. Copied corruption witnesses reject a failure marked successful, a deleted
failed candidate, altered native parameters and an altered selected objective.

Valid native constitutive failures, nonzero exits and timeouts retain failed
test outcomes and the historical 1e30 candidate penalty. All three tests are still
attempted. Malformed/nonfinite/duplicate-key JSON, catalogue changes and launch
errors abort the workflow; they are not assigned a constitutive objective.
Every process output is hash-bound. Source and executable hashes are checked
before fitting; no author implementation is executed and no build is performed.

Eight new synthetic test groups plus five strict-reader groups pass;
[log](tests.log). They verify legitimate-failure preservation, strict transport
rejection, timeout receipts, exact control comparison, budget-inclusive failed
candidates/all test attempts, calibration-only selection, tie order and failed
start exclusion. These checks do not supply independent scientific review.

## Reproduction and next dependency

Requires the exact archived budget96 executable, source/model snapshots, report,
reservation/parameter/scenario metadata and three calibration experiment files
pinned by policy. Loading the report permits historical control comparison;
its previously generated evaluation predictions do not enter the optimizer.
The optimizer receives only the three prepared calibration records. Use fresh
private output paths from the repository root:

```python
from pathlib import Path
import subprocess, sys

output = Path("/private/tmp/kfs-tmd13-calibration-replay")
for index in range(6):
    subprocess.run([sys.executable,
        "docs/benchmarks/kfs-tmd13-calibration-sensitivity-v1/run_fit.py",
        "--fit", str(index), "--output-dir", str(output)], check=True)
```

```sh
python3 docs/benchmarks/kfs-tmd13-calibration-sensitivity-v1/assess.py --private-dir /private/tmp/kfs-tmd13-calibration-replay --output /private/tmp/kfs-tmd13-calibration-results.json
python3 docs/benchmarks/kfs-tmd13-calibration-sensitivity-v1/check_saved.py --private-dir /private/tmp/atlas-kfs-tmd13-calibration-v1 --output /private/tmp/kfs-tmd13-saved-audit.json
```

The saved audit binds the original private receipts. New timing and process
hashes may differ on reproduction; do not replace the retained first result.
Lost private journals prevent a full receipt audit until rerun. This establishes
local archived-executable reproduction, not a clean-source cross-platform build.

The next bounded continuation must freeze these selected vectors before using
evaluation responses, and distinguish calibration-only from combined
calibration/evaluation initialization changes. Do not retune on evaluation error.
The historical pressure3 fit is unchanged because none of its calibration states
is disputed in this scenario. Evaluation refinement, model/source qualifications,
data-reuse rights and independent scientific admission remain separate gates.
