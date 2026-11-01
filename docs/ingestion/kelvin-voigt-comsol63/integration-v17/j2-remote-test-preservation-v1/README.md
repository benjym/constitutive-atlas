# J2 remote test preservation v1

Preserves exact isolated `tests/test_j2_main_routing.mjs` SHA256 e7785a916a7e80a8ab99ae7170dd86b8e6301207561eef2c4fe6b7ebe724766e before the coordinator adopts the cf0697f09c3737f6e8d28ba9815984d79944e7d8 fixture repair. The original b31 predecessor test is also retained canonically. No test, production code, living document, build artifact, or Git state was changed.

`receipt.json` lists two snapshots and two sidecars preserving both exact current test receipt bindings. The cf0697 remote map deltas were compared structurally with isolated maps: all remote document guards and archive entries are already present in both isolated maps. Keep isolated catalogue/agent-reviews and docs/admission/maxwell-agent-v2 maps unchanged; overlaying the smaller remote maps would drop existing preservation. Exact comparison hashes/counts are in `remote-map-comparison.json`.

```sh
python3 docs/ingestion/kelvin-voigt-comsol63/integration-v17/j2-remote-test-preservation-v1/verify.py
python3 -m unittest tests.test_evidence_archives
```

All 20 agent reviews, two exact bindings, original receipt hashes, installation file inventory, and 14 archive tests replay successfully. Original test and receipt bytes are retained independently of the coordinator replacement.
