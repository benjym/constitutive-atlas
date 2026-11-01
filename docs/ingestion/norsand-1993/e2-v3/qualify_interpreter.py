"""Frozen-source comparison and transaction checks for staged interpreter."""
from pathlib import Path
import json,sys,math,copy,hashlib
HERE=Path(__file__).resolve().parent;STAGE=Path('/private/tmp/atlas-norsand-path-v1');sys.path.insert(0,str(STAGE))
from atlas.model import load
from atlas.path import initialize,advance,evaluate_stage,stage_inputs,Settings

def run():
 model=load(STAGE/'candidate.json');policy=json.loads((HERE/'reference_policy-v2.json').read_text());requests=json.loads((HERE/'interpreter-requests-v1.json').read_text());refs=json.loads((HERE/'references-v2.json').read_text());rows=[]
 settings=Settings(**policy['candidate_settings']);progress=float(policy['endpoint_progress'])
 for req,case in zip(requests['cases'],refs['cases']):
  assert req['id']==case['id'];state=req['state'];params=req['parameters'];start=req['controls_start'];end=req['controls_end'];origin=req['coordinate']
  parent=initialize(model,state,origin,start,params);saved=copy.deepcopy(parent)
  result=advance(model,parent,progress,start,end,settings)
  _,obs=evaluate_stage(model,result.state,params,stage_inputs(model,result.coordinate,start,end,1,progress))
  outputs={**result.state,**obs};errors={}
  for k,v in case['reference']['outputs'].items():
   expected=v if isinstance(v,list) else [v];actual=outputs[k] if isinstance(outputs[k],list) else [outputs[k]]
   scale=130000 if k in ('mean_pressure','deviatoric_stress','image_pressure','stress') else 1
   errors[k]=max(abs(a-float(b))/scale for a,b in zip(actual,expected))
  max_error=max(errors.values());assert max_error<=float(policy['candidate_reference_max_normalized']),(req['id'],errors)
  invariant=abs((1+result.state['e'])*math.exp(result.state['ev'])/(1+state['e'])-1)
  assert invariant<=float(policy['kinematic_invariant_max_relative'])
  assert abs((result.state['eq']-result.coordinate)-(state['eq']-origin))<1e-12
  half={n:(start[n]+end[n])/2 for n in start}
  left=advance(model,parent,progress/2,start,half,settings)
  restarted=initialize(model,left.state,left.coordinate,left.controls,left.parameters)
  right=advance(model,restarted,progress/2,half,end,settings)
  restart_error=max(abs(result.state[n]-right.state[n]) for n in result.state)
  assert restart_error<float(policy['candidate_reference_max_normalized'])
  assert advance(model,result,0,end,end,settings)==result
  rejects=0
  for call in [lambda:advance(model,parent,-1,start,end,settings),lambda:advance(model,parent,0,start,end,settings) if start!=end else advance(model,parent,.1,{**start,'pressure_control':1},end,settings),lambda:advance(model,parent,progress,start,{**end,'pressure_control':-130000},settings),lambda:advance(model,parent,progress,start,{**end,'pressure_control':float('nan')},settings),lambda:advance(model,parent,progress,start,end,Settings(max_trials=1))]:
   try:call()
   except (ValueError,ArithmeticError):rejects+=1
   else:raise AssertionError('negative transaction accepted '+req['id'])
  assert parent==saved
  recovery=advance(model,parent,progress,start,end,settings);assert recovery==result
  rows.append(dict(id=req['id'],max_reference_error=max_error,field_errors=errors,kinematic_invariant_relative=invariant,restart_error=restart_error,rejection_checks=rejects,outputs=outputs))
  print(req['id'],'PASS',max_error,flush=True)
 result=dict(result='PASS',case_count=len(rows),source_policy_sha256=hashlib.sha256((HERE/'reference_policy-v2.json').read_bytes()).hexdigest(),references_sha256=hashlib.sha256((HERE/'references-v2.json').read_bytes()).hexdigest(),requests_sha256=hashlib.sha256((HERE/'interpreter-requests-v1.json').read_bytes()).hexdigest(),script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows)
 (HERE/'interpreter-qualification-v1.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':run()
