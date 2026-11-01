# KFS current-TMD7 private evidence retention

The existing current-source TMD7 comparison and its archived baseline are retained durably under ignored `.local/private-evidence/kfs-current-tmd7-v1/`. [Receipts](receipts.json) bind every copied byte to its original path and SHA-256: 93 current files, 91 baseline files, 34 direct root inputs, six governing files and the current engine. Original files, policies, paths and numerical reports are unchanged. Retained executable bytes have no execute permissions and were not invoked.

Run from the repository root:

```sh
python3 -B docs/benchmarks/kfs-private-retention-v1/verify.py
```

Use `--private-root PATH` for a securely transferred copy. The checker needs no original temporary directory, measurement parser, solver or network. It checks retention integrity, not scientific correctness or numerical reproduction.

Only this metadata and checker are public. Measurements, predictions, process responses, binaries and source snapshots remain private. Retention grants no data/code redistribution permission. A public clone cannot perform this private audit without the assets.

This closes temporary-storage risk for the named TMD7 inputs/outputs, not the whole KFS development campaign. The original saved-data auditor still depends on its pinned source/import closure and historical absolute paths; full portable replay remains separate. Archived source/build association, specimen-state disagreement, original failed refinement, experimental validity and data rights remain unresolved as recorded in the original packets. No fit, build, material call, new experiment or deployment was performed.
