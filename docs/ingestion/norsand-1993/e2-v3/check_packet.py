"""Hash/check evidence without executing a compiled artifact or private source."""
from pathlib import Path
import json,hashlib,ast,math
HERE=Path(__file__).resolve().parent

def main():
 count=0;manifests=[]
 for manifest in sorted(HERE.glob('*freeze*.json')):
  data=json.loads(manifest.read_text())
  for rel,expected in data.get('files',{}).items():
   file=HERE/rel;assert file.is_file(),str(file);assert hashlib.sha256(file.read_bytes()).hexdigest()==expected,(manifest.name,rel);count+=1
  manifests.append(manifest.name)
 reviews=[]
 for manifest in sorted((HERE/'independent-review').glob('*bindings*.json')):
  data=json.loads(manifest.read_text())
  for rel,expected in data.get('files',{}).items():
   file=HERE/rel;assert hashlib.sha256(file.read_bytes()).hexdigest()==expected,(manifest.name,rel);count+=1
  for key in ('inputs','frozen_inputs'):
   for rel,expected in data.get(key,{}).items():
    assert hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==expected,(manifest.name,rel);count+=1
  if 'freeze_sha256' in data:
   assert any(hashlib.sha256(f.read_bytes()).hexdigest()==data['freeze_sha256'] for f in HERE.glob('*freeze*.json'));count+=1
  for rel,expected in data.get('reviewer_outputs',{}).items():
   assert hashlib.sha256((HERE/'independent-review'/rel).read_bytes()).hexdigest()==expected,(manifest.name,rel);count+=1
  reviews.append(manifest.name)
 for file in HERE.glob('*.py'):ast.parse(file.read_text(),filename=str(file))
 refs=json.loads((HERE/'references-v2.json').read_text());policy=json.loads((HERE/'reference_policy-v2.json').read_text());assert len(refs['cases'])==9
 for row in refs['cases']:
  assert float(row['refinement_error'])<=float(policy['reference_refinement_max_normalized']);assert float(row['precision_error'])<=float(policy['reference_precision_max_normalized'])
 qual=json.loads((HERE/'interpreter-qualification-v1.json').read_text());assert qual['result']=='PASS' and qual['case_count']==9
 for row in qual['rows']:
  assert row['max_reference_error']<=float(policy['candidate_reference_max_normalized']);assert row['kinematic_invariant_relative']<=float(policy['kinematic_invariant_max_relative']);assert row['rejection_checks']==5
 legacy=json.loads((HERE/'legacy-generation-results.json').read_text());assert legacy['result']=='byte-identical' and legacy['model_count']==13
 reqs=json.loads((HERE/'backend-requests-v2.json').read_text())['requests'];assert len(reqs)==58 and len({r['id'] for r in reqs})==58
 assert sum('state_from' in r for r in reqs)==9
 backend=json.loads((HERE/'backend-qualification-v2.json').read_text());assert backend['result']=='PASS' and backend['requests_per_backend']==58 and backend['native_wasm_max_normalized_error']==0
 for receipt in ['native-qualification-v1.json','backend-qualification-v2.json','wasm-harness-failure-v1.json']:
  data=json.loads((HERE/receipt).read_text())
  for rel,expected in data.get('files',data.get('artifact_files',{})).items():
   assert hashlib.sha256((HERE/rel).read_bytes()).hexdigest()==expected,(receipt,rel);count+=1
 report=dict(result='PASS',hash_bindings=count,freeze_manifests=manifests,review_manifests=reviews,reference_cases=9,interpreter_cases=9,generic_checks=29,backend_requests_frozen=58,compiled_requests=116,scope='Staged source/static/interpreter/native/Wasm capability evidence; no E5, browser or live approval')
 (HERE/'packet-check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
