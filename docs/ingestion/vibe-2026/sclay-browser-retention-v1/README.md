# Historical S-CLAY1 browser screenshot retention

An inherited full-CI failure was reproduced with the unchanged `test_local_packet_receipts`: five tracked PNG screenshots under the S-CLAY1 ingestion tree violate its existing source-binary prohibition. This task relocates only those images into canonical content-addressed `catalogue/source-snapshots/<SHA256>/<original-repo-path>` locations. It neither changes that test nor removes its binary restriction.

`plan-v1.json` froze all five names, hashes, sizes, original manifest identity, consumer audit and recovery policy before relocation. All five archives were byte-compared and SHA-verified before any original was removed; the before-removal receipt records that sequence. The original browser manifest, command records, scientific model, source/E5/E7 documents and all other tracked S-CLAY1 files are unchanged. The sole new file in the historical browser folder is `RETENTION.md`, linking its original relative keys to exact retained images and this receipt/resolver.

Consumer inspection found screenshot hash pins only in the original browser manifest's folder-relative `screenshots/*.png` keys. Integration scoped-changes contains original path strings, and original browser commands record their output/playwright capture provenance. No automated screenshot reader or source/E5 direct screenshot pin was found. The existing browser export checker reads request/result JSON, not screenshots. Adding full-path entries to the agent-review archive map would not resolve this folder-relative manifest; the generic resolver and all maps remain unchanged.

The new pure `retention.py` verifies the frozen plan identity, exact original browser-manifest SHA and all five original relative screenshot/hash pairs, enforces canonical full-original-path archives, checks PNG signature, size and SHA, and provides explicit historical relative-key resolution. Its verification recovers all five original PNG bytes into a new temporary fixture, checks exact equality and removes that fixture. Unknown keys are rejected. The retained screenshots are historical UI evidence, not equation inputs or new scientific/browser qualification.

Checks:

```
python3 -B docs/ingestion/vibe-2026/sclay-browser-retention-v1/retention.py
python3 -B -m unittest tests.test_ingestion_packets.IngestionPackets.test_local_packet_receipts -v
```

The original targeted failure is retained in `baseline-test-v1.log`; the same unchanged test passes afterward in `after-test-v1.log`. Five files / 572358 bytes are losslessly recoverable in `recovery-receipt-v1.json`. Original removal is relocation, with zero bytes discarded and no net storage-reclamation claim. No build, native/Wasm/module/material/browser/remote/commit action occurred. Recovery temporary resources were removed; original archived evidence remains durable. Independent preservation review and coordinator integration are still required.
