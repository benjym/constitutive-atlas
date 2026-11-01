# Exact archive-aware integrity follow-up

The original direct verifier and manifest remain unchanged. While the packet was being finalized, a separate solver task added correct source-archive redirects for the pinned solver.hpp and the old archive-map bytes. Consequently the original live-path verifier now raises AssertionError on source-archive-map.json. The subsequent local commit still ran after this failure; no successful final direct verification is claimed.

Every original manifest binding resolves exactly through the existing standard checked_receipt mechanism, including the archived original map. The new saved-only verifier changes only the manifest lookup to that standard resolver, retaining all source snapshot, artifact, execution-freeze, reference-result and document checks. It does not repin any original manifest, change a numerical policy/checker/runner or execute binaries.

Run `python3 -B docs/ingestion/barodesy-clay-2017/ncl-laboratory-v1/integrity-followup-v1/verify.py`. The original live-path failure is expected and retained. Independent interface acceptance remains a separate reviewer decision.
