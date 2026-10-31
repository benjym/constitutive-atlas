"""Portable exact saved-evidence replay; no builds or candidate execution."""
from pathlib import Path
import json,hashlib,tempfile,shutil,subprocess,sys
s=Path(__file__).resolve().parent;parent=Path(sys.argv[1])if len(sys.argv)>1 else s.parent/'mc-laboratory-preview-v1'
pins=json.loads((s/'manifest.json').read_text())
for n,p in pins.items():assert hashlib.sha256((s/n).read_bytes()).hexdigest()==p,n
with tempfile.TemporaryDirectory(prefix='mc-envelope-v2-replay-')as d:
 t=Path(d);shutil.copytree(s,t,dirs_exist_ok=True)
 (t/'assessment.json').unlink()
 for label,args in [('preflight',['preflight.py']),('apply',['apply.py',str(parent.resolve())])]:
  p=subprocess.run([sys.executable,'-B',*args],cwd=t,capture_output=True,text=True)
  assert p.returncode==(0 if label=='preflight'else 1),(label,p.stdout,p.stderr)
 assert json.loads((t/'preflight-results.json').read_text())==json.loads((s/'preflight-results.json').read_text())
 assert json.loads((t/'assessment.json').read_text())==json.loads((s/'assessment.json').read_text())
print(json.dumps({'replay_passed':True,'failed_overall_outcome_preserved':not json.loads((s/'assessment.json').read_text())['passed'],'new_candidate_calls':0,'new_builds':0}))
