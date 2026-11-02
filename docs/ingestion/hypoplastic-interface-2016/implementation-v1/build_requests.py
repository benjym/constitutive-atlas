#!/usr/bin/env python3
"""Freeze flat ABI and browser package cases solely from predeclared source references."""
import copy,hashlib,json
from pathlib import Path
from reference import rk4,stress
ROOT=Path(__file__).resolve().parent
MODEL=ROOT.parents[3]/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json'
NAMES=['sigma_normal','sigma_plane','tau_x','tau_z','e'];KEYS=['gamma_x','gamma_z','normal_strain']
def main():
 p=json.loads((ROOT/'policy.json').read_text());rr=json.loads((ROOT/'references.json').read_text());m=json.loads(MODEL.read_text());sha=hashlib.sha256(MODEL.read_bytes()).hexdigest()
 metadata=json.loads((ROOT/'generated/path_catalogue.json').read_text())['models'][0]
 assert metadata['parameters']==list(p['parameters']) and metadata['controls']==KEYS
 settings=p['qualification']['python_settings'];ss=[settings[k] for k in ['absolute','relative','min_step','max_step','max_depth','max_trials']]
 reqs=[];expects={};package=[]
 def expected(y,coordinate):return {'status':1,'state':y,'stress':stress(y),'coordinate':coordinate,'observables':stress(y)+[(y[0]+2*y[1])/3,y[4]]}
 def request(id,y,co,current,end,prog=1.,state_from=None,opts=None):
  q={'id':id,'model':0,'state':y,'coordinate':co,'parameters':list(p['parameters'].values()),'current_controls':[current[k] for k in KEYS],'start_controls':[current[k] for k in KEYS],'end_controls':[end[k] for k in KEYS],'progress':prog,'settings':ss[:],'observable_count':8}
  if state_from:q['state_from']=state_from
  if opts:q.update(opts)
  reqs.append(q);return q
 for case,ref in zip(p['cases'],rr['rows']):
  for repetition in [1,2]:
   y=case['initial'][:];co=0.;controls=case['start_controls'];previous=None
   for i,(seg,refend) in enumerate(zip(case['segments'],ref['refinements'][-1]['endpoints'])):
    ident=f"{case['name']}-segment{i+1}-repeat{repetition}";end=seg['end_controls'];prog=seg['progress']
    request(ident,y,co,controls,end,prog,previous);expects[ident]=expected(refend['state'],co+prog)
    if repetition==1:
     context={'state':dict(zip(NAMES,y)),'coordinate':co,'controls':controls,'parameters':p['parameters']}
     endctx={'state':dict(zip(NAMES,refend['state'])),'coordinate':co+prog,'controls':end,'parameters':p['parameters']}
     package.append({'id':f"{case['name']}-segment{i+1}",'request':{'context':context,'progress':prog,'controls_end':end,'samples':1,'settings':settings},'expected':[{'context':context,'observables':{'stress':stress(y)}},{'context':endctx,'observables':{'stress':refend['stress']}}]})
     # Restart split references reuse the same fixed-step RK4 method and policy.
     d=[(end[k]-controls[k])/prog for k in KEYS];middle={k:(controls[k]+end[k])/2 for k in KEYS}
     ym=rk4(y,d,p['parameters'],256,prog/2)
     half1=ident+'-restart1';half2=ident+'-restart2'
     request(half1,y,co,controls,middle,prog/2);expects[half1]=expected(ym,co+prog/2)
     request(half2,ym,co+prog/2,middle,end,prog/2,half1);expects[half2]=expected(refend['state'],co+prog)
    y=refend['state'];co+=prog;controls=end;previous=ident
 base=p['cases'][0];y=base['initial'];co=0.;controls=base['start_controls'];end={**controls,'gamma_x':.004}
 for name,index,value in [('normal_zero',0,0.),('plane_zero',1,0.),('schur_negative',2,100000.),('density_below',4,.1),('density_above',4,2.)]:
  yy=y[:];yy[index]=value;q=request('invalid-'+name,yy,co,controls,controls);expects[q['id']]={'status':0}
 for name,key,value in [('unordered_limits','ed0',1.),('negative_hardness','hs',-1.)]:
  pp=p['parameters'].copy();pp[key]=value;q=request('invalid-'+name,y,co,controls,controls,opts={'parameters':list(pp.values())});expects[q['id']]={'status':0}
 for name,opts in [('missing_control',{'current_controls':[0.,0.]}),('nonfinite_control',{'end_controls':['nan',0.,0.]}),('mismatched_start',{'start_controls':[.001,0.,0.]}),('zero_progress_changed',{'progress':0.}),('negative_progress',{'progress':-1.}),('trial_budget',{'settings':[ss[0],ss[1],ss[2],.01,ss[4],1]})]:
  q=request('invalid-'+name,y,co,controls,end,opts=opts);expects[q['id']]={'status':0}
 q=request('recovery-after-trial-budget',y,co,controls,end);xref=next(x for x in rr['rows'] if x['case']=='x_shear')['refinements'][-1]['endpoints'][-1]['state'];expects[q['id']]=expected(xref,1.)
 q=request('zero-progress-identity',y,co,controls,controls,0.);expects[q['id']]=expected(y,0.)
 artifact={'identity':'interface2016-flat-ABI-requests-v1','model':m['id'],'definition_sha256':sha,'policy_sha256':rr['policy_sha256'],'metadata':metadata,'requests':reqs}
 (ROOT/'backend-requests.json').write_text(json.dumps(artifact,indent=2)+'\n')
 (ROOT/'backend-expectations.json').write_text(json.dumps({'requests_sha256':hashlib.sha256((ROOT/'backend-requests.json').read_bytes()).hexdigest(),'source_reference_sha256':hashlib.sha256((ROOT/'references.json').read_bytes()).hexdigest(),'scaled_tolerance':p['qualification']['endpoint_scaled_absolute'],'state_scales':p['reference']['scale'],'expected':expects,'repeat_pairs':[[f"{c['name']}-segment{i+1}-repeat1",f"{c['name']}-segment{i+1}-repeat2"] for c in p['cases'] for i in range(len(c['segments']))]},indent=2)+'\n')
 (ROOT/'package-cases.json').write_text(json.dumps({'model':m['id'],'definition_sha256':sha,'policy_sha256':rr['policy_sha256'],'tolerance':{'stress_absolute_Pa':.2,'void_ratio_absolute':2e-6},'cases':package},indent=2)+'\n')
 ex=next(x for x in package if x['id']=='multishear-segment1');r=ex['request']
 example={'id':'hvwe2016-illustrative-multishear','model':m['id'],'definition_sha256':sha,'description':'Illustrative prescribed source-angle path; inherited Hochstetten host example, not an interface calibration or reproduced experiment. Fixed local zero spin.','context':r['context'],'advance':{'progress':r['progress'],'controls_start':r['context']['controls'],'controls_end':r['controls_end']},'execution':settings,'expected':ex['expected'][-1]}
 (ROOT/'example.json').write_text(json.dumps(example,indent=2)+'\n')
 print(json.dumps({'candidate_sha256':sha,'flat_requests':len(reqs),'package_cases':len(package),'settings_order':['absolute','relative','min_step','max_step','max_depth','max_trials']}))
if __name__=='__main__':main()
