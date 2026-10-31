# KFS development comparison: scientific-review handoff v1

Prepared 1 November 2026. **Technical evidence assembled; independent scientific
review pending.** This is a review guide to existing observations, not a new
experiment, acceptance policy or signed approval. The bounded question is whether
the base-VW96 KFS development comparison can be reported with these qualifications.
No reviewer is assigned. Start with the [unsigned decision sheet](SCIENTIFIC_REVIEW.md).

## Read in this order

1. [Active VW96 dossier](../../models/hypoplastic-sand-vw96.md),
   [full original-equation technical review](../../ingestion/hypoplastic-sand-vw96/original-equation-review-v2/README.md)
   and [applicability decision](../../decisions/0004-vw96-igs-applicability.md).
   The original paper has been technically read; that work is not independent
   scientific admission. Review compression-positive Mandel conventions,
   effective stress, infinitesimal zero-spin scope, explicit stress/e initialization,
   strict density-domain restrictions and project numerical continuations.
2. [Input accounting](../kfs-development-checkpoint-v1/input-review.md),
   [whole-test allocation](../../../studies/kfs-development-v1/allocation.json)
   and [source-linked initialization alternatives](../../../studies/kfs-development-v1/initialization-v1/README.md).
   These historical packets have next-step statements superseded by later packets;
   read them for their frozen scope, not as the current task board.
3. [Calibration sensitivity](../kfs-tmd13-calibration-sensitivity-v1/README.md)
   and [six-test factorial evaluation](../kfs-tmd13-evaluation-propagation-v1/README.md).
   The exact claim/evidence map is [claims.json](claims.json).
4. [Original failed refinement](../kfs-propagation-refinement-v1/README.md),
   [saved partition diagnosis](../kfs-partition-diagnostic-v1/README.md), then
   [separate nested-partition result](../kfs-nested-partitions-v1/README.md).
5. [Current build receipt](../current-source-build-v1/README.md),
   [synthetic compatibility](../current-archived-vw96-v1/README.md), and
   [single current-source TMD7 replay](../current-kfs-tmd7-v1/README.md).
   [Website evidence review](../../reviews/web-current-tmd7-v1/README.md) documents
   the scalar presentation; it is not evidence that the website Wasm binary ran
   the archived six-test study or the current native replay.

## Comparison to assess

This handoff centers on **base VW96, density3**, not a ranking of the pilot's
elasticity, Drucker–Prager and VW96 fits. Four constants (phi, hs, alpha, beta)
were fitted; four (n, ed0, ec0, ei0) were inherited. p_ref is a fixed project
numerical scale, not a ninth material constant. Stress and e are specimen inputs.
The [parameter policy](../../../studies/kfs-development-v1/parameters-v1/parameter-policy.json)
and input accounting expose bounds and prior information.

Density3 calibration uses whole tests TMD3/8/13. Evaluation uses TMD1/5/7/9/12/14;
they were excluded from fitting but previously exposed during development, so
this is **not blind validation**. The separate pressure3 package uses TMD2/3/4;
it is background, not another factorial arm here. Fourteen reserved tests stay
excluded. The allocation was reconstructed after the original development run;
subsequent sensitivity and compatibility studies have their own prospective
freezes. This handoff does not retrospectively preregister the original pilot.

Acquired axial coordinates retain order/reversals to the last observation at or
below the existing 2% cutoff. No physical time is inferred. The calibration
objective uses a uniform strain grid; evaluation instead integrates squared
piecewise-linear residuals over absolute acquired axial travel. Evaluation
scales q by each file's initial mean effective pressure and volumetric strain
by 0.01. The root mean of twelve scaled channel MSEs gives equal weight to six
tests and two channels; see [ordered metrics](../../ORDERED_METRICS.md).

Six fits cover two TMD13 e0 assumptions × seeds 0/17/41 × 96 candidates per fit.
All terminate at the candidate budget. Both select seed 0 using calibration
only; alpha changes from 0.1290625 to 0.14, with the other selected constants
unchanged. The inherited constants, search bounds and budget prevent claims of
unique parameters, global optimality or equal-information model comparisons.

