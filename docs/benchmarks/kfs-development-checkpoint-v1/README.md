# Bounded KFS development checkpoint — 1 November 2026

This package consolidates existing results; it introduces no fits, solver calls,
model admission or scientific acceptance thresholds. It closes the first task of
this delivery cycle: establish which usable comparison already exists and what
prevents treating it as a reviewed benchmark. M1 and M4 remain open.

## Question and fixed scope

Within each model, how does choosing three pressure-spanning rather than three
density-spanning calibration tests change prediction on the same development
panel? Keep the existing matched-count design, three formulations, two packages,
three optimizer starts, and the already completed 96/384-budget sensitivity.
Do not add models, optimizers, data families or another parameter sweep to this
work package. The twenty-formulation release remains the roadmap target; the
paper's 50+ collection ambition is a later expansion, not this cycle's dependency.

The archived study uses linear elasticity, a cohesionless Drucker–Prager
specialization and base VW96 sand hypoplasticity. Elasticity is a diagnostic
baseline. These results support within-model development contrasts; they do not
establish a fair cross-model ranking.

| Role | Whole-test IDs |
| --- | --- |
| pressure3 calibration | TMD2, TMD3, TMD4 |
| density3 calibration | TMD3, TMD8, TMD13 |
| Shared development evaluation | TMD1, TMD5, TMD7, TMD9, TMD12, TMD14 |

All IDs have the KFS prefix. Evaluation tests are excluded from each fit but were
previously inspected; this is not blind or final evaluation. Reserved tests stay
reserved. Calibration and evaluation use the first 2% axial strain with the
archived distinctions: calibration is a monotonic ramp/uniform-strain objective;
evaluation replays acquisition-order strain with travel-weighted endpoint errors.
No response records outside the existing development snapshots were opened here.

## Result recovered from existing evidence

The existing report command regenerated a JSON summary identical to the retained
summary. The [snapshot audit](audit.json) verifies 33 files per run: archived
analysis code, three model definitions, executable, reservation policy and eleven
normalized experiment files. It checks whole-test separation and selected
prediction coverage. Each budget has 36 selected evaluations and 108 evaluations
across starts, all successful. Failed calibration vectors remain in the original
journals: one at budget 96 and nine at budget 384.

Evaluation root scaled MSE uses equal test/channel weights, stress divided by
initial mean effective pressure, and volume strain divided by 0.01. These are
physical reference scales, not measurement-noise estimates. Lower is better for
this specified development metric; the rows do not form a model leaderboard.

| Formulation | Calibration package | Budget96 | Budget384 |
| --- | --- | ---: | ---: |
| Elastic diagnostic | pressure3 | 0.667925 | 0.667925 |
| Elastic diagnostic | density3 | 1.12686 | 1.12686 |
| Cohesionless Drucker–Prager | pressure3 | 0.411329 | 0.388800 |
| Cohesionless Drucker–Prager | density3 | 0.334725 | 0.330275 |
| VW96, four fitted constants | pressure3 | 0.169110 | 0.177080 |
| VW96, four fitted constants | density3 | 0.129421 | 0.125362 |

Calibration-test selection matters in this panel. More search improves the VW96
pressure-package calibration objective but worsens its evaluation score. This is
a reason to report calibration and transfer separately; it is not evidence that
the density package is universally preferable. Bound hits and budget-limited
starts remain visible in the regenerated report. The existing maximum adjacent
resolution change is 1.51872e-5 in normalized RMS; that is a path-refinement
observation, not equation verification or a newly adopted pass threshold.

## Admission and information accounting

