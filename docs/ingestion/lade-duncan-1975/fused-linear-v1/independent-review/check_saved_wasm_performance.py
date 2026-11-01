"""Saved-only Wasm prerequisite, source and native parity audit."""
from pathlib import Path
import hashlib,json,math,struct
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
def pin(p):pins[str(p.relative_to(ROOT))]=h(p)
for name in ['freeze-v3.json','wasm-build-receipt.json']:
 q=P/name;d=read(q);pin(q)
 for n,s in d['files'].items():assert h(ROOT/n)==s,n
source=P/'proposed-native-source';mirror=ROOT/'.local/lade-fused-linear-v1/wasm-source';count=0
for q in source.rglob('*'):
 if q.is_file():
  counterpart=P/'wasm-bounded-v1/CMakeLists.txt' if q.name=='CMakeLists.txt' else q
  assert (mirror/q.relative_to(source)).read_bytes()==counterpart.read_bytes(),str(q);count+=1
report=P/'wasm-performance-results.json';r=read(report);pin(report);m=ROOT/r['manifest']['path'];assert h(m)==r['manifest']['sha256'];pin(m)
records=read(m)['records'];assert len(records)==1;row=records[0]
assert row['timeout_ms']==120000 and row['maxBuffer']==67108864 and row['status']==0 and row['signal'] is None and row['error'] is None and 0<row['elapsed_ms']<120000
for key in ['stdout','stderr']:
 q=Path(row[key]['path']);assert h(q)==row[key]['sha256'];pin(q)
req=row['request'];assert req['name']=='atlas_run_scope_with_settings' and req['result']=='string' and req['types']==['string']*3+['number']*4+['string']
for key in ['loader','wasm']:assert h(Path(req[key]))==req[key+'_sha256']
assert h(P/'wasm-bounded-v1/worker.mjs')==req['worker_sha256']
args=[struct.unpack('>d',bytes.fromhex(v['binary64']))[0] if isinstance(v,dict) else v for v in req['encoded_args']]
assert args==[read(P/'model.json')['id'],'101325,103,40,0.44,0.957,0.000255,1.32,2300,0.8,0','60000,60000,60000,0,0,0,13,0',1.,.005,1600.,0.,'7.8125e-13,1e-06,45,20,200000,11,3.90625e-10,1']
a=read(Path(row['stdout']['path']));native=ROOT/'.local/lade-fused-linear-v1/performance-raw.json';n=read(native);pin(native)
assert r['passed'] and a['ok'] and n['ok'] and len(a['points'])==len(n['points'])==1601
for key in ['integration_settings','loading','response_contract','stress','catalogue_hash']:assert a.get(key)==n.get(key),key
def bound(s):
 x,y,z,b,c,d=s[:6];b/=math.sqrt(2);c/=math.sqrt(2);d/=math.sqrt(2);det=x*y*z+2*b*c*d-x*c*c-y*d*d-z*b*b;t=x+y+z
 assert x>0 and x*y-b*b>0 and det>0 and t**3/det<=103*(1+1e-10)
 return 4*t/(103*(1+1e-10))
mx={'scaled_state':0.,'pressure_relative_stress':0.,'strain':0.,'control':0.}
for wp,np in zip(a['points'],n['points']):
 s,t=wp['state'],np['state'];assert len(s)==len(t)==8 and len(wp['strain'])==len(np['strain'])==6
 assert all(isinstance(x,(int,float)) and math.isfinite(x) for x in s+t+wp['strain']+np['strain']+[wp['control'],np['control']])
 mx['scaled_state']=max(mx['scaled_state'],max(abs(x-y)/z for x,y,z in zip(s,t,[101325]*6+[40,101325])))
 mx['pressure_relative_stress']=max(mx['pressure_relative_stress'],math.hypot(*(x-y for x,y in zip(s[:6],t[:6])))/min(bound(s),bound(t)))
 mx['strain']=max(mx['strain'],max(abs(x-y) for x,y in zip(wp['strain'],np['strain'])))
 mx['control']=max(mx['control'],abs(wp['control']-np['control']))
assert all(mx[k]<=v for k,v in {'scaled_state':1e-8,'pressure_relative_stress':1e-6,'strain':1e-10,'control':1e-12}.items())
ref=next(x['reference'] for x in read(P/'triaxial-reference-results.json')['cases'] if x['set']=='dense' and x['reference']['axial_strain']==.005);pt=a['points'][-1]
errors={'relative_axial_stress':abs(pt['state'][0]-ref['axial_stress'])/ref['axial_stress'],'absolute_radial_strain':abs(pt['strain'][1]-ref['radial_strain']),'relative_work_using_1Pa_floor':abs(pt['state'][7]-ref['wp'])/max(1,abs(ref['wp']))}
assert errors==r['errors'] and all(errors[k]<=v for k,v in read(P/'triaxial-policy.json')['native_final_reference_bounds'].items())
assert pt['control']==.005
for name,key in [('model.json','model_sha256'),('triaxial-reference-results.json','reference_sha256'),('triaxial-policy.json','policy_sha256')]:
 assert h(P/name)==r[key];pin(P/name)
pin(P/'independent-review/saved-native-performance-review-receipt.json')
out={'passed':True,'scope':'saved exact Wasm hardcase prerequisite only, not full qualification','source_mirror_files':count,'points':1601,'elapsed_ms_including_initialization':row['elapsed_ms'],'source_errors':errors,'maximum_allpoint_native_Wasm_differences':mx,'pins':pins}
(P/'independent-review/saved-wasm-performance-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='pins'}))
