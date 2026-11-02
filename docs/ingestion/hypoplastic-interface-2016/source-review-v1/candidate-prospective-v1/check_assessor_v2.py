"""Independent synthetic V2 assessor tests; no compiled/material calls."""
from pathlib import Path
import copy,hashlib,importlib.util,json,math
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016/implementation-v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
path=P/'check_backend_results_v2.py';assert sha(path)=='9adabe6bc0bbc1ef4fc0a7b996ceca1a4ee539348d88a260f207403d768c1933'
spec=importlib.util.spec_from_file_location('assessorv2',path);checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
req=read(P/'backend-requests.json');ex=read(P/'backend-expectations.json');rows=[]
for q in req['requests']:
 e=ex['expected'][q['id']]
 rows.append(dict(id=q['id'],status=e['status'],state=e['state'] if e['status'] else [-1234567.]*5,coordinate=e['coordinate'] if e['status'] else -7654321.,observables=e['observables'] if e['status'] else [-1234567.]*8))
base=dict(request_sha256=sha(P/'backend-requests.json'),rows=rows);assert checker.assess(base)['passed']
count=0
for ri,row in enumerate(rows):
 for field in ['state','observables']:
  for ix in range(len(row[field])):
   for val in [float('nan'),float('inf'),float('-inf')]:
    bad=copy.deepcopy(base);bad['rows'][ri][field][ix]=val
    try:checker.assess(bad)
    except (AssertionError,ValueError,TypeError):count+=1
    else:raise AssertionError(('nonfinite passed',row['id'],field,ix))
 for val in [float('nan'),float('inf'),float('-inf')]:
  bad=copy.deepcopy(base);bad['rows'][ri]['coordinate']=val
  try:checker.assess(bad)
  except (AssertionError,ValueError,TypeError):count+=1
  else:raise AssertionError(('coordinate nonfinite passed',row['id']))
extras=[]
for field in ['state','observables']:
 for val in [[],rows[0][field]+[0],None,True]:
  bad=copy.deepcopy(base);bad['rows'][0][field]=val;extras.append(bad)
bad=copy.deepcopy(base);bad['rows'][0]['status']=True;extras.append(bad)
bad=copy.deepcopy(base);bad['rows'][-1]['id']=bad['rows'][0]['id'];extras.append(bad)
bad=copy.deepcopy(base);bad['rows'][-1]['id']='unexpected-id';extras.append(bad)
bad=copy.deepcopy(base);bad['rows'][-1]['state'][0]+=.3;extras.append(bad)
bad=copy.deepcopy(base);bad['rows'][-1]['observables'][2]+=.1;extras.append(bad)
for bad in extras:
 try:checker.assess(bad)
 except (AssertionError,ValueError,TypeError):count+=1
 else:raise AssertionError('malformed/layout/binding/bound test passed')
result=dict(passed=True,checker_sha256=sha(path),baseline_synthetic_expected_report_accepted=True,independent_synthetic_faults_rejected=count,all_59_rows_and_14_numeric_components_covered=True,compiled_or_material_calls=0)
(OUT/'assessor-v2-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
