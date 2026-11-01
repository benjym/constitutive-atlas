# Controlled-path host preservation v1

Preserves exact pre-edit `tools/build_controlled_path_web.py` SHA256 2fe5bf29b0e6a58bd18012a526fa910a30ca97eb11341dfd718ea8089852e3f1 before the coordinator changes supporting-file resolution to the existing archive-aware review binding. This source-only task made no code changes. The original failed package-v6 attempt remains retained.

`receipt.json` lists 19 canonical snapshots, 19 additive sidecars, and 46 preserved direct/reverse-map bindings. Original receipt bytes remain unchanged. The installation script targets only this builder and affected old-map pins. All catalogue agent reviews and the 14 archive tests are replayed separately.

```sh
python3 docs/ingestion/kelvin-voigt-comsol63/integration-v16/controlled-path-host-preservation-v1/verify.py
python3 -m unittest tests.test_evidence_archives
```

`preserve.py` is the exact one-shot installer and refuses to overwrite its receipt. The coordinator may now change the live builder; replay verifies the original byte snapshots independently.
