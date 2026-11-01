from pathlib import Path
import hashlib,json
P=Path(__file__).resolve().parent
ROOT=P.parents[2]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
for rel,expected in read(P/'manifest.json')['files'].items():
 assert sha(P/rel)==expected,rel
result=read(P/'results.json');assert result['outcome']=='failed' and result['failed_gate']=='P01'
assert all(v=='not-run' for k,v in result['gates'].items() if k!='P01')
assert read(P/'package-receipt.json')['returncode']==1
assert 'Invalid scoped laboratory envelope or catalogue.' in (P/'package.stderr').read_text()
d=read(P/'diagnostic.json')
assert d['in_memory_rebinding_error'] is None and d['source_unchanged'] and d['definition_semantically_identical']
assert sha(ROOT/'protocols/gis2024-small-drained-example.json')==d['source_document_sha256']
old=read(ROOT/'protocols/gis2024-small-drained-example.json')
assert old['catalogue_hash']==old['result']['catalogue_hash']==d['old_catalogue_hash']
assert len(list((ROOT/'models').glob('*.json')))==11
assert not (ROOT/'models/mohr-coulomb.json').exists()
print('PASS: original P01 failure retained; later gates not run; eleven live models unchanged')
