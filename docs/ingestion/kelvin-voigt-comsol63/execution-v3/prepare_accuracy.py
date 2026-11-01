"""Freeze control-only v3 after retained accuracy failures; no compiled calls."""
import copy,hashlib,json,math
from pathlib import Path
import study
B=Path(__file__).resolve().parent;OLD=B.parent/'execution-v2'
REPLACEMENTS=[("controls=dict(rtol=1e-8,atol=1e-11,minimum=1e-12,maximum=1e6,budget=100000)","controls=dict(rtol=3e-11,atol=3e-14,minimum=1e-12,maximum=1e6,budget=1000000)"),("relative_tolerance=1e-8,absolute_scale_fraction=1e-11,maximum_substeps=100000","relative_tolerance=3e-11,absolute_scale_fraction=3e-14,maximum_substeps=1000000"),("[('coarse',1e-4,1e-7),('fine',1e-8,1e-11)]","[('coarse',1e-5,1e-8),('fine',3e-11,3e-14)]")]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def expected_case(old):
 c=copy.deepcopy(old)
 if c['kind']=='observe':return c
 fine=c['id']!='refine-coarse';rtol,atol=(3e-11,3e-14)if fine else(1e-5,1e-8)
 # Direct ABI: rtol6/atol7/budget10. Schedule ABI: rtol8/atol9/budget12.
 indices=(6,7,10)if c['kind']=='direct'else(8,9,12)
 c['args'][indices[0]]=rtol;c['args'][indices[1]]=atol
 budget=2 if c['args'][indices[2]]==2 else 1000000;c['args'][indices[2]]=budget
 for flag,value in[('--rtol',rtol),('--atol',atol),('--max-substeps',budget)]:c['argv'][c['argv'].index(flag)+1]=str(value)
 if c['kind']=='schedule':c['specification']['solver'].update(relative_tolerance=rtol,absolute_scale_fraction=atol,maximum_substeps=budget)
 return c

def differences(a,b,path=''):
 if isinstance(a,dict)and isinstance(b,dict):
  assert set(a)==set(b)
  for k in a:yield from differences(a[k],b[k],path+'/'+str(k))
 elif isinstance(a,list)and isinstance(b,list):
  assert len(a)==len(b)
  for n,(x,y)in enumerate(zip(a,b)):yield from differences(x,y,path+'/'+str(n))
 elif a!=b:yield {'pointer':path,'old':a,'new':b}
def verify_inputs():
 expected=(OLD/'study.py').read_text()
 for before,after in REPLACEMENTS:assert expected.count(before)==1;expected=expected.replace(before,after)
 assert(B/'study.py').read_text()==expected,'Only three exact solver-control source replacements permitted'
 for name in['reference.py','collect_wasm.mjs']:assert(B/name).read_bytes()==(OLD/name).read_bytes(),name
 assert sha(B.parent/'source-v1/candidate.json')==study.SHA
 old=json.loads((OLD/'cases.json').read_text())['cases'];new=study.make_cases();assert len(old)==len(new)==43
 for a,b in zip(old,new):assert b==expected_case(a),a['id']
 return old,new

def main():
 assert not(B/'freeze.json').exists(),'Already frozen; preserve original evidence'
 old,new=verify_inputs();study.dump(B/'cases.json',{'cases':new})
 changes=[dict(id=a['id'],changes=list(differences(a,b)))for a,b in zip(old,new)];study.dump(B/'comparison.json',{'identity':'kelvin-control-only-comparison-v3','previous_cases_sha256':sha(OLD/'cases.json'),'new_cases_sha256':sha(B/'cases.json'),'same_case_ids_order_count':43,'model_references_C_ABI_and_physical_inputs_identical':True,'unchanged_assessor_source':True,'unchanged_acceptance_gates':True,'cases':changes})
 rows=json.loads((OLD/'native-raw.json').read_text());basis=[];factor=math.sqrt(1e-8/3e-11)
 for c,r in zip(old,rows):
  if c['kind']!='schedule'or not c['ok']:continue
  result=json.loads(r['calls'][0]['stdout']);counts=sum(p['substeps']for p in result['points']);basis.append({'id':c['id'],'v2_accepted_substeps':counts,'indicative_fine_projection':math.ceil(counts*factor),'v3_allowance':1000000})
 study.dump(B/'budget-basis.json',{'identity':'kelvin-v3-prospective-step-allowance','source_raw_sha256':sha(OLD/'native-raw.json'),'indicative_work_factor':factor,'projection_limitation':'Planning approximation only, not a proved bound; v3 budget failure remains failure','fine_public_budget':1000000,'negative_budget_cases_unchanged':2,'schedule_counts':basis})
 names=['study.py','reference.py','collect_wasm.mjs','PLAN.md','README.md','prepare_accuracy.py','check_preparation.py','cases.json','comparison.json','budget-basis.json','../execution-v2/study.py','../execution-v2/reference.py','../execution-v2/cases.json','../execution-v2/freeze.json','../execution-v2/native-raw.json','../execution-v2/accuracy-diagnosis.json','../source-v1/candidate.json']
 study.dump(B/'freeze.json',{'identity':'NUM-kelvin-voigt-accuracy-v3','model':study.M,'model_sha256':study.SHA,'chronology':'New study after retained v2 accuracy failures; frozen before v3 compiled observations','compiled_calls_by_preparer':0,'fine_controls':{'rtol':3e-11,'atol':3e-14,'maximum_substeps':1000000},'coarse_controls':{'rtol':1e-5,'atol':1e-8,'maximum_substeps':1000000},'negative_budget':2,'source_runtime_build_freeze':'Parent separately freezes exact unchanged source closure and Release toolchain flags before compiled observations','pins':{n:sha(B/n)for n in names}});print('Frozen43cases; exact physical/reference/assessor identity, solver-controls-only changes')
if __name__=='__main__':main()
