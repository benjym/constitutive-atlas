# Calibration/evaluation propagation refinement — v1

**The prospective refinement gate fails.** All 32 case/channel comparisons have
both adjacent output changes below 1% of their matched calibration-response
shift, but four q comparisons fail the separate nonincrease requirement. This
packet completes execution and audit of the bounded study; it does not close the
numerical refinement gate or provide scientific admission.

## Frozen scope

The [policy](policy.json), [runner](run_case.py), [assessor](assess.py) and four
synthetic test groups are [hash-frozen](freeze.json) before any new native calls.
All sixteen cases from the [factorial propagation study](../kfs-tmd13-evaluation-propagation-v1/README.md)
are replayed at maximum axial increments 0.0001 and 0.00005, against the retained
0.0002 curves: both calibration-selected vectors, six file-state evaluation tests
and the two disputed alternative evaluation states. There are 32 new serial
replays, with no fitting, retuning, new data or builds.

Every input, vector, observation window, ordered metric, stress and specimen
state remains as in the preceding study. The
[source-linked initialization scenarios](../../../studies/kfs-development-v1/initialization-v1/README.md)
retain the file/original-Table-3 conflict and hybrid-state qualification.
Both selected vectors remain search-budget-limited. Four unchanged specimen
states reuse the same case within each resolution's two evaluation-state panels.
The exact archived base-VW96 solver is used; this is not current-engine or
independent equation verification.

For each of sixteen cases and each q/volume-strain channel, the frozen gate
requires BOTH adjacent normalized RMS output changes to be no greater than 1%
of the coarse response difference between the two calibration-selected vectors
at the same evaluation state. It also requires medium-to-fine change to be no
greater than coarse-to-medium plus the declared 1e-12 absolute normalized floor.
Zero calibration signal cannot pass a relative gate. This adopts the earlier
study's separation fraction/nonincrease policy, with a distinct calibration-response
reference; it is not a physical error tolerance or probabilistic uncertainty bound.

## Retained failure

| Test | Calibration vector | q coarse→medium | q medium→fine | Nonincrease |
| --- | --- | ---: | ---: | --- |
| TMD7 | File | 7.3961024e-6 | 9.7344676e-6 | Fail |
| TMD9 | File | 4.3632819e-6 | 4.7258124e-6 | Fail |
| TMD7 | Alternative | 7.4205725e-6 | 9.8222395e-6 | Fail |
| TMD9 | Alternative | 4.3280391e-6 | 4.7599606e-6 | Fail |

Numbers are RMS differences normalized by each fixed channel scale. All other
28 case/channel nonincrease checks pass. All 64 adjacent comparisons pass the
1% separation condition; the largest adjacent change is 0.840902% of its matched
calibration-response shift. The largest absolute normalized adjacent change is
1.526247e-5. These small changes do not override the four failed checks.
The [complete scalar result](results.json) retains every check, both predicates,
all case metrics and all twelve six-test panels. No gate is relaxed or omitted.

| Maximum axial increment | File/file | File/alternative | Alternative/file | Alternative/alternative |
| --- | ---: | ---: | ---: | ---: |
| 0.0002 | 0.129344363 | 0.136771734 | 0.124701176 | 0.132294397 |
| 0.0001 | 0.129342641 | 0.136770085 | 0.124699687 | 0.132292968 |
| 0.00005 | 0.129341599 | 0.136768872 | 0.124698837 | 0.132291923 |

Entries are root mean scaled MSE, with calibration/evaluation scenario order in
each column. The previously reported effect signs persist at these resolutions.
This is descriptive stability; it does not prove convergence, resolve the source
state, identify unique parameters or establish predictive superiority. No
Richardson order or extrapolated error is claimed.

A saved-record inspection supplies a concrete next lead. TMD7's aggregate native
rejection counts are 65/0/0 across the three limits for both vectors. TMD9 counts
are 97/13/0 (file vector) and 98/13/0 (alternative vector). Caller segment step
counts also change because each acquisition interval uses a ceiling of its
length divided by the maximum increment. Thus these are different caller and
adaptive partitions, not a proven asymptotic sequence. This observation does not
establish the cause of the q nonmonotonicity. Diagnose TMD7/TMD9 partition and
accepted-step behaviour before claiming refinement closure; any further study
must freeze a separate policy and preserve this failed result.

## Audit and tests

All 32 native replays complete successfully: 1284 segments plus 32 catalogue
calls yield 1316 new process receipts. The assessor additionally reconstructs
all 658 coarse receipts. Every generated command, parameter order, committed
initial state, target, step count, raw-output hash, exit status, strict JSON and
catalogue identity is checked offline. All full predictions match reconstruction
after removing elapsed time only; all metrics and gate predicates recompute.
No native process is launched by assessment. Runtime failure would stop the
serial run and retain partial state/receipts; successful prefixes receive no score.

The [saved audit](saved-audit.json) reproduces the exact scalar result, including
`gate_passed: false`. Copied corruptions reject altered commands, nonzero exit
marked accepted, repinned altered prediction values and changed scores. Originals
are untouched. Four new synthetic groups test inclusive separation boundaries,
both adjacent levels, the explicit nonincrease floor, invalid/zero/nonfinite
signals and rejection of partial/failed replays before scoring. Together with
propagation, calibration, selection and strict-reader regressions, 23 tests pass;
[log](tests.log). Passing software tests do not turn the scientific/numerical gate
into a pass.

Raw commands, native outputs and predictions stay private in
`/private/tmp/atlas-kfs-propagation-refinement-v1/`. The preceding coarse and prior
alternative controls remain in their original private directories. No measured
rows or predicted curves are redistributed. Full receipt auditing requires those
local files; their loss requires a separately retained rerun. No clean-source
cross-platform build, public data-reuse permission, paper edit, model/schema
change, deployment or scientific admission is added.

## Reproduction

With the pinned archived executable and all private inputs, run serially from
the repository root into a fresh directory:

```python
from pathlib import Path
import subprocess, sys

output = Path('/private/tmp/kfs-propagation-refinement-replay')
for index in range(32):
    subprocess.run([sys.executable,
        'docs/benchmarks/kfs-propagation-refinement-v1/run_case.py',
        '--case', str(index), '--output-dir', str(output),
        '--coarse-dir', '/private/tmp/atlas-kfs-tmd13-evaluation-v1',
        '--prior-dir', '/private/tmp/atlas-kfs-locked-initialization-v1'], check=True)
```

```sh
python3 docs/benchmarks/kfs-propagation-refinement-v1/assess.py --private-dir /private/tmp/atlas-kfs-propagation-refinement-v1 --coarse-dir /private/tmp/atlas-kfs-tmd13-evaluation-v1 --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/refinement-result-replay.json
python3 docs/benchmarks/kfs-propagation-refinement-v1/check_saved.py --private-dir /private/tmp/atlas-kfs-propagation-refinement-v1 --coarse-dir /private/tmp/atlas-kfs-tmd13-evaluation-v1 --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/refinement-audit-replay.json
```

The assessor is expected to exit **1** after writing the retained failed result.
The saved audit exits 0 when it correctly reproduces that failure and rejects
corruptions. The current website still presents the previous conditional locked
comparison; it has not promoted these factorial scores or this failed gate.
