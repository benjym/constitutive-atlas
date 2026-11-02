# Isolated local source-commit preparation

Source-only specialist `/root/hill_interface`; 2026-11-02. No Git mutation, material, compiled, build, browser or remote command was executed. All outputs are confined to this new preparation directory.

Current source parent is `54f409b37deaed0ab82a85cdac9f489bc65e1309`; isolated release is `/private/tmp/atlas-interface2016-delivery-v1/release-v2`; additive owned ref is `refs/heads/delivery/interface2016-v1`. The shared checkout's HEAD, index and unrelated files are not targets.

`inventory-v2.json` is the current exact whitelist and digest plan; `paths-v2.txt` is its readable path list. It contains 209 files: 200 additions and nine modifications. Modified paths are precisely the six reviewed shared integration inputs plus coordinator tracking checkpoints:

- `.github/workflows/verify.yml`
- `IMPLEMENTATION_PLAN.md`
- `ROADMAP.md`
- `catalogue/approved-models.json`
- `catalogue/manifest.json`
- `docs/STATUS.md`
- `tools/build_web.py`
- `web/app.js`
- `web/model-profile-data.mjs`

Other entries are explicit model-owned additions, the eleven reviewed integration paths, exact historical map/preimage preservation dependencies, qualified public engine assets and the four-file independent tracking review. All 97 E5 artifact paths are included. The 22 integration preservation events and eight tracking preservation events resolve to correctly hashed documents and original source archives; 26 included snapshot files match their content-addressed directory names. Existing historical interface packet files remain exact parent objects. This is a bounded whitelist inspection, not a full isolated-tree diff. Private source originals, native libraries, `paper/`, `output/`, unrelated model files and cache/credential directories are excluded. Private source paths/hashes appearing as provenance strings are retained; their private contents are excluded.

Version 1's 200-file inventory is preserved. Independent review identified that the ordinary clean-checkout builder consumes five public engine/generated assets directly. Version 2 adds those five exact E4-reviewed files under `web/engines/interface2016/`, plus tracking-review `REPORT.md`, `check-results.json`, `check_tracking.py` and `decision.json`. Their complete public engine digests are in `public-engine-pins-v2.json`. The Wasm module is an expressly included qualified public delivery artifact; the private native dylib remains excluded. The later `commit-dry-validation.json` is not one of the four source tracking-review files and is deferred to evidence closeout.

`postcopy-verification-v2.json` confirms all 209 isolated files exist and match their exact inventory digests, including all five public engine assets. There are no missing or changed inputs. The inventory's earlier `parent_copy_required_before_execution` field records initial copy obligations; this completed postcopy receipt supersedes their outstanding status.

## Guarded parent invocation

The script defaults to read-only validation and must be given the current version explicitly:

```sh
python3 docs/ingestion/hypoplastic-interface-2016/integration-v1/commit-preparation-v1/create_commit.py --inventory docs/ingestion/hypoplastic-interface-2016/integration-v1/commit-preparation-v1/inventory-v2.json
```

Only the parent may add `--execute` after review. Execution creates a temporary alternate Git index, reads the exact parent, writes each independently hashed isolated file as an object, installs only whitelist entries, verifies the staged path set, writes a tree and commit, and creates the previously absent owned ref. It never checks out, resets, stages into the shared index, updates HEAD/main, pushes or triggers CI. It refuses an already existing owned ref. Real HEAD/index digests are checked around ref creation. A failed operation preserves its alternate index and failure report. Successful invocation writes a separate `commit-result.json`; no commit is claimed by this preparation packet.

The inventory scripts are read-only with respect to Git. `prepare_inventory.py` preserves the initial whitelist derivation; `prepare_inventory_v2.py` applies the explicit engine/tracking-review correction. Regenerating them is a new source freeze and requires review if source bytes have changed. The first initial derivation assumed every recorded preimage had an archive; the unreferenced app/workflow preimages correctly had none. The derivation was corrected to include only actual archives and to require every receipt-referenced preimage. No receipt-resolution gate was weakened.

This preparation packet is deliberately outside its own commit inventory, avoiding recursive manifest hashes. It and actual commit/package/browser/release receipts can enter a later evidence commit. `verification.json` is the retained v1 source inclusion check; `postcopy-verification-v2.json` records the current corrected set. Script AST parsing passed; the parent owns execution.
