#!/usr/bin/env python3
"""Explicit coordinator-only native VIBE qualification; never builds artifacts."""
import argparse,ctypes as C,hashlib,json,math,os,sys,traceback
from pathlib import Path
from dataclasses import asdict
from copy import deepcopy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from atlas.model import load
from atlas.controlled_time import Settings,context_from_dict,components,stage_controls
from atlas.controlled_time_native import NativeEngine

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def stateflat(c):return [*c['state']['sigma_net'],c['state']['e'],c['state']['a_scan']]
def close(a,b,bound,label):
 b=float(b);error=abs(a-b);limit=bound[0]+bound[1]*max(abs(a),abs(b))
 if not math.isfinite(a) or error>limit:raise AssertionError((label,a,b,error,limit))
 return dict(error=error,limit=limit)
def endpoint(result,case,plan):
 comparisons=[]
 for j,(a,b) in enumerate(zip(stateflat(result['context']),case['expected_state'])):comparisons.append(close(a,b,plan['bounds']['trajectory_stress' if j<6 else 'trajectory_scalar'],case['id']+' state'+str(j)))
 for row in result['points']:
  for j,(x,y) in enumerate(zip(row['observables']['stress'],row['context']['state']['sigma_net'])):comparisons.append(close(x,y,plan['bounds']['trajectory_stress'],case['id']+' source stress binding'+str(j)))
 final=result['points'][-1]['observables']
 for n,v in case['expected_observables'].items():comparisons.append(close(final[n],v,plan['bounds']['observable'],case['id']+' '+n))
 return comparisons
def rawsafe(value):
 if isinstance(value,float) and not math.isfinite(value):return {'nonfinite':repr(value)}
 if isinstance(value,dict):return {k:rawsafe(v) for k,v in value.items()}
 if isinstance(value,(list,tuple)):return [rawsafe(v) for v in value]
 return value
