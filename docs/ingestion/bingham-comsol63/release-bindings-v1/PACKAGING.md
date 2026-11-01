# Lossless audit inventory publication

The three broad/current scanner inventories are published as deterministic gzip files, with exact raw and compressed hashes in compressed-audit-receipts.json. Original raw outputs are retained unchanged locally and are ignored solely to avoid publishing116MB of repetitive JSON. All active plans, staging/application manifests, scripts, source snapshots, maps and independent checks remain ordinary files. No scientific source or acceptance gate changes.

Restore each inventory beside its compressed file with `gzip -dk inventory.json.gz` (likewise within fast-v2/ and current-v3/). Verify its raw SHA against the index. The original audit scripts also regenerate raw outputs. Coordinator archival helpers consume the small exact pinned plans and do not require inventory expansion. Independent integration review already resolved the actual73affected receipt bindings; this compressed form does not substitute a different inventory.
