"""Saved-only delivery handoff verification. Never runs compiled/material code."""
from pathlib import Path
import json,hashlib,subprocess,sys,sqlite3
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=BASE.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 freeze=json.loads((HERE/'input-freeze.json').read_text())
 for n,h in freeze.items():
  q=Path(n);q=q if q.is_absolute() else ROOT/q
  if sha(q)!=h:raise RuntimeError('changed input '+n)
 runtime=BASE/'runtime-v1'
 proc=subprocess.run([sys.executable,'-B',str(runtime/'assess.py')],capture_output=True,text=True,check=True)
 assessed=json.loads(proc.stdout)
 if assessed!=json.loads((runtime/'ASSESSMENT.json').read_text()) or not assessed['pass']:raise RuntimeError('runtime saved-only replay mismatch')
 replay=subprocess.run([sys.executable,'-B',str(BASE/'browser-v2/check_replay.py')],capture_output=True,text=True,check=True)
 replayed=json.loads(replay.stdout)
 if replayed!=json.loads((BASE/'browser-v2/REPLAY_CHECK.json').read_text()):raise RuntimeError('browser replay mismatch')
 identity=subprocess.run([sys.executable,'-B',str(BASE/'browser-identity-v1/check.py')],capture_output=True,text=True,check=True)
 delivered=json.loads(identity.stdout)
 if delivered['status']!='pass':raise RuntimeError('browser identity failed')
 site=ROOT/'.local/clay2013-current-delivery-v1/site'
 package=json.loads((BASE/'PACKAGE_MANIFEST.json').read_text())['files']
 actual={str(q.relative_to(site)) for q in site.rglob('*') if q.is_file()}
 if actual!=set(package):raise RuntimeError('package filename set changed')
 for n,item in package.items():
  q=site/n
  if q.stat().st_size!=item['bytes'] or sha(q)!=item['sha256']:raise RuntimeError('package identity '+n)
 for n in ['models/hypoplastic-clay-2013.json','evidence-records/catalogue/agent-reviews/hypoplastic-clay-2013-agent-v1.json','evidence-records/catalogue/approved-models.json']:
  root_name=n.removeprefix('evidence-records/')
  if (site/n).read_bytes()!=(ROOT/root_name).read_bytes():raise RuntimeError('packaged canonical identity '+n)
 return {'status':'PASS','input_bindings':len(freeze),'package_files':len(package),'current_runtime_saved_assessment':assessed,'browser_full_state_replay':replayed,'fresh_browser_server_delivered_identity':{'status':delivered['status'],'assets':sorted(delivered['required_deliveries']),'journal_sha256':delivered['journal_sha256'],'export_sha256':delivered['export_sha256']},'reviewer_builds':0,'reviewer_compiled_calls':0,'reviewer_material_calls':0,'remote_actions':0}
if __name__=='__main__':print(json.dumps(main(),indent=2))