| Item | Existing evidence | Remaining gate |
| --- | --- | --- |
| Elastic inputs | E and nu fitted; p_ref fixed as numerical scale | Diagnostic scope; cannot represent irreversible sand response |
| DP inputs | E, nu, M and Md fitted; c=0 specialization, p_ref fixed | Restricted noncontractive flow; bound/search sensitivity and current-law reconciliation |
| VW96 inputs | phi, hs, alpha, beta fitted; n, ed0, ec0, ei0 inherited from literature | Extra calibration information must remain explicit; independent source review |
| Initialization | File effective stress and void ratio explicitly used | TMD12–14 file/later-table versus original-table void-ratio conflict unresolved |
| Model identity | Archived definitions and executable verified by hashes | Current DP equations/derived expressions differ; current VW96 parameter declarations differ. Do not relabel these runs as current implementations |
| Published baseline | Existing literature-constant transfer demonstration | Base-law transfer does not reproduce the source's IGS/projection simulations; BENCH-01/02 remain open |
| Reproducibility | Existing report/figure regeneration and local snapshot audit | Clean-checkout source/build/data-access reproduction remains open; local snapshots are required |
| Distribution | This packet contains aggregate metrics and hashes | Review measurement reuse terms before publishing measured curves or observations |

Current versus archived field differences were inspected without running either
implementation. Elastic definition bytes match. DP changes include equations,
derived expressions, description and sources; VW96 changes are six parameter labels and sources; the [input review](input-review.md)
checks every other definition field for equality. This checkpoint makes no equivalence claim.

Sources and existing decisions are recorded in the
[paper development protocol](../../../paper/DEVELOPMENT.md),
[matched-count configuration](../../../paper/study/pilot_matched.json),
[information protocol](../../../paper/study/information_protocol.md),
[metadata conflict register](../../../paper/study/metadata_conflicts.json) and
[void-ratio source follow-up](../../../paper/study/kfs_void_ratio_followup.json).
Those working paper files are independently owned and were not modified here.

## Reproduce this checkpoint without a build

From the repository root, with the existing local pilot snapshots and paper
Python dependencies available, choose a fresh output directory:

```sh
PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/private/tmp/atlas-kfs-mpl python3 paper/scripts/report_pilot.py --report paper/results/pilot-matched96/report.json --comparison paper/results/pilot-matched384/report.json --output /private/tmp/atlas-kfs-checkpoint-replay
python3 docs/benchmarks/kfs-development-checkpoint-v1/audit.py --diagnostics /private/tmp/atlas-kfs-checkpoint-replay
```

The audit compares regenerated metrics with the retained local summary and checks
snapshot hashes; it does not execute the saved binary. The checked aggregate
[summary](summary.json) is retained here, alongside the exact [audit code](audit.py).
Missing local snapshots are an explicit reproduction dependency, not a reason to
fetch or expose reserved measurements. Source/build reproduction is not claimed.
The current audit result is saved in [audit.json](audit.json).

The regenerated figure files remain local under
`/private/tmp/atlas-bounded-kfs-checkpoint-v1/`: `development-curves-1.png`,
`development-curves-2.png` and `development-data-budget.png`. The detailed report
includes physical per-test errors, completion, failed calibration counts and
budget/boundary diagnostics. No measured curves are bundled in this packet.

## Delivery checklist and stopping rules

- [X] Recover the existing comparison and regenerate its summary/figures.
- [X] Verify archived inputs and preserve failures, scope and source conflicts.
- [X] Account for VW96 source/parameter inputs and compare archived/current definition fields; [bounded review](input-review.md). Independent scientific review and engine replay remain open.
- [ ] Resolve or explicitly bound initialization assumptions for this panel without choosing them by prediction error. If unresolved, keep the matched-density result development-only and identify a source-supported smaller baseline separately.
- [ ] Identify one complete published model/parameter/material example matching an implemented law. The IGS-to-base transfer demonstration does not satisfy this gate.
- [ ] Produce a reviewed development figure/table with fixed input-information and implementation labels, and prepare the same evidence summary for the website. Distribution review precedes measurement publication.

Only the first three items are closed by this packet. Published-baseline
source selection is the next task. A demonstrated blocker may receive a separate bounded solver fix;
it does not authorize a new general capability project. If the review cannot
establish equivalence, retain these archived development results and specify a
small prospective replay before any new compiled observations. Do not relax
numerical gates, release reserved data or repeatedly enlarge the study.

Mohr–Coulomb browser work is deferred at its prebuild source-audit checkpoint.
No new build or material call is needed to complete this checkpoint. SANISAND and
Terra Cotta remain explicit near-term model priorities, but do not block this
existing-data review. No push, deployment or remote CI was performed.
