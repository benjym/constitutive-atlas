# Independent KFS development reporting review

**Accept qualified reporting of the exact C1-C7 density3 development comparison.**
Reviewer `/root/kfs_development_review`, a separate agent run, 1 November 2026.
This review did not author the study, choose parameters or observe new material
runs. It supplies an actual scoped agent judgment, not a human signature,
general model admission, publication approval or a review of TMD2+IGS.
The original unsigned handoff and every failed study remain unchanged.

The scope is the bytes bound by [manifest](manifest.json) and
[decision](decision.json). The eight independent check groups and eight existing
saved-only auditors in [results](check-results.json) pass. A subprocess-launch
guard was active during the saved auditors. No build, compiled material call,
fit, new experiment, release or private-array publication occurred.

## C1 - Formulation: accept within the declared reporting scope

I independently inspected the exact user-supplied von Wolffersdorff (1996) PDF
(hash `70eb1297cd25e67daf8b35b8f8c22f42c3a7fae2c0a62ae9e0079e3b03e64100`),
visually reading PDF pages 2, 12, 13 and 20 (printed 252, 262, 263, 270).
Eqs 1-2, 40-46 and Appendix C10 support the source-to-record factors and eight
material parameters. With source tension-positive T=-sigma and D=-de,
normalization T/tr(T) is unchanged: reversing the stress-rate sign preserves
the linear term and reverses the nonlinear norm term. Void continuity becomes
`e_prime=-(1+e)trace(de)`. Independent scalar sign and Mandel-contraction
witnesses pass; these are algebra, not a trajectory verification corpus.

The source's Jaumann footnote requires the stated zero-spin restriction before
using ordinary stress derivatives. The reviewed comparison uses effective
stress, compression-positive Mandel components, explicit stress/e state and
infinitesimal strain-path coordinates. Numerical pressure/density guards,
midpoint/adaptive settings and the finite small-invariant cutoff are Atlas
choices. Appendix C's isotropic F=1 and stated shape range do not certify every
runtime-admitted mixed-sign state. No full-path internal-stage admissibility
check is supplied by this review. The prior full technical reading remains
useful evidence; I did not independently repeat all 21 pages or its full
Appendix A/B derivation. These limits permit qualified development reporting,
not universal physical applicability or finite-deformation equivalence.

Evidence: [crosswalk](../../ingestion/hypoplastic-sand-vw96/formulation-crosswalk.json),
[original reading](../../ingestion/hypoplastic-sand-vw96/original-equation-review-v2/README.md),
[applicability policy](../../decisions/0004-vw96-igs-applicability.md),
and the frozen original/current model definitions bound in the manifest.

## C2 - Information and objectives: accept development-only description

The allocation separates whole calibration tests TMD3/8/13 from evaluation
TMD1/5/7/9/12/14. Fourteen reserved tests remain excluded from this review;
whole-test separation does not imply independent specimen preparation. The
allocation was reconstructed after development and evaluation responses were
previously exposed. Consequently these scores are not blind validation.

Only phi, hs, alpha and beta are fitted. n=.27, ed0=.677, ec0=1.054 and ei0=1.212
remain inherited; p_ref=100000 Pa is numerical scaling. Exploratory bounds,
literature-derived starting information, three seeds and the 96-candidate budget
remain part of the information supplied. I checked the policy and retained
accounting; I did not obtain or independently verify the cited 2026 parameter
Table 3. Acceptance covers this explicit recorded inheritance, not a newly
verified source calibration.

The calibration uses 100 increments and 101 uniform-strain objective samples.
Evaluation uses the exact squared linear residual integral over absolute acquired
axial travel, q scaled by each file's initial mean effective pressure and volume
strain by .01. The distinction is substantive: the evaluation is not the
optimizer's objective and has no physical-time weighting. My separate closed-form
segment integration reproduces all 32 case/channel scores from private saved
predictions and measured rows without importing Atlas metrics.

Evidence: [allocation](../../../studies/kfs-development-v1/allocation.json),
[parameter policy](../../../studies/kfs-development-v1/parameters-v1/parameter-policy.json),
[calibration policy](../kfs-tmd13-calibration-sensitivity-v1/policy.json),
[evaluation policy](../kfs-tmd13-evaluation-propagation-v1/policy.json),
[metric contract](../../ORDERED_METRICS.md).

## C3 - Source-state conflict: accept unresolved hybrid sensitivity only

The exact Wichtmann and Triantafyllidis (2016) original PDF is locally available
(hash `de1cb4945548850539d4b312a1a703a3152bd1836bfdb6f032e19110aa75336c`).
I visually read its complete PDF page 5: Table 3 gives TMD12/13/14 e0
.819/.824/.822, with the caption identifying conditions at initial mean pressure
before shearing. Exact normalized-file e0 values are .816769337/.817760544/
.813569451. The conflict is real at the level of the inspected original table
and retained normalized files. Later-table/provider-correction provenance was
not independently re-acquired in this review; no physical winner is established.

The alternative changes only those three e0 values. Every recorded effective
stress is preserved, so these are explicitly hybrid sensitivity assumptions,
not reconstructed published preparation states. Lower error, repetition in later
papers or rounding does not resolve the conflict. Two assumptions are not an
uncertainty distribution or a confidence interval.

Evidence: [state assignments](../../../studies/kfs-development-v1/initialization-v1/states.json),
[initialization policy](../../../studies/kfs-development-v1/initialization-v1/policy.json),
[qualified source account](../../../studies/kfs-development-v1/initialization-v1/README.md).

## C4 - Selection and four panels: accept conditional scores

