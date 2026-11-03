"""Independent saved-evidence checks only; never launches compiled artifacts."""
from pathlib import Path
import hashlib,json,math
import numpy as np
O=Path(__file__).resolve().parent.parent;R=O.parents[3]
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((O/'candidate/s-clay1.json').read_text());assert h(O/'candidate/s-clay1.json')=='2d1518c1aee44d9adec35229adc83b32a9f39d9175f307c8ddfd90cdfbd1caec'
assert h(R/'.local/private-sources/s-clay1/supplied-original-v3/original.pdf')=='1923aff43b80f14970dec624deb8f78b09635f419adbf71d797fa0a1a4169511'
manifest=json.loads((O/'build-source-manifest.json').read_text())
for p,d in manifest['files'].items(): assert h(R/manifest['root']/p)==d,p
for p,d in json.loads((O/'policy.json').read_text())['files'].items(): assert h(R/p)==d,p
base=[float(x) for f in m['state'] for x in (f['initial'] if f['shape']=='sym' else [f['initial']])]
scales=np.array([20000.]*6+[1.]*7+[20000.])
mat=lambda x:np.array([[x[0],x[3]/math.sqrt(2),x[5]/math.sqrt(2)],[x[3]/math.sqrt(2),x[1],x[4]/math.sqrt(2)],[x[5]/math.sqrt(2),x[4]/math.sqrt(2),x[2]]])
def check_state(z,M=1.1,pref=20000):
 assert len(z)==15 and all(math.isfinite(x) for x in z)
 S,A=mat(z[:6]),mat(z[6:12]);p=np.trace(S)/3;s=S-p*np.eye(3);t=s-p*A;a2=1.5*np.trace(A@A)
 f=(1.5*np.trace(t@t)-(M*M-a2)*(z[13]-p)*p)/pref**2
 assert p>0 and z[12]>1 and z[13]>0 and a2<M*M and abs(np.trace(A))<1e-8
 assert f<=2e-8 and z[14]>=-1e-9,(f,z[14])
 return float(f)
logs=[];counts={};states=0;maxyield=-math.inf
for name in ['native-v1','native-v2']:
 rows=[json.loads(l) for l in (O/name/'calls.jsonl').read_text().splitlines()];counts[name]=len(rows)
 for row in rows:
  out=json.loads(row['stdout']); args=dict(zip(row['argv'][1::2],row['argv'][2::2]));assert row['returncode']==(0 if out['ok'] else 1)
  if out['ok'] and args['--model']=='s-clay1':
   par=[float(f['default']) for f in m['parameters'].values()] if '--parameters' not in args else list(map(float,args['--parameters'].split(',')))
   for z in ([out['state']] if 'state' in out else [x['state'] for x in out.get('points',[])]):
    maxyield=max(maxyield,check_state(z,par[1],par[0]));states+=1
  logs.append((args,out))
assert counts=={'native-v1':1435,'native-v2':9}
r1=json.loads((O/'native-v1/results.json').read_text());assert not r1['ok'] and 'IndexError' in r1['failure']
r2=json.loads((O/'native-v2/results.json').read_text());assert r2['ok'] and r2['checks']==716
reference_errors=[]
for n in [128,256,512]:
 entry=r1['reference_'+str(n)];error=float(np.max(np.abs(np.array(entry['actual'][:14])-np.array(entry['reference'][:14]))/scales))
 assert error==entry['error'];reference_errors.append(error)
assert reference_errors[-1]<reference_errors[0] and reference_errors[-1]<3e-3
# Explicit fullsaved default curves, declared parameter edits and controls.
for i,(args,out) in enumerate(logs[-9:-2]):
 pts=out['points'];assert len(pts)==101 and pts[-1]['q']!=pts[0]['q']
 assert pts[-1]['control']==.01
 if args['--protocol']=='2': assert all(abs(x['state'][12]-3.46)<1e-12 for x in pts)
 else: assert max(abs(x['state'][1]-12500) for x in pts)<.01
# Forced whole-call failure carries incoming full parent, recovery/replay deterministic.
forced=[(a,o) for a,o in logs if '--integration-settings' in a];assert len(forced)==1 and not forced[0][1]['ok'] and forced[0][1]['state']==base
assert logs[1431][1]['state']==logs[1432][1]['state']
assert logs[1433][1]['state']==logs[1434][1]['state']
# Independently inspect fifty stored interpreted/native residual comparisons.
res=json.loads((O/'native-interpreter-calls.json').read_text());maximum=0.
for row in res:
 out=json.loads(row['stdout']);assert out['ok'] and row['returncode']==0 and len(out['values'])==len(row['interpreter'])==15
 err=max(abs(a-b)/s for a,b,s in zip(out['values'],row['interpreter'],list(scales)+[1.]));assert err<1e-10;maximum=max(maximum,err)
assert len(res)==50
result={'ok':True,'reviewer':'/root/norsand_original_review','source_manifest_files':len(manifest['files']),'native_calls':counts,'checked_full_persistent_states':states,'maximum_normalized_yield':maxyield,'reference_errors':reference_errors,'residual_parity_cases':50,'maximum_interpreter_native_residual_error':maximum,'forced_failure_parent_exact':True,'deterministic_recovery_replay':True,'candidate_sha256':h(O/'candidate/s-clay1.json'),'native_sha256':r1['executable_sha256'],'scope':'saved histories/hash/physics/math audit only; no compiled execution'}
print(json.dumps(result,indent=2))
