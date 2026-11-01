"""Read-only source/manifest audit plus pure JSON tests; no compiled calls."""
from pathlib import Path
import json,hashlib,runpy,sys
D=Path(__file__).resolve().parent;B=D.parent;OLD=B.parent/'hierarchical-seeds-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=B/'freeze-v1.json'
assert sha(f)=='f4931baef40d2addfdefec27cee460eb102629ebf1955b626dfc913721baa7d4'
j=json.loads(f.read_text())
for p,h in j['files'].items():assert sha(B/p)==h,p
assert sha(B/'model.json')==sha(OLD/'model.json')=='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
checks=[]
for p in B.glob('check*'):
 if (OLD/p.name).exists():
  assert (OLD/p.name).read_text().replace('lade-hierarchical-seeds-v1','lade-outer-reuse-v1')==p.read_text(),p
  checks.append(p.name)
for p in ['triaxial-reference-results.json','triaxial-policy.json','SUPPLEMENT_POLICY.json','proposed-native-source/include/atlas/tensor.hpp','proposed-native-source/include/atlas/trace_accuracy.hpp','proposed-native-source/include/atlas/path_error_control.hpp','proposed-native-source/include/atlas/implicit_seed.hpp','proposed-native-source/include/atlas/derivative_tail.hpp','proposed-native-source/include/atlas/numerics/symmetric_spectral.hpp','proposed-native-source/main.cpp']:
 assert (OLD/p).read_bytes()==(B/p).read_bytes(),p
sys.dont_write_bytecode=True;sys.path.insert(0,str(B));r=runpy.run_path(str(B/'test_fidelity.py'));assert len(r['checks'])==15 and all(r['checks'])
local=Path('.local/lade-outer-reuse-v1/native-source');n=0
for p in (B/'proposed-native-source').rglob('*'):
 if p.is_file():assert p.read_bytes()==(local/p.relative_to(B/'proposed-native-source')).read_bytes(),p;n+=1
out={'id':'REVIEW-lade-outer-reuse-closure-v1','freeze_sha256':sha(f),'verified_frozen_files':len(j['files']),'path_only_checker_changes':checks,'local_source_mirror_files':n,'pure_parsing_tests':15,'compiled_execution':False,'material_advance':False}
(D/'freeze-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'files':len(j['files']),'checkers':len(checks),'mirror':n,'pure_parsing_tests':15}))
