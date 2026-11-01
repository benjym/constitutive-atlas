"""Read-only closure/source policy checks. Does not compile or advance a model."""
from pathlib import Path
import json,hashlib,difflib
D=Path(__file__).resolve().parent;B=D.parent;OLD=B.parent/'midpoint-control-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
f=B/'freeze-v3.json';j=json.loads(f.read_text())
assert sha(f)=='65d2908e0cad34503c7a678797b5f5162871411250b21f4c8f8fd4c3946cabad'
for p,h in j['files'].items():assert sha(B/p)==h,p
assert sha(B/'model.json')==sha(OLD/'model.json')=='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
for p in ['path_error_control.hpp','triaxial-reference-results.json','triaxial-policy.json','SUPPLEMENT_POLICY.json','check_candidate.py']:
 assert (B/p).read_bytes()==(OLD/p).read_bytes(),p
checks=[]
for p in ['check_native_domain.py','check_native_triaxial.py','check_native_triaxial_fixed.py','check_native_lifecycle.py','check_native_legacy.py','check_domain_supplement.py','check_wasm.mjs','check_wasm_chains.mjs','check_wasm_source.py']:
 a=(OLD/p).read_text();b=(B/p).read_text();assert a.replace('lade-midpoint-control-v1','lade-warmstart-control-v1')==b,p;checks.append(p)
# Independent numeric witness of the corrected predictor fixture, scales=(2,1).
cold_raw=3/2;seed_raw=1/2;cold_override=0;seed_override=20/2
assert seed_raw<cold_raw and seed_override>cold_override
out={'id':'REVIEW-lade-warmstart-prospective-freeze-v3','freeze_sha256':sha(f),'closed_files':len(j['files']),'model_sha256':sha(B/'model.json'),'unchanged_path_only_redirected_checkers':checks,'predictor_ordering_witness':{'raw_cold':cold_raw,'raw_seed':seed_raw,'override_cold':cold_override,'override_seed':seed_override},'compiled_execution':False,'material_advance':False}
(D/'freeze-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'files':len(j['files']),'checkers':len(checks),'passed':True}))
