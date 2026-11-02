# Current-live database preservation gate

This is the unchanged accepted package-v2 nine-table row-bag/integrity/exact-admission check with only its baseline path changed to the independently downloaded current-live Perzyna database and an explicit frozen SHA256 assertion added. The original checker remains unchanged. Baseline receipt: ../publication-source-v3/published-database-baseline.json. All old row multiplicities must be preserved; no dropping a model or approval to pass. New actual package observations remain pending.

Future command:

```sh
python3 -B docs/ingestion/hypoplastic-interface-2016/package-v4-database/check_packaged_database.py /private/tmp/atlas-interface2016-delivery-v1/site-v4 docs/ingestion/hypoplastic-interface-2016/package-v4-database/result.json
```