class Journal:
 def __init__(self,path):self.path=path;self.f=(path/'events.jsonl').open('x')
 def emit(self,event):self.f.write(json.dumps(rawsafe(event),allow_nan=False,separators=(',',':'))+'\n');self.f.flush();os.fsync(self.f.fileno())
 def save(self,name,value):
  with (self.path/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n');f.flush();os.fsync(f.fileno())
class RecordedEngine(NativeEngine):
 def __init__(self,*args,journal,**kw):self.journal=journal;super().__init__(*args,**kw)
 def drain(self):
  for row in self.trace:self.journal.emit(dict(kind='raw-native',data=row))
  self.trace=[]
 def evaluate(self,*args,**kw):
  try:return super().evaluate(*args,**kw)
  finally:self.drain()
 def advance(self,*args,**kw):
  self.journal.emit(dict(kind='before-native-advance',parent=asdict(args[1]),duration=args[2],end=args[4],settings=asdict(args[5]) if len(args)>5 else asdict(Settings())))
  try:return super().advance(*args,**kw)
  finally:self.drain()
def instrument(engine,journal):
 # Capture the actual C buffers around every material call, including refusals.
 for name,inputs,outputs,scalars in [
  ('controlled_time_evaluate',[(1,2),(3,4),(6,7),(8,9)],[(11,12),(13,14),(15,16)],[0,5,10]),
  ('controlled_time_advance',[(1,2),(3,4),(7,8),(9,10),(11,12),(13,14),(15,16)],[(17,18),(19,20),(21,22),(23,24),(25,26),(27,28)],[0,5,6])]:
  original=getattr(engine.lib,name)
  def checked(*a,_fn=original,_name=name,_ins=inputs,_outs=outputs,_scalars=scalars):
   read=lambda pairs:[[a[p][i] for i in range(a[n])] for p,n in pairs]
   before=read(_ins);sentinels=read(_outs);journal.emit(dict(kind='before-CABI',operation=_name,scalars=[a[i] for i in _scalars],inputs=before,outputs=sentinels))
   status=_fn(*a);after=read(_ins);output=read(_outs);journal.emit(dict(kind='after-CABI',operation=_name,status=status,inputs=after,outputs=output))
   assert before==after,'Compiled material call changed input buffers'
   if status!=1:assert output==sentinels,'Failed compiled material call changed output buffers'
   return status
  setattr(engine.lib,name,checked)

def run(engine,m,request):
 spec=deepcopy(request);q=context_from_dict(m,spec['context']);points=[];engine.evaluate(q)
 for s in spec['segments']:
  start=q
  for i in range(1,s['samples']+1):
   end,_=stage_controls(m,start.controls,s['controls_end'],s['duration'],i/s['samples']);time=start.time+s['duration'] if i==s['samples'] else start.time+s['duration']*i/s['samples'];r=engine.advance(m,q,time-q.time,q.controls,end,Settings(**spec['settings']))
   if i==1:
    points.append(dict(segment=s['id'],side='left',context=asdict(q),observables=r.left_observables));right=asdict(q);right['control_rates']=deepcopy(r.context.control_rates);points.append(dict(segment=s['id'],side='right',context=right,observables=r.right_observables))
   points.append(dict(segment=s['id'],side='end',context=asdict(r.context),observables=r.observables,diagnostics=r.diagnostics));q=r.context
 return dict(profile=spec['profile'],model=spec['model'],model_sha256=q.model_sha256,request=spec,context=asdict(q),points=points)
def split_request(m,request):
 prefix=deepcopy(request);suffix=deepcopy(request);prefix['segments']=[];suffix['segments']=[];left=sum(s['samples'] for s in request['segments'])//2;values=request['context']['controls']
 for s in request['segments']:
  if left>=s['samples']:prefix['segments'].append(deepcopy(s));left-=s['samples']
  elif left>0:
   mid,_=stage_controls(m,values,s['controls_end'],s['duration'],left/s['samples']);prefix['segments'].append(dict(s,duration=s['duration']*left/s['samples'],samples=left,controls_end=mid));suffix['segments'].append(dict(s,duration=s['duration']*(s['samples']-left)/s['samples'],samples=s['samples']-left));left=0
  else:suffix['segments'].append(deepcopy(s))
  values=s['controls_end']
 return prefix,suffix
def raw_domain(engine,m,plan,journal):
 e=engine;ns,np,nc,no,_,_=e.shapes;fields=e.fields
 for case in plan['invalid_cases']:
  for kind in (['evaluate','advance'] if 'advance_end' in case else ['evaluate']):
   ctx=deepcopy(case['invalid_context'] if kind=='evaluate' else case['valid_context']);valid=context_from_dict(m,case['valid_context']);values=ctx['controls'];end=case.get('advance_end',values);duration=case.get('advance_duration',1.)
   arrays=[e.array(components(ctx['state'],m['state'])),e.array([ctx['parameters'][n] for n in m['parameters']]),e.array(components(values,fields)),e.array(components(ctx['control_rates'],fields)),e.array(components(values,fields)),e.array(components(end,fields)),e.array(list(plan['settings'].values()))];z,pa,v,cr,start,ep,sett=arrays
   sizes=[ns,no,ns] if kind=='evaluate' else [ns,1,nc,nc,no,4];outs=[e.array([-1234567.]*n) for n in sizes];before=[list(a) for a in arrays]
   journal.emit(dict(kind='before-raw-domain',case=case['id'],operation=kind,inputs=before,output_sentinels=[list(o) for o in outs],duration=duration))
   if kind=='evaluate':status=e.lib.controlled_time_evaluate(e.index,z,ns,pa,np,ctx['time'],v,nc,cr,nc,0,outs[0],ns,outs[1],no,outs[2],ns)
   else:status=e.lib.controlled_time_advance(e.index,z,ns,pa,np,ctx['time'],duration,v,nc,cr,nc,start,nc,ep,nc,sett,6,outs[0],ns,outs[1],1,outs[2],nc,outs[3],nc,outs[4],no,outs[5],4)
   after=[list(a) for a in arrays];raw=[list(o) for o in outs];journal.emit(dict(kind='after-raw-domain',case=case['id'],operation=kind,status=status,inputs_after=after,outputs=raw))
   assert status==0 and after==before and all(x==-1234567. for o in raw for x in o),'Raw compiled refusal/transaction gate failed'
   recovered=e.advance(m,valid,1.,valid.controls,valid.controls,Settings(**plan['settings']));assert asdict(valid)==case['valid_context'];assert recovered.context.time==valid.time+1

def main():
 a=argparse.ArgumentParser();a.add_argument('--module',type=Path,required=True);a.add_argument('--catalogue',type=Path,required=True);a.add_argument('--model',type=Path,required=True);a.add_argument('--plan',type=Path,required=True);a.add_argument('--source-manifest',type=Path,required=True);a.add_argument('--output',type=Path,required=True);args=a.parse_args()
 plan=json.loads(args.plan.read_text());assert digest(args.model)==plan['model_file_sha256'];freeze=json.loads(args.source_manifest.read_text());
 for pin in [*freeze['files'],*plan['source_files']]:assert digest(Path(pin['path']) if Path(pin['path']).is_absolute() else ROOT/pin['path'])==pin['sha256'],pin['path']
 args.output.mkdir(parents=True,exist_ok=False);j=Journal(args.output)
 bindings=dict(backend='native',plan_sha256=digest(args.plan),model_file_sha256=digest(args.model),module_sha256=digest(args.module),catalogue_sha256=digest(args.catalogue),source_manifest_sha256=digest(args.source_manifest),collector_sha256=digest(__file__),plan_identity=plan['identity']);j.save('bindings.json',bindings);j.emit(dict(kind='before-module-load',bindings=bindings));summary=dict(status='started',bindings=bindings,cases=[],parity='requires independent Wasm peer run')
 try:
  m=load(args.model);engine=RecordedEngine(args.module,args.catalogue,m,journal=j);instrument(engine,j);j.emit(dict(kind='loaded',artifact_identity=engine.artifact_identity,shapes=engine.shapes));bounds=plan['bounds'];point_results=[]
  for c in plan['points']:
   q=context_from_dict(m,c['context']);before=asdict(q);j.emit(dict(kind='before-point',id=c['id'],context=before));rate,obs,scales=engine.evaluate(q);assert asdict(q)==before
   flat=[*rate['sigma_net'],rate['e'],rate['a_scan']];checks=[close(x,y,bounds['point_stress_rate' if k<6 else 'point_scalar_rate'],c['id']+' rate'+str(k)) for k,(x,y) in enumerate(zip(flat,c['expected_rate']))]
   for k,(x,y) in enumerate(zip(obs['stress'],q.state['sigma_net'])):checks.append(close(x,y,bounds['trajectory_stress'],c['id']+' source stress binding'+str(k)))
   for name,y in c['expected_observables'].items():checks.append(close(obs[name],y,bounds['observable'],c['id']+' '+name))
   j.emit(dict(kind='point-pass',id=c['id'],rate=rate,observables=obs,scales=scales,comparisons=checks));point_results.append(dict(id=c['id'],rate=rate,observables=obs,scales=scales));summary['cases'].append(dict(id=c['id'],kind='point',status='pass'))
  j.save('points.json',point_results)
  for c in plan['histories']:
   before=deepcopy(c['request']);j.emit(dict(kind='before-history',id=c['id'],request=before));r=run(engine,m,before);assert c['request']==before;checks=endpoint(r,c,plan);j.save(c['id']+'.json',r)
   replay=run(engine,m,deepcopy(before));assert replay==r,'Full deterministic replay mismatch'
   pre,post=split_request(m,before);mid=run(engine,m,pre);post['context']=asdict(context_from_dict(m,mid['context']));restarted=run(engine,m,post);endpoint(restarted,c,plan);j.save(c['id']+'-restart.json',restarted)
   for cap in plan['refinement_max_steps']:
    spec=deepcopy(before);spec['settings']['maximum_step_seconds']=cap;refined=run(engine,m,spec);endpoint(refined,c,plan);j.save(c['id']+'-maxstep-'+str(cap)+'.json',refined)
   j.emit(dict(kind='history-pass',id=c['id'],comparisons=checks));summary['cases'].append(dict(id=c['id'],kind='history',status='pass'))
  parent=context_from_dict(m,plan['histories'][0]['request']['context']);before=asdict(parent)
  for settings in [dict(plan['settings'],maximum_trials=1,maximum_step_seconds=.001),dict(plan['settings'],maximum_depth=1,maximum_step_seconds=.001)]:
   try:engine.advance(m,parent,100.,parent.controls,parent.controls,Settings(**settings))
   except ValueError:pass
   else:raise AssertionError('Expected budget/depth refusal')
   assert asdict(parent)==before;engine.advance(m,parent,1.,parent.controls,parent.controls,Settings(**plan['settings']))
  raw_domain(engine,m,plan,j);summary['status']='pass-native-pending-Wasm-parity'
 except BaseException as exc:
  summary['status']='failed';summary['error']=dict(type=type(exc).__name__,message=str(exc),traceback=traceback.format_exc());j.emit(dict(kind='failure',error=summary['error']));raise
 finally:
  j.f.close();summary['events_sha256']=digest(args.output/'events.jsonl');summary['result_files']={p.name:digest(p) for p in sorted(args.output.glob('*.json'))};j.save('summary.json',summary)
if __name__=='__main__':main()
