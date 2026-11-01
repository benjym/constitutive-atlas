"""Saved-evidence independent audit. No compiled artifacts are executed."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib,struct,sys,math
P=Path(__file__).resolve().parent; M=P.parents[1]; B=M/'execution-v2'; V1=M/'execution-v1'; ROOT=M.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bits(x):return struct.pack('>d',float(x)).hex()
def wire(x):
 if isinstance(x,float):return bits(x)
 if isinstance(x,list):return [wire(v) for v in x]
 if isinstance(x,dict):return {k:wire(v) for k,v in x.items()}
 return x
freeze=json.loads((B/'freeze.json').read_text());bindings={}
for name,h in freeze['files'].items():
 actual=(B/'frozen'/name) if not name.startswith('docs/') else ROOT/name
 assert actual.is_file(),str(actual)
 assert sha(actual)==h,name
 bindings[str(actual.relative_to(ROOT))]=h
assert len(bindings)==115
for name in ['candidate.json','requests.json','requests-binary64.json']:
 assert (B/name).read_bytes()==(V1/name).read_bytes(),name
assert sha(B/'candidate.json')=='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
assert (B/'assess-v2.py').read_bytes()==(V1/'assess-v2.py').read_bytes()
req=json.loads((B/'requests.json').read_text());assert wire(req)==json.loads((B/'requests-binary64.json').read_text())
raw=json.loads((B/'native-results.json').read_text());assert raw['requests_sha256']==sha(B/'requests.json')
assert json.loads((P/'native-assessment-replay.json').read_text())==json.loads((B/'native-assessment.json').read_text())
assert json.loads((P/'native-partition-replay.json').read_text())==json.loads((B/'native-partition-assessment.json').read_text())
source=json.loads((P.parent/'execution-v1/native-failure/analytical-partition-v1/results.json').read_text()); expected={x['id']:x for x in source['rows']}; rows=[]
for path in raw['paths']:
 for index,call in enumerate(path['calls']):
  out=json.loads(call['stdout'],parse_int=float);d=out.get('diagnostics',{})
  if not d.get('partition_retries'):continue
  e=expected[path['id']];v=e['variants'][1];assert index==e['failed_call_index'] and out['ok']
  assert d['substeps']==v['accepted_leaf_count'] and d['attempted_substeps']==v['global_attempted_accepted_steps']
  assert d['discarded_substeps']==d['first_attempt_substeps']==v['discarded_original_substeps']
  assert [[bits(x) for x in row] for row in d['accepted_increment_tensors']]==[[bits(float.fromhex(x)) for x in leaf['de']] for leaf in v['leaves']]
  error=max(abs(float(x)-float(y))/1e5 for x,y in zip(out['state'],v['final_state']));assert error<2e-8
  de=list(map(float,call['args'][3].split(','))); rational_sums=[]
  for i,parent in enumerate(de):
   defect=sum(F(float(inc[i])) for inc in d['accepted_increment_tensors'])-F(parent)
   reported=F(float(d['partition_defect'][i]));assert defect==reported
   assert abs(defect)<=2*F(sys.float_info.epsilon)*abs(F(parent))
   rational_sums.append(str(defect))
  rows.append({'id':path['id'],'index':index,'same_actual_leaf_tensors_as_independent_source_analysis':True,'substeps':d['substeps'],'attempted_substeps':d['attempted_substeps'],'source_feasible_encoded_endpoint_error_over_p_ref':error,'exact_rational_sum_defect':rational_sums})
assert len(rows)==4
print(json.dumps({'identity':'independent-duncan-native-v2-e4-audit','pass':True,'freeze_files_checked':len(bindings),'candidate_and_requests_identical_v1':True,'source_assessor_identical_v1':True,'native_saved_assessment_reproduced':True,'native_saved_partition_assessment_reproduced':True,'source_partition_comparisons':rows,'compiled_calls':0,'closure_bindings':bindings},indent=2))
