"""Saved-output qualification against the prospective independent rational references."""
from pathlib import Path
from fractions import Fraction as F
import json,math,importlib.util
P=Path(__file__).parent;ROOT=P.parents[2]
def exact_module(root):
 p=root/'docs/reviews/certified-spectral-range-v1/exact.py';s=importlib.util.spec_from_file_location('lab_exact_membership',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def assess(rows,inputs,refs,policy,root=ROOT):
 assert len(rows)==len(inputs['cases']);tol=policy['tolerances'];exact=exact_module(root);failures=[];details=[];components=0;admissibility=0;maxstress=0.;maxstrain=0.;recovered=0
 def check(ok,label,kind,**kw):
  if not ok:failures.append(dict(label=label,kind=kind,**kw))
 def scope(response,label):
  check(response.get('api_version')=='experimental-laboratory-scope-0.1',label,'api-version')
  check(response.get('stress')=={'source':'state','name':'sigma','measure':'cauchy','scope':'total','tensor_representation':'mandel','sign':'compression_positive'},label,'scope')
  check(response.get('pore_pressure')=={'quantity':'change','availability':'unavailable','reason':'total_stress_without_pore_pressure_law'},label,'pore-descriptor')
 def finite(v):return isinstance(v,(int,float))and not isinstance(v,bool)and math.isfinite(v)
 for row,c in zip(rows,inputs['cases']):
  label=c['label'];assert row['label']==label;check(row['inputs_unchanged'],label,'inputs-mutated');response=row['response'];recovery=row['recovery'];scope(recovery,label+'-recovery')
  good=recovery.get('ok')is True and len(recovery.get('points',[]))==2
  for point in recovery.get('points',[]):good=good and point['state']==[64.]*3+[0.]*9 and point['strain']==[0.]*6 and point['control']==0 and point['u']is None
  check(good,label,'recovery');recovered+=int(good)
  if c['kind']=='reject':
   check(response.get('ok')is False,label,'invalid-request-accepted');check(not response.get('points'),label,'invalid-request-committed');details.append({'label':label,'expected':'reject','ok':response.get('ok'),'points':len(response.get('points',[]))});continue
  scope(response,label);ref=refs[label];expected_ok=c['kind']=='success';check(response.get('ok')is expected_ok,label,'run-status',expected=expected_ok,actual=response.get('ok'))
  check(response.get('parameters')==c['parameters']and response.get('initial')==c['initial']and response.get('protocol')==c['protocol'],label,'request-identity')
  check(response.get('integration_settings')=={'version':'incremental-settings-0.1','norm':'scaled_component_max','residual_tolerance':2e-10,'rate_tolerance':1e-6,'max_iterations':45,'max_depth':0,'max_substeps':20000,'max_backtracks':11},label,'settings')
  check(response.get('loading')=={'version':'laboratory-controls-0.1','controls':c['controls'],'encoding':'ieee754-binary64-hex','controls_bits':c['controls_bits']},label,'control-wire')
  points=response.get('points',[]);check(len(points)==len(ref['points']),label,'prefix-length',expected=len(ref['points']),actual=len(points))
  for step,(point,target)in enumerate(zip(points,ref['points'])):
   check(point['control']==float(F(target['control'])),label,'control',step=step);check(point.get('u')is None,label,'fabricated-pore-pressure',step=step)
   state=point.get('state',[]);strain=point.get('strain',[]);check(len(state)==12 and len(strain)==6 and all(finite(v)for v in state+strain),label,'full-finite-layout',step=step)
   if len(state)!=12 or len(strain)!=6 or not all(finite(v)for v in state+strain):continue
   for i,(got,wanted)in enumerate(zip(state+strain,target['state']+target['strain'])):
    error=abs(F.from_float(float(got))-F(wanted));budget=tol['state_stress_absolute_Pa']if i<6 else tol['strain_and_plastic_absolute'];components+=1
    if i<6:maxstress=max(maxstress,float(error))
    else:maxstrain=max(maxstrain,float(error))
    check(error<=F.from_float(budget),label,'reference-value',step=step,component=i,error=float(error),budget=budget)
   member=exact.range_le(state[:6],2*c['parameters'][3]);assert member==exact.sturm_range_le(state[:6],2*c['parameters'][3]);admissibility+=1;check(member,label,'source-inadmissible-commit',step=step)
   q=F(target['state'][0])-F(target['state'][1]);mean=sum(F(x)for x in target['state'][:3])/3
   for name,value in [('p',mean),('q',abs(q)),('q_signed',q)]:check(finite(point.get(name))and abs(float(point[name])-float(value))<=tol['p_q_absolute_Pa'],label,'observable-'+name,step=step)
   if c['protocol']==1:check(abs((state[1]+state[2])/2-c['initial'][1])<=tol['controller_radial_or_q_absolute_Pa'],label,'radial-control',step=step)
   if c['protocol']==3:check(abs(state[0]-(state[1]+state[2])/2-(c['initial'][0]-c['initial'][1])-point['control'])<=tol['controller_radial_or_q_absolute_Pa'],label,'q-control',step=step)
  details.append({'label':label,'expected':c['kind'],'ok':response.get('ok'),'points':len(points),'reference_points':len(ref['points'])})
 return {'qualification_pass':not failures,'requests':len(rows),'reference_components':components,'admissibility_checks':admissibility,'recoveries':recovered,'maximum_stress_error_Pa':maxstress,'maximum_strain_plastic_error':maxstrain,'failures':failures,'cases':details}
def run(packet=P,root=ROOT):
 inputs=json.loads((packet/'inputs.json').read_text());refs=json.loads((packet/'references.json').read_text());policy=json.loads((packet/'policy.json').read_text());result={}
 for backend in ['native','wasm']:result[backend]=assess([json.loads(l)for l in (packet/(backend+'-responses.jsonl')).read_text().splitlines()],inputs,refs,policy,root)
 result['overall_pass']=all(result[b]['qualification_pass']for b in ['native','wasm']);return result
if __name__=='__main__':print(json.dumps(run(),indent=2))
