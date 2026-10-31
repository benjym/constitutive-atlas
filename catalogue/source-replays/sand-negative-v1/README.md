# Sand2015 original compiled negative: frozen re-audit v1

This closure preserves107 exact project source/data files for the original `barodesy2015-rates-v1` study. It re-audits the retained raw native/Wasm journals with the original assessor and comparison wrapper, verifies the complete original failed comparison, runs the six original regression groups (including descriptor-order and duplicate-key mutation checks), and invokes the original comparison CLI with its required exit status1. The adapter exits0 only when those original negative findings are faithfully reproduced.

```sh
python3 -B -m atlas.source_replay sand-negative --registry catalogue/source-replays/sand-negative-v1/registry.json
python3 -B -m unittest discover -s tests -p test_barodesy2015_rate_evidence.py -v
```

Expected historical finding:71 rows/backend, native and Wasm each fail component6 of `valid:audit-trace-cancellation`; cross-backend parity passes; the overall study remains **failed**. The lost tiny void rate is checked against an exact rational sum of the actual binary64 inputs. Native/Wasm agreement does not override independent reference failure.

The capsule includes the original protocol's72 source pins, original study documents/raw companions/command receipts/generated source, the original regression file and a trusted Python adapter. Original protocol and results-manifest bytes bind all pre-existing study/source pins. `registry.json` binds those documents, the capsule and exact adapter stdout; `manifest.json` freezes this additive packet. Original files are unchanged. The root regression wrapper delegates historical execution to this archive so future live source edits do not refresh old evidence pins.

No compiled artifact is included, reopened, executed or rebuilt. Absolute artifact paths in the original receipts are preserved as provenance. This is portable archival re-assessment on the recorded current Python interpreter/stdlib, not a bit-identical reconstruction of the old compiler environment. Missing/corrupt archive inputs or changed original document bindings reject. Trusted Python replay is not a security sandbox. No finite integration, material AD, experimental validation or scientific admission is claimed.

Closure assembly initially attempted to include `tests/__init__.py`, which does not exist in this namespace-based test tree. The inventory was corrected before capsule creation or replay; no observations or numerical policy changed. The final closure includes the original regression module loaded explicitly by file path.
