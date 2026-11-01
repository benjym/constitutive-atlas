"""Saved-only prerequisite verification. No subprocess/material API."""
from pathlib import Path
import hashlib,json,math
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=P/'native-performance-results.json';r=read(report);raw=ROOT/'.local/lade-outer-predictor-v1/performance-raw.json';a=read(raw)
f=read(P/'freeze-v1.json')
for n,s in f['files'].items():assert h(P/n)==s,n
build=read(P/'native-build-receipt.json')
for n,s in build['files'].items():assert h(ROOT/n)==s,n
assert h(raw)==r['raw_sha256'] and h(Path(r['command'][0]))==r['exe_sha256']
expected=[str(ROOT/'.local/lade-outer-predictor-v1/native-build/atlas_lade_domain_candidate'),'--model','lade-duncan-1975-midpoint-elastic-eq19-gap-v4','--parameters','101325,103,40,0.44,0.957,0.000255,1.32,2300,0.8,0','--initial','60000,60000,60000,0,0,0,13,0','--protocol','1','--target','0.005','--steps','1600','--response-contract','stress-scope-0.1','--integration-settings','7.8125e-13,1e-06,45,20,200000,11,3.90625e-10,1']
assert r['command']==expected and r['timeout_seconds']==120 and 0<r['elapsed_seconds']<120
assert r['passed'] and r['returncode']==0 and r['ok'] and a['ok'] and len(a['points'])==1601
minpressure=math.inf
for pt in a['points']:
 s=pt['state'];de=pt['strain'];assert len(s)==8 and len(de)==6 and all(math.isfinite(x) for x in s+de+[pt['control']])
 x,y,z,b,c,d=s[:6];b/=math.sqrt(2);c/=math.sqrt(2);d/=math.sqrt(2);det=x*y*z+2*b*c*d-x*c*c-y*d*d-z*b*b;T=x+y+z
 assert x>0 and x*y-b*b>0 and det>0
 criterion=T**3/det;H=max(40,criterion+max(s[6],0))
 assert criterion<=103*(1+1e-10) and H>=criterion and s[7]>=-1e-10
 minpressure=min(minpressure,4*T/(103*(1+1e-10)))
ref=next(x['reference'] for x in read(P/'triaxial-reference-results.json')['cases'] if x['set']=='dense' and x['reference']['axial_strain']==.005);last=a['points'][-1]
errors={'relative_axial_stress':abs(last['state'][0]-ref['axial_stress'])/ref['axial_stress'],'absolute_radial_strain':abs(last['strain'][1]-ref['radial_strain']),'relative_work_using_1Pa_floor':abs(last['state'][7]-ref['wp'])/max(1,abs(ref['wp']))}
assert errors==r['errors']
bounds=read(P/'triaxial-policy.json')['native_final_reference_bounds'];assert all(errors[k]<=v for k,v in bounds.items())
assert last['control']==.005
files=[report,raw,P/'freeze-v1.json',P/'native-build-receipt.json',P/'triaxial-policy.json',P/'triaxial-reference-results.json',P/'independent-review/saved-helper-review-receipt.json']
out={'passed':True,'scope':'exact saved native hardcase prerequisite only','points':1601,'elapsed_seconds':r['elapsed_seconds'],'source_errors':errors,'bounds':bounds,'all_points_finite_SPD_and_prefailure':True,'minimum_conservative_least_pressure_bound_Pa':minpressure,'pins':{str(q.relative_to(ROOT)):h(q) for q in files}}
(P/'independent-review/saved-performance-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='pins'}))
