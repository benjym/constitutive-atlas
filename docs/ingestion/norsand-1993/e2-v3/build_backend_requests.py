"""Freeze native/Wasm requests after independent references and interpreter checks."""
from pathlib import Path
import json,copy,math
HERE=Path(__file__).resolve().parent

def main():
 cat=json.loads((HERE/'backend-proposal-v4/generated/path_catalogue.json').read_text());indices={m['id']:i for i,m in enumerate(cat['models'])};qual=json.loads((HERE/'interpreter-qualification-v1.json').read_text());inputs=json.loads((HERE/'interpreter-requests-v1.json').read_text());policy=json.loads((HERE/'reference_policy-v2.json').read_text());settings=list(policy['candidate_settings'].values());requests=[]
 model=indices['norsand-jefferies-1993-active-axial'];meta=cat['models'][model]
 for req,row in zip(inputs['cases'],qual['rows']):
  assert req['id']==row['id'];outs=row['outputs']
  obs=[x for f in meta['observables'] for x in (outs[f['name']] if f['size']==6 else [outs[f['name']]])]
  scales=[130000 if f['name'] in ('stress','mean_pressure','deviatoric_stress','image_pressure') else 1 for f in meta['observables'] for _ in range(f['size'])]
  requests.append(dict(id=req['id'],model=model,state=[req['state'][f['name']] for f in meta['state']],coordinate=req['coordinate'],parameters=[req['parameters'][n] for n in meta['parameters']],current_controls=[req['controls_start'][n] for n in meta['controls']],start_controls=[req['controls_start'][n] for n in meta['controls']],end_controls=[req['controls_end'][n] for n in meta['controls']],progress=.16,settings=settings,observable_count=len(obs),expected_status=1,expected_state=[outs[f['name']] for f in meta['state']],expected_observables=obs,observable_scales=scales))
 def add_negative(base,name,**changes):
  r=copy.deepcopy(base);r.update(changes,id=name,expected_status=0);r.pop('expected_state',None);r.pop('expected_observables',None);requests.append(r)
 base=requests[0]
 add_negative(base,'material-negative-progress',progress=-.01)
 add_negative(base,'material-zero-change',progress=0,end_controls=[140000,1/3])
 add_negative(base,'material-control-start-mismatch',start_controls=[120000,1/3])
 add_negative(base,'material-whole-parent-rollback',end_controls=[-130000,1/3])
 add_negative(base,'material-nonfinite-control',end_controls=['NaN',1/3])
 add_negative(base,'material-budget-exhaustion',settings=[1e-10,1e-8,1e-12,.001,40,1])
 add_negative(base,'material-invalid-domain',state=[0,-1,0,0])
 add_negative(base,'material-parameter-bound',parameters=[1.2,.5,280,.0135,.82,1000])
 add_negative(base,'material-unrepresentable-coordinate',coordinate=1e30,progress=1)
 add_negative(base,'material-missing-state',state=[])
 # Analytical scalar+Mandel tensor fixtures; coordinates are explicitly nonzero.
 for model_id,progress,expected_scalar,expected_tensor in [('synthetic-controlled-path',.25,3.75,2750.),('synthetic-curved-path',.5,math.exp(.5),0.)]:
  index=indices[model_id];m=cat['models'][index]
  req=dict(id=model_id,model=index,state=[1.]+[0.]*6,coordinate=7.,parameters=[1000.],current_controls=[2.,3.],start_controls=[2.,3.],end_controls=[4.,3.] if model_id=='synthetic-controlled-path' else [2.,3.],progress=progress,settings=settings,observable_count=6,expected_status=1,expected_state=[expected_scalar]+[expected_tensor]*3+[0.]*3,expected_observables=[expected_tensor]*3+[0.]*3,observable_scales=[1000.]*6,analytical=True)
  requests.append(req)
  if model_id=='synthetic-controlled-path':
   add_negative(req,'synthetic-unused-nonfinite',end_controls=[4.,'NaN'])
   add_negative(req,'synthetic-parent-rollback-domain',progress=60,end_controls=[2.,3.])
   add_negative(req,'synthetic-error-weight-overflow',settings=[1e308,1e308,1e-12,.001,40,100000])
   add_negative(req,'synthetic-zero-setting',settings=[0,1e-8,1e-12,.001,40,100000])
   add_negative(req,'synthetic-fractional-budget',settings=[1e-10,1e-8,1e-12,.001,40.5,100000])
   add_negative(req,'synthetic-missing-settings',settings=[])
   add_negative(req,'synthetic-invalid-model',model=-1)
 # Exact no-progress identity; observations are compared separately only on successes with expected outputs.
 req=copy.deepcopy(base);req.update(id='material-zero-identity',progress=0,end_controls=base['start_controls'],expected_state=base['state']);req.pop('expected_observables');requests.append(req)
 (HERE/'backend-requests-v1.json').write_text(json.dumps(dict(identity='controlled-path-native-wasm-v1',source_policy='reference_policy-v2.json',comparison='Source references checked independently in interpreter; backend candidate states/observables must agree with that interpreter at2e-11 normalized; analytical fixtures at2e-7. Negative outputs/input preservation exact.',requests=requests),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
