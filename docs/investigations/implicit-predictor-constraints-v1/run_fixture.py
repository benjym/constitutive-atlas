#!/usr/bin/env python3
"""Coordinator-run frozen requests; preserve exact raw output and all failures."""
import argparse,hashlib,json,subprocess,math
from pathlib import Path
p=argparse.ArgumentParser();g=p.add_mutually_exclusive_group(required=True);g.add_argument('--solver',type=Path);g.add_argument('--wasm',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();here=Path(__file__).parent;request_bytes=(here/'requests.json').read_bytes();requests=json.loads(request_bytes);a.output.mkdir(parents=True,exist_ok=False)
worker=None
if a.wasm:worker=subprocess.Popen(['node',str(here/'wasm_worker.mjs'),str(a.wasm.resolve())],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=open(a.output/'worker-stderr.txt','w'),text=True)
by_id={c['id']:c for c in requests['cases']}
execution=requests['cases']+[by_id[id] for pair in requests['recovery_pairs'] for id in pair]
report={'kind':'predictor-constraint-compiled-report-1','status':'running','backend':'wasm' if worker else 'native','request_sha256':hashlib.sha256(request_bytes).hexdigest(),'engine_path':str((a.wasm or a.solver).resolve()),'engine_sha256':hashlib.sha256((a.wasm or a.solver).read_bytes()).hexdigest(),'rows':[],'failures':[]};previous=None
try:
 for original in execution:
  c=json.loads(json.dumps(original))
  if c['id'] in ['unload','reload','hold']:
   if previous is None or not previous.get('ok'):raise RuntimeError('chain predecessor failed; cannot manufacture restart state')
   c['initial']=previous['state']
  row={'request':c};report['rows'].append(row)
  if worker:
   worker.stdin.write(json.dumps(c)+'\n');worker.stdin.flush();wire=worker.stdout.readline();row['wire']=wire;transport=json.loads(wire)
   if 'error'in transport:raise RuntimeError(transport['error'])
   raw=transport['raw'];row['stdout']=raw
  else:
   csv=lambda x:','.join(format(v,'.17g') for v in x)
   cmd=[str(a.solver.resolve()),'--mode','integrate','--model',c['model'],'--parameters',csv(c['parameters']),'--initial',csv(c['initial']),'--strain',csv(c['strain']),'--integration-settings',csv(c['integration_settings'])];r=subprocess.run(cmd,text=True,capture_output=True,timeout=60);row.update(command=cmd,returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);raw=r.stdout
  result=json.loads(raw);row['response']=result;previous=result
  errors=[]
  if result.get('ok')!=c['expected']['ok']:errors.append('unexpected outcome')
  if c['expected']['ok'] and result.get('ok'):
   z=result.get('state',[]);expected=c['expected']['state']
   if len(z)!=8 or not all(math.isfinite(v) for v in z):errors.append('invalid full state')
   else:
    if any(abs(v-w)>(1e-8 if i<6 else 1e-10) for i,(v,w) in enumerate(zip(z,expected))):errors.append('analytic state mismatch')
    K,Y,cap=c['parameters'];mean=sum(z[:3])/3
    if (mean-Y)/K>1e-10 or z[7]<-1e-12 or mean>cap or mean<=0:errors.append('physical constraint violation')
  elif not c['expected']['ok']:
   if result.get('state')!=c['initial']:errors.append('full rollback mismatch')
  row['errors']=errors
  if errors:report['failures'].append({'id':c['id'],'errors':errors})
except Exception as error:report['failures'].append({'error':str(error)})
finally:
 if worker:worker.stdin.close();worker.wait(timeout=10)
 report['status']='passed' if not report['failures'] and len(report['rows'])==len(execution) else 'failed';(a.output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(report['status']);raise SystemExit(0 if report['status']=='passed' else 1)
