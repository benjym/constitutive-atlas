# KFS development initialization scenarios — v1

The initialization decision is now explicit: retain the historical file-based
results and represent the original-table values as a separate, qualified
sensitivity scenario. **The source disagreement is not resolved.** No state is
selected by its prediction error. This closes the bounded policy task, not the
full initialization-uncertainty or scientific-admission gate.

## Source evidence and assignments

The coordinator visually rechecked Table 3 on PDF page 5 of
[Wichtmann & Triantafyllidis (2016)](https://doi.org/10.1007/s11440-015-0402-z).
Its caption identifies void ratio and relative density at initial mean pressure
prior to shearing. The [source PDF](https://www.torsten-wichtmann.de/paper/2016-AG-data-base-part1.pdf)
is hash-pinned in the [policy](policy.json) and remains private. No source image
or full text is redistributed.

| Test | Exact normalized-file e0 | Original 2016 Table 3 e0 | Alternative minus file | Study role |
| --- | ---: | ---: | ---: | --- |
| KFS-TMD12 | 0.816769337 | 0.819 | +0.002230663 | evaluation |
| KFS-TMD13 | 0.817760544 | 0.824 | +0.006239456 | density3 calibration |
| KFS-TMD14 | 0.813569451 | 0.822 | +0.008430549 | evaluation |

The file values round to the competing later-table values recorded in the
existing conflict register. That register and its follow-up are exact-byte pinned;
the later publication is **not freshly reviewed here**. The previous follow-up
found a later accepted/proof paper repeating the original values, without an
explanation or correction notice. Repetition is not independent measurement.
No averaging, majority vote or physical source preference is inferred.

The alternative changes only the three disputed void ratios. All other void
ratios and all six recorded effective-stress components are identical to the
file scenario. It is deliberately a hybrid sensitivity assumption, not a
reproduction of a complete published nominal initialization. Two discrete
assumptions do not define a probability distribution, confidence interval or
empirical range covering every possible initial state.

## How the scenarios may be used

- **Historical reporting:** keep the original file-state labels and the
  development-only qualification on all saved fits and scores. Do not overwrite
  or relabel those artifacts.
- **Locked-parameter evaluation sensitivity:** retain existing selected fits,
  and change evaluation initialization only for TMD12 and TMD14. This measures
  conditional response to those inputs; it cannot propagate the TMD13
  calibration-state disagreement.
- **Full scenario recalibration:** the density3 calibration also changes TMD13,
  then evaluates with the matching scenario. Definitions, information inputs,
  bounds, objective, seeds, budgets, loading/window and failure handling must
  be frozen together in a distinct numerical study before execution. Report all
  frozen scenarios, never choose among them using evaluation error.

The third workflow is deferred; no new fit or solver call is made here. The
separate [source-matched TMD2+IGS reproduction](../../../docs/benchmarks/kfs-tmd2-research-range-v1/README.md)
avoids these disputed specimens and uses its own published nominal state. It
does not establish equivalence to the base-VW96 partial-fit panel.

## Audited artifact and reproduction

[States](states.json) provide 22 explicit named initialization assignments: two
scenarios for each of the eleven allocated development tests. This is initial
metadata, not an executable loading deck. The archived base-law definitions bind
sigma and e; the DP transient multiplier is zero. No fabric or additional memory
is inferred, and these states cannot initialize IGS, SANISAND or Terra Cotta.

[Audit](audit.py) first validates allocation/parameter metadata, then verifies
exact input, source and snapshot hashes. Whole experiment files are hashed and
decoded; response rows are not analyzed or exported. Checks retain exactly the
three changed void ratios, unchanged stresses, original/later source-register
agreement, declared test roles and supported archived state layout. Reserved
numerical files are never opened.

Run from the repository root with a fresh output path and the existing private
source/snapshots available:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 studies/kfs-development-v1/initialization-v1/audit.py --output /private/tmp/kfs-initialization-replay.json
```

[Freeze](freeze.json) binds the policy and audit before metadata generation.
[Execution receipt](execution.json), [stdout](execution.stdout) and
[stderr](execution.stderr) retain the successful first run; exact deterministic
replay is verified. No fit, build, model execution, manuscript edit or scientific
promotion occurs. Independent review and provider clarification remain open.
