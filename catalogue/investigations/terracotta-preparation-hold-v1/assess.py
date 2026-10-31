"""Recompute complete phase errors from retained raw schedule responses."""
import json,math
from pathlib import Path
from assemble import requests

CHANNELS={'state':('state',4),'strain':('strain',6),'rate':('strain_rate',6)}

def assess_response(request,response,case,policy,catalogue_hash):
 assert response.get('ok') is True,response.get('message')
 assert response.get('catalogue_hash')==catalogue_hash
 for key in ('schema_version','units','model','start_time','parameters','initial','initial_strain','initial_strain_rate','segments'):
  assert response[key]==request[key],key
 settings={'method':'backward-euler-step-doubling','relative_tolerance':1e-6,'absolute_scale_fraction':1e-9,'minimum_step':1e-12,'maximum_step':1e6,'maximum_substeps':20000,'nonlinear_tolerance':1e-10,'maximum_iterations':40,'maximum_depth':40}|request['solver']
 assert response['solver']==settings
 points=response['points']
 grid=[(-1,'left',0),(0,'right',0)]+[(0,'left',i) for i in range(1,11)]+[(1,'right',10)]+[(1,'left',i) for i in range(12,31,2)]
 assert len(points)==23
 for point,expected in zip(points,grid):
  assert (point['segment'],point['side'],point['time'])==expected
  for name,size in [('state',4),('strain',6),('strain_rate',6),('observables',13)]:
   value=point[name];assert len(value)==size
   if name=='strain_rate' and expected[:2]==(1,'right'):
    assert value==[None,None,None,0,0,0]
   else:assert all(type(v) in (int,float) and math.isfinite(v) for v in value)
  for name in ('iterations','substeps','rejected'):assert type(point[name]) is int and point[name]>=0
  assert 0<=point['temporal_error_norm']<=1
  assert 0<=point['nonlinear_residual_norm']<=1e-10
 for left,right in [(points[0],points[1]),(points[11],points[12])]:
  assert left['state']==right['state'] and left['strain']==right['strain']
 assert points[0]['state']==request['initial'] and points[0]['strain']==request['initial_strain']
 assert points[0]['strain_rate']==request['initial_strain_rate']
 target=points[11]['observables'][6:8]
 for point in points[12:]:
  assert all(abs(a-b)<=policy['controls_held_residual_Pa'] for a,b in zip(point['observables'][6:8],target))
 selected=[points[0]]+points[2:]
 assert len(selected)==len(case['points'])==22
 errors={phase:{'state':[0.]*4,'strain':[0.]*6,'rate':[0.]*6,'elastic_stress_Pa':[0.,0.],'total_stress_Pa':[0.,0.]} for phase in ('preparation','hold')}
 magnitudes={phase:{key:[1.]*len(values) for key,values in channels.items()} for phase,channels in errors.items()}
 for actual,expected in zip(selected,case['points']):
  assert actual['time']==expected['time']
  phase='hold' if actual['segment']==1 else 'preparation';assert expected['phase']==phase
  pairs=[]
  for key,(field,size) in CHANNELS.items():
   if key=='rate' and actual['side']=='right':continue
   pairs.append((key,actual[field],expected[key]))
  pairs.extend([('elastic_stress_Pa',actual['observables'][8:10],[expected['elastic_pressure'],expected['elastic_q']]),('total_stress_Pa',actual['observables'][6:8],[expected['pressure'],expected['signed_q']])])
  for key,values,wanted in pairs:
   for i,(a,b) in enumerate(zip(values,wanted)):
    errors[phase][key][i]=max(errors[phase][key][i],abs(a-b));magnitudes[phase][key][i]=max(magnitudes[phase][key][i],abs(b))
 return {'errors':errors,'reference_magnitudes':magnitudes,'captured_runtime_targets_P_Q':target}

def assess(records,reference,model,policy,catalogue_hash):
 matrix=requests(reference,model);expected={(r['case'],r['relative_tolerance']):r['request'] for r in matrix}
 seen={};results=[]
 for record in records:
  key=(record['case'],record['relative_tolerance']);assert key in expected and key not in seen
  assert record['request']==expected[key]
  case=next(c for c in reference['cases'] if c['id']==key[0])
  result=assess_response(record['request'],record['response'],case,policy,catalogue_hash);seen[key]=result
  results.append({'case':key[0],'relative_tolerance':key[1],**result})
 assert set(seen)==set(expected)
 for case in reference['cases']:
  coarse=seen[(case['id'],1e-4)];fine=seen[(case['id'],1e-8)]
  for phase in ('preparation','hold'):
   for channel,errors in fine['errors'][phase].items():
    bounds=policy['fine_bounds'][channel]
    if not isinstance(bounds,list):bounds=[bounds]*len(errors)
    for i,(error,bound) in enumerate(zip(errors,bounds)):
     assert error<=bound,(case['id'],phase,channel,i,error,bound)
     assert error<=coarse['errors'][phase][channel][i]+1e-12*fine['reference_magnitudes'][phase][channel][i],(case['id'],phase,channel,'fine worse than coarse')
 return results
