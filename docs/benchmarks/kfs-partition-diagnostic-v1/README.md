# TMD7/TMD9 partition diagnostic — v1

The saved responses support a concrete explanation for the failed q refinement
checks: decreasing the caller's nominal increment changes adaptive subdivision,
and does not monotonically decrease the mean axial travel per reported substep
on every acquisition interval. This is supporting evidence, not proof of cause.
The original [failed gate](../kfs-propagation-refinement-v1/README.md) is unchanged.
No solver execution, build, fitting or new experiment is performed here.

## Saved evidence

[Analysis](analyze.py) first reconstructs all 1974 coarse/fine native process
receipts and exactly reproduces the retained failed scalar report. It then checks
caller commands against the frozen ceiling rule, validates echoed targets/step
counts, caller point counts, integer diagnostic counters and prediction aggregate
counters. All selected saved noninitial caller points satisfy the full-binary-tree counter
relation `substeps = 2 * (rejected + 1)`.

| Test/vector | Caller steps, coarse/medium/fine | Reported substeps | Reported rejected | Intervals where coarse mean travel/substep is smaller than medium |
| --- | --- | --- | --- | --- |
| TMD7/file | 125 / 220 / 419 | 380 / 440 / 838 | 65 / 0 / 0 | 16 of 43 |
| TMD7/alternative | 125 / 220 / 419 | 380 / 440 / 838 | 65 / 0 / 0 | 16 of 43 |
| TMD9/file | 125 / 220 / 413 | 444 / 466 / 826 | 97 / 13 / 0 | 17 of 47 |
| TMD9/alternative | 125 / 220 / 413 | 446 / 466 / 826 | 98 / 13 / 0 | 17 of 47 |

For each acquisition interval the proxy is absolute native segment target divided
by its sum of reported substeps. Its maximum medium/coarse ratio is 1.2 under all
four cases: on at least one interval the medium run has 20% more axial travel
per reported substep. This is a segment average, not a maximum internal increment
or a reconstruction of the accepted-step sequence. Nominal caller refinement
alone is therefore insufficient to assert nested or uniformly finer internal
partitions in these saved records.

[Scalar results](results.json) retain count histograms and acquisition-index
locators without publishing measured or predicted curve arrays. Exact integration
of squared linear q differences reproduces the prior normalized RMS values.
The three largest acquisition-interval contributions account for 11.16–14.20%
of the total squared difference across the eight adjacent comparisons. The
largest interval contributes less than 4.75%; there is no single interval that
accounts for most of the difference. The index locations are diagnostic only;
no source-data row is removed or reweighted.

## Source interpretation and its limit

The [source receipt](source-receipt.json) pins the repository solver header at
commit `131637d3b20c1da43acafe87b1e3e84aa05222bf`, recorded in the original report.
A [read-only source snapshot](source/solver-at-report-commit.hpp) preserves the
exact bytes. Lines 63–68 compare a full midpoint step with two half midpoint
steps using fixed model state scales; accepted rate updates commit the two-half
result and add two to `substeps`. Lines 71–73 recursively bisect on rejection.
Lines 97–108 show fresh mixed-control trials from the same committed state, with
only the converged constitutive result returned. Lines 133–140 emit caller
endpoints under uniform per-segment control increments.

This source is consistent with the observed counters. It explains how changing
caller ceilings can switch rejection branches, so the nominally coarse caller
can take smaller accepted increments in some intervals. However, the report's
executable originates from an earlier result directory, and no binary-to-this-
source build receipt is available. C++ paths are not listed dirty in the recorded
working tree, but that alone does not prove which source built the executable.
This packet does not establish exact source/binary identity.

The legacy responses also omit accepted fraction trees and internal midpoint
states. Aggregate counters cannot recover branch order or unequal leaf lengths
when multiple branches reject. The `error` field in the inspected source is the
last evaluated local estimate, not a maximum physical error bound. Diagnostics
from unsuccessful mixed-control trials are not accumulated into the final point
counters. Thus these counts cannot establish total work, exact adaptive paths,
convergence order, or a causal explanation for q error cancellation.

## Next bounded experiment

[The proposed follow-up](NEXT_STUDY.md) isolates a nested caller sequence from
the existing finest, rejection-free records. It proposes eight serial replays:
two further per-segment count doublings for the four affected cases, with fixed
parameters, initial states and acquisition endpoints. The policy must be frozen
before native observations. It retains the failed study, requires explicit
rejection-free diagnostics, and does not alter a model, material law or the old
gate. This follow-up is queued, not executed here.

Four new synthetic groups independently check constant/sign-crossing linear
integrals, redundant sampling, coordinate mismatch, the count-based proxy and
rejection of inconsistent counters/ceiling policies. Together with refinement,
propagation and strict-reader regressions, 19 tests pass; [log](tests.log).
[Saved replay](saved-audit.json) reproduces the diagnostic exactly without native
calls. These are software/data-consistency checks, not independent scientific
review. Public reuse rights, source-state resolution and scientific admission
remain open; no paper, model/schema or website change/deployment is made.

## Reproduction

From the repository root with the existing private response directories:

```sh
python3 docs/benchmarks/kfs-partition-diagnostic-v1/analyze.py --fine-dir /private/tmp/atlas-kfs-propagation-refinement-v1 --coarse-dir /private/tmp/atlas-kfs-tmd13-evaluation-v1 --prior-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-partition-diagnostic-replay.json
```

The output should equal `results.json` exactly after JSON decoding. No native
subprocess is invoked. Missing private responses prevent full reconstruction;
do not replace retained evidence or silently rerun a solver to fill gaps.
