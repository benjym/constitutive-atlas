# Bingham release hash-binding audit v1

Read-only isolated baseline `b529a0efc3415b2bc567178a68174575c220cadc`. All nine target working files matched `git show HEAD:path` before scanning. No shared file, sidecar, historical receipt, schema, compiler, model or git metadata was changed. No build or compiled artifact was executed.

## Exact identities and dependents

Full per-file identities, exact dependent record paths and pins are in `current-v3/plan.json`; JSON pointers and current receipt resolution are in `current-v3/inventory.json`. `logical-plan.json` separates original logical receipt namespaces from retained receipt-byte/context copies. All187 current-hash primary pairs resolved against the isolated root; none is pre-existing unresolved. The wider stock scan also retained historical unresolved mentions; those are not newly caused failures or targets for automatic repair.

| Planned shared file | Base SHA-256 | All current edges | Logical original edges |
|---|---|---:|---:|
| `.github/workflows/verify.yml` | `0afc51708fe23a02da080d472023d10a75cc1aac92537ee84144be1f842809c8` | 8 | 5 |
| `IMPLEMENTATION_PLAN.md` | `0782033a1584911595e20ddad8a4f98e7bf6f490d7c7755379cd0c6db6b29f3f` | 1 | 1 |
| `ROADMAP.md` | `1894d97a8e64c1d23837864358b2eade263b5673b049dd4ee6ca4c2e64859ce6` | 0 | 0 |
| `catalogue/approved-models.json` | `39ab123fb57d8233f60fd174649ce1e921b4b51c9343a7341503582603ac9932` | 8 | 5 |
| `catalogue/manifest.json` | `c37e40404ddab730b163975fbaefcbc8bbdb2dcc62343d67554b0eeab304644e` | 8 | 5 |
| `catalogue/publications.json` | `31992f7dfa3a9b0cd92f1501a7a0872d8090940fcda0fda668ab9422763e1f1a` | 96 | 11 |
| `docs/STATUS.md` | `e1fa55bec7fb6d11232c1f923eec789e2bb26d7ad796a6fc305bad48527f5f6f` | 0 | 0 |
| `tools/build_web.py` | `4e98b1ba8af4bdf51cd7564d8d6628a8d2060bb36ba53f5122727f188ab6856d` | 60 | 8 |
| `web/app.js` | `9612893e73052b905959d47affd535404f355986d27b2088c204857b53b55a4b` | 6 | 5 |

Full conservative current-edge inventory:187primary edges,292ordinary-receipt reverse-map edges,67candidate sibling maps, no existing current document-pin conflict. Those counts include copied records nested in prior preservation/context packets. Applying all67 blindly is not the minimal recommendation: some copied subtrees have owner inventories and are evidence artifacts rather than fresh root receipt identities. Preserve their exact bytes and namespace. The logical plan has 40primary edges, 23reverse-map edges, 11maps. Its explicit copied-path classification must be reviewed against the owner receipts before any narrower closure is installed; substring exclusion alone is not a scientific or archival gate.

## Actual consumers and safe preservation pattern

- `atlas/evidence.py:checked_receipt` checks an exact original document pin, an original path/hash pair present in its JSON, and a unique canonical archive entry. Its selection is `catalogue/source-snapshots/<sha>/<original-path>`. An absent/corrupt archive cannot fall back to changed live bytes. `verify_manifest_files` checks the dependencies/files union.
- `atlas/agent_review.py:validate_review` uses those document-bound mappings for review artifacts; it still requires the exact current model identity for approval. `atlas/review_export.py:collect` independently validates historical artifact/definition bytes in an isolated exact context. Neither permits changing the review record hash.
- `tools/build_evidence.py` validates each selected research manifest through `verify_manifest_files` before exporting it. `tools/build_database.py` includes approval-registry/review-map provenance. Packaging reaches these consumers through `tools/build_web.py`.
- `tests/test_evidence_archives.py` checks immutable document bindings, canonical paths, duplicate/escape rejection and sibling file-manifest coverage. Its frozen-owner namespace check requires complete owner-pinned copied subtrees. `tests/test_agent_review_archives.py`, `tests/test_agent_review_export.py` and `tests/test_build_evidence.py` exercise real consumers.
- `tests/historical_sources.py:pinned_source` permits an exact canonical snapshot without a sidecar for its specifically pinned regression context. Test callers include `tests/test_resolution_diagnosis.py`. Adding that snapshot preserves a historical reference; substituting a new expected hash would not.

