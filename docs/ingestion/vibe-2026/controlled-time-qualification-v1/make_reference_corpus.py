"""Prospective independent synthetic references; stdlib only, no Atlas import."""
from pathlib import Path
from decimal import Decimal,getcontext
import hashlib,json
getcontext().prec=80
D=Decimal
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
cases=[]
for fixture in ['transport','branch','capacity-max']:
 path=ROOT/f'tests/fixtures/controlled-time/{fixture}.json';model=json.loads(path.read_text())
 state={f['name']:f['initial'] for f in model['state']};params={n:f['default'] for n,f in model['parameters'].items()};start={n:([0.]*6 if f['shape']=='sym' else 0.) for n,f in model['formulation']['controls'].items()};start.update(suction=200000.,temperature=300.);incoming={n:([0.]*6 if f['shape']=='sym' else 0.) for n,f in model['formulation']['controls'].items()}
 def append(name,end,duration=4,partitions=1):
  h=D(duration);ds=D(str(end['suction']))-D(200000);dt=D(str(end['temperature']))-D(300);strain=[D(str(x)) for x in end['strain']]
  extra=D('.3')*ds+D(100)*dt+D(7)*h*(D(300)+D(str(end['temperature'])))/D(600)
  expected={n:str(D(str(v))) for n,v in state.items() if not isinstance(v,list)}
  expected['sigma']=[str(D(v)+D(2000000)*de+(extra if i<3 else 0)) for i,(v,de) in enumerate(zip(state['sigma'],strain))]
  expected['clock_memory']=str(D('-3.5')+((D(11)+h)**2-D(121))/D(8)) if fixture!='branch' else str(D('-3.5')+h*(1 if ds>0 else -2 if ds<0 else 0))
  expected['e']=str(D('1.8')*(-sum(strain)).exp()-1);expected['memory']=str(D(2)*(-h/2).exp())
  if fixture=='capacity-max':
   for i in range(23):expected['history'+str(i)]=str(h/2)
   expected['history22']=str(D(249)*h/2+D(str(end['field23'])))
  cases.append(dict(id=fixture+'-'+name,fixture=str(path.relative_to(ROOT)),definition_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),state=state,parameters=params,start_time=11,duration=duration,controls=start,incoming_rates=incoming,controls_end=end,partitions=partitions,settings=dict(absolute_scale_fraction=1e-11,relative_tolerance=1e-10,minimum_step_seconds=1e-12,maximum_step_seconds=1.,maximum_depth=40,maximum_trials=100000),expected_state=expected))
 if fixture=='transport':
  mixed={**start,'strain':[.001,-.0003,.0002,.0004,-.0005,.0006],'suction':350000.,'temperature':330.}
  for n in [1,2,4]:append('mixed-partition'+str(n),mixed,partitions=n)
  append('hold',start);append('clock-mid',start,duration=2)
  for i in range(6):end={**start,'strain':[.0007 if i==j else 0. for j in range(6)]};append('basis'+str(i),end)
  append('suction',{**start,'suction':100000.});append('temperature',{**start,'temperature':270.});append('opposing-thm',{**start,'suction':100000.,'temperature':330.})
 elif fixture=='branch':
  append('positive',{**start,'suction':350000.});append('negative',{**start,'suction':100000.});append('hold',start)
 else:append('max-coupling',{**start,'field23':.25})
payload=dict(identity='controlled-time-independent-corpus-v1',prospective=True,oracle='Decimal80 closed-form source-independent synthetic equations; no production interpreter imported',acceptance=dict(stress_absolute=1e-7,stress_relative=1e-12,scalar_absolute=1e-8,scalar_relative=2e-7,clock_absolute=1e-12,clock_relative=1e-12),cases=cases)
(OUT/'reference-corpus-v1.json').write_text(json.dumps(payload,indent=2)+'\n')
print('Prospective closed-form cases:',len(cases))
