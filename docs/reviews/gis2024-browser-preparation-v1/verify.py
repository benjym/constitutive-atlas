"""Saved-only prospective identity and exhaustive case-coverage check."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def read(p):return json.loads(p.read_bytes())
def verify():
 for filename in ['inputs.json','freeze.json']:
  for name,digest in read(HERE/filename)['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,(filename,name)
 rows=read(HERE/'laboratory-cases.json')['cases'];assert len(rows)==60 and len({r['id']for r in rows})==60
 actual={(r['id'].split('/')[0],r['specification']['protocol'],r['id'].split('/')[2],r['loading_wire'])for r in rows}
 expected={(state,p,loading,wire)for state in ['model-example-origin','axisymmetric-memory-example']for p in range(5)for loading in ['zero','monotonic','cyclic']for wire in ['exact','legacy']};assert actual==expected
 policy=read(HERE/'policy.json');model=read(ROOT/policy['identity']['model_path']);assert model['id']==policy['identity']['model_id']and hashlib.sha256((ROOT/policy['identity']['model_path']).read_bytes()).hexdigest()==policy['identity']['model_sha256']
 for row in rows:
  s=row['specification'];assert s['model']==model['id']and len(s['initial'])==14 and len(s['parameters'])==19 and row['expected']=='complete_success'
 guards=read(HERE/'guard-cases.json');assert len(guards)==8 and len({g['id']for g in guards})==8
 browser=read(HERE/'browser-cases.json');assert [b['id']for b in browser]==['B'+str(i).zfill(2)for i in range(1,13)]and all(b['status']=='unexecuted'for b in browser)
 assert read(HERE/'failure-case.json')['expected']=='failed_update_with_initial_point_only'
 assert read(HERE/'python-preflight.json')['constitutive_integrations']==0 and read(HERE/'node-preflight.json')['compiled_calls']==0
 return {'plan_identity_pass':True,'prospective_laboratory_cases':60,'guard_cases':8,'forced_failure_cases':1,'browser_cases':12,'future_rate_cases':26,'controller_or_browser_cases_executed':0,'scientific_admission':False}
if __name__=='__main__':print(json.dumps(verify(),indent=2))
