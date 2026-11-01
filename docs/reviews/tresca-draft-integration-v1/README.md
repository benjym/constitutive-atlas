# Tresca local draft integration v1

Completed 2026-11-01, scoped to IMPL-tresca-draft-integration-v1. The atlas now contains **ten executable models** (four transcribed, six draft); all **19 source reviews remain pending**. Tresca is a total-stress draft, with no pore-pressure law, soil calibration, experimental validation or independent scientific admission.

- [X] Install the exact source-bound proposal (`19acebed37d59120e49c5dff698e2b7d2a2693bbce9ec35c8bcbc65954819e18`), retaining the distinct generic Tresca discovery entry.
- [X] Register the byte-identical pending unsigned review and separate bounded numerical evidence.
- [X] Retain [mixed ten-model native/Wasm qualification](../../../catalogue/investigations/tresca-mixed-catalogue-v1/README.md). Reuse its hash-verified Wasm; no compilation in this integration task.
- [X] Extend applicability with an explicitly unassessed total-stress row; package ten models under the Pages project prefix.
- [X] Check all ten packaged default runs (101 points each) with the scope-aware website consumer.
- [X] Exercise the actual browser: full state, nonzero plastic strain, reversal, export/import, invalid-state rejection, forced failure/committed-prefix retention, recovery, source review, total-stress plots and unavailable pore pressure. Fix and retest reload form restoration.
- [X] Deliver canonical dossiers byte-for-byte plus escaped readable HTML views; preserve source hyperlinks, pending-review status and scoped evidence separately.

`package-inventory.json` records every delivered asset, exact reused engine hashes and source asset identity. `package-check.json` retains the ten numerical smoke results. `browser/` contains actual downloaded JSON, accessibility observations and screenshots; `observations.json` records scope, corrected failures and limits. The original Markdown viewer block, missing-applicability package rejection, old export-test expectation and form restoration problem remain described; no numerical acceptance gate was relaxed. Archive plans/results preserve exact prior bytes and document-specific receipts.

Focused checks: 57 Python tests and eight Node tests pass; process output is retained. Existing SQLite ResourceWarnings remain visible. Replay saved evidence without building or running compiled code:

```sh
python3 -B docs/reviews/tresca-draft-integration-v1/verify.py
```

The browser check used `http://127.0.0.1:8948/constitutive-atlas/`; this is a local delivery, not a deployment receipt. Source review remains unsigned and unassigned. Stop here: the next research work returns to roadmap source/admission priorities (including SANISAND and Terra Cotta), rather than expanding Tresca fits or numerical scope.
