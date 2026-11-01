# Durable private retention of the KFS development campaign

The accepted [independent C1–C7 reporting review](../kfs-development-agent-v1/README.md) identified temporary-only campaign evidence as a reproducibility gap. This follow-up retains **9,423 exact files,158,115,877bytes**, under ignored `.local/private-evidence/kfs-development-campaign-v1/`. It covers all six named calibration/evaluation/locked-initialization/refinement/nested/TMD7 study trees, the complete43file pilot-matched96 directory, the earlier225file TMD7 retention, all254explicit review-bound private inputs and governing review records. Source membership and every original byte were checked again after copying. No original file was moved or modified.

[The prospective inventory](inventory-before.json) and [final receipts](receipts.json) are byte-identical. They publish paths, lengths and SHA256hashes only. Measured rows, predictions, raw process streams, source PDFs, executables and other copied contents remain private. Every retained file has execute permission removed; no retained executable, author code, compiler or material solver was run. This copy supplies no redistribution permission.

From the repository root:

```sh
python3 -B docs/benchmarks/kfs-full-private-retention-v1/verify.py
python3 -B docs/benchmarks/kfs-full-private-retention-v1/check.py --output /private/tmp/kfs-retention-check.json
```

`verify.py --private-root PATH` accepts a transferred private copy. It needs no original temporary directories, numerical imports, solver or network. The [saved audit](check-results.json) verifies every retained file after removing origin fields from verifier input, checks all254original review bindings through the retained binding document, and rejects eight missing/corrupt/unsafe/duplicate/executable/symlink probes. An alternate-root fixture also passes.

This closes temporary-storage risk for these exact named trees and explicit bindings. It does **not** establish a complete historical transitive import/execution closure or portable saved numerical replay: the original auditors still reference historical paths and source imports. Those require a distinct relocation/replay task. Byte retention does not resolve the archived source/build association, specimen-state disagreements, experimental validity or reuse rights. The original failed refinement, separate passing nested study and accepted bounded reporting decision remain unchanged. No new fitting, experiments, numerical qualification, model admission or deployment occurred.

`retain.py` records the one-time capture procedure; it deliberately refuses to replace an existing inventory or destination. Do not rerun it to overwrite this evidence. The public manifest binds this packet; private bytes are governed by the exact receipt list.
