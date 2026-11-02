"""Read saved references and fault-inject synthetic assessor outputs; no model execution."""
from pathlib import Path
import copy,hashlib,importlib.util,json,math
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[4];P=ROOT/'docs/ingestion/hypoplastic-interface-2016/implementation-v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
model=ROOT/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json';assert sha(model)=='8ab12775390be5f5aa8f7db7a37da0990d444a343d037bd35fa36e3b5bdbc7ce'
policy=read(P/'policy.json');refs=read(P/'references.json');req=read(P/'backend-requests.json');ex=read(P/'backend-expectations.json');m=read(model)
assert refs['policy_sha256']==sha(P/'policy.json');assert refs['reference_script_sha256']==sha(P/'reference.py')
assert req['definition_sha256']==sha(model) and ex['requests_sha256']==sha(P/'backend-requests.json') and ex['source_reference_sha256']==sha(P/'references.json')
assert len(req['requests'])==len(ex['expected'])==59
assert len(refs['rows'])==10 and refs['all_converged']
convergence=[];density_checked=0
for c,r in zip(policy['cases'],refs['rows']):
 assert c['name']==r['case'] and [x['steps'] for x in r['refinements']]==[128,256,512]
 delta=max(abs(a-b)/s for aa,bb in zip(r['refinements'][-2]['endpoints'],r['refinements'][-1]['endpoints']) for a,b,s in zip(aa['state'],bb['state'],policy['reference']['scale']))
 assert delta==r['last_refinement_scaled_difference'] and delta<=2e-8
 d0=max(abs(a-b)/s for aa,bb in zip(r['refinements'][0]['endpoints'],r['refinements'][1]['endpoints']) for a,b,s in zip(aa['state'],bb['state'],policy['reference']['scale']))
 convergence.append(dict(case=c['name'],first_scaled_difference=d0,last_scaled_difference=delta,ratio=d0/delta if delta else None))
 for v in r['refinements']:
  for seg,ep in zip(c['segments'],v['endpoints']):
   e=(1+c['initial'][4])*math.exp(-(seg['end_controls']['normal_strain']-c['start_controls']['normal_strain']))-1
   assert abs(e-ep['state'][4])<1e-12;density_checked+=1
   s=ep['state'];assert ep['stress']==[s[0],s[1],s[1],math.sqrt(2)*s[2],0.,math.sqrt(2)*s[3]]
spec=importlib.util.spec_from_file_location('backend_assessor',P/'check_backend_results.py');checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
rows=[]
for q in req['requests']:
 e=ex['expected'][q['id']]
 rows.append(dict(id=q['id'],status=e['status'],state=e['state'] if e['status'] else [-1234567.]*len(q['state']),coordinate=e['coordinate'] if e['status'] else -7654321.,observables=e['observables'] if e['status'] else [-1234567.]*q['observable_count']))
base=dict(request_sha256=sha(P/'backend-requests.json'),rows=rows);assert checker.assess(base)['passed']
faults=[]
for field,index in [('state',4),('observables',7)]:
 bad=copy.deepcopy(base);r=next(x for x in bad['rows'] if x['id']=='zero-progress-identity');r[field][index]=float('nan')
 try:accepted=bool(checker.assess(bad)['passed'])
 except Exception:accepted=False
 faults.append(dict(field=field,index=index,synthetic_nonfinite_accepted=accepted))
py=read(P/'python-results.json');assert py['passed'] and py['candidate_sha256']==sha(model) and py['policy_sha256']==sha(P/'policy.json') and py['references_sha256']==sha(P/'references.json')
python_components=0;python_max=0.
for c,r in zip(py['cases'],refs['rows']):
 assert c['case']==r['case']
 for end,ref in zip(c['endpoints'],r['refinements'][-1]['endpoints']):
  state=[end['state'][f['name']] for f in m['state']]
  for actual,expected,scale in zip(state+end['stress'],ref['state']+ref['stress'],policy['reference']['scale']+[100000]*6):
   assert math.isfinite(actual) and abs(actual-expected)/scale<=2e-6
   python_components+=1;python_max=max(python_max,abs(actual-expected)/scale)
 assert c['repeat_exact'] and c['restart_passed']
assert len(py['negative_cases'])==13 and all(v['rejected'] and v['parent_unchanged'] for v in py['negative_cases'])
result=dict(python_saved_components_checked=python_components,python_max_scaled_error=python_max,candidate_sha256=sha(model),requests=59,successful=sum(e['status'] for e in ex['expected'].values()),negative=sum(not e['status'] for e in ex['expected'].values()),reference_cases=10,density_analytical_comparisons=density_checked,refinement=convergence,assessor_v1_faults=faults,compiled_or_material_calls=0,bindings={str(p.relative_to(ROOT)):sha(p) for p in [model,*[P/n for n in ['CONTRACT.md','policy.json','reference.py','references.json','build_requests.py','backend-requests.json','backend-expectations.json','check_backend_results.py','example.json','package-cases.json','qualify_python.py','python-results.json']]]})
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('bindings','refinement')},indent=2))
