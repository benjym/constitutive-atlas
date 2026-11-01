# Shared-hook preservation revision v2: uncovered concurrent receipt

The frozen metadata plan is not yet accepted. An independent scan of immutable JSON consumers found two additional bindings in `docs/ingestion/barodesy-clay-2017/browser-current-v3/independent-review/inputs.json` (SHA-256 `ee7ff1a4bfe5cbee7b4e6ce7b8605a25d8ce7eb57dc67a65767db2a270b1e465`):

- `web/app.js`: `59678da9584090ca55171757c55398820430cdc6cdbcee4826cff410df02f552`.
- `catalogue/approved-models.json`: `7abba1ef96a7abf5886712d786fce5cb99e8c6604e5a4c551584654b61010fd0`.

That receipt's directory currently has no `source-archive-map.json`, and neither obligation occurs in the frozen plan's 103 simulated obligations. Both currently valid live bindings would fail after the named source replacements without an added exact receipt-bound sidecar. This is new concurrent coverage, not permission to alter Barodesy evidence or repair unrelated historical failures.

Smallest next action: retain exact revision-v2 bytes and create a new additive preservation revision including this consumer, its peer document pins, canonical old source pairs and any transitive map consumers. Refresh the whitelist/freeze, then independently recheck the revised overlay. The seven actual source replacements remain separately owned and separately reviewed; the current proposal leaves two replacement byte hashes unspecified and cannot authorize installing those sources.

The 60 recorded unrelated preexisting peer failures remain failures. Their existence is not itself a new blocker to preserving previously valid bindings, and none should be rewritten or waived. Remaining frozen metadata/overlay checks are being independently replayed in `check_preservation.py`, which writes only this review directory and performs no builds or material calls.
