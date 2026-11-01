"""Read-only frozen source/checker closure; no model or compiled calls."""
from pathlib import Path
import json,hashlib
D=Path(__file__).resolve().parent;B=D.parent;OLD=B.parent/'finite-tail-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();f=B/'freeze-v2.json'
assert sha(f)=='a795a628b3dd2147408f9c8638b3aad2691ffc243b5a6f3f373f4e81150325a7'
j=json.loads(f.read_text())
for p,h in j['files'].items():assert sha(B/p)==h,p
assert sha(B/'model.json')==sha(OLD/'model.json')=='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
checks=[]
for p in B.glob('check*'):
 if (OLD/p.name).exists():
  assert (OLD/p.name).read_text().replace('lade-finite-tail-v1','lade-hierarchical-seeds-v1')==p.read_text(),p
  checks.append(p.name)
for p in ['triaxial-reference-results.json','triaxial-policy.json','SUPPLEMENT_POLICY.json','proposed-native-source/include/atlas/tensor.hpp','proposed-native-source/include/atlas/trace_accuracy.hpp','proposed-native-source/include/atlas/path_error_control.hpp','proposed-native-source/include/atlas/implicit_seed.hpp','proposed-native-source/include/atlas/derivative_tail.hpp','proposed-native-source/include/atlas/numerics/symmetric_spectral.hpp']:
 assert (OLD/p).read_bytes()==(B/p).read_bytes(),p
checkpoint=OLD/'checkpoint-manifest.json';assert sha(checkpoint)=='885b324bfc8213b570b21fe03a6a5f7ae3634d5adda2f5ef8043c97b06f3aa6d'
r=json.loads((OLD/'native-performance-results.json').read_text());assert r['passed'] is False and r['timeout']
out={'id':'REVIEW-lade-hierarchical-seeds-closure-v2','freeze_sha256':sha(f),'verified_frozen_files':len(j['files']),'path_only_checker_changes':checks,'model_sha256':sha(B/'model.json'),'prior_failed_checkpoint_sha256':sha(checkpoint),'prior_timeout_seconds':r['elapsed_seconds'],'compiled_execution':False,'material_advance':False}
(D/'freeze-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'files':len(j['files']),'checkers':len(checks),'prior_failure_retained':True}))
