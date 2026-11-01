# Preservation proposal v2 — not applied

This revision merges all 24 recovered historical raw-response bindings and the exact original saved-wasm-legacy-check-results.json document pin into the prospective fused-linear-v1 independent-review sidecar. The 33 other legacy raw responses retain their original live hashes. All 57 current full-campaign raw responses remain unchanged. No numerical acceptance is inferred.

The entire original proposal is preserved exactly under prior-v1/ and indexed by PRESERVED_V1.json. No original plan, candidate, receipt, freeze, production map or source was rewritten. The 24 recovered canonical snapshots already exist in production and are not additional apply writes.

Recomputing the transitive closure against current production detects concurrent ordinary-model deeplink preservation work. Two Barodesy sidecars already equal the v1 candidates and require no write. The current Duncan–Chang sidecar includes three additional entries, which are retained. Its current bytes and a consumer sidecar in docs/reviews/ordinary-model-deeplinks-v1/ also require archival. The result is 20 candidate sidecars (5 replacements, 15 creations) and 6 new canonical snapshots: 26 exact production paths in APPLY_WHITELIST.json. Every replacement has an exact current old hash; every creation requires absence. Recheck these immediately before any later reviewed application. The solver installation remains a separate gated action.

Checks: compute_current.py rescans live docs/catalogue JSON, excludes canonical snapshots and this entire prospective proposal context, and computes the fixed-point preservation closure. Its CURRENT_BASE.json retains 62 obligations and 94 recognized existing candidate-map bindings. plan_revision.py rechecks those 156 bindings plus all 62 original saved-checker pins using the current atlas.evidence.checked_receipt in a temporary future-source overlay: 218 passing checks. All 57 live full-response hashes also match RECOVERY.json. Baseline saved-checker verification has exactly 24 expected failures before the proposed sidecar. New records use original_path/old_sha256 to avoid becoming accidental receipt pairs.

To reproduce from this frozen proposal, run:

```
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/profile-install-v1/revision-v2/plan_revision.py
```

This uses the retained CURRENT_BASE.json and candidates and refuses detected production map drift. To start a distinct fresh proposal, recompute using compute_current.py into a new revision; do not overwrite frozen v2 records. No compiled code, material calls, browser, build, model changes, production writes or independent approval occurred.
