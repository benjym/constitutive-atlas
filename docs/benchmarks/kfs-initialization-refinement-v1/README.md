# KFS initialization-effect refinement — v1

The observed conditional initialization effect is larger than the tested
discretization changes. All frozen output-separation and nonincrease checks pass
for both file/original-table e0 scenarios and both locked calibration packages.
This adds numerical evidence to the [previous sensitivity study](../kfs-locked-initialization-sensitivity-v1/README.md);
it does not resolve the source conflict or propagate TMD13 calibration uncertainty.

## Prospective scope and gate

[Policy](policy.json) and [source freeze](freeze.json) precede finer native calls.
The previous 0.0002-increment curves and their observed initialization shifts are
fixed by hashes, not described as unseen data. Each of eight retained cases is
replayed at maximum axial increments 0.0001 and 0.00005: sixteen new serial replays.
Parameters, recorded initial effective stresses, acquisition rows, 2% window,
archived executable and model definitions are unchanged. No build or fit occurs.

For each case/channel, require both adjacent-resolution normalized RMS changes
to be no more than **1% of the matching coarse alternative-versus-file shift**.
Also require medium-to-fine change not to exceed coarse-to-medium change plus
an explicit 1e-12 normalized floor. This floor does not loosen the separation
threshold. Both q and volumetric strain use the exact frozen scales and ordered
linear-residual metric from the prior study.

These are project numerical-separation gates, not published physical accuracy
bounds, measurement uncertainty or independent constitutive-equation verification.
Passing demonstrates separation over these tested increments only; it supplies
neither an asymptotic error bound nor a zero-step extrapolation.

## Results

All sixteen replays succeed: 648 loading-segment processes and sixteen catalogue
descriptions. Strict finite/unique-key JSON, successful exits, catalogue identity,
full original-coordinate coverage, exact prediction hashes and reconstructed
metrics pass. The eight retained coarse runs/controls are re-audited first.

| Adjacent resolutions | Largest normalized RMS change | Largest change / matching coarse initialization shift |
| --- | ---: | ---: |
| 0.0002 → 0.0001 | 1.51776364e-05 | 0.2731% |
| 0.0001 → 0.00005 | 8.93053785e-06 | 0.1572% |

All 16 case/channel records pass both gates; each contains two adjacent comparisons
(32 comparisons total). No threshold is revised. Every medium-to-fine change is
nonincreasing under the frozen rule. No fourth-order rate or other convergence
order is claimed.

The following quantities compare the two initialization scenarios at the same
resolution, using stress divided by recorded mean effective pressure and volume
strain divided by 0.01. They measure response differences, not experimental errors.

| Locked package / test | Maximum increment | Normalized RMS q shift | Normalized RMS volume shift |
| --- | ---: | ---: | ---: |
| pressure3 / KFS-TMD12 | 0.00020 | 0.005158114 | 0.002899645 |
| pressure3 / KFS-TMD12 | 0.00010 | 0.005158153 | 0.002899649 |
| pressure3 / KFS-TMD12 | 0.00005 | 0.005158225 | 0.002899656 |
| pressure3 / KFS-TMD14 | 0.00020 | 0.019192326 | 0.010476098 |
| pressure3 / KFS-TMD14 | 0.00010 | 0.019192606 | 0.010476085 |
| pressure3 / KFS-TMD14 | 0.00005 | 0.019192165 | 0.010476095 |
| density3 / KFS-TMD12 | 0.00020 | 0.008557643 | 0.004265846 |
| density3 / KFS-TMD12 | 0.00010 | 0.008557728 | 0.004265887 |
| density3 / KFS-TMD12 | 0.00005 | 0.008557725 | 0.004265869 |
| density3 / KFS-TMD14 | 0.00020 | 0.027467395 | 0.014241163 |
| density3 / KFS-TMD14 | 0.00010 | 0.027468052 | 0.014241227 |
| density3 / KFS-TMD14 | 0.00005 | 0.027467583 | 0.014241127 |

[Scalar results](results.json) retain all comparison records, shifts, metrics,
case identities and private-file hashes. Raw predictions, intermediate states
and process outputs remain private under
`/private/tmp/atlas-kfs-initialization-refinement-v1/`. No measured rows or curves
are bundled. The [saved audit](saved-audit.json) reconstructs the result exactly
without solver calls, verifying 664 new and 332 retained coarse process receipts.

[Six synthetic decision tests](../../../tests/test_kfs_initialization_refinement.py)
cover unresolved signals, growing small changes, exact threshold behavior, the
explicit numerical floor and invalid magnitudes. Combined with existing ordered
metric/sensitivity/process checks, 32 tests pass; [log](tests.log).

## Reproduce and stop

Requires all exact private/local dependencies of the prior study, including its
eight coarse predictions/receipts. The new policy pins those curve bytes. A
recreated coarse run must satisfy these identities or be a separately identified
study; it cannot silently replace the retained evidence.

From the repository root, use a fresh output directory and run one case at a time:

```python
from pathlib import Path
import subprocess, sys

output = Path("/private/tmp/kfs-initialization-refinement-replay")
for index in range(16):
    subprocess.run([sys.executable,
        "docs/benchmarks/kfs-initialization-refinement-v1/run_case.py",
        "--case", str(index), "--output-dir", str(output),
        "--coarse-dir", "/private/tmp/atlas-kfs-locked-initialization-v1"], check=True)
```

```sh
python3 docs/benchmarks/kfs-initialization-refinement-v1/assess.py --private-dir /private/tmp/kfs-initialization-refinement-replay --coarse-dir /private/tmp/atlas-kfs-locked-initialization-v1 --output /private/tmp/kfs-refinement-replay.json
python3 -m unittest discover -s tests -p test_kfs_initialization_refinement.py -v
```

Exclusive output creation prevents overwriting evidence. A gate failure is saved
before a nonzero exit. Runtime failures retain raw receipts and stop later native
cases. Full receipt audit depends on the private files remaining available.

This closes the tested-output refinement slice only. It is an archived-executable
study on one material and previously exposed development tests, with no
current-engine equivalence or scientific admission. Calibration-state propagation,
physical feature errors and independent scientific review remain open.
