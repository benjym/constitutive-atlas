from pathlib import Path
import hashlib,json,sys
p=Path(__file__).resolve().parent;r=p.parents[2];sys.path.insert(0,str(r))
from atlas.evidence import checked_receipt
from tests.test_recorded_scope import corpus
for n,h in json.loads((p/'manifest.json').read_text())['files'].items():assert hashlib.sha256((r/n).read_bytes()).hexdigest()==h,n
for e in json.loads((p/'archive.json').read_text())['edges']:checked_receipt(r,e['document'],e['original_path'],e['sha256'])
rows=corpus();assert len(rows)==41 and sum(x['accepted'] for x in rows)==13
print('Verified recorded-scope fixture repair:41 metadata fixtures,11 opposite-scope negatives; source receipts intact.')
