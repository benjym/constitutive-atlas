# TMD13 calibration-to-evaluation propagation — v1

Changing the disputed TMD13 calibration void ratio changes the selected VW96
parameters and therefore the six-test evaluation score. At the frozen historical
output resolution, recalibration alone lowers the score, while changing both
calibration and evaluation states raises it relative to the file-state baseline.
This is development sensitivity, not evidence for selecting a source value.

## Frozen comparison

The [policy](policy.json), [runner](run_case.py), [assessor](assess.py) and six
synthetic test groups are [hash-frozen](freeze.json) before native execution.
The two complete parameter vectors come from the preceding
[calibration-only selection](../kfs-tmd13-calibration-sensitivity-v1/README.md):
both select seed 0 under the original three-seed, 96-candidate-per-seed budget.
Only selected alpha differs (0.1290625 versus 0.14). No fit, selection or tuning
uses the new evaluation scores. Both fits remain budget-limited.

Evaluation comprises whole tests TMD1, TMD5, TMD7, TMD9, TMD12 and TMD14, under the
existing [development allocation](../../../studies/kfs-development-v1/README.md).
Only TMD13's e0 changes in calibration; only TMD12/14 e0 change in evaluation.
The [source-linked initialization scenarios](../../../studies/kfs-development-v1/initialization-v1/README.md)
retain all recorded stresses and the unresolved file/original-2016-Table-3
conflict. This does not replace file metadata with a supposedly corrected state
or reproduce the complete nominal published preparation.

Sixteen serial replays cover two selected parameter vectors, each applied to all
six file-state tests and the two alternative-state tests. Four evaluation tests
have unchanged states, so their same predictions are explicitly reused within
each vector's two six-test panels; there are no duplicate native replays.

The exact archived base-VW96 implementation replays acquired coordinates in
original order to the last observation at or below 2% axial strain. Maximum
native axial increment is 0.0002; each replay has a 30-second total limit. The
[ordered linear-residual metric](../../ORDERED_METRICS.md) scales q by file initial
mean effective pressure and volume strain by 0.01. Equal channel MSE and equal
test weights are averaged before taking the square root. This evaluation metric
is distinct from the historical uniform-strain-grid calibration objective.

## Six-test results

| Calibration e0 scenario | Evaluation e0 scenario | Root mean scaled MSE |
| --- | --- | ---: |
| File | File | 0.129344363 |
| File | Original-table alternative | 0.136771734 |
| Original-table alternative | File | 0.124701176 |
| Original-table alternative | Original-table alternative | 0.132294397 |

[Scalar results](results.json) preserve all sixteen case summaries and the exact
six-case membership of each panel. Against file/file, the signed changes are
−0.004643187 for calibration alone, +0.007427371 for evaluation alone and
+0.002950034 combined. The root-error interaction is +0.000165850, defined as
combined minus the two isolated changes. These are differences of nonlinear
root errors, not a variance decomposition or confidence interval.

A lower evaluation error does not resolve the source disagreement or establish
unique parameters, predictive superiority, a global optimum or blind validation.
These evaluation data were previously exposed during development. No pressure3
fit is changed or new model ranking inferred here.

## Execution and audit

All sixteen replays succeed: 642 native segments and sixteen catalogue
descriptions produce 658 process receipts. Six file-vector/file-state controls
numerically reproduce every historical selected point dictionary. Two
file-vector/alternative-state controls reproduce the hash-pinned prior locked
study. Equality is numerical Python dictionary equality; no bitwise or signed-zero
identity is claimed.

The offline assessor regenerates every native command, including parameter order,
initial state after each committed segment, target and increment count. It must
consume exactly the recorded command sequence. Strict unique-key, finite JSON,
zero exit status, true success, catalogue identities and all stdout/stderr hashes
are checked. The unchanged archived adapter reconstructs the full prediction
from the saved responses, matching every field after removing elapsed time only;
metrics and scalar summaries are then recomputed. No native process is launched
by assessment. Failures retain partial state/receipts privately and stop the
serial run; successful prefixes receive no score.

[Saved audit](saved-audit.json) repeats exact scalar reconstruction and rejects
four copied corruptions: altered command, nonzero exit marked accepted, altered
prediction with repinned hash and altered score. Originals remain unchanged.
Six new synthetic test groups cover factorial weights/coverage, shared unchanged
states, missing/duplicate/nonfinite scores, command order/exhaustion, process
status/catalogue, raw hashes and elapsed-only normalization. With calibration,
selection and strict-reader regression groups, nineteen tests pass; [log](tests.log).
The first pre-freeze synthetic run failed an exact sqrt/square assertion because
2 rounded to 2.0000000000000004; only the test assertion changed to approximate
equality. The production aggregation and numerical gates did not change.

Raw predictions, command ledgers and native responses remain in
`/private/tmp/atlas-kfs-tmd13-evaluation-v1/`; prior alternative controls are in
`/private/tmp/atlas-kfs-locked-initialization-v1/`. Neither measured rows nor
prediction curves are bundled. Receipt audit needs those private directories;
loss requires a separately retained rerun, not rewriting this first result.
The exact executable/model and archived source snapshots are hash-bound; this
establishes local archived execution, not a clean-source cross-platform build or
current-engine equivalence.

## Reproduction and remaining gate

From the repository root, with the pinned local inputs and prior control directory:

```python
from pathlib import Path
import subprocess, sys

output = Path('/private/tmp/kfs-tmd13-evaluation-replay')
for index in range(16):
    subprocess.run([sys.executable,
        'docs/benchmarks/kfs-tmd13-evaluation-propagation-v1/run_case.py',
        '--case', str(index), '--output-dir', str(output),
        '--prior-dir', '/private/tmp/atlas-kfs-locked-initialization-v1'], check=True)
```

```sh
python3 docs/benchmarks/kfs-tmd13-evaluation-propagation-v1/assess.py --private-dir /private/tmp/kfs-tmd13-evaluation-replay --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-tmd13-evaluation-replay.json
python3 docs/benchmarks/kfs-tmd13-evaluation-propagation-v1/check_saved.py --private-dir /private/tmp/atlas-kfs-tmd13-evaluation-v1 --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-tmd13-evaluation-audit-replay.json
```

The next numerical dependency is refinement for the newly selected alternative
vector. The earlier refinement packet covers the original locked vectors only
and cannot certify these new responses. Source resolution, independent scientific
review, broader parameter identifiability/uncertainty and data-reuse rights remain
open. This task adds no build, fit, model/schema change, paper edit, deployment,
new experimental data or scientific admission. The current website still shows
the previous conditional locked-parameter comparison, not these new panels.