| Calibration e0 | Evaluation e0 | Archived six-test root mean scaled MSE |
| --- | --- | ---: |
| File | File | 0.129344363 |
| File | Original-table alternative | 0.136771734 |
| Original-table alternative | File | 0.124701176 |
| Original-table alternative | Original-table alternative | 0.132294397 |

These four panels use sixteen unique replays, reusing unchanged specimen states
within a vector. They are conditional sensitivity, not uncertainty intervals,
variance decomposition or evidence that the lower-error source value is correct.
TMD12/13/14 file e0 values conflict with original Table 3. Alternatives change e0
only while retaining recorded stresses: hybrid assumptions, not a verified
reconstruction of published preparation. The source disagreement remains open.

## Numerical and provenance limits that must travel with the table

The original three-resolution refinement gate **failed** four q nonincrease
checks (TMD7/TMD9 under both vectors), although every adjacent change was below
1% of its matched calibration-response signal. A separately defined nested,
rejection-free follow-up passed eight case/channel gates on those affected
cases. It does not convert the original FAIL to PASS, certify the whole panel,
prove an asymptotic order or identify a causal mechanism. Stop the numerical
branch here; no new sweep is implied by this review.

The archived executable is hash-identified, but its exact source/build
association is unresolved. A separate traceable current build and synthetic
comparison provide limited additional evidence. **Only TMD7, file/file, has the
current experimental replay:** 44 endpoints, 43 segments, 125 caller increments,
within the existing 2% development window. All seven compatibility gates pass;
maximum stress difference is 1.7463e-10 Pa. Both engines report 380 substeps and
65 rejections. These are software-compatibility results, not physical accuracy
or integration-error bounds. Current descriptive RMSE remains about 6660.027 Pa
for q and 0.000649124 for volume strain. No current six-test result or general
engine equivalence is claimed.

The [TMD2 published-case reconstruction](../kfs-tmd2-appendix-law-v1/README.md)
is separate evidence for **VW96+IGS**, with a separate unsigned review and
qualified 0–25% operational coordinates. It is not an independent published
base-VW96 validation of these fitted panels. Neither packet establishes exact
historical decks or finite-deformation equivalence.

## Reproduction and access tiers

From the repository root, these existing saved-only audits need no compiler,
solver execution, experimental files or network:

```sh
python3 docs/benchmarks/current-source-build-v1/verify.py
python3 docs/benchmarks/current-archived-vw96-v1/check_saved.py
```

They verify the public saved build/synthetic evidence, not the private KFS
curves. For the latter, follow the exact commands and asset identities in the
[factorial packet](../kfs-tmd13-evaluation-propagation-v1/README.md) and
[TMD7 packet](../current-kfs-tmd7-v1/README.md). Saved-only TMD7 audit:

```sh
python3 docs/benchmarks/current-kfs-tmd7-v1/check_saved.py --private-dir /private/tmp/atlas-current-kfs-tmd7-v1
```

That command requires private measurements, baseline receipts and source snapshots
pinned by its policy. A public checkout alone is insufficient. Temporary paths
are not durable hosting; preserve the private evidence before publication.
Raw measurements, predictions and source PDFs remain private while rights are
unresolved. This guide publishes no arrays and grants no redistribution rights.
Fresh material replays/builds are separate coordinated serial operations, never
an automatic step in this documentation review.

## Completion boundary

The [decision sheet](SCIENTIFIC_REVIEW.md) asks for evidence-located judgments,
not checkbox-only approval. Accepting qualified reporting would not admit the
model generally, close M1/M4, authorize data release or complete the paper.
If corrections are requested, scope the smallest affected claim and evidence;
do not automatically add models, fits, experimental campaigns or solver features.
Source-state resolution, durable private reproducibility and signed independent
review remain open. No new build, fit, material call, deployment or admission
was performed to prepare this handoff.
