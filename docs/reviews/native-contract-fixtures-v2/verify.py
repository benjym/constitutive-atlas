from pathlib import Path
import json,hashlib,sys
P=Path(__file__).resolve().parent;ROOT=P.parents[2];sys.path.insert(0,str(ROOT))
from atlas.evidence import checked_receipt
read=lambda p:json.loads((P/p).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for rel,h in read('manifest.json')['files'].items():assert sha(P/rel)==h,rel
for freeze in ['pre-build-freeze.json','post-build-gate-freeze.json']:
 for rel,h in read(freeze)['files'].items():assert sha(ROOT/rel)==h,rel
for ref in read('archive-plan.json')['references']:assert sha(checked_receipt(ROOT,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256']
for name in ['numerical','recorded']:
 x=read('native-v2-'+name+'.json');assert x['status']==0 and x['stderr']==''
 assert x['stdout'].startswith('Explicit valid-domain/GIS-depth20 fixtures; models=12\n')
r=read('native-v2-original-contracts.json');assert r['status']=='passed'and len(r['processes'])==4 and all(x['returncode']==1 for x in r['processes'])
assert '100% tests passed out of 2'in(P/'native-v2-ctest.stdout').read_text()
assert 'Ran 26 tests'in(P/'native-v2-python.stderr').read_text()and(P/'native-v2-python.stderr').read_text().rstrip().endswith('OK')
x=read('results.json');assert x['recorded_cases']==79 and x['recorded_checks']==2404 and x['runtime_model_default_tolerance_changes']is False
# Every original C++ assertion message survives. Original sources are available byte-for-byte.
for name in ['test_solver.cpp','test_recorded.cpp']:
 path='tests/'+name;pin=read('archive-plan.json')['original_bytes'][path];old=(ROOT/'catalogue/source-snapshots'/pin/path).read_text();new=(ROOT/path).read_text()
 import re
 messages=re.findall(r'require\([^;]*?,\s*"([^"\n]+)"\)',old)
 for message in messages:assert message in new,(path,message)
assert 'unknown native fixture profile'in(ROOT/'tests/test_solver.cpp').read_text()
print('PASS: complete two-group explicit native qualification,79recorded cases/2404checks,26source checks,4retained strict/unknown failures; original bounds retained.')
