"""Source-only replay and exact parent/artifact binding verification."""
from pathlib import Path
import json,hashlib,subprocess,sys,tempfile,shutil
s=Path(__file__).resolve().parent;base=s.parent/'terracotta-preparation-hold-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((s/'manifest.json').read_text());bindings=json.loads((s/'parent-bindings.json').read_text())
assert bindings['directory']=='../terracotta-preparation-hold-v1'
for n,h in manifest.items():assert sha(s/n)==h,n
for n,h in bindings['files'].items():assert sha(base/n)==h,n
if(s/'evidence-manifest.json').exists():
 for n,h in json.loads((s/'evidence-manifest.json').read_text()).items():assert sha(s/n)==h,n
freeze=json.loads((s/'prospective-freeze.json').read_text());assert freeze['new_compiled_observations']==0 and freeze['parent_compiled_observations']==18
assert freeze['manifest_sha256']==sha(s/'manifest.json') and freeze['parent_bindings_sha256']==sha(s/'parent-bindings.json')
old=json.loads((base/'requests.json').read_text())['records'];rows=json.loads((s/'requests.json').read_text())['records']
assert len(old)==9 and len(rows)==3
for added in rows:
 parent=next(r for r in old if r['case']==added['case'] and r['relative_tolerance']==1e-8)
 wanted=json.loads(json.dumps(parent));wanted['relative_tolerance']=2.5e-9;wanted['request']['solver']['relative_tolerance']=2.5e-9;assert wanted==added
receipts={}
for role in ('native','wasm'):
 out=s/role;receipt=json.loads((out/'receipt.json').read_text());receipts[role]=receipt
 parent=json.loads((base/role/'receipt.json').read_text())
 assert receipt['completed'] is True and receipt['rebuild'] is False
 assert receipt['parent_receipt_sha256']==sha(base/role/'receipt.json') and receipt['artifacts']==parent['artifacts']
 for item in receipt['artifacts'].values():assert sha(Path(item['path']))==item['sha256']
 assert receipt['journal_sha256']==sha(out/'journal.json')
 assert all(c['returncode']==0 for c in receipt['commands'])
 observations=json.loads((out/'journal.json').read_text());assert len(observations)==3
 if role=='native':
  for i,row in enumerate(observations):assert row['raw']==(out/('request-'+str(i)+'.stdout.txt')).read_text()
assert freeze['utc']<=receipts['native']['started_utc'] and receipts['native']['finished_utc']<=receipts['wasm']['started_utc']
assert json.loads((base/'assessment.json').read_text())['status']=='failed'
with tempfile.TemporaryDirectory(prefix='atlas-terracotta-v2-replay-') as temp:
 parent=Path(temp)/base.name;clone=Path(temp)/s.name;parent.mkdir();clone.mkdir()
 for name in bindings['files']:
  target=parent/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/name,target)
 for name in manifest:
  target=clone/name;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(s/name,target)
 for role in ('native','wasm'):
  (clone/role).mkdir();shutil.copyfile(s/role/'journal.json',clone/role/'journal.json')
 subprocess.run([sys.executable,'-I','-B',str(parent/'verify_study.py')],check=True,capture_output=True)
 subprocess.run([sys.executable,'-I','-B',str(clone/'evaluate.py')],check=True,capture_output=True)
 original=json.loads((s/'assessment.json').read_text());replay=json.loads((clone/'assessment.json').read_text())
 def physical(value):
  if isinstance(value,dict):return {k:physical(v) for k,v in value.items() if k!='traceback'}
  if isinstance(value,list):return [physical(v) for v in value]
  return value
 assert physical(original)==physical(replay)
 exact=(s/'assessment.json').read_bytes()==(clone/'assessment.json').read_bytes()
print(json.dumps({'evidence_verified':True,'status':original['status'],'parent_outcome':'failed','parent_bindings':len(bindings['files']),'old_pairs_retained':9,'new_pairs':3,'exact_assessment_bytes':exact,'compiled_execution':False,'artifact_bytes_rehashed':True}))
