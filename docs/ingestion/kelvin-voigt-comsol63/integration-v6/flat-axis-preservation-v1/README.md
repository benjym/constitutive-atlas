# Pre-axis-fix merged app preservation

The coordinator requested a presentation-only shared axisRange correction after observing that tiny held-stress roundoff expanded to full chart height. This source-only task preserves the exact current merged app before that change. It does not change app bytes, numerical results, controls, model, acceptance gates or original receipts.

The canonical archive preserves app SHA256 a989a23c5cdc19c4d02a9b28c5f051ee77795e6983d246e0627068acd0f48ab7. New document-bound sidecars preserve the package-v3/freeze.json and integration-v5/merge-receipt.json app references; each map registers every existing sibling JSON. A scan of active model-local receipts found exactly these two matching current-app pins. Original hashes remain unchanged.

receipt.json records exact installed paths and original document hashes. Both app bindings resolve to the archive; the installation file manifest replays, and all14 pure archive tests pass. package-v3 retains its historical prospective identity; preservation does not assert compiled observation or package acceptance. The coordinator may now change the app under a fresh source/package identity.
