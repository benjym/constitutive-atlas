"""Source-only evidence replay; never executes a compiled artifact."""
from pathlib import Path
import json,hashlib,gzip,sys,subprocess,tempfile,shutil
from datetime import datetime
P=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def verify():
 freeze=load(P/'prospective-freeze.json')
 assert freeze['compiled_calls_observed']==0
 for name,digest in freeze['files'].items():assert sha(P/name)==digest,name
 evidence=load(P/'evidence-manifest.json')
 for name,digest in evidence['files'].items():assert sha(P/name)==digest,name
 reference=load(P/'reference/manifest.json')
 for name,record in reference['files'].items():
  digest=record['sha256']if isinstance(record,dict)else record
  assert sha(P/'reference'/name)==digest,name
 # Explicit trusted capsule; no live Atlas/compiler modules or root replacement.
 with tempfile.TemporaryDirectory(prefix='atlas-spectral-source-replay-')as temp:
  capsule=Path(temp)
  for name in freeze['files']:
   src=P/name;dst=capsule/name;assert not src.is_symlink();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
  for role in ('native','wasm'):
   dst=capsule/role;dst.mkdir();shutil.copyfile(P/role/'responses.jsonl.gz',dst/'responses.jsonl.gz')
  code="""import sys,json,gzip,subprocess
from pathlib import Path
sys.path.insert(0,sys.argv[1])
import study,check_assessor
p=Path(sys.argv[1])
assert gzip.decompress((p/'requests.json.gz').read_bytes())==(json.dumps(study.assemble(),separators=(',',':'))+'\n').encode()
ref=subprocess.run([sys.executable,'-B',str(p/'reference/check.py')],check=True,capture_output=True,text=True)
assert json.loads(ref.stdout)==study.load(p/'reference/check-results.json')
assert check_assessor.check()==study.load(p/'assessor-contract-results.json')
for role in ('native','wasm'):
 rows=[json.loads(line)for line in gzip.decompress((p/role/'responses.jsonl.gz').read_bytes()).splitlines()]
 a=study.assess(rows)
 print(json.dumps({'role':role,'assessment':a},sort_keys=True))
"""
  completed=subprocess.run([sys.executable,'-I','-B','-c',code,str(capsule)],check=True,capture_output=True,text=True)
  replayed=[json.loads(line)for line in completed.stdout.splitlines()]
  assert len(replayed)==2
  for row in replayed:assert row['assessment']==load(P/row['role']/'assessment.json')
 executions={role:load(P/role/'execution.json')for role in ('native','wasm')}
 assert datetime.fromisoformat(executions['native']['finished'])<=datetime.fromisoformat(executions['wasm']['started'])
 artifact_counts={'verified':0,'unavailable':0}
 for role,record in executions.items():
  assert record['freeze_sha256']==sha(P/'prospective-freeze.json')and record['compiled_calls']==1136
  assert record['configure']['returncode']==record['build']['returncode']==record['runtime_returncode']==0
  assert record['commands'][1][-4:]==['--target','atlas_spectral_study','--parallel','1']
  for name,digest in record['artifacts'].items():
   artifact=Path(name)
   if artifact.exists():assert sha(artifact)==digest;artifact_counts['verified']+=1
   else:artifact_counts['unavailable']+=1
 n=[json.loads(x)for x in gzip.decompress((P/'native/responses.jsonl.gz').read_bytes()).splitlines()]
 w=[json.loads(x)for x in gzip.decompress((P/'wasm/responses.jsonl.gz').read_bytes()).splitlines()]
 assert len(n)==len(w)==1136
 return {'prospective_source_files_verified':len(freeze['files']),'evidence_files_verified':len(evidence['files']),'copied_source_replay_exact_assessments':True,'reference_adequacy_reproduced':True,'literal_requests_regenerated':True,'synthetic_assessor_checks_reproduced':True,'native_then_wasm_serial_order_verified':True,'artifact_hashes':artifact_counts,'requests_per_backend':1136,'independent_accuracy_passed_both_backends':all(load(P/r/'assessment.json')['passed']for r in executions),'observed_exact_output_matches':sum(a['output']==b['output']for a,b in zip(n,w)),'observed_status_matches':sum(a['status']==b['status']for a,b in zip(n,w)),'cross_backend_bit_equality_is_acceptance_gate':False,'compiled_calls_during_verification':0,'production_DSL_integrated':False,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2,sort_keys=True))
