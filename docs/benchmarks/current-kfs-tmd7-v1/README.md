# Current-source KFS-TMD7 development replay v1

**The pinned current executable reproduces the archived TMD7 development
prediction within the prospective compatibility limits.** This connects a
traceable current build to one actual model-to-experiment development comparison.
It does not validate the model or establish general engine equivalence.

## Fixed scope

Use base [VW96 hypoplasticity](https://doi.org/10.1002/(SICI)1099-1484(199607)1:3%3C251::AID-CFM13%3E3.0.CO;2-3)
and the existing [Wichtmann KFS-TMD7 record](https://www.torsten-wichtmann.de/KFSDB-TMD.htm).
The same file-initial density3 parameter vector, measured file initialization,
acquisition order and 0.0002 maximum caller increment are preserved. This is the
**complete existing development window up to the first 2% axial-strain cutoff**,
not the full acquired experimental test: 44 observations, 43 segments and 125 caller
increments. Data were already inspected; this is not blind evaluation.

The archived control is case 02 of the
[existing evaluation propagation](../kfs-tmd13-evaluation-propagation-v1/README.md).
TMD7 was chosen because it is one of the retained original nonnested refinement
failures. This comparison does not reopen that study or change its failed gate.
No alternative initialization, fit, optimizer or model definition was introduced.

[Policy](policy.json), source/input hashes, exact archived file hashes and
[code freeze](freeze.json) were retained before current observations. The
archived prediction was first reconstructed from saved receipts without native
execution. Only the current engine ran: 44 serial processes, including one
catalogue query and 43 loading segments; no builds or fits.

## Result and limits

| Comparison over all 44 acquisition endpoints | Observed maximum | Frozen limit |
| --- | --- | --- |
| Stress components | 1.7463e-10 Pa | 10 Pa |
| Signed deviator stress q | 1.7463e-10 Pa | 10 Pa |
| Void ratio | 0 | 1e-7 |
| Strain components | 8.674e-19 | 1e-7 |
| Volumetric strain | 1.735e-18 | 1e-7 |

All seven gates pass, including curve-RMS limits: scaled q RMS difference is
6.319e-16 (initial mean-stress scale 101644.07 Pa), and scaled volumetric-strain
RMS difference 8.463e-17 (scale 0.01). These software compatibility criteria were
fixed before execution; they are not physical-accuracy or integration-error
bounds. Current and archived states are not claimed bitwise identical.

Both runs use 125 caller increments, 380 reported substeps and 65 rejections.
Maximum radial-stress drift is 0.001543 Pa for each. All actual native request
parameters, initial states, targets, step counts and complete point coverage are
checked. Each engine chains its own preceding committed state; all other
segment arguments match the archived requests exactly. Full native outputs
reconstruct both predictions, including all state and strain components.

Agreement between engines does not remove model-to-measurement error.
Descriptive current experimental RMSE is 6660.027 Pa for q and 0.000649124 for
volumetric strain, effectively unchanged from the archived result. Errors use
exact squared piecewise-linear residual integration over absolute acquired axial
travel; no physical time, extrapolation, source correction or new model ranking
is inferred. See [scalar results](results.json) for every score and gate.

## Provenance and saved audit

The current executable is SHA
`960d6f8ebcc0c3296555dd6e294a3650a5ec2318108d30850216ee5a69e4f574`,
from source commit `6ff25a9fb01de0fa9360c1bd04149877490319ef`; its
[source/build receipt](../current-source-build-v1/README.md) and
[bounded synthetic compatibility study](../current-archived-vw96-v1/README.md)
remain separate evidence. The exact archived executable is pinned too, but its
historical source/build association remains unresolved.

Raw normalized measurements, acquired controls, trajectories, native outputs
and prediction files remain private because redistribution rights are unresolved.
The [private evidence index](private-evidence-index.json) publishes only file
hashes. The current evidence is at `/private/tmp/atlas-current-kfs-tmd7-v1/`;
temporary storage is not durable artifact hosting. The baseline/source snapshots
and experimental paths required for reproduction are explicitly pinned in the
policy; a source-only checkout without those private assets cannot run this audit.

With those private inputs available, reconstruct 88 process receipts and the exact
public scalar result without compiling or executing the solver:

```sh
python3 docs/benchmarks/current-kfs-tmd7-v1/check_saved.py --private-dir /private/tmp/atlas-current-kfs-tmd7-v1
python3 -m unittest discover -s tests -p test_current_kfs_tmd7.py -v
```

[All six software/evidence checks pass](tests.log), none skipped in this run.
They cover exact reconstruction, altered actual command, nonzero false-success
process, changed native step echo and substituted prediction, including rebound
hashes. A consistent 11 Pa fixture retains a failed compatibility gate. Tests
skip explicitly when required private data are absent; they never download data,
build or run native code. These checks are not independent scientific review.

To intentionally reproduce current material observations, coordinate serial
execution and use a new output directory with the exact pinned assets:

```sh
python3 docs/benchmarks/current-kfs-tmd7-v1/replay.py run /private/tmp/atlas-current-kfs-tmd7-replay
```

Do not overwrite the original evidence or replace a pinned executable silently.
Hashes/receipts detect accidental changes, not deliberate signed provenance.

## Stop condition and next delivery

This completes the declared single-test comparison. Do not automatically expand
to other tests, refit, retune the caller ceiling or rerun the refinement campaign.
This result covers one vector, initialization, acquired window and executable
pair. It does not migrate existing model schemas, identify the archived source,
resolve source-state/data-rights questions, deploy the site or admit a model.

The next bounded delivery should surface this limited current-build connection
in the provisional website's evidence links, alongside the unchanged original
refinement failure and review limits. Independent original-paper/equation and
scientific review remain the gates for a reviewed benchmark release.
