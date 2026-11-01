"""Saved-only recomputation of all57 legacy parity records; no artifact calls."""
from pathlib import Path
import hashlib,json,math,struct
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];read=lambda p:json.loads(p.read_text());h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();pins={}
def pin(q):pins[str(q.relative_to(ROOT))]=h(q)
for name in ['freeze-v3.json','wasm-build-receipt.json']:
 q=P/name;pin(q)
 for n,s in read(q)['files'].items():assert h(ROOT/n)==s,n
count=0
for q in (P/'proposed-native-source').rglob('*'):
 if q.is_file():
  r=P/'wasm-bounded-v1/CMakeLists.txt' if q.name=='CMakeLists.txt' else q
  assert (ROOT/'.local/lade-fused-linear-v1/wasm-source'/q.relative_to(P/'proposed-native-source')).read_bytes()==r.read_bytes(),str(q);count+=1
r=read(P/'wasm-legacy-prerequisite-results.json');pin(P/'wasm-legacy-prerequisite-results.json');native=read(P/'native-legacy-results.json');pin(P/'native-legacy-results.json')
assert r['passed'] is True and r['historical_legacy_passed'] is True and len(r['records'])==len(native['requests'])==57
assert r['input_report_hashes']=={'native-legacy-results.json':h(P/'native-legacy-results.json')}
assert r['checker_sha256']==h(P/'check_wasm_legacy_prerequisite.mjs')
m=ROOT/'.local/lade-fused-linear-v1/wasm-legacy-prerequisite-bounded/manifest.json';pin(m);workers=read(m)['records'];assert len(workers)==57
for file,key in [('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256')]:assert h(ROOT/'.local/lade-fused-linear-v1/wasm-build'/file)==r[key]
def compare(a,b,unit=False):
 assert isinstance(a,list) and isinstance(b,list) and len(a)==len(b) and all(type(v) in (int,float) and math.isfinite(v) for v in a+b)
 return max([0.]+[abs(x-y)/(1 if unit else ([101325]*6+[40,101325])[i] if i<8 else 101325) for i,(x,y) in enumerate(zip(a,b))])
maxerr=0.
for i,(row,rec,wk) in enumerate(zip(native['requests'],r['records'],workers)):
 assert rec['index']==i and rec['study']=='native-legacy-results.json'
 cmd=row['command'];get=lambda k,f='':cmd[cmd.index(k)+1] if k in cmd else f
 n=row.get('response') or read(ROOT/row['raw_path']);w=read(ROOT/rec['raw_path']);assert h(ROOT/rec['raw_path'])==rec['raw_sha256'];pin(ROOT/rec['raw_path'])
 req=wk['request']
 for key in ['loader','wasm']:assert h(Path(req[key]))==req[key+'_sha256']
 assert h(P/'wasm-bounded-v1/worker.mjs')==req['worker_sha256']
 args=[struct.unpack('>d',bytes.fromhex(v['binary64']))[0] if isinstance(v,dict) else v for v in req['encoded_args']]
 expected=[get('--model'),get('--parameters'),get('--initial')]
 if get('--mode')=='integrate':expected+=[get('--strain')]+([get('--integration-settings')] if get('--integration-settings') else [])
 else:expected += [float(get('--protocol','0')),float(get('--target','0')),float(get('--steps','1')),float(get('--cycles','0')),get('--integration-settings')]
 assert args==expected
 assert wk['status']==0 and wk['signal'] is None and wk['error'] is None and wk['elapsed_ms']<120000 and wk['timeout_ms']==120000 and wk['maxBuffer']==67108864
 for key in ['stdout','stderr']:
  q=Path(wk[key]['path']);assert h(q)==wk[key]['sha256']
 assert read(Path(wk['stdout']['path']))==w
 assert n['ok']==w['ok']==rec['native_ok']==rec['wasm_ok'] and rec['status_match'] and rec['shape_match'] and rec['passed']
 error=strain=control=0.
 if 'points' in n:
  assert len(n['points'])==len(w['points'])
  for a,b in zip(n['points'],w['points']):
   error=max(error,compare(a['state'],b['state']));strain=max(strain,compare(a['strain'],b['strain'],True));control=max(control,abs(a['control']-b['control']))
 else:
  assert isinstance(n.get('state'),list)==isinstance(w.get('state'),list)
  if 'state' in n:error=compare(n['state'],w['state'])
 if '--strain' in cmd:
  parent=list(map(float,get('--initial').split(',')));de=list(map(float,get('--strain').split(',')))
  if (w['ok'] and all(x==0 for x in de)) or (not w['ok'] and 'state' in w):assert w['state']==parent
 for key in ['integration_settings','loading','response_contract','stress','catalogue_hash']:assert n.get(key)==w.get(key),key
 assert error==rec['max_scaled_state_error'] and strain==rec['max_absolute_strain_error'] and control==rec['max_absolute_control_error']
 assert error<=1e-8 and strain<=1e-10 and control<=1e-12 and rec['max_relative_stress_error']==0
 maxerr=max(maxerr,error)
assert r['records'][44]['native_ok'] is True and r['records'][44]['wasm_ok'] is True
out={'passed':True,'scope':'all57 legacy backend prerequisite only, no vacuous v4 flag used','source_mirror_files':count,'records':57,'max_scaled_state_error':maxerr,'old_case44_status_matches':True,'compiled_execution':False,'pins':pins}
(P/'independent-review/saved-wasm-legacy-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='pins'}))
