from pathlib import Path
import hashlib,importlib.util,json,sys
ROOT=Path(__file__).resolve().parents[4]
N=ROOT/'docs/delivery/unheld-finalisation-20261105-v1'
P=Path(__file__).resolve().parent
plan=json.loads((P/'plan.json').read_text())
for x in plan['pins']:
 q=Path(x['path']);assert q.stat().st_size==x['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==x['sha256']
phase=sys.argv[1];assert phase in plan['commands']
if phase!='freeze':
 prior={'native':'freeze','wasm':'native','pair':'wasm'}[phase]
 r=json.loads((P/('outer-'+prior)/'receipt.json').read_text());assert r['status']=='passed' and r['returncode']==0 and r['mandatory_reap'] is True
observer=Path(plan['observer']);spec=importlib.util.spec_from_file_location('original_observer',observer);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
r=m.observe(plan['commands'][phase],plan['cwd'],P/('outer-'+phase),env=plan['environment'],timeout=1800)
print(json.dumps({'phase':phase,'returncode':r.returncode,'status':r.receipt['status'],'mandatory_reap':r.receipt['mandatory_reap']}))
assert r.returncode==0,'first failure retained; no later phase'
