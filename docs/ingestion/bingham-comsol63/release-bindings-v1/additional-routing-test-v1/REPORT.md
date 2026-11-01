# Additional J2 routing-test preservation audit

Task TEST-bingham-routing-policy, read-only current isolated checkout. Single prospective target `tests/test_j2_main_routing.mjs`, SHA-256 `9d047d8f3b03bfb802302bd2552568c6704368b7bb504561cfb1183e50583069`. This is its exact pre-edit identity, not the git SHA-1 blob ID. Earlier nine-target maps were already installed; this audit pins their current map bytes and does not rerun the original baseline-HEAD assertion.

Result: four current live primary receipts, six current live reverse-map receipts, five maps (four existing, one new), no unresolved current edge and no document-pin conflicts. Seven references to other historical test hashes remain historical;64mentions inside copied/archive namespaces remain untouched. Direct and reverse consumers are listed exactly in `plan.json`. Each selected edge passed normal `atlas.evidence.checked_receipt` before any change. Actual archived-consumer semantics and namespace limitations remain those documented in the parent audit.

The new map is beside `header-source-review/review-receipt.json`. Existing changed-map originals include current Duncan release-v2, Lade live-release, shared-hook revision-v4 and workflow maps. Before extension the helper preserves each current exact map byte sequence, even where the first nine-file preservation already changed it. The old routing test receives its canonical snapshot; none of the original review/receipt JSON is rewritten.

`prepare_preservation.py` is syntax inspected only and NOT EXECUTED. Coordinator command from isolated root:

```sh
python3 -B docs/ingestion/bingham-comsol63/release-bindings-v1/additional-routing-test-v1/prepare_preservation.py
```

Default writes only this packet’s `prepared-v1/` staged archives/maps and simulates all10new bindings with old live sources absent in a private context. Coordinator reviews those exact bytes before `--apply`. The single-target plan is hash pinned in the helper; all before-hashes are checked again before installation. No test code, shared hooks, maps, git state, compiler or compiled artifacts were changed by this worker.

After coordinator archival and additive test expectation update, rerun the exact15routing tests and the archive/review/export checks; retain the original14pass/1fail attempt rather than rewriting it.

Plan SHA-256: `84f95bcbefea99f1f1122147a39783fa152d940cacb5a8af1e2eb055198b8730`. Helper SHA-256: `ecdbf3e7e2d3ec747ce7b259512accba2ead2981f844ebcb2c046a2136e47d01`.