Reusable adaptation: `docs/ingestion/duncan-chang-1970/release-v2/prepare_preservation_v3.py` demonstrates current-edge selection, exact source/map archival, explicit document binding, reverse-map closure and preflight concurrency checks. The newer Lade prospective helper `docs/ingestion/lade-duncan-1975/atlas-integration-v1/shared-hook-install-v1/revision-v3/plan_preservation.py` also stages candidate maps and simulates preservation without installation. Reuse the algorithm and exact logical namespace; do not execute either one-shot helper unchanged (it owns another assignment and freezes another source set).

## Minimal additive plan

1. Before any planned file edit, copy the exact nine baseline source bytes into their canonical content-addressed snapshot paths. `current-v3/plan.json.targets` supplies every path/hash and existing-copy status. Verify bytes, not just filenames; refuse to overwrite any existing differing snapshot. STATUS and ROADMAP have no discovered current-hash JSON consumers, but preserving their base bytes is inexpensive and protects the stated change boundary.
2. For each logical primary pair, leave its receipt document unchanged. Preserve the old sibling sidecar bytes first, then add its exact document SHA and an entry for the old source path/hash/canonical snapshot. No old entry is removed or rewritten. A newly created map must bind every sibling file/dependencies manifest; current plan lists those siblings.
3. For every old sidecar being extended, preserve its exact bytes before serializing the extension. Follow ordinary receipt reverse references to that old map identity recursively, using the same original-document rule. Existing sidecar `entries` already naming an old map identity should keep pointing to its canonical exact snapshot, rather than rewriting those entries or proliferating map changes.
4. Treat retained `receipt-bytes` and review `context` trees as immutable owner-scoped evidence. Their paths appear in the full inventory for visibility. Resolve any needed replays in their original source-root namespace; do not add maps into a copied subtree merely because a nested JSON mentions `web/app.js`. Verify owner inventories before choosing the smaller logical plan. If an actual consumer addresses a copied document as a root receipt, include that documented consumer edge and extend the closure prospectively.
5. Stage all proposed sidecar JSON under the new Bingham-owned packet first. Assert all source/document/map before-hashes are unchanged; simulate `checked_receipt` with old source bytes removed/replaced in a private temporary context. Validate every affected original document and all pre-existing bindings, preserving before/after results. Only coordinator installs exact-byte snapshots and approved additive maps.
6. Then edit shared integration files. Re-run archive, review-export, evidence/database/catalogue checks plus the package gates appropriate to those changes. Do not repair failures by recomputing historical expected hashes. Re-run this audit if upstream/main or any planned-file before-hash changes.

## Retained attempts and reproducibility

`audit.py` reuses the existing stock scanner against the explicit isolated root. Its initial invocation failed on historical absolute external-worktree paths; the corrected script excludes absolute/parent-traversal references explicitly. That failure occurred before any report or shared mutation. `audit_fast_v2.py` adds an rg-derived filename candidate index. `audit_current_v3.py` additionally limits to current byte identities; its inventory is the authoritative scope for newly broken edges. All three corrected scans finished successfully; no scan remains running. Their outputs are retained separately. The original wide scan reports1692 historical unresolved mentions, the indexed wide scan1686 (six parse-independent filename candidates omitted); current-v3 reports0unresolved current pairs. No broad historical-resolution pass is claimed.

Reproduce the filename index from the isolated worktree with `rg -l -F -g "*.json"` for the nine target paths and `source-archive-map.json`, writing `/private/tmp/bingham-receipt-candidates.txt`; run `PYTHONDONTWRITEBYTECODE=1 python3 <packet>/audit_current_v3.py`, then `python3 <packet>/summarize.py`. The helper asserts exact baseline HEAD and source equality. `quick-current.json` is a separate direct current-hash index cross-check, not the archival consumer proof.

No blocker prevents coordinator preservation. The small next action is reviewing the logical namespace classification and preparing prospective additive maps from the frozen isolated baseline.

## Final coordinator-selected preparation

The coordinator withdrew the conservative all67-map option and selected the logical11-map plan:40primary/23reverse edges; all147copied-context mentions remain unchanged. `prepare_preservation.py` stages the nine old source archives plus old logical-map bytes and proposed additive maps, and simulates all63document-bound resolutions. It never rewrites a receipt/review document. It is syntax-parsed only, NOT EXECUTED by the auditor. Default prepares owned `prepared-v1/`; coordinator may review it and explicitly invoke `--apply`. The superseded all67-map helper is retained as `superseded-conservative-not-executed.py`; do not run it. `copy-namespace-check.json` records the copied-document namespace distinction and static-search limit. Final preparation pins both input plans, guards all copied-document before-hashes and verifies every receipt remains unchanged.
