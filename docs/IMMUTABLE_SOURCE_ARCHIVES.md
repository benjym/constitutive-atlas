# Historical source archives and evolving runtime capabilities

Retained numerical evidence describes the implementation used to produce it. Extending the DSL/compiler/runtime does not authorize replacing an old source hash with the new implementation hash. Historical receipts and their enclosing JSON bytes remain unchanged.

A packet-local `source-archive-map.json` identifies exact original receipt document bytes, the original source path and expected hash, and an archived source path. Shared snapshots live at `catalogue/source-snapshots/<original-sha256>/<original-path>`. Multiple packets may reference the same bytes. Snapshots are archival data: do not automatically import/compile them or treat them as the current runtime.

`atlas.evidence.checked_receipt(root, document, original_path, expected_sha256)` checks that the supplied source/path hash pair exists in the original receipt, the exact sidecar/document binding and the source hash. An explicitly mapped source always resolves to that archive; a missing or corrupt archive fails even when current source matches. Unmapped files must still match their unchanged live receipt. Paths cannot escape the repository. `verify_manifest_files` checks an existing manifest's dependencies/files union with this policy.

The immutable manifest is not rewritten. The sidecar is reviewable migration metadata; its exact document hash prevents silently rewriting old receipts to match new semantics. The helper does not replace expected hashes, regenerate evidence, accept arbitrary alternative paths, or skip numerical assessment. A historical reviewer observation of a temporary source hash is not automatically a current dependency receipt.

Archival identity and current compatibility answer different questions. Old native/Wasm results remain bound to original source. Retained-result comparisons against independent references still run, but do not execute a newly compiled runtime. A changed kernel needs its own new conformance/build/run receipts and regression execution. Do not describe old evidence as validation of the new expm kernel, derivative checks or lowering semantics.

The [migration inventory](../catalogue/investigations/symmetric-expm-v1/source-migration-inventory.json) records the pinned baseline commit and exact original source versions recovered from git by SHA256. It never substitutes revised source bytes for missing originals. Any nonempty unresolved list requires investigation, never rehashing revised code. Retain the baseline receipt and explicit original-to-archive inventory with migration review.
