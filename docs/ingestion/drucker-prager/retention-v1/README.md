# Drucker–Prager private source retention v1

Two original OpenSees files are durably retained under ignored `.local/private-sources/drucker-prager/`. [Receipts](receipts.json) identify exact locations, original acquisition hashes/lengths/URLs and retention date. The original acquisition record is unchanged. No upstream code was built or executed; public commits contain receipts only.

The Itasca page was separately read through the web tool. Its original acquisition receipt has no raw HTML hash; this packet does not claim a retained original for that page. This distinction remains explicit in `not_retained`.

Run from the repository root to verify retained bytes against both receipt layers:

```sh
python3 -B - <<'PYCODE'
from pathlib import Path
import hashlib, json
root = Path.cwd()
r = json.loads((root/'docs/ingestion/drucker-prager/retention-v1/receipts.json').read_text())
p = root/r['original_receipts_path']
assert hashlib.sha256(p.read_bytes()).hexdigest() == r['original_receipts_sha256']
original = {x['url']: x for x in json.loads(p.read_text()) if 'sha256' in x}
assert len(r['files']) == len(original) == 2
assert {x['url'] for x in r['files']} == set(original)
for x in r['files']:
    source = original[x['url']]
    assert (source['sha256'], source['bytes']) == (x['sha256'], x['bytes'])
    data = (root/x['local_path']).read_bytes()
    assert len(data) == x['bytes']
    assert hashlib.sha256(data).hexdigest() == x['sha256']
print('PASS: two privately retained OpenSees originals match unchanged acquisition receipts.')
PYCODE
```

A fresh public clone must retrieve the exact linked sources and verify their hashes. Retention is not numerical qualification, scientific acceptance or release authorization.
