"""Diagnostic fidelity gates; no revised constitutive accuracy or promotion gate."""
from pathlib import Path
import json,math,sys
if not __debug__:raise RuntimeError('assertions required')
def load(p):return json.loads(Path(p).read_text())
def same(x,y):
 if isinstance(y,list):return isinstance(x,list)and len(x)==len(y)and all(same(a,b)for a,b in zip(x,y))
 if isinstance(y,dict):return isinstance(x,dict)and x.keys()==y.keys()and all(same(x[k],y[k])for k in y)
 if type(y)is bool:return type(x)is bool and x==y
 if isinstance(y,(int,float)):return type(x)in(int,float)and math.isfinite(x)and float(x).hex()==float(y).hex()
 return type(x)is type(y)and x==y
def q(state):return state[0]-.5*(state[1]+state[2])
def point_subset(p):return {k:p[k]for k in ('control','state','strain','u')}
def assess(doc,request,parent_response=None):
 assert doc['schema']=='control-trace-diagnostic-v1'and len(doc['streams'])==2
 expected_ids=['backend-sine','common-literal'];reports=[]
 for stream,sid in zip(doc['streams'],expected_ids):
  assert stream['id']==sid
  a,b=stream['baseline'],stream['traced'];assert same(a,b),'instrumentation perturbs baseline'
  assert a['ok']is True and len(a['points'])==65
  if sid=='backend-sine'and parent_response is not None:
   assert all(same(point_subset(x),point_subset(y))for x,y in zip(a['points'],parent_response['points'])),'new baseline differs from original artifact'
  points=a['points'];calls=stream['calls'];assert len(calls)>=64;assert [x['step']for x in calls]==sorted(x['step']for x in calls)
  assert same(points[0]['state'],request['initial'])and same(points[0]['strain'],[0.]*6)
  maxres=0.;trialcounts=[];steps=[]
  for i in range(1,65):
   point,prev=points[i],points[i-1];group=[x for x in calls if x['step']==i];assert group
   if sid=='common-literal':assert float(point['control']).hex()==request['common_controls_hex'][i-1]
   for c in group:
    assert c['ok']is True and c['role']in('trial','pert','test')and type(c['iteration'])is int and c['iteration']>=0
    assert same(c['parent'],prev['state'])
    for k in ('de','state'):assert len(c[k])==6 and all(type(v)in(int,float)and math.isfinite(v)for v in c[k])
    assert c['de'][1]==c['de'][2]==-.5*c['de'][0]and c['de'][3:]==[0.,0.,0.]
   chosen=group[-1];assert chosen['role']=='trial'
   assert same(chosen['state'],point['state'])and same(chosen['diagnostics'],point['diagnostics'])
   assert same([prev['strain'][j]+chosen['de'][j]for j in range(6)],point['strain'])
   residual=q(point['state'])-q(prev['state'])-(point['control']-prev['control']);assert abs(residual)<.001
   trials=[c for c in group if c['role']=='trial'];assert [c['iteration']for c in trials]==list(range(len(trials)))
   maxres=max(maxres,abs(residual));trialcounts.append(len(trials));steps.append({'step':i,'accepted_outer_residual':residual,'trial_iterations':len(trials),'chosen_axial_increment':chosen['de'][0]})
  reports.append({'stream':sid,'calls':len(calls),'maximum_accepted_outer_residual':maxres,'trial_iterations':trialcounts,'steps':steps,'physical_logging_identity':True,'original_artifact_identity_checked':sid=='backend-sine'and parent_response is not None})
 return {'diagnostic_fidelity_passed':True,'streams':reports}
if __name__=='__main__':
 s=Path(__file__).resolve().parent;doc=load(sys.argv[1]);parent=load(sys.argv[2]);r=next(json.loads(x['raw'])for x in parent if x['id']=='protocol-3/cyclic');print(json.dumps(assess(doc,load(s/'request.json'),r),indent=2))
