"""Independent closed-form check of actual live-browser exports and replay."""
from pathlib import Path
import json,sys
HERE=Path(__file__).resolve().parent
PACKET=HERE.parents[1]/'integration-v1'
sys.path.insert(0,str(PACKET))
from reference import reference
requests=json.loads((PACKET/'requests.json').read_text())
results={}
for mode in ['relaxation','creep']:
 run=json.loads((HERE/('live-'+mode+'.json')).read_text())
 spec=next(x['spec'] for x in requests['schedules'] if x['id']==mode)
 assert run['controls']['parameters']==spec['parameters'] and run['controls']['initial']==spec['initial']
 assert run['controls']['duration']==2 and run['controls']['samples']==8 and run['controls']['start']==4
 exact=reference(spec,100);observed=run['result']['points'];assert len(observed)==len(exact)==10
 errors=dict(stress_Pa=0.,Kelvin_strain=0.,strain=0.)
 for actual,target in zip(observed,exact):
  assert actual['time']==float(target['time']) and actual['side']==target['side'] and actual['segment']==target['segment']
  for name,field,lo,hi in [('stress_Pa','state',0,6),('Kelvin_strain','state',6,12),('strain','strain',0,6)]:
   errors[name]=max(errors[name],max(abs(x-float(y)) for x,y in zip(actual[field][lo:hi],target[field][lo:hi])))
 assert errors['stress_Pa']<=20 and errors['Kelvin_strain']<=2e-6 and errors['strain']<=2e-6,errors
 results[mode]=errors
assert json.loads((HERE/'live-relaxation.json').read_text())==json.loads((HERE/'live-replay.json').read_text())
report=dict(independent_reference='integration-v1 closed-form Decimal,100digits',frozen_gates=dict(stress_Pa=20,Kelvin_strain=2e-6,strain=2e-6),cases=results,exact_full_result_replay=True)
(HERE/'browser-analytical.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
