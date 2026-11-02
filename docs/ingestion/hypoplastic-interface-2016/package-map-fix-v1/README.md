# Receipt-sidecar registration for normal packaging

Source-only specialist `/root/hill_interface`; 2026-11-02. This fixes metadata discovered by the parent's first actual ordinary package run. Its stdout/stderr and prospective package metadata remain retained by the parent. The failure is not recategorized as success, and no package/build/runtime/material/browser command was rerun by this worker.

The existing `catalogue/agent-reviews/source-archive-map.json` sidecar requires the exact calling document to be listed in `documents` before any supporting receipt is checked. The new accepted E5 review is byte-exact, but its document pin was absent. Consequently all 97 supporting `checked_receipt` calls failed at document registration before evaluating their original expected artifact digests.

The isolated old sidecar was first archived at the canonical path:

`catalogue/source-snapshots/13cf65684c64fb3dd15d7043fdd26a6f87abbd5f196a99a15c6da25e11284aad/catalogue/agent-reviews/source-archive-map.json`

Its original bytes match parent commit `e6f734d5988d941776995bd48900c1a9b230fec2`. Atomic replacement then added only:

```json
"catalogue/agent-reviews/hvwe2016-reconciled-fixed-local-agent-v1.json": "13aa0f267736a9a5ad246e34461ead944fea5aa052ee74d2cec0ab3426a8ee0b"
```

All 23 pre-existing document pins and 18 archive entries remain unchanged. The new sidecar SHA-256 is `8f80339c5f89f39c18f228a013300477ed4c9536ef2795e6760bc85727d5ede0`. `check-results.json` retains all 97 original failures and all 97 successful normal receipt resolutions after the fix. No expected artifact hash was changed or recomputed into a replacement pin. The model, E5 record, approval, qualified executable source and all 209 original source-commit entries are unchanged, confirmed separately in `protected-source-check.json`.

`fix_and_check.py` performs the narrowly scoped atomic operation and source receipt checks. It deliberately refuses a repeated application; it is retained as the action record, not an idempotent maintenance utility. Root shared maps were not touched. The only isolated original-source change is the sidecar; its canonical exact-byte preimage is additive.

The additive commit inventory targets parent `e6f734d5988d941776995bd48900c1a9b230fec2` and new owned ref `refs/heads/delivery/interface2016-v2`. Its whitelist consists of the sidecar, canonical preimage and this source-fix evidence. Copy the listed evidence to the same relative isolated paths before invoking the guarded script. It verifies every source byte, the fixed parent ref, and real HEAD/index before creating its alternate-index commit. It never updates HEAD/main/the real index or pushes. Default invocation is read-only; only the parent may invoke `--execute` after independent review:

```sh
python3 docs/ingestion/hypoplastic-interface-2016/package-map-fix-v1/create_commit.py --inventory docs/ingestion/hypoplastic-interface-2016/package-map-fix-v1/inventory.json
```

The inventory and execution result themselves are deferred to a later evidence closeout, avoiding recursive self-hashes. Parent owns the next package run and all remaining E7/E8 work. This task claims source metadata repair only.
