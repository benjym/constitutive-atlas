# Locked-parameter KFS initialization sensitivity — v1

Changing only the disputed evaluation void ratios raises the six-test base-VW96
development error, while the density3-versus-pressure3 contrast keeps its sign.
This is conditional evaluation-input sensitivity at locked historical fits.
**Uncertainty through the TMD13 calibration state is not propagated.**

## Frozen scope and outcome

The [policy](policy.json) and [freeze](freeze.json) precede all native execution.
Eight replays cover two existing selected package fits, two development evaluation
tests (TMD12/TMD14), and two [initialization scenarios](../../../studies/kfs-development-v1/initialization-v1/README.md).
The exact archived budget96 executable and definitions are reused. No build,
optimization, recalibration or new data acquisition occurs.

All eight replays succeed. Every point dictionary in each of the four file-state
controls is numerically equal to the corresponding saved selected prediction.
This is exact numeric reproduction, without a signed-zero/bitwise claim. The
alternative changes only void ratio; recorded initial effective stresses,
parameters, acquisition coordinates and mixed controls remain fixed.

| Locked calibration package | File initialization | Alternative evaluation e0 | Relative error increase |
| --- | ---: | ---: | ---: |
| pressure3 | 0.169042679 | 0.174213042 | 3.059% |
| density3 | 0.129344363 | 0.136771734 | 5.742% |

Root scaled MSE uses equal q/volume channel weights and equal weights across the
six development evaluation tests. Only TMD12 and TMD14 are replaced in the
[previous locked six-test panel](../kfs-metric-sensitivity-v1/README.md); the other
four scores remain unchanged. Stress is scaled by file initial mean effective
pressure and volumetric strain by 0.01. Errors use the separately identified
piecewise-linear residual integral over absolute axial-strain travel.

| Within-model contrast: density3 minus pressure3 | Root scaled MSE difference |
| --- | ---: |
| file_initial | -0.039698316 |
| original_table_disputed_e0 | -0.037441308 |

The smaller magnitude under the alternative means a weaker conditional package
contrast in this panel. It does not establish a preferred source, generally
superior calibration design or cross-model ranking. The study uses one archived
formulation and previously exposed development observations.

## Completion, process integrity and numerical limits

The eight sequential invocations comprise 324 native loading-segment calls plus
eight catalogue descriptions. Each process has retained stdout/stderr hashes,
zero exit status, strict finite/unique-key JSON and the frozen catalogue identity.
The original replay algorithm is loaded from its exact archived source, with
process logging and strict decoding overlaid; no archived files are edited.
All four controls were required to match before continuing past them.

The [scalar results](results.json) retain metrics, response-change magnitudes,
control outcomes, native-call counts and hashes of the private ledgers. Raw
processes, propagated states and predicted curves remain private under
`/private/tmp/atlas-kfs-locked-initialization-v1/`; no measured response arrays
or curves are redistributed. Lost private receipts prevent a full receipt audit
until the frozen experiment is rerun.

[Saved audit](saved-audit.json) verifies all 332 raw process receipts and exact
deterministic scalar reconstruction without native calls. Four copied corruption
witnesses reject: nonzero process exit despite an accepted payload, duplicate
JSON keys with rebound hashes, altered control points and altered metrics.
[Seven synthetic process-gate tests](../../../tests/test_kfs_locked_initialization.py)
also cover timeouts, launch failures, nonfinite unused fields and false success.
With existing metric/diagnostic tests,26checks pass; [log](tests.log).

This task retains the historical maximum axial increment 0.0002 and first-crossing
2% acquisition window, with a 30 second deadline per replay. It does not establish
refinement for the alternative states. The existing full-panel refinement result
cannot be substituted for that missing check. No scientific accuracy threshold
is inferred from process success or small control drift.

The original-table e0 values remain competing discrete assumptions. TMD13 would
also change density3 calibration in a full scenario study. Its fitted-vector
change and uncertainty are not included, so these numbers are not total
initialization uncertainty. Source resolution, independent scientific review,
feature/parameter uncertainty and current-engine equivalence remain open.

## Reproduction

Requires the exact local archived executable, model/source snapshots, development
report and two experiment files pinned by policy, plus the previous metadata and
scalar-evidence packets. This is local archived-executable reproducibility, not
a clean-source rebuild or cross-platform verification. Use a fresh private output
directory. From the repository root:

```python
from pathlib import Path
import subprocess, sys

output = Path("/private/tmp/kfs-locked-initialization-replay")
for index in range(8):
    subprocess.run([sys.executable,
        "docs/benchmarks/kfs-locked-initialization-sensitivity-v1/run_case.py",
        "--case", str(index), "--output-dir", str(output)], check=True)
```

Then export/verify using fresh output filenames:

```sh
python3 docs/benchmarks/kfs-locked-initialization-sensitivity-v1/summarize.py --private-dir /private/tmp/kfs-locked-initialization-replay --output /private/tmp/kfs-locked-init-results.json
python3 docs/benchmarks/kfs-locked-initialization-sensitivity-v1/check_saved.py --private-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-locked-init-saved-audit.json
python3 -m unittest discover -s tests -p test_kfs_locked_initialization.py -v
```

The saved audit targets the original private receipts bound by the checked-in
result. A new execution can reproduce numeric outcomes while process hashes may
differ with paths or output formatting; compare the documented scalar fields
explicitly. It cannot silently replace the retained first execution.
