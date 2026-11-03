# Retained browser screenshots

The unchanged [browser manifest](manifest.json) records five screenshots using historical relative keys. Their original PNG bytes are now retained in canonical source snapshots so the ingestion packet satisfies its unchanged source-binary guard. The images document the historical UI; this relocation changes no model, scientific approval or browser result.

See the [retention receipt](../../../vibe-2026/sclay-browser-retention-v1/recovery-receipt-v1.json) and [pure relative-pin resolver](../../../vibe-2026/sclay-browser-retention-v1/retention.py). The resolver verifies the exact original manifest SHA, its five relative keys and hashes, and every canonical archive byte. Generic `checked_receipt` does not resolve this manifest’s folder-relative keys; no ineffective global map entries were added.

Exact original images:

- `screenshots/drained-desktop.png`: [retained PNG](../../../../../catalogue/source-snapshots/8bcc11bad1fd2680279119b616ff092b00a255643b1b92cee869673d889c5cd1/docs/ingestion/s-clay1/supplied-original-v3/browser-v1/screenshots/drained-desktop.png), SHA-256 `8bcc11bad1fd2680279119b616ff092b00a255643b1b92cee869673d889c5cd1`.
- `screenshots/final-drained-plots.png`: [retained PNG](../../../../../catalogue/source-snapshots/def4de2ad20a46df28d1c02aa943720cbdf51ed2dbb8170a57f7681e4ee9a325/docs/ingestion/s-clay1/supplied-original-v3/browser-v1/screenshots/final-drained-plots.png), SHA-256 `def4de2ad20a46df28d1c02aa943720cbdf51ed2dbb8170a57f7681e4ee9a325`.
- `screenshots/profile-desktop.png`: [retained PNG](../../../../../catalogue/source-snapshots/18abe282937fea73edaa03b767517121eee0137427099714fedf012219f13675/docs/ingestion/s-clay1/supplied-original-v3/browser-v1/screenshots/profile-desktop.png), SHA-256 `18abe282937fea73edaa03b767517121eee0137427099714fedf012219f13675`.
- `screenshots/profile-mobile-final.png`: [retained PNG](../../../../../catalogue/source-snapshots/b61c9b54f6bdb24fc7d282a68b1971ccd2468038cb471c156bc3b1d8a0fd1b34/docs/ingestion/s-clay1/supplied-original-v3/browser-v1/screenshots/profile-mobile-final.png), SHA-256 `b61c9b54f6bdb24fc7d282a68b1971ccd2468038cb471c156bc3b1d8a0fd1b34`.
- `screenshots/profile-mobile-v4.png`: [retained PNG](../../../../../catalogue/source-snapshots/6cb3271cd99160972cccf3830da66b704658848d32a9170a1c22e046e611f371/docs/ingestion/s-clay1/supplied-original-v3/browser-v1/screenshots/profile-mobile-v4.png), SHA-256 `6cb3271cd99160972cccf3830da66b704658848d32a9170a1c22e046e611f371`.

Run `python3 -B docs/ingestion/vibe-2026/sclay-browser-retention-v1/retention.py` from the repository root to verify and losslessly recover all five images into a temporary fixture that is removed after verification. No image is rendered or browser executed.
