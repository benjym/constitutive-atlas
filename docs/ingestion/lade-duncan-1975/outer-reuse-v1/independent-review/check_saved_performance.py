"""Saved-only exact prerequisite/reference check. Never invokes an artifact."""
from pathlib import Path
import json,hashlib,math
D=Path(__file__).resolve().parent;B=D.parent;sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((B/'native-performance-results.json').read_text());raw=Path('.local/lade-outer-reuse-v1/performance-raw.json');assert sha(raw)==r['raw_sha256'];assert sha(Path(r['command'][0]))==r['exe_sha256'];response=json.loads(raw.read_text())
assert r['passed'] and r['returncode']==0 and r['ok'] is True and response['ok'] is True and len(response['points'])==1601
assert r['timeout_seconds']==120 and r['elapsed_seconds']<120
expected=['--model','lade-duncan-1975-midpoint-elastic-eq19-gap-v4','--parameters','101325,103,40,0.44,0.957,0.000255,1.32,2300,0.8,0','--initial','60000,60000,60000,0,0,0,13,0','--protocol','1','--target','0.005','--steps','1600','--response-contract','stress-scope-0.1','--integration-settings','7.8125e-13,1e-06,45,20,200000,11,3.90625e-10,1'];assert r['command'][1:]==expected
ref=next(x['reference'] for x in json.loads((B/'triaxial-reference-results.json').read_text())['cases'] if x['set']=='dense' and x['reference']['axial_strain']==.005);bounds=json.loads((B/'triaxial-policy.json').read_text())['native_final_reference_bounds'];point=response['points'][-1]
errors={'relative_axial_stress':abs(point['state'][0]-ref['axial_stress'])/ref['axial_stress'],'absolute_radial_strain':abs(point['strain'][1]-ref['radial_strain']),'relative_work_using_1Pa_floor':abs(point['state'][7]-ref['wp'])/max(1,abs(ref['wp']))}
assert errors==r['errors'] and all(math.isfinite(v) and v<=bounds[k] for k,v in errors.items())
for i,p in enumerate(response['points']):
 assert len(p['state'])==8 and len(p['strain'])==6 and all(math.isfinite(v) for v in p['state']+p['strain']);assert p['control']==.005*i/1600
out={'id':'REVIEW-lade-outer-reuse-saved-performance-v1','raw_sha256':sha(raw),'exe_sha256':r['exe_sha256'],'point_count':1601,'elapsed_seconds':r['elapsed_seconds'],'independently_recomputed_errors':errors,'frozen_bounds':bounds,'prerequisite_passed':True,'full_qualification':False,'compiled_execution':False,'material_advance':False}
(D/'saved-performance-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
