from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt,validate_record
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
for rel,h in read(P/'manifest.json')['files'].items():assert sha(P/rel)==h,rel
for rel,h in read(P/'installed.json')['files'].items():assert sha(ROOT/rel)==h,rel
baseline=read(ROOT/'docs/reviews/mc-browser-plan-v3/baseline.json')
assert len(list((ROOT/'models').glob('*.json')))==12
for rel,h in baseline['files'].items():
 if rel.startswith('models/'):assert sha(ROOT/rel)==h,rel
for ref in read(P/'archive-plan.json')['references']:
 assert sha(checked_receipt(ROOT,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256']
comparison=read(P/'package-comparison.json');assert len(comparison['files'])==810
assert comparison['added']==comparison['removed']==comparison['changed']==[]
for record in ['catalogue/reviews/mohr-coulomb-source-v1.json','catalogue/evidence/mohr-coulomb-current-backends-v3.json']:validate_record(ROOT/record,ROOT,current=True)
assert 'Ran 36 tests'in(P/'python.stderr').read_text() and (P/'python.stderr').read_text().rstrip().endswith('OK')
assert 'tests 16'in(P/'node.stdout').read_text() and 'fail 0'in(P/'node.stdout').read_text()
strict=read(P/'strict-defaults.json');assert strict['status']=='failed'
assert strict['models'][-1]['id']=='research-hp-extracted-asbs-gis-2024-v03' and strict['models'][-1]['result']['ok'] is False
assert all(row['result']['ok']for row in strict['models'][:-1])
print('PASS: exact root integration/810-byte-identical assets;24receipt edges;52focused checks; strict GIS default remains failed')