All six calibration fits terminate at budget96; seed0 minimizes the successful
calibration objective in both scenarios. Only selected alpha changes (.1290625
to .14); phi/hs/beta match. All 576 candidate evaluations and 1734 saved process
receipts reconstruct. The seed0/TMD8 failed candidate is preserved, not omitted.
Selection uses calibration scores only, not the new evaluation scores.

My independent panel aggregation gives, in calibration/evaluation order:

| Calibration e0 | Evaluation e0 | Root mean of twelve scaled channel MSEs |
| --- | --- | ---: |
| File | File | 0.12934436297532312 |
| File | Original-table alternative | 0.1367717339283584 |
| Original-table alternative | File | 0.12470117631676818 |
| Original-table alternative | Original-table alternative | 0.13229439741406743 |

Sixteen unique saved replays supply four six-test panels. Unchanged specimen
states share the same case within a vector's two panels. Equal weighting is of
channel MSEs before the square root, not an average of channel RMSEs. Exact saved
command/output reconstruction also passes for all 658 factorial process receipts.
The scores support conditional sensitivity only: no model ranking, global optimum,
parameter uniqueness, confidence interval or variance decomposition is accepted.

Evidence: [calibration result](../kfs-tmd13-calibration-sensitivity-v1/results.json),
[factorial result](../kfs-tmd13-evaluation-propagation-v1/results.json),
[own independent arithmetic and audits](check-results.json).

## C5 - Refinement: accept both outcomes with the original FAIL retained

I independently recomputed all stored separation and nonincrease predicates.
The original 32 case/channel gate fails exactly four q nonincrease checks:
TMD7/TMD9 under both vectors. All adjacent differences meet the 1% separation
condition; smallness does not override failure. Saved reconstruction preserves
that failed verdict and checks all 1316 new plus 658 coarse process receipts.

The distinct prospective nested regime passes eight case/channel gates for
those four affected cases, with rejection-free N/2N/4N caller schedules. Its
368 new process receipts and preceding evidence reconstruct. This supports that
specific regime; it neither repairs the original sequence nor certifies a new
common-resolution six-test panel. No asymptotic order, causal explanation,
physical integration-error bound or further sweep follows.

Evidence: [failed result](../kfs-propagation-refinement-v1/results.json),
[partition diagnosis](../kfs-partition-diagnostic-v1/README.md),
[separate nested result](../kfs-nested-partitions-v1/results.json).

## C6 - Implementation: accept the narrow pinned-build connection

The archived binary is hash-identified but its exact build/source association
remains unresolved. The separate build receipt audits 351 source pins, six
successful command receipts and nine-model metadata. Its word "current" means
the exact pinned commit `6ff25a9fb01de0fa9360c1bd04149877490319ef`, not an
assertion about today's evolving HEAD or deployed website. Twenty-two synthetic
saved processes reconstruct and pass their bounded compatibility limits.

Only TMD7 file/file connects that build to an experimental window: 44 endpoints,
43 segments, 125 caller increments, 380 substeps and 65 rejections per engine.
All 44 current plus 44 baseline receipts reconstruct and all seven frozen gates
pass. Maximum stress difference is 1.7463e-10 Pa. Experimental RMSE nevertheless
remains about 6660.027 Pa for q and .000649124 for volume strain. Agreement of
software outputs is not agreement with measurements or an integration-error
bound. No current six-test, Wasm, cross-platform, general engine or live-site
execution claim is accepted. The separate TMD2+IGS study is not evidence for
this fitted base-VW96 factorial comparison.

Evidence: [build](../current-source-build-v1/README.md),
[synthetic comparison](../current-archived-vw96-v1/README.md),
[TMD7 result](../current-kfs-tmd7-v1/results.json),
[website evidence limits](../../reviews/web-current-tmd7-v1/README.md).

## C7 - Reproducibility and rights: accept disclosed access-limited reporting

All private directories needed for the saved calibration/factorial/refinement/
nested and TMD7 audits existed and passed during this review. I accessed their
measurements, saved predictions, candidate journals and native response receipts
locally. This is stronger than public scalar-file agreement, but a public clone
cannot reproduce these private audits unaided. Public build/synthetic saved
audits run without experimental assets. No author binaries were executed.

The coordinator's new [private retention](../kfs-private-retention-v1/README.md)
independently verifies 225 exact files (14,184,778 bytes), covering direct current
TMD7 and archived baseline evidence outside temporary paths. Its byte retention
is useful, but does not make the complete source/import closure portable or
retain the full six-test/calibration/refinement campaign durably. The other
study directories still use temporary paths. Loss would prevent this full audit;
a separately identified rerun must never replace the first retained evidence.

Rights remain unresolved. Source PDFs, measured rows, acquisition arrays, native
trajectories, predictions and retained executables remain private. Hash receipts
are not permission to redistribute and this review grants none. Durable complete
private reproduction and source-state clarification remain open; neither is
silently reclassified as model admission or a paper/release completion gate.

## Reproduce this review and bounded next action

From the repository root with all pinned private assets still available:

```sh
python3 -B docs/benchmarks/kfs-development-agent-v1/check.py --output /private/tmp/kfs-development-agent-replay.json
```

This reruns scalar algebra, independent saved-curve integration/aggregation,
selection/state/gate arithmetic and eight saved-only auditors. It never launches
a compiler or solver. The manifest distinguishes review outputs, exact public
inputs, original private sources and hash-bound private study metadata. Native
stdout/stderr bytes are transitively bound by the exact per-process ledgers and
were verified by the saved auditors; they are not republished here.

Smallest next action: attach this scoped decision to the development reporting
view and retain the qualifications next to its table. Keep full campaign private
durability, portable replay, source-state resolution and any broader admission/
release work separately open. No new fitting or numerical sweep is requested.
