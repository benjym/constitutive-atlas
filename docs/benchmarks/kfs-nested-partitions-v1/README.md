# Rejection-free nested caller partitions — v1

All eight bounded replays pass the separately frozen nested-regime checks.
Every noninitial caller point remains rejection-free with two reported substeps;
q and volumetric-strain differences decrease under the two count doublings and
remain below 1% of their matched calibration-response shift. **The original
[failed refinement sequence](../kfs-propagation-refinement-v1/README.md) remains
failed.** This result supports a distinct tested caller regime, not retrospective
acceptance of that sequence, causal proof or scientific admission.

## Prospective scope and driver choice

The [policy](policy.json), [runner](run_case.py), [assessor](assess.py) and five
synthetic groups are [hash-frozen](freeze.json) before native execution. The
[preceding diagnosis](../kfs-partition-diagnostic-v1/README.md) supplies four
cases: TMD7 and TMD9 under both calibration-selected VW96 vectors, all with file
evaluation states. Baselines are the retained 0.00005-limit predictions. Their
native command/response ledgers, prediction bytes and per-segment schedules are
hash-pinned; all baseline noninitial caller points have substeps=2/rejected=0.
The full preceding failed study/diagnostic is reconstructed before new execution.

Within each acquired segment, the new driver requests 2N and 4N caller steps,
where N is the pinned baseline count. The archived adapter still requests its
original baseline counts; a declared command overlay replaces **only `--steps`**.
Parameters, initial states, acquisition endpoints/order, targets, mixed controls,
material equations and native implementation remain unchanged. Private overlay
journals retain both requested and actual counts. Native echoes and point counts
must match actual requests. Each baseline caller knot must match the corresponding
new knot within 1e-14 axial strain; observed maximum difference is numerically zero,
without claiming bitwise/signed-zero identity.

Eight serial replays run in listed case/multiplier order, with the inherited
30-second total replay deadline. There are no retries, builds, fits, tuning,
model/schema changes or new experiments. Runtime/transport/echo/knot/completion
failure stops execution and preserves receipts. A return of adaptation would
remain a failed diagnostic predicate rather than a reason to discard the run.
The source-linked [initialization scenarios](../../../studies/kfs-development-v1/initialization-v1/README.md),
budget-limited calibration selections, prior observation exposure and missing
exact executable-to-source build receipt all remain qualified.

## Results

Each number below is an RMS output difference normalized by the fixed channel
scale. N→2N uses the retained baseline; 2N→4N compares the two new replays.

| Test/vector | Channel | N→2N | 2N→4N | Later/earlier |
| --- | --- | ---: | ---: | ---: |
| TMD7/file | q | 2.725252e-6 | 6.827420e-7 | 0.25052 |
| TMD7/file | Volume strain | 3.093437e-7 | 7.823826e-8 | 0.25292 |
| TMD9/file | q | 1.645307e-6 | 4.037380e-7 | 0.24539 |
| TMD9/file | Volume strain | 2.557820e-7 | 6.226522e-8 | 0.24343 |
| TMD7/alternative | q | 2.737538e-6 | 6.874319e-7 | 0.25111 |
| TMD7/alternative | Volume strain | 3.093434e-7 | 7.832360e-8 | 0.25319 |
| TMD9/alternative | q | 1.658825e-6 | 4.087524e-7 | 0.24641 |
| TMD9/alternative | Volume strain | 2.574680e-7 | 6.205247e-8 | 0.24101 |

All eight case/channel checks pass both separation and nonincrease predicates,
covering sixteen adjacent differences. The largest change is 0.023570% of its
matched previously observed coarse calibration-response shift, below the frozen
1% criterion. Nonincrease retains the original normalized 1e-12 floor. All
9984 new noninitial caller points report zero rejections and two substeps,
19968 reported substeps in total. The descriptive ratios range 0.24101–0.25319;
two differences do not establish an asymptotic order or justify extrapolating
a physical error bound. [Scalar results](results.json) retain every predicate,
full case metrics, exact input identities and private-output hashes.

This is consistent with the earlier partition-change explanation, but does not
prove it uniquely: no controlled change of adaptive tolerance or exact accepted
tree was observed. It creates no new common-resolution six-test panel, source e0
selection, pressure3 comparison, independently verified equation implementation,
parameter identifiability claim or blind validation.

## Audit and tests

The eight new replays comprise 360 native segments plus eight catalogue calls,
368 process receipts. Offline assessment reconstructs the actual modified command
sequence and complete predictions from strict hash-bound successful outputs,
requires every receipt to be consumed, and checks private overlay journals.
Only elapsed-time fields are removed during prediction comparison. Metrics,
count diagnostics, nesting checks and numerical predicates are recomputed.
The 1974 preceding receipts are also reconstructed; no native process is launched
by assessment.

[Exact saved replay](saved-audit.json) verifies all scalar fields and rejects
four copied corruptions: altered actual step command, nonzero exit marked
accepted, repinned altered prediction and repinned altered overlay journal.
Original private files remain untouched. Five new synthetic groups verify the
single-option overlay, immutable original request, wrong/duplicate requests,
missing/extra segments, integer multiplier/native count limits, wrong echoes,
nonnested knots and retention of adaptation as a failed diagnostic. Together
with partition/refinement/propagation and strict-reader regressions, 24 tests
pass; [log](tests.log). These software checks do not provide scientific review.

Raw command/response/overlay journals and predictions remain private in
`/private/tmp/atlas-kfs-nested-partitions-v1/`; no measured rows, acquisition
coordinate arrays or predicted curves are bundled. Complete auditing requires
those files and the prior private directories. Losing them requires a separately
retained rerun, not replacement of the first result. Archived execution is not
a clean-source cross-platform reproduction or current-engine equivalence claim.

## Reproduction and stopping point

From the repository root with all pinned private inputs, use a fresh output:

```python
from pathlib import Path
import subprocess, sys

output = Path('/private/tmp/kfs-nested-partitions-replay')
for index in range(8):
    subprocess.run([sys.executable,
        'docs/benchmarks/kfs-nested-partitions-v1/run_case.py',
        '--case', str(index), '--output-dir', str(output),
        '--fine-dir', '/private/tmp/atlas-kfs-propagation-refinement-v1',
        '--coarse-dir', '/private/tmp/atlas-kfs-tmd13-evaluation-v1',
        '--prior-dir', '/private/tmp/atlas-kfs-locked-initialization-v1'], check=True)
```

```sh
python3 docs/benchmarks/kfs-nested-partitions-v1/assess.py --private-dir /private/tmp/atlas-kfs-nested-partitions-v1 --fine-dir /private/tmp/atlas-kfs-propagation-refinement-v1 --coarse-dir /private/tmp/atlas-kfs-tmd13-evaluation-v1 --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-nested-result-replay.json
python3 docs/benchmarks/kfs-nested-partitions-v1/check_saved.py --private-dir /private/tmp/atlas-kfs-nested-partitions-v1 --fine-dir /private/tmp/atlas-kfs-propagation-refinement-v1 --coarse-dir /private/tmp/atlas-kfs-tmd13-evaluation-v1 --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-nested-audit-replay.json
```

Stop this numerical branch here; do not start an increment sweep. The next
bounded delivery is to expose the factorial sensitivity and both refinement
outcomes in the existing provisional website evidence view, preserving the
original failed gate and review/source/build limitations. No website edit,
deployment, paper edit, source correction, rights change or scientific admission
occurs in this packet. Independent review remains outstanding.
