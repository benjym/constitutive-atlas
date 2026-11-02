# Cleanup-status successor to accepted ledger proposal v2

Source-only v3, not applied. Accepted v2 (review4c91b599) and all92 manifest files remain byte-exact. Only the DELIVERY cleanup paragraph and CHECKLIST cleanup bullets changed; prefixes/suffixes outside those ranges were checked byte-identical. E0–E7 accepted exactdcc6457 evidence, E8 pending/new106a9cf8 Perzyna source composition, candidate/E5 and publication scope remain unchanged.

The new five cleanup-v3 receipts bind actual archive creation, streaming verification, exact1,546-entry bytes/modes/nanosecond-mtime recovery, empty immediate consumer checks and completed unlink-only removal of failedsite1/guardcopies. Archive SHA-256a70787d63a3f4cf026dfd612911d8cdd68b48096aaa570c0eab2ea4301c35fe8 is243,000,472 bytes in durable ignored evidence. Observed free increase1,105,551,360 bytes was measured after the archive existed and can include concurrent disk effects. Original replay source/native/wasm, em-cache, currentrelease-v2/site-v2, private originals, qualified artifacts and all failure receipts remain retained. The worker read receipts only; it did not execute archive/recovery/deletion.

Fresh owned-packet scan again finds5actual ledger consumers including package-v2/run.json (216pins),4additive sidecars and27existing sibling JSON document pins. Proposal simulation resolves all10old-ledger receipt pairs to exact canonical predecessor bytes after simulated replacement. Old ledgers/decisions and all live maps remain unchanged. Prior proposals/simulation copies are excluded from the actual-consumer scan. Future sibling receipts require explicit registration.

Current artifacts: preservation-proposal.json, proposed-maps/, proposal-check-results.json, simulation/, evidence-checkpoint.json, minimal-change-check.json, install-plan.json and two successor drafts. The guarded installer is identical to v2; the plan now pins the new cleanup receipts, v2 accepted decision and new drafts/results. Default read-only preflight passed; --apply was NOT executed.

After independent v3 review, coordinator only:

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/ledger-update-v3/install_reviewed_successors.py
# After accepted review; retain complete stdout/stderr:
python3 -B docs/ingestion/hypoplastic-interface-2016/ledger-update-v3/install_reviewed_successors.py --apply
```

Archives precede maps, maps precede ledgers; original receipt resolution is checked before/after. Guarded replacements are atomic per file, not a whole multi-file transaction. A partial failure requires inspection and preserved output, never blind repinning. Scope is root's two predecessor snapshots, four additive sidecars and two ledgers. No isolated qualified source/site, Git, package, browser, compiler/material or remote mutation occurs. E8 remains coordinator work.
