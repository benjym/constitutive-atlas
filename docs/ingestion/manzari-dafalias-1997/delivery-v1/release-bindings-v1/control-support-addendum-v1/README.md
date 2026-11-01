# Control-support prospective addendum v1

Read-only extension of the frozen release-bindings audit, requested before observations. Original packet files and manifest remain byte-identical. This directory adds published-base reverse audit coverage for `catalogue/laboratory-control-support.json` and hashes the coordinator's current `delivery-v1/public-control-scope-v1.md`. No production policy, source, archive or map was edited.

Exact published-base support-policy bytes: 591 bytes, SHA-256 `69eadfece1422cdb2f6fa2518a6205ab554ca596aa22492e1d4ce6ed9c9c6089`. Canonical old-byte target if changing this policy:

`catalogue/source-snapshots/69eadfece1422cdb2f6fa2518a6205ab554ca596aa22492e1d4ce6ed9c9c6089/catalogue/laboratory-control-support.json`

That canonical archive is absent in the published base. Exact source is `git show d1c3a19409adaa32791c105429a4167e5bac9d9d:catalogue/laboratory-control-support.json`. It has 14 current-byte receipt documents within the same bounded scan, plus existing sidecar metadata references. `delta.json` lists their exact documents, current hashes/locators and the 28 additional reverse binding occurrences. Four additional candidate mutation paths appear relative to the original audit: support policy itself and three OCC sidecars (integration-v1, its independent review, finish-checklist independent release review). The rest of the sidecar candidate closure overlaps the original audit. No candidate map was installed. All original cautions about custom raw-hash consumers, live policies versus historical receipts, excluded nested copies and unchanged document hashes still apply.

The current prospective public-scope record is NEW and is not a file in published-base d1c3a194. `delta.json` records its actual current bytes and SHA. It restricts inverse axial stress protocol3 (monotonic and cycles) because no such study is qualified; it does not claim an observed failure or alter material requests. Preserve that distinction in dossier/review/browser evidence. Prior statement that no MD support entry was required in integration-plan-v1 is superseded by this explicitly frozen prospective scope, not by a fabricated numerical observation.

The existing support declaration can add exact MD definition id/hash with unsupported `{protocol:3, minimum_cycles:0, reason:"Axial stress control has not been qualified for this formulation. Use drained or undrained strain control within the documented scope."}` while preserving every existing entry. `tools/build_web.py` checks definition hash. `web/laboratory-support.mjs::unsupportedReason` applies for cycles>=minimum_cycles; `requireSupportedControl` rejects matching requests before ordinary execution. This is a qualification restriction; never register it as a numerical declared failure in laboratory-package-policy.

Important exact consumer behavior: `web/app.js::updateControlSupport` disables matching CYCLES options and shows the explanation; it does not disable the PROTOCOL option. With minimum_cycles0, all protocol3 history choices are disabled, and ordinary simulation is blocked by requireSupportedControl. Browser acceptance should verify the visible restriction, no misleading successful curve/export, and recovery to supported protocols1/2/4. If literal disabling of the protocol3 selector option is required, that needs a generic UI change plus expanded app reverse-binding/source qualification; data-only policy integration cannot claim that behavior. No UI change is performed here.

Reproduce the full extended structural report without rewriting the original packet:

```sh
python3 -B docs/ingestion/manzari-dafalias-1997/delivery-v1/release-bindings-v1/control-support-addendum-v1/audit_addendum.py
```

The addendum runner imports the frozen original audit, adds only the support-policy target, and writes only this directory's audit.json. Other files are the read-only delta and manifest. No builds/compiled calls/browser observations/acceptance occurred. Coordinator owns fresh drift checks and eventual minimal preservation installation after E5.
