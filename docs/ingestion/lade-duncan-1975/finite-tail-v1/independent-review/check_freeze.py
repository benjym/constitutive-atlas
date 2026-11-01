"""Read-only closure/source-diff check; no compiled execution."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;B=D.parent;OLD=B.parent/'derivative-tail-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=B/'freeze-v1.json';assert sha(f)=='c9aead821f7b68662c7feed896034edc287833de8c2318b97fa7bbd48c940f60'
j=json.loads(f.read_text())
for p,h in j['files'].items():assert sha(B/p)==h,p
assert sha(B/'model.json')==sha(OLD/'model.json')=='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
checkers=[]
for p in B.glob('check*'):
 if (OLD/p.name).exists():
  assert (OLD/p.name).read_text().replace('lade-derivative-tail-v1','lade-finite-tail-v1')==p.read_text(),p
  checkers.append(p.name)
for p in ['triaxial-reference-results.json','triaxial-policy.json','SUPPLEMENT_POLICY.json','proposed-native-source/include/atlas/path_error_control.hpp','proposed-native-source/include/atlas/implicit_seed.hpp','proposed-native-source/include/atlas/derivative_tail.hpp','proposed-native-source/include/atlas/solver.hpp','proposed-native-source/include/atlas/numerics/symmetric_spectral.hpp']:
 assert (OLD/p).read_bytes()==(B/p).read_bytes(),p
checkpoint=OLD/'checkpoint-manifest.json';assert sha(checkpoint)=='e728c2faa4a7b8be68993200c34205c1344de83bbe9a8b41173d6f44678f8f30'
r=json.loads((OLD/'native-performance-results.json').read_text());assert r['passed'] is False and r['timeout'] is True
out={'id':'REVIEW-lade-finite-tail-prospective-closure','freeze_sha256':sha(f),'verified_frozen_files':len(j['files']),'path_only_checker_changes':checkers,'prior_failed_checkpoint_sha256':sha(checkpoint),'prior_timeout_seconds':r['elapsed_seconds'],'compiled_execution':False,'material_advance':False}
(D/'freeze-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'files':len(j['files']),'checkers':len(checkers),'prior_failure_retained':True}))
