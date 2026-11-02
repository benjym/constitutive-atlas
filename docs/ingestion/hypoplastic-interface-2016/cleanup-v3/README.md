# Verified retention and removal

The failed standard package-v1 and source-only guard copies were retained in one private, ignored lossless PAX/gzip archive before their temporary trees were removed. No source, numerical threshold, failure log or independent decision changed.

Archive: `.local/private-evidence/hypoplastic-interface-2016/cleanup-v3/a70787d63a3f4cf026dfd612911d8cdd68b48096aaa570c0eab2ea4301c35fe8.tar.gz` (243,000,472 bytes). SHA-256 is the filename stem. `../cleanup-v2/recovery-inventory.json` is the exact 1,546-entry path, content, mode and nanosecond-mtime restoration inventory (SHA-256 `da775677a5eb9ebc80fe2c77fd58c1d1ec9e1047c3213b43ec02418b994b61d7`). The archive has top-level `site-v1/` and `source-guard-checks-v1/` only.

`archive-stream-verification.json` records complete member/content/mode checks using `../cleanup-v2/verify_recovery_archive.py`. `recovery-drill.json` records an actual separate reconstruction of every file and directory, exact SHA-256/mode/nanosecond-mtime checks, and removal of only the verified disposable reconstruction. Reapply inventory nanosecond mtimes after ordinary PAX extraction when exact restoration metadata is required. Do not substitute a regenerated website for these retained failed bytes.

Immediately before unlink-only removal, complete filtered process and `lsof +D` checks found no consumers of either exact owned tree. Current membership/content were rechecked against the inventory; the archive hash was reverified. `removal-receipt.json` records removal and observed free-space increase 1,105,551,360 bytes, measured after the archive already existed. Concurrent disk activity limits attribution of this observation.

Current qualified release-v2/site-v2, original source/native/wasm replay paths, em-cache, private source originals, durable qualified artifacts and original failure/review receipts remain retained. Other tasks' assets and the paper tree were untouched.
