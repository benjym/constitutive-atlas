# Prospective profile-source preservation plan

PRESERVE-lade-qualified-profile-v1; nonmutating implementation by /root/lade_interface_review. No production sidecar, source, evidence, Maxwell record/helper, compiled artifact or frozen manifest was edited. The proposed F profile was used only as temporary overlay bytes; it was not installed. This handoff requires exact independent review before coordinator application and full scientific gates before any later source replacement.

The old solver SHA256 is 098e1b926e3eb99545567111415f54d35c08f52e7afbaa796fa23a551fe4a6c0. The future exact copy SHA256 is e2e517d9cb5a90383779d4d26eed66284b774d3646d1f74149541589f6ac1026. The one canonical old solver target is:

```text
catalogue/source-snapshots/098e1b926e3eb99545567111415f54d35c08f52e7afbaa796fa23a551fe4a6c0/cpp/profiles/implicit-path-v1/include/atlas/solver.hpp
```

The fixed point contains five old pairs: that solver and four changed existing source-archive-map.json files. Each existing map's original bytes are queued exactly once; their consumers receive their own sidecar proposals. There are 20 candidate maps: four existing maps gain entries/document pins and 16 new maps are proposed. Existing map content, entries and document pins are retained; there are no ambiguous or incompatible existing entries. Every candidate entry has the canonical catalogue/source-snapshots/<oldhash>/<originalpath> location. No duplicate archive trees are proposed.

PLAN.json gives every exact old/new map hash, document pin, archive path, transitive obligation and result. APPLY_WHITELIST.json is the smallest exact write-path proposal: 20 map files and five canonical old-byte snapshots. It lists the later solver copy as a separately gated operation, not part of metadata-preservation authorization. candidates/ contains the exact 20 map proposals; snapshots/ contains each of the five canonical old-byte destinations, rooted inside this owned context; prior-map-bytes/ retains the four original map files; receipt-bytes/ retains every original receipt participating in the 32 obligations. Unchanged receipt files must not be repinned or replaced.

The four existing map targets requiring exact-byte archival before application are:

- docs/ingestion/duncan-chang-1970/integration-v2/independent-review/source-archive-map.json
- docs/ingestion/lade-duncan-1975/atlas-integration-v1/source-archive-map.json
- docs/ingestion/maxwell-itasca900/atlas-ci-regression-v1/independent-review/final-v1/source-archive-map.json
- docs/reviews/common-scalar-functions-v1/dependent-independent-review/source-archive-map.json

## Scan and verification

The scanner reads all parseable docs/ and catalogue/ JSON outside this new prospective context and the central canonical snapshot target tree. It recursively recognizes exactly the current checked_receipt forms: a dict key equal to an original path whose value is its expected hash, or a dict with path plus sha256/hash. A source-archive-map's own recognized pairs are included when they actually reference a queued old source/map pair. Existing maps are preserved transitively, including consumer receipts that share the same candidate sidecar.

catalogue/source-snapshots/** is scanned as an archive target when needed, not a new receipt namespace. Its JSON bytes are historical source targets already reached through original receipt document identities. Treating them as new document identities would create nested canonical archive trees and does not preserve the original checked_receipt contract. Historical receipt copies elsewhere under docs/ remain included. The exact scan counts and ten preexisting nonparseable JSON files are retained in PLAN.json; none of those ten files mentions the old profile pair and none can be a checked_receipt JSON document as-is.

The actual current atlas.evidence.checked_receipt is used without modification, first against live baseline receipts, then against a temporary overlay containing the future solver, candidate maps, exact original documents and canonical old-byte snapshots. All 32 affected receipt obligations pass in that overlay. All 52 recognized entry bindings from documents pinned by candidate maps also pass, preserving unrelated existing map entries. No unsupported/corrupt/ambiguous candidate or document-pin mismatch remains. This is bounded verification of the affected preservation closure, not a claim that every unrelated repository receipt passes.

Four live baseline checks fail because existing sidecars omit the relevant original document pin (the error message says "original evidence document changed after archival" even for an absent pin): installed-source-receipt.json; post-package-install-bindings-v1.json for the solver and its same-parent map; and dossier-correction-v1.json for its same-parent map. Their exact bytes and hashes are retained. Candidates add those original-byte document pins; no existing document pin is changed. PLAN.json retains each baseline failure separately from the passing overlay result.

The planner aborts on concurrent changes to any scanned original JSON receipt, existing candidate map or old source bytes. Prospective report records use original_path/old_sha256 and original_document/old_document_sha256, preventing the plan's descriptions from masquerading as new source receipts. Actual map candidates retain the required checker schema. This new context is excluded from future planning scans to avoid prospective self-dependency.

Reproduce from repository root:

```sh
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/profile-install-v1/plan_preservation.py
```

The command reads JSON/source bytes, writes proposals only inside this directory and runs Python receipt checks in a temporary owned overlay. It performs no build, material, browser, remote action or production update. Candidate maps, snapshots and exact plan/report hashes are frozen in SOURCE_FREEZE.json. SOURCE_PINS.json binds the planner's governing checker and source inputs without changing any historical receipt.

## Coordinator handoff

Review APPLY_WHITELIST.json and exact candidate bytes with a separate agent. Immediately before application, check that original map/receipt/source hashes still match PLAN.json; otherwise regenerate under a new reviewed identity rather than forcing stale candidates. Copy canonical snapshots first without replacing existing different bytes, then install reviewed candidate sidecars. Re-run affected current checked_receipt checks. Only after scientific qualification and the separate installation authorization should the solver receive the exact F copy; then repeat the bounded receipt checks against the real tree. This task does not authorize any application or Maxwell qualification rebind.
