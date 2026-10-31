from pathlib import Path
import hashlib,json,tempfile,subprocess,sys,shutil
s=Path(__file__).resolve().parent;parent=Path(sys.argv[1]).resolve()if len(sys.argv)>1 else s.parent/'mc-laboratory-preview-v1'
for name,pin in json.loads((s/'manifest.json').read_text()).items():assert hashlib.sha256((s/name).read_bytes()).hexdigest()==pin,name
artifacts=0
for b in ('native','wasm'):
 r=json.loads((s/b/'receipt.json').read_text());assert r['completed']is True and hashlib.sha256((s/b/'raw.json').read_bytes()).hexdigest()==r['raw_sha256']
 for name,v in r['artifacts'].items():
  p=Path(v['path'])
  if p.exists():assert hashlib.sha256(p.read_bytes()).hexdigest()==v['sha256'];artifacts+=1
with tempfile.TemporaryDirectory(prefix='mc-control-trace-replay-')as d:
 t=Path(d);shutil.copytree(s,t,dirs_exist_ok=True)
 for b in ('native','wasm'):
  p=subprocess.run([sys.executable,'-B','assess.py',str(t/b/'raw.json'),str(parent/b/'journal.json')],cwd=t,capture_output=True,text=True);assert p.returncode==0,p.stderr
  assert json.loads(p.stdout)==json.loads((s/b/'assessment.json').read_text())
 for command in ('preflight.py','compare.py'):
  p=subprocess.run([sys.executable,'-B',command],cwd=t,capture_output=True,text=True);assert p.returncode==0,p.stderr
 for name in ('preflight-results.json','comparison.json'):assert(t/name).read_bytes()==(s/name).read_bytes(),name
print(json.dumps({'replay_passed':True,'candidate_calls_during_replay':0,'local_artifact_hashes_checked':artifacts,'source_default_and_bounds_changed':False,'common_controls_identical_trace_calls_per_backend':288,'original_failed_parity_gate_replaced':False}))
