#!/usr/bin/env python3
"""Generic frozen request orchestration; native CLI or persistent Node Wasm worker.

This file contains no constitutive equations/kernel. Execution is coordinator-owned.
"""
import argparse,gzip,hashlib,json,os,subprocess,sys,time
from pathlib import Path
D=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def csv(v):return ','.join(str(x) for x in v)
def persistent(z):return list(z[:13])+[0.]
class Backend:
 def __init__(self,args,out):
  self.args=args;self.out=out;self.worker=None;self.calls=0
  if args.wasm_engine:
   self.worker=subprocess.Popen(['node',str(D/'run_wasm.mjs'),'--worker','--engine',str(Path(args.wasm_engine).resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=(out/'worker-stderr.txt').open('w'),text=True,bufsize=1)
   ready=self.worker.stdout.readline();assert json.loads(ready).get('ready'),ready
 def call(self,req,log):
  self.calls+=1;started=time.time();wire=json.dumps(req,allow_nan=False,separators=(',',':'))
  raw='';err='';rc=None;argv=None
  try:
   if self.worker:
    self.worker.stdin.write(wire+'\n');self.worker.stdin.flush();reply=json.loads(self.worker.stdout.readline());raw=reply.get('raw','');err=reply.get('error','');rc=0 if not err else 1
   else:
    argv=[str(Path(self.args.solver).resolve()),'--mode',req['mode'],'--model',req['model'],'--parameters',csv(req['parameters']),'--initial',csv(req['initial']),'--integration-settings',csv(req['settings'])]
    if req['mode'] in ['integrate','linearize']:argv+=['--strain',csv(req['strain'])]
    elif req['mode']=='run-controls':
     file=self.out/'controls'/('call-'+str(self.calls)+'.txt');file.parent.mkdir(exist_ok=True);file.write_text(','.join(req['controls_bits']));argv+=['--protocol',str(req['protocol']),'--laboratory-controls-file',str(file.resolve()),'--response-contract','stress-scope-0.1']
    elif req['mode']=='run':argv+=['--protocol',str(req['protocol']),'--target',str(req['target']),'--steps',str(req['steps']),'--cycles','0','--response-contract','stress-scope-0.1']
    r=subprocess.run(argv,capture_output=True,text=True,timeout=180);raw=r.stdout;err=r.stderr;rc=r.returncode
   response=json.loads(raw,parse_constant=lambda token: (_ for _ in ()).throw(ValueError('nonfinite JSON token: '+token)))
   json.dumps(response,allow_nan=False) # reject numeric overflow inside preservation catch
  except Exception as e:response={'ok':False,'harness_error':str(e)}
  record={'call_index':self.calls,'request':req,'argv':argv,'returncode':rc,'elapsed_seconds':time.time()-started,'raw_stdout':raw,'stderr':err,'response':response}
  log.write(json.dumps(record,allow_nan=False,separators=(',',':'))+'\n');log.flush()
  return response
 def close(self):
  if self.worker:self.worker.stdin.close();self.worker.wait(timeout=30)
def base(plan,c,mode):return {'mode':mode,'model':plan['model'],'parameters':c['parameters'],'initial':c['initial'],'settings':plan['settings']}
def run_case(plan,c,backend,log):
 r={'id':c['id'],'group':c['group'],'kind':c['kind'],'resolution':c.get('resolution'),'points':[]}
 if c['kind'] in ['run','controls']:
  req=base(plan,c,'run' if c['kind']=='run' else 'run-controls');req['protocol']=c['protocol']
  if c['kind']=='run':req.update(target=c['target'],steps=c['steps'])
  else:req['controls_bits']=c['controls_bits']
  ans=backend.call(req,log);r['ok']=ans.get('ok') is True;r['response_metadata']={k:v for k,v in ans.items() if k!='points'}
  r['points']=[{'coordinate':p['control'],'state':p['state'],'strain':p['strain']} for p in ans.get('points',[])]
 else:
  z=c['initial'];r['points']=[{'coordinate':c['coordinates'][0],'state':z,'strain':[0.]*6}];strain=[0.]*6;r['ok']=True
  for i,(coord,de) in enumerate(zip(c['coordinates'][1:],c['increments']),1):
   parent=persistent(z)
   if i==c.get('restart_index'):parent=json.loads(json.dumps(parent,allow_nan=False));r['restart_receipt']={'index':i,'all_persistent_state':parent[:13]}
   req=base(plan,c,'integrate');req.update(initial=parent,strain=de,chain_index=i,coordinate=coord)
   ans=backend.call(req,log)
   if not ans.get('ok'):r.update(ok=False,failed_index=i,failed_response=ans);break
   z=ans['state'];strain=[a+b for a,b in zip(strain,de)];r['points'].append({'coordinate':coord,'state':z,'strain':strain.copy()})
 return r
def special(plan,backend,log,results):
 s=plan['special'];r={};c={'parameters':s['parameters'],'initial':s['initial']}
 def call(name,z,de,settings=None,params=None,mode='integrate'):
  req=base(plan,c,mode);req.update(initial=z,strain=de,label=name)
  if settings is not None:req['settings']=settings
  if params is not None:req['parameters']=params
  ans=backend.call(req,log);r[name]=ans;return ans
 z=s['initial'];valid=s['valid_increment'];zero=[0.]*6
 a=call('zero',z,zero);call('hold',persistent(a['state']) if a.get('ok') else z,zero)
 clean=call('clean-valid',z,valid)
 bad=z.copy();bad[:3]=[-1000.]*3;call('invalid-negative-pressure',bad,valid);call('recovery-negative-pressure',z,valid)
 bad=z.copy();bad[7]=100.;call('invalid-alpha',bad,valid);call('recovery-alpha',z,valid)
 badp=s['parameters'].copy();badp[0]='nan';call('invalid-nan-parameter',z,valid,params=badp);call('recovery-nan-parameter',z,valid)
 bad=call('forced-rollback',z,s['forced_increment'],settings=s['forced_settings'])
 if isinstance(bad.get('state'),list) and len(bad['state'])==14:call('rollback-recovery',bad['state'],valid)
 else:r['rollback-recovery']={'ok':False,'harness_error':'forced failure did not return complete14entry parent state; no replacement parent fabricated'}
 prior=results.get(s['ad_parent_case'],{})
 pp=next((p for p in prior.get('points',[]) if p['coordinate']==s['ad_parent_coordinate']),None)
 if pp is None:r['linearize']={'ok':False,'harness_error':'required interior parent unavailable'}
 else:
  z=persistent(pp['state']);de=s['ad_increment'];call('linearize',z,de,mode='linearize')
  for j in range(6):
   for sign in [-1,1]:
    d=de.copy();d[j]+=sign*s['fd_step'];call('fd-'+str(j)+'-'+str(sign),z,d)
 return r
def main():
 ap=argparse.ArgumentParser();group=ap.add_mutually_exclusive_group(required=True);group.add_argument('--solver');group.add_argument('--wasm-engine');ap.add_argument('--output',required=True);ap.add_argument('--case',action='append',default=[]);args=ap.parse_args()
 out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False)
 for name,h in json.loads((D/'manifest.json').read_text()).items():assert sha(D/name)==h,'harness freeze mismatch: '+name
 plan=json.loads((D/'requests.json').read_text())
 for name,h in plan['source_inputs'].items():assert sha(D.parent/name)==h,'reference/candidate mismatch: '+name
 identity={'backend':'wasm' if args.wasm_engine else 'native','artifact_path':str(Path(args.wasm_engine or args.solver).resolve()),'artifact_sha256':sha(args.wasm_engine or args.solver),'model_sha256':plan['model_sha256'],'requests_sha256':sha(D/'requests.json'),'policy_sha256':sha(D/'POLICY.md'),'manifest_sha256':sha(D/'manifest.json'),'harness_only_no_constitutive_kernel':True}
 if args.wasm_engine:
  wasm=Path(args.wasm_engine).with_suffix('.wasm')
  if wasm.exists():identity['wasm_binary_sha256']=sha(wasm)
 (out/'identity.json').write_text(json.dumps(identity,indent=2)+'\n');backend=Backend(args,out);results={};report={'identity':identity,'cases':results}
 try:
  for c in plan['cases']:
   if args.case and c['id'] not in args.case:continue
   print('RUN '+identity['backend']+' '+c['id'],file=sys.stderr,flush=True)
   with gzip.open(out/(c['id']+'.jsonl.gz'),'wt',encoding='utf-8') as log:
    try:results[c['id']]=run_case(plan,c,backend,log)
    except Exception as e:results[c['id']]={'id':c['id'],'ok':False,'harness_error':str(e),'points':[]}
   (out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
  if not args.case:
   with gzip.open(out/'special.jsonl.gz','wt',encoding='utf-8') as log:report['special']=special(plan,backend,log,results)
 finally:
  report['call_count']=backend.calls;(out/'report.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');backend.close()
 print(json.dumps({'backend':identity['backend'],'cases':len(results),'calls':backend.calls,'report':str(out/'report.json')}))
if __name__=='__main__':main()
