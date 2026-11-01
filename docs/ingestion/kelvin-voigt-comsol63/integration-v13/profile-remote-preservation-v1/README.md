# Profile remote preservation v1

Source-only archival installation before merging committed 8cab145bacde8b0f25cb93c0aebef826e318710f to b31c0a94ea04b7282e0780112940a362e8f9d315. The exact commit diff has 17 paths; 11 existed in the isolated release. All 11 current predecessor inputs and available committed predecessor bytes are preserved in canonical content-addressed snapshots. Six new remote paths have no isolated predecessor to archive.

The receipt records 188 affected exact source/map bindings across 101 immutable documents. Additive sidecars in 77 contexts preserve direct overwritten-input pins and recursively preserve old sidecars pinned by earlier receipts. Existing source documents were unchanged by this task. Snapshot archives are the original bytes; no historical document hash was retargeted.

No code, living documentation, model, controls, gates, build artifacts, or Git state was changed. The broad filesystem search selected only exact changed-input and affected sidecar edges; it did not change unrelated map contents.

Reproduce replay from the isolated release root:

```sh
python3 docs/ingestion/kelvin-voigt-comsol63/integration-v13/profile-remote-preservation-v1/verify.py
python3 -m unittest tests.test_evidence_archives
```

`preserve.py` is the exact one-shot installation script and refuses to overwrite its receipt. `receipt.json` inventories all installed canonical snapshots and maps. `manifest.json` binds the packet files. Original source bytes may subsequently be replaced by the authorized coordinator merge; replay uses their immutable snapshots.
