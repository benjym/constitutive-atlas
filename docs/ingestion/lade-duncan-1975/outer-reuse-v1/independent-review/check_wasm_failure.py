"""Saved bytes only: no material API, subprocess, build or evidence rewrite."""
import hashlib,json,math,struct
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'docs/ingestion/lade-duncan-1975/outer-reuse-v1'
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p): return json.loads(p.read_text())
pins={}
for name in ['checkpoint-manifest.json','wasm-build-receipt.json','wasm-source-receipt.json']:
 p=BASE/name; d=read(p);pins[str(p.relative_to(ROOT))]=digest(p)
 for path,sha in d['files'].items():
  q=ROOT/path;assert digest(q)==sha,(path,sha)
m=ROOT/'.local/lade-outer-reuse-v1/wasm-bounded-literal/manifest.json'
pins[str(m.relative_to(ROOT))]=digest(m)
records=read(m)['records'];assert len(records)==12
native=read(BASE/'native-triaxial-results.json')['requests'];summary=[]
def bound(s,k):
 x,y,z,a,b,c=s[:6];a/=math.sqrt(2);b/=math.sqrt(2);c/=math.sqrt(2)
 det=x*y*z+2*a*b*c-x*b*b-y*c*c-z*a*a;t=x+y+z
 assert x>0 and x*y-a*a>0 and det>0 and t**3/det<=k*(1+1e-10)
 return 4*t/(k*(1+1e-10))
for i,r in enumerate(records):
 assert r['timeout_ms']==120000 and r['maxBuffer']==67108864
 req=r['request'];a=[struct.unpack('>d',bytes.fromhex(v['binary64']))[0] if isinstance(v,dict) else v for v in req['encoded_args']]
 cmd=native[i]['command'];get=lambda k:cmd[cmd.index(k)+1]
 assert a==[get('--model'),get('--parameters'),get('--initial'),float(get('--protocol')),float(get('--target')),float(get('--steps')),float(get('--cycles')) if '--cycles' in cmd else 0.0,get('--integration-settings')]
 for key in ['stdout','stderr']:
  q=Path(r[key]['path']);assert digest(q)==r[key]['sha256'];pins[str(q.relative_to(ROOT))]=digest(q)
 for key in ['loader','wasm']:
  assert digest(Path(req[key]))==req[key+'_sha256']
 if i<11:
  assert r['status']==0 and r['error'] is None and r['signal'] is None
  w=read(Path(r['stdout']['path']));n=native[i].get('response') or read(ROOT/native[i]['raw_path'])
  assert w['ok'] is True and n['ok'] is True and len(w['points'])==len(n['points'])==int(a[5])+1
  for k in ['integration_settings','loading','response_contract','stress','catalogue_hash']:
   assert w.get(k)==n.get(k),k
  maxstate=maxrelative=maxstrain=maxcontrol=0.
  k1=float(a[1].split(',')[1]);scales=[101325]*6+[40,101325]
  for wp,np in zip(w['points'],n['points']):
   s,t=wp['state'],np['state'];assert len(s)==len(t)==8 and all(math.isfinite(v) for v in s+t)
   maxstate=max(maxstate,max(abs(x-y)/z for x,y,z in zip(s,t,scales)))
   maxrelative=max(maxrelative,math.hypot(*(x-y for x,y in zip(s[:6],t[:6])))/min(bound(s,k1),bound(t,k1)))
   assert len(wp['strain'])==len(np['strain'])==6
   maxstrain=max(maxstrain,max(abs(x-y) for x,y in zip(wp['strain'],np['strain'])))
   maxcontrol=max(maxcontrol,abs(wp['control']-np['control']))
  assert maxstate<=1e-8 and maxrelative<=1e-6 and maxstrain<=1e-10 and maxcontrol<=1e-12
  summary.append(dict(index=i,points=len(w['points']),max_scaled_state=maxstate,max_pressure_relative_stress=maxrelative,max_strain=maxstrain,max_control=maxcontrol))
 else:
  assert r['status'] is None and r['signal']=='SIGKILL' and r['error']['code']=='ETIMEDOUT'
  assert Path(r['stdout']['path']).stat().st_size==Path(r['stderr']['path']).stat().st_size==0
  assert a[4]==.005 and a[5]==1600 and r['elapsed_ms']>=120000
for name in ['wasm-results.json','wasm-source-results.json','wasm-chains-results.json']:
 assert not (BASE/name).exists(),name
result=dict(verdict='FAILED bounded Wasm prerequisite; no aggregate or complete backend qualification',checkpoint_files=len(read(BASE/'checkpoint-manifest.json')['files']),verified_completed_literal_responses=11,failed_request_1based=12,failed_elapsed_ms=records[-1]['elapsed_ms'],completed=summary,pins=pins)
out=Path(__file__).with_name('wasm-failure-check-results.json');out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['pins','completed']}))
