# Pre-registration DSL/compiler source-binding inventory

Task REV-normalized-determinant-source-bindings-v1. Read-only audit, 2026-10-31. Final authoritative output: inventory.json, produced by scan.py before normalized_determinant registration edits. No shared edits, archival, builds, compiled execution, commits or gate changes were made.

## Scope and method

Recursively scan every JSON file beneath catalogue/, docs/, tools/, schemas/, tests/, including untracked/ignored files found by Path.rglob. Parse JSON and recurse objects/arrays. Recognize exact `atlas/dsl.py`, `atlas/compiler.py`, `atlas/history_compiler.py` keys with lowercase64hex values, and exact `{path:...,sha256/hash:...}` objects at arbitrary nesting. Record JSON pointers, exact document SHA, source path/hash and current resolution from the real atlas.evidence.checked_receipt function. Deduplicate identical document/source/hash pairs but retain every recognized occurrence pointer.

Exclude path components source-snapshots, source-snapshot, snapshots, frozen, frozen-sources, reviewed-sources. Source-archive-map.json files are excluded from PRIMARY source receipts. Encoded capsule payload strings are not decoded as nested JSON; payload byte encodings are not primary receipts. Descriptive `original_path` inventory objects are not the primary receipt syntax supported by checked_receipt. Consequently the frozen inventory's own descriptive rows do not introduce new primary bindings. Secondary scanning additionally recognizes original_path objects for source-archive-map.json references.

The scan read 1325 non-snapshot JSON files, excluded 462 snapshot/frozen JSON files and found no parse errors. It found 225 primary document/source/hash pairs in 108 documents: 208 resolve through archived snapshots, 10 resolve live and 7 old pairs are unresolved. This is broader than the old v5 report's stated 59-reference pre-change-hash scope. The latter remains historical, unchanged evidence; it did not claim this 225-pair scope.

The final report contains every exact document SHA and source pair. `checked_receipt_source_sha256` also identifies the verifier inspected. It establishes identity resolution, not dynamic source-execution closure, complete runtime dependency discovery, or scientific correctness. Raw duplicate JSON key analysis is outside this scan; JSON parsing follows the same ordinary decoder used by checked_receipt.

## Required additions before changing the three live files

Ten current-live pairs appear in four documents:

- catalogue/investigations/clay2005-determinant-rates-v1/protocol.json: all three sources.
- catalogue/investigations/determinant-expressions-v1/prospective-freeze.json: all three sources.
- catalogue/investigations/determinant-expressions-v1/registration-checks.json: all three sources.
- docs/ingestion/hypoplastic-clay-2005/determinant-input-rounding-v1/prospective-freeze.json: atlas/dsl.py only.

The source hashes requiring preservation are DSL `8a9da4dd24fa554991c691330069b18251cceb79f5cece1153943fc79aded02b`, compiler `fa6f8564ce1c46732524af4619901b5acb1cee8fc976a46d5445881eb567ba22` and history compiler `d09363f3ef3d62b261be8338bda6c0cb70a0556e50e75e53a79b0423fc57559e`. Archive those exact bytes and bind exact immutable documents before editing. Do not recompute or replace an expected old hash from a new source file. This worker did not perform archival.

## Seven older unresolved pairs

Three compiler bindings use SHA d241f835c39e4129d1b550e25d5bfad3a70c9b70a3f4dbbc15938d19c7856b60: solver-rollback-v1/protocol.json and native/receipt.json and wasm/receipt.json. **Exact bytes exist** at catalogue/investigations/solver-rollback-v1/frozen/atlas/compiler.py. The canonical source-snapshot file is absent and existing sibling sidecars do not redirect these pairs. Root can archive verified frozen bytes and add bindings without altering original receipt documents.

Three old_sources summary bindings in catalogue/source-replays/dsl-identity-v5/complete-receipt-audit.json use pre-determinant DSL/compiler/history identities. All three canonical source-snapshot files already exist and have the correct hashes. This descriptive historical audit document has no sibling sidecar binding, so asking checked_receipt to resolve those old_sources fields currently fails despite recoverable bytes. Root can register this exact immutable audit document if complete recursive identity resolution is desired. This is not evidence that the prior 59 checks failed at their observation time.

The remaining compiler binding, docs/reviews/solver-rollback-design-v1/source-checks.json, expects 147a9c547ca73e756ed211f087e02e619e27342bd847752f17d6e3936511db86. **No matching bytes located** among 96 compiler.py files in the repository/private tmp and 11 git source-changing commits across all local refs. The canonical source-snapshot file is absent. See compiler-availability.json and old-source-availability.json for exact search scope. This is a historical acquisition gap, not permission to infer replacement bytes from a nearby revision or relax an identity gate. The search does not prove absence from every external archive or unindexed renamed file.

## Secondary sidecars

The independent scan found 286 non-snapshot source-map references: 106 resolve through checked_receipt archives, 50 resolve live and 130 are historical sidecar original_path entries whose archived bytes match their pins. All 286 resolve within this explicitly reported secondary policy; the original_path-entry cases are checked as sidecar entries, not misrepresented as primary checked_receipt successes.

The inventory lists prospective sidecar locations for the 10 current pairs and 7 old unresolved pairs, then computes a reverse-reference closure through secondary sidecar dependencies. No secondary reference currently points to those prospective new/extended sidecar locations. Therefore no secondary source-map byte pin was identified as requiring repair for these specific additions. This does not authorize arbitrary edits to unrelated sidecars: if root changes a different existing map, rerun the reverse-reference check before mutation and preserve its original bytes.

## Reproduce and limitations

Run `python3 -B scan.py /Users/bmar5496/code/constitutive-atlas --output /private/tmp/fresh-source-bindings.json`. It imports the current checked_receipt implementation but mutates no project files. A rerun after source/sidecar changes is expected to produce different resolution statuses and must have its own result identity; preserve this pre-change inventory.

Eight bounded extraction-shape probes passed, including nested maps/objects, malformed dict-valued path, non-hash strings and encoded JSON payload exclusion. A preliminary scratch scanner failed on a dict-valued schema path; the final scanner guards string types and the regression is retained in scanner-checks.json. There were no final scan parse/resolution implementation failures; the seven unresolved identities above are reported rather than waived.

Exact deliverables for integration: README.md, scan.py, inventory.json, scanner-checks.json, compiler-availability.json, old-source-availability.json, manifest.json. The private initial-inventory.json is retained as an intermediate but must NOT be integrated: its earlier formatting contained a direct live-source summary and would create extra primary binding pairs. The final format uses original_path descriptors and adds none. Manifest pins only final owned artifacts. AGENTS.md, implementation-plan bytes, source equations and old frozen records remain unchanged.

Coordinator decision: archive only the 10 currently live bindings for the imminent three-file registration change. The seven pre-existing old gaps remain explicit; recovery/legacy-sidecar amendments are separately scoped and are not part of this archival action. No claim that all 225 pairs resolve is made.
