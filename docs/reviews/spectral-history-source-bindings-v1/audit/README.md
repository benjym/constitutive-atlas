# History-only source bindings and reverse-map closure v1

2026-10-31. Read-only follow-up to the staged spectral code review's history phase-guard fix. Target ONLY `atlas/history.py`. No shared edits, archives, builds, commits or replay. original-scan.py preserves the inherited normalized-determinant scanner byte-for-byte; scan.py changes only TARGETS to this one path. Scope/exclusions/primary shapes are otherwise unchanged. Parent alone owns archival/integration.

## Exact current binding plan

Current history.py SHA256 is `1ae77baaf0f5fd30b6e9ff3c8043795e21ae0b83ceac0388627c45986969f28a`. The scan reads1615 non-snapshot JSON files, excludes658 frozen/snapshot files, and finds30 primary document/source/hash pairs across30 documents. All30 equal the current history hash and resolve live. There are no historical unresolved primary history pairs in this declared scope. This is not a claim about the other sources' pre-existing historical gaps.

Before editing history.py, archive its exact bytes and bind all30 immutable primary documents. Unlike the earlier four-file archival, this requires an actual reverse-map closure: one sibling map to be extended is `catalogue/investigations/gis2024-hp-host-v1/source-archive-map.json`, whose current bytes are directly live-bound by five other immutable documents. Archive those map bytes before mutation and register those five documents against the original map hash `7196eaeda3339b65dafcdd1c64b3517602383999ddbb09a59dfac9efb41e36e0`:

- catalogue/investigations/barodesy2017-hydro-ad-v1/source-migration-inventory.json
- catalogue/investigations/barodesy2017-integration-v1/source-migration-inventory.json
- catalogue/investigations/barodesy2017-wider-reference-v1/source-migration-inventory.json
- catalogue/investigations/symmetric-expm-v1/manifest.json
- catalogue/investigations/symmetric-expm-v1/study-review/reviewed-manifest.json

plan.json is the exact actionable result:35 document/source pairs across35 documents and35 existing maps to extend, each with original document SHA, source path/hash, canonical archive destination, existing document-pin state and pre-append map identity. No existing document pin mismatch was found. All35 map paths already exist; no new map file is needed. Preserve their exact bytes first. source-bytes/ contains36 verified immutable byte snapshots:history.py and all35 existing maps. These staging copies are not registered archives by themselves.

## Inherited scanner limitation and independent closure

inventory.json preserves the original scanner result:30 initial sibling maps; a conservative33-map closure and36 secondary attention rows. That scanner propagates reverse edges only when the referencing document itself is named source-archive-map.json. It therefore does not completely model the necessary `live receipt document -> that document's sibling map` mutation edges.

plan.py independently starts with the30 initial sibling maps. For every secondary primary-syntax source-map reference that resolves live and points to a map being changed, it records the original document/source/hash and adds that document's sibling map. It iterates to a fixed point. This adds five maps, including two that the inherited closure missed:

- catalogue/investigations/symmetric-expm-v1/source-archive-map.json
- catalogue/investigations/symmetric-expm-v1/study-review/source-archive-map.json

The other three are the Barodesy sibling maps listed above. This yields35 maps. Existing archived edges need no new binding/mutation because checked_receipt already selects exact old snapshot bytes. Descriptive original_path entries are tracked separately and must not be mistaken for live primary receipt documents requiring sidecar additions. The old scanner is preserved, not silently rewritten to claim it had this stronger closure.

Within the minimal35-map set there are58 secondary reference rows:12 archived primary-syntax,37 archived descriptive sidecar-entry references,5 live primary-syntax,4 live descriptive entries. Only the five live primary-syntax rows generate additional document bindings. Archiving the GIS map's exact original bytes also preserves resolution for the four descriptive entries without rewriting the descriptive audit documents. Every pre-append map byte is staged even if no current reverse binding needs it; later evidence must retain its original identity.

## Existing contextual secondary diagnostics

The full secondary inventory has432 pairs:106 archived,230 archived-sidecar entries,51 live,42 live-sidecar entries,3 root-relative unresolved. These three concern the same `frozen-sources/docs/ingestion/hypoplastic-clay-2005/determinant-input-rounding-v1/source-archive-map.json` identity:

1. The original clay2005-homogeneous-rates-v1/manifest.json uses a packet-local frozen-sources path. Exact matching bytes exist below its own packet directory; it is not missing source data.
2. Two prior spectral binding audit inventories describe that contextual source using original_path rows. checked_receipt does not treat those descriptive objects as primary receipts, and their literal path is not repository-root relative.

Those original scanner statuses/errors remain unchanged in inventory.json and plan.json. They are outside the mutable35-map root-relative closure. Do not amend old audit documents or force these local/descriptive paths into primary receipt syntax to obtain an all-resolved summary.

## Strongest next action and checks

Coordinator should archive the36 staged byte identities at their exact canonical content-addressed locations, append the35 exact document/source bindings to their existing maps while preserving all existing content and document pins, then verify all35 original document/source pairs through checked_receipt. Also rerun the secondary closure and confirm already-archived edges still select their original bytes. Only then edit shared history.py. Preserve this pre-change inventory; post-archive verification needs a separate result identity.

Reproduction:

```
python3 -B scan.py /Users/bmar5496/code/constitutive-atlas --output fresh-inventory.json
python3 -B plan.py
```

plan.py has explicit repository/staging paths; adjust intentionally for a different checkout. Inherited scanner source is unchanged except for the target set. Extraction is recursive direct exact path->lowercase64hex or {path,sha256/hash}; snapshots/frozen source trees, source-map sidecars as primary receipts and JSON encoded inside payload strings remain excluded. Secondary scan recognizes source-map paths and descriptive original_path objects. Python bytecode writes were disabled. No author or compiled code executed.

A single-file identity archive is not an execution closure. Any future history replay must materialize the exact original package/data/schema/entrypoint layout with all explicit document-bound dependencies and original expected output; importing archived history.py against revised DSL dependencies is not historical reproduction. This task performed no replay and makes no numerical/scientific admission claim.
