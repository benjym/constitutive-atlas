"""Source-only identity/semantics comparison; never executes material APIs."""
from pathlib import Path
import ast,hashlib,json
D=Path(__file__).resolve().parent;P=D.parent;ROOT=D.parents[4]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def check():
 old=json.loads((P/'ordinary-regression-v6/policy.json').read_text());new=json.loads((P/'ordinary-regression-v7/policy.json').read_text());fields=[k for k in old if old[k]!=new[k]];assert fields==['identity','source_freeze_sha256'] and old.keys()==new.keys();assert len(new['cases'])==16
 expected=(P/'ordinary-regression-v6/run.py').read_text().replace("D.parent/'runtime-rebind-v1/source-freeze.json'","D.parent/'runtime-rebind-v5/source-freeze.json'").replace("'identity': 'md1997-ordinary-regression-v6'","'identity': 'md1997-ordinary-regression-v7'");assert (P/'ordinary-regression-v7/run.py').read_text()==expected
 assert sha(D/'source-freeze.json')==new['source_freeze_sha256']=='4bdaf4c5ac59324a644d533e2699d32b2272036803e9927968552e86ebb5dea8'
 source=json.loads((D/'source-freeze.json').read_text());before=json.loads((P/'runtime-rebind-v1/source-freeze.json').read_text())['source_files'];after=source['source_files'];assert len(after)==582
 changed=[n for n,h in before.items()if after.get(n)!=h];added=sorted(set(after)-set(before));assert changed==['cpp/include/atlas/solver.hpp'];assert added==['cmake/control-partition-derivative/CMakeLists.txt','tests/fixtures/control-partition-derivative/main.cpp','tests/fixtures/control-partition-derivative/rate.json','tests/fixtures/control-partition-derivative/residual.json'];assert not(set(before)-set(after))
 for n,h in after.items():assert sha(Path(source['source_directory'])/n)==h,n
 for c in new['cases']:assert sha(Path(source['source_directory'])/'models'/(c['model']+'.json'))==c['definition_sha256'],c['model']
 coarse=json.loads((D/'coarse-diagnostic-policy.json').read_text());oldplan=json.loads((P/'execution-v3/requests.json').read_text());oldcase=next(c for c in oldplan['cases']if c['id']=='drained-dense-compression-128');assert coarse['case']==oldcase and len(oldcase['controls'])==133 and coarse['settings']==oldplan['settings'] and coarse['model_sha256']==oldplan['model_sha256']
 manifests=[]
 for rel in ['resolution-study-v4/manifest.json','execution-v3/manifest.json','parity-v6/manifest.json','ordinary-regression-v6/manifest.json','runtime-rebind-v1/manifest.json','control-trace-actual-v1/manifest.json']:
  f=P/rel
  for n,h in json.loads(f.read_text()).items():assert sha(f.parent/n)==h,(rel,n)
  manifests.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f)})
 plan=json.loads((P/'resolution-study-v4/requests.json').read_text());assert len(plan['cases'])==35;assert len([c for c in plan['cases']if c['group']in ['axis','interior']])==28
 for p in list(D.glob('*.py'))+list((P/'ordinary-regression-v7').glob('*.py')):ast.parse(p.read_text(),filename=str(p))
 if (D/'full-freeze.json').exists():
  for n,h in json.loads((D/'full-freeze.json').read_text())['files'].items():assert sha(ROOT/n)==h,n
 if (D/'manifest.json').exists():
  for n,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/n)==h,n
 return {'identity':'md1997-control-runtime-rebind-comparison-v5','status':'passed-source-only','compiled_calls':0,'source_files':582,'ordinary_cases':16,'ordinary_policy_changed_fields':fields,'ordinary_all_cases_gates_expected_outcomes_exactly_unchanged':True,'ordinary_runner_only_two_identity_path_substitutions':True,'material_cases':35,'material_paths':14,'material_requests_checkers_all_numeric_gates_unchanged':True,'coarse_diagnostic_exact_old_request_points':133,'new_runtime_changed':changed,'new_runtime_added':added,'new_runtime_removed':[],'unchanged_historical_manifests':manifests,'approval_or_actual_qualification':'not asserted'}
if __name__=='__main__':print(json.dumps(check(),indent=2))
