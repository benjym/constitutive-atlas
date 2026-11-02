# Prospective offline check of actual UI exports

`check_actual_exports.py` is source-only and has not been run on exports. It neither starts a browser nor imports/runs a module, solver or material. The coordinator supplies three independently downloaded JSON files from the actual UI: default, qualified reset after edits, and import/fresh replay of the default. Keep all downloaded bytes unchanged with their CUA/server/browser evidence; this checker cannot establish download provenance itself.

After the actual standard package-v2 succeeds, and after actual UI downloads exist:

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/browser-v1/check_actual_exports.py \
  --package /private/tmp/atlas-interface2016-delivery-v1/site-v2 \
  --default /ABSOLUTE/PATH/default.json \
  --reset /ABSOLUTE/PATH/reset.json \
  --replay /ABSOLUTE/PATH/replay.json \
  --output docs/ingestion/hypoplastic-interface-2016/browser-v1/actual-exports-check-v1.json
```

The output path must be new; retain failures separately. The checker binds the exported full identity to the exact package identity and verifies its declared asset/component hashes. It requires the unchanged frozen example and package-cases hashes, exact model/default40-interval request/settings and complete 41-point finite state/stress/context data. Each export's initial and endpoint five states and six Mandel stress components are checked against the unique frozen default case at the original absolute tolerances: 0.2 Pa for stress-valued fields, 2e-6 for void ratio. It then requires exact parsed JSON equality of all three complete exports, including identity, request and every result point; whitespace/key order is not significant. It reports input byte hashes and every reference error. This is 66 comparisons across three exports, with no trajectory recomputation.

A pass supports only those supplied downloads and packaged identity. Visible parameter/start-state changes, reset/import controls, stale-worker handling, rejection/recovery, responsive layout, console/network, delivered asset provenance and final publication need their separate actual browser/evidence checks. This helper does not change the 216 accepted source inputs or any frozen reference, tolerance or prior result.
