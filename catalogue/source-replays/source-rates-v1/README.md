# Frozen source-rate study replays v1

These explicit closures preserve the original sand2015 v2 and clay2005 v2 source-study reports and all29 original Python test groups before common arithmetic changes. The adapters invoke the original verifiers and original tests without editing them. They compare complete original reports, including runtime pins; this is historical execution rather than a check against the current engine.

Sand:43 archived project files,38 valid rate records,20 operational rejections and11 test groups. Clay:33 files,41 rate records,10 historical invalids,29 support cases and18 test groups. No private papers, author programs, compiled artifacts or Git metadata are needed. Original source manifests/provenance/protocols bind the archived model, reference, verifier and runtime hashes. `registry.json` binds the capsule, original report and exact expected adapter stdout. `manifest.json` freezes this additive replay packet.

```sh
python3 -B -m atlas.source_replay sand --registry catalogue/source-replays/source-rates-v1/registry.json
python3 -B -m atlas.source_replay clay --registry catalogue/source-replays/source-rates-v1/registry.json
python3 -B -m unittest tests.test_source_replay tests.test_source_rate_runtime -v
```

The original report comparison includes the recorded Python interpreter string for sand and platform-sensitive binary64 results. Interpreter/stdlib remain external; this does not promise cross-version bit reproduction. Exact disagreement fails honestly. Current-runtime rate/rejection/support checks live separately in `tests/test_source_rate_runtime.py`; they retain the original numerical gates while checking current runtime identities rather than substituting them in old evidence.

The sand compiled negative study and finite-study verifiers are not migrated by this packet. Their closures must be preserved separately before shared C++/collector edits. This packet runs only project Python, including generation of header text in a temporary directory during an original test; no compiler or generated binary executes. It provides no scientific admission or new constitutive-law validation.
