# Shared-hook preservation proposal v1 — not applied

This is a nonmutating preservation implementation, not an independent source acceptance. Exact pending source changes come from hooks-proposed-v1/rebased-v5/PROPOSAL.json (web/app.js, tools/build_web.py, catalogue/manifest.json and catalogue/publications.json) and workflow-v1/PROPOSAL.json (.github/workflows/verify.yml). The sixth source is tools/provision_maxwell_assets.py, whose current f58e3aa0… bytes are preserved; its future narrow provenance edit remains unspecified. No Maxwell replacement hash is invented.

The final scan ran after the coordinator reported successful reviewed profile installation in profile-install-v1/coordinator-install-v1/INSTALLED.json. It reads actual installed source/maps and merges all current map content. It excludes canonical snapshot trees as historical targets, this owned prospective context, and the frozen profile-install prospective context. All other docs/catalogue JSON is searched for exactly the two receipt shapes recognized by current atlas.evidence.checked_receipt: dictionary path-to-hash bindings and path plus sha256/hash fields. New plan metadata uses original_path/old_sha256 to avoid accidental self-dependencies.

The fixed point has 26 source/map pairs and 78 receipt obligations. Twenty existing maps require additive replacements, four maps are new; each replacement preserves the exact current map bytes and enqueues its old pair to discover transitive consumers. There are 26 new canonical snapshots. APPLY_WHITELIST.json therefore enumerates exactly 50 production metadata/archive paths. It excludes the six later source replacements. Every replacement requires its stated current hash; every new path requires absence. Recheck immediately before any future reviewed application. No production file was written.

All original old source bytes, changed old maps, and checked receipt documents are retained under initial-source-bytes/, snapshots/, prior-map-bytes/ and receipt-bytes/. Canonical snapshots have one canonical destination each; no production duplicate tree is proposed. SOURCE_PINS.json binds all live inputs used by the supplementary checker, including the successful profile installation notice. SOURCE_FREEZE.json binds this entire owned deliverable.

Checks: 78 new/transitive obligations and 234 recognized existing candidate-map bindings pass using current checked_receipt in a temporary overlay of the five exact proposed source files. The unspecified Maxwell live source is omitted from that overlay, proving that old bindings resolve through preserved snapshots without assuming replacement bytes. check_overlay.py additionally rechecks all 218 previously verified profile/recovered-raw bindings: 530 checks pass. The installed F source and all existing recovery mappings are retained.

The baseline has three failures caused by missing document pins in existing sidecars, not a differing existing document pin: common-scalar-functions package-installed-v1.json, its independent-review/post-install-bindings-v1.json, and Maxwell atlas-ci-v2/review-inputs-v1.json. Candidate maps add their exact original document pins. No original receipt bytes or expected artifact hashes change. Ten preexisting unparseable JSON files have no replacement source/hash pair mentions; the scan retains their errors and byte hashes in PLAN.json.

Reproduction (pure Python metadata/source processing, no compiled/material calls):

```
python3 -B docs/ingestion/lade-duncan-1975/atlas-integration-v1/shared-hook-install-v1/check_overlay.py
```

The original full fixed-point planner is plan_preservation.py. Do not overwrite this frozen proposal with a new scan after source/map drift: create a distinct revision. Independent source review is required before coordinator application. Source review and scientific/model/browser/package qualification remain separate.
