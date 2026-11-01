"""Read-only hash/model/checker closure audit; no compiled or model calls."""
from pathlib import Path
import json,hashlib,sys
D=Path(__file__).resolve().parent;B=D.parent;OLD=B.parent/'warmstart-control-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=B/(sys.argv[1] if len(sys.argv)>1 else 'freeze-v1.json');j=json.loads(f.read_text())
for p,h in j['files'].items():assert sha(B/p)==h,p
assert sha(B/'model.json')==sha(OLD/'model.json')=='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
checkers=[]
for p in B.glob('check*'):
 if (OLD/p.name).exists():
  assert (OLD/p.name).read_text().replace('lade-warmstart-control-v1','lade-derivative-tail-v1')==p.read_text(),p
  checkers.append(p.name)
for p in ['triaxial-reference-results.json','triaxial-policy.json','SUPPLEMENT_POLICY.json','proposed-native-source/include/atlas/path_error_control.hpp','proposed-native-source/include/atlas/implicit_seed.hpp']:
 assert (OLD/p).read_bytes()==(B/p).read_bytes(),p
out={'id':'REVIEW-lade-derivative-tail-prospective-closure','freeze_path':str(f),'freeze_sha256':sha(f),'verified_frozen_files':len(j['files']),'model_sha256':sha(B/'model.json'),'path_only_checker_changes':checkers,'compiled_execution':False,'material_advance':False}
(D/'freeze-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'files':len(j['files']),'checkers':len(checkers),'passed':True}))
