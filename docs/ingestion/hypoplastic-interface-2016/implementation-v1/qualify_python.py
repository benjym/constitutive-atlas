#!/usr/bin/env python3
"""Candidate interpreter qualification against pre-observation frozen Cartesian references."""
import copy, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[3]))
from atlas.model import load
from atlas.path import initialize,advance,evaluate_stage,stage_inputs,Settings,Context
from reference import rhs,stress
MODEL=ROOT.parents[3]/'models/research/interface2016/hvwe2016-reconciled-fixed-local.json'
NAMES=['sigma_normal','sigma_plane','tau_x','tau_z','e']
def state(v):return dict(zip(NAMES,v))
def vector(s):return [s[n] for n in NAMES]
def main():
 p=json.loads((ROOT/'policy.json').read_text());refs=json.loads((ROOT/'references.json').read_text());assert refs['all_converged']
 assert refs['policy_sha256']==hashlib.sha256((ROOT/'policy.json').read_bytes()).hexdigest()
 m=load(MODEL);settings=Settings(**p['qualification']['python_settings']);scale=p['reference']['scale'];rows=[]
 def err(a,b,sc):return max(abs(x-y)/s for x,y,s in zip(a,b,sc))
 for c,r in zip(p['cases'],refs['rows']):
  parent=initialize(m,state(c['initial']),0.,c['start_controls'],p['parameters']);baseline=[];row={'case':c['name']}
  maxstate=maxstress=maxrate=0.
  for seg,expected in zip(c['segments'],r['refinements'][-1]['endpoints']):
   start=parent.controls;end=seg['end_controls'];d=[(end[k]-start[k])/seg['progress'] for k in ['gamma_x','gamma_z','normal_strain']]
   inp=stage_inputs(m,parent.coordinate,start,end,0.,seg['progress']);rates,obs=evaluate_stage(m,parent.state,parent.parameters,inp)
   rateerror=err(vector(rates),rhs(vector(parent.state),d,p['parameters']),scale);maxrate=max(maxrate,rateerror)
   snapshot=copy.deepcopy(parent)
   child=advance(m,parent,seg['progress'],start,end,settings)
   repeated=advance(m,parent,seg['progress'],start,end,settings)
   assert child==repeated and parent==snapshot
   mid={k:(start[k]+end[k])/2 for k in start}
   split=advance(m,parent,seg['progress']/2,start,mid,settings)
   # Simulate JSON restart of every context member.
   packed=json.loads(json.dumps({'state':split.state,'coordinate':split.coordinate,'controls':split.controls,'parameters':split.parameters}))
   restart=initialize(m,packed['state'],packed['coordinate'],packed['controls'],packed['parameters'])
   restarted=advance(m,restart,seg['progress']/2,mid,end,settings)
   assert err(vector(restarted.state),vector(child.state),scale)<=p['qualification']['endpoint_scaled_absolute']
   assert restarted.coordinate==child.coordinate and restarted.controls==child.controls and restarted.parameters==child.parameters
   se=err(vector(child.state),expected['state'],scale);te=err(stress(vector(child.state)),expected['stress'],[scale[0]]*6)
   _,out=evaluate_stage(m,child.state,child.parameters,stage_inputs(m,child.coordinate,end,end,0,0))
   assert out['stress']==stress(vector(child.state))
   maxstate=max(maxstate,se);maxstress=max(maxstress,te)
   assert se<=p['qualification']['endpoint_scaled_absolute'] and te<=p['qualification']['endpoint_scaled_absolute']
   if c['name']=='hold':assert child.state==parent.state
   baseline.append({'state':child.state,'stress':out['stress'],'coordinate':child.coordinate,'controls':child.controls});parent=child
  row.update(max_state_scaled_error=maxstate,max_stress_scaled_error=maxstress,max_rate_scaled_error=maxrate,endpoints=baseline,repeat_exact=True,restart_passed=True);rows.append(row)
 # Invalid contexts/advances must reject without mutating parent.
 c=p['cases'][0];base=initialize(m,state(c['initial']),0.,c['start_controls'],p['parameters']);negative=[]
 def rejects(name,call):
  saved=copy.deepcopy(base)
  try:call()
  except (ValueError,ArithmeticError,TypeError) as exc:
   assert base==saved;negative.append({'case':name,'rejected':True,'error':str(exc),'parent_unchanged':True});return
  raise AssertionError('unexpected acceptance '+name)
 def badstate(**changes):
  s=copy.deepcopy(base.state);s.update(changes);return initialize(m,s,0.,base.controls,base.parameters)
 rejects('nonpositive normal stress',lambda:badstate(sigma_normal=0.))
 rejects('nonpositive inplane stress',lambda:badstate(sigma_plane=0.))
 rejects('nonpositive Schur determinant',lambda:badstate(tau_x=100000.))
 rejects('e below dense limit',lambda:badstate(e=.1))
 rejects('e above loose limit',lambda:badstate(e=2.))
 def badparam(**changes):
  pp=copy.deepcopy(base.parameters);pp.update(changes);return initialize(m,base.state,0.,base.controls,pp)
 rejects('unordered limiting void ratios',lambda:badparam(ed0=1.))
 rejects('negative hs',lambda:badparam(hs=-1.))
 rejects('missing control',lambda:initialize(m,base.state,0.,{},base.parameters))
 cc={**base.controls,'gamma_x':float('nan')}
 rejects('nonfinite control',lambda:initialize(m,base.state,0.,cc,base.parameters))
 wrong={**base.controls,'gamma_x':.001};end={**base.controls,'gamma_x':.004}
 rejects('mismatched committed start controls',lambda:advance(m,base,1.,wrong,end,settings))
 rejects('zero progress with changed control',lambda:advance(m,base,0.,base.controls,end,settings))
 rejects('negative progress',lambda:advance(m,base,-1.,base.controls,end,settings))
 rejects('low trial budget rollback',lambda:advance(m,base,1.,base.controls,end,Settings(**{**p['qualification']['python_settings'],'max_trials':1,'max_step':.01})))
 recovery=advance(m,base,1.,base.controls,end,settings);assert recovery==advance(m,base,1.,base.controls,end,settings)
 zero=advance(m,base,0.,base.controls,base.controls,settings);assert zero==base
 report={'identity':'interface2016-python-qualification-v1','passed':True,'candidate_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),'policy_sha256':refs['policy_sha256'],'references_sha256':hashlib.sha256((ROOT/'references.json').read_bytes()).hexdigest(),'qualifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':rows,'negative_cases':negative,'rollback_recovery_exact':True,'zero_progress_exact':True,'compiled_calls':0,'scientific_approval':False}
 (ROOT/'python-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'cases':len(rows),'increments':sum(len(r['endpoints']) for r in rows),'negative_cases':len(negative),'maximum_state_scaled_error':max(r['max_state_scaled_error'] for r in rows),'maximum_rate_scaled_error':max(r['max_rate_scaled_error'] for r in rows)}))
if __name__=='__main__':main()
