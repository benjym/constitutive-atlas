# Kelvin release source-binding audit v1

AUDIT-kelvin-release-bindings-v1. Read-only baseline `b529a0efc3415b2bc567178a68174575c220cadc`; source/map installation belongs to the coordinator. No shared source, receipt, map, index, Git state, compiled artifact or model approval was changed by this audit.

The final recommendation is **[plan.json](plan.json)** and **scope-v2-planned-sidecars/**: 33 original source/receipt pairs, 29 reverse map/receipt pairs, 14 additive sidecars and 18 canonical prior-byte snapshots. Publication graph `catalogue/publications.json` is unchanged and excluded from scope. The routing fixture `tests/test_j2_main_routing.mjs` is included, with its exact baseline hash. Board own rows remain a planned change. ROADMAP.md and docs/STATUS.md have no currently-live source pair requiring a new redirect; older archived or unresolved pairs remain historical.

[virtual-check-scope-v2.json](virtual-check-scope-v2.json) simulates replacement of all scoped source bytes and the exact proposed maps. All **14,360 previously resolved active pairs** still resolve their original expected hashes, with **zero new failures**. Existing map entries and document bindings remain unchanged. This is an integrity simulation, not a build, numerical/browser check, approval or installation witness. Actual parent integration should replay saved checks after installing the reviewed exact delta.

[own-interface-plan.json](own-interface-plan.json) separately preserves the new Kelvin interface v1 freeze and runtime-test manifest: two new document-bound maps and one exact prior laboratory snapshot, recovered from interface-v2/prior/web/kelvin-voigt-laboratory.mjs with hash18aae46c…. INITIAL_REVIEW.md remains unchanged prose and needs no JSON source redirect. The original runtime-test manifest also includes an absolute private/tmp app.js path: atlas.evidence rejects absolute source paths, so this existing receipt must not be silently described as fully portable. The v1 laboratory relative pair is preserved without rewriting that historical manifest. Proposed maps are under own-interface-planned-sidecars/.

The scan uses committed Git blob identity. Extracted bytes are accepted only when their Git object hash matches the baseline; otherwise `git show` supplies exact original bytes. It recognizes recursive direct path/hash maps and path/sha256 or path/hash objects, with original_path objects distinguished as metadata rather than checked_receipt input. Existing archival resolution is respected. Raw exploratory inventory includes copied context/receipt trees for visibility; final scope excludes their immutable local namespaces, canonical snapshots and frozen-source subtrees. These copies retain their enclosing evidence's original identities and must not receive live-root map edits. Namespace markers and exact exclusions are reproducible in minimal_scope_v2.py. JSON embedded inside encoded payload strings is not decoded.

The first broad exploration and first virtual failure are retained. The broad exploration would alter copied contexts and is superseded; **do not apply planned-sidecars.tar.gz or minimal-planned-sidecars.tar.gz**. The first virtual failure demonstrated that a newly created sidecar introduces a document guard for every sibling receipt. Final new sidecars therefore register all unchanged sibling JSON documents; existing sidecars retain old bindings and add required ones. The corrected prospective simulation passes unchanged source/hash gates.

Coordinator installation plan, after independent review:

1. For each plan.json canonical_archives row, obtain original_path bytes from `git show b529a0efc3415b2bc567178a68174575c220cadc:<original_path>`, verify sha256, and write the exact bytes to archived_path in the isolated release tree. Refuse corrupt/conflicting existing snapshots.
2. Verify each existing destination sidecar still matches its baseline_sha256. Copy only the fourteen named files from scope-v2-planned-sidecars/ into that isolated tree, verifying proposed_sha256. All sibling receipt bytes and expected source hashes stay unchanged.
3. Install the own-interface plan's one prior laboratory snapshot and two new maps after verifying their exact source/document/map hashes. Do not change either original v1 receipt or the old review prose.
4. Apply only authorized Kelvin source/catalogue/router-fixture/tracking deltas, then run repository archive coverage and affected saved-evidence checks. If the baseline or source delta changes, re-inventory first; no overwrite of concurrent root maps is authorized by these proposals.

Reproduction from repository root (analytical/read-only inspection only; output stays in this audit directory):

```sh
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/scan.py --commit b529a0ef --tree /private/tmp/atlas-kelvin-voigt-delivery-v1/release-source --output docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/add_router_scope.py
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/minimal_scope_v2.py
python3 -B docs/ingestion/kelvin-voigt-comsol63/release-bindings-v1/verify_scope_v2.py
```

Original large inventories are retained byte-for-byte compressed as inventory.json.gz, inventory-scope-v2.json.gz and minimal-inventory.json.gz. compressed-evidence.json pins original and compressed identities; scripts accept these compressed inputs. Fresh reproduction writes uncompressed outputs but does not install any proposal. The final reviewable plan omits repetitive full copied-edge payloads; raw inventory retains them. The audit manifest pins every delivered file except itself.
