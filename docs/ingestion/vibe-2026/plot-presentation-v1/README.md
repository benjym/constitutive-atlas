# Shared chart tick presentation

This patch formats finite numeric tick arrays using enough precision to distinguish every distinct tick. It chooses short plain or scientific strings, retaining ordinary short decimal labels. Parsed labels remain within 5% of minimum tick spacing; this is a presentation accuracy check, not a numerical-model tolerance. Seventeen significant digits provide a round-trip fallback. Range-relative near-zero roundoff is rendered as zero without collapsing genuinely small axes.

The shared chart uses these labels for axes only. Its left margin reserves seven SVG units per character plus 24 units; the right edge remains 454 in the existing 480-unit viewBox. Pure tests check positive label clearance at a 315px display width and useful plot width for the frozen cases. Actual font layout and browser rendering require the coordinator's new package/browser check.

`check_projection.py` reverses the added import, chart tick-label/margin lines and one builder copy entry, then compares both complete files to archived preimages. This proves every other byte, including axis-range logic, data handling, kernel/engine routing and previous dependency-hook changes, remains unchanged. The controlled-time laboratory component is untouched. No model-specific branch is introduced.

## Reproduction

```
node --test tests/test_plot_labels.mjs
node --check web/app.js
PYTHONPATH=. python3 docs/ingestion/vibe-2026/plot-presentation-v1/check_projection.py
```

The final pure suite passes 9 groups, including original repeated-label witnesses at stress 5110 and void ratio 0.725; signs, ordinary and tiny scales, subnormals, adjacent representable values, large magnitudes, duplicates, signed zero and invalid inputs. Projection checks pass both complete byte reversals. All 281 original VIBE supporting files pass `checked_receipt` and direct live SHA checks after the separately owned archive-map preservation addition. The support receipt binds the exact map, approval document and registry used.

## Retained attempts and limits

`pure-tests-v1.log` retains the original 8/9 result: the new formatter shortened ordinary 1000 to 1e3 despite the intended plain-label test. `pure-tests-v2.log` retains the identical failure after a shell correction attempt used unavailable `python`; the shell continued to run Node. The implementation now retains plain strings of six characters or fewer, and `pure-tests-v3.log` records 9/9. No test expectation or acceptance tolerance changed. The unavailable-command attempt changed no source.

`scientific-support-baseline-v1.json` retains the pre-edit 0/281 receipt failure caused by missing immutable approval-document entries in the archive map. The coordinator separately preserved and corrected that map with independent review. `scientific-support-after-v1.json` records 281/281 canonical and direct hash successes; no supporting evidence bytes changed.

No builds, real bundlers, compiled modules, material calls, browser calls or remote actions were performed. The coordinator retains the original package3 and screenshots and will repackage and inspect the charts separately. No temporary processes or disposable build trees were created by this task.
