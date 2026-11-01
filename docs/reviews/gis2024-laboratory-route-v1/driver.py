"""Frozen own-input collector. Every raw process response is saved before parsing."""
import argparse,copy,hashlib,json,select,subprocess,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=ROOT/'docs/reviews/gis2024-browser-preparation-v1';MIX=ROOT/'docs/reviews/gis2024-mixed-catalogue-v1'
def read(p):return json.loads(p.read_bytes())
def dump(p,x):p.write_text(json.dumps(x,indent=2,allow_nan=False)+'\n')
def csv(v):return ','.join(format(x,'.17g')for x in v)
def settings(s):return csv([s[k]for k in ['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks']])
class Client:
 def __init__(self,backend,directory):
  self.backend=backend;self.directory=directory;self.count=0;self.child=None
  self.exe=next(k for k in read(MIX/(backend+'-artifacts.json'))['artifacts']if k.endswith('atlas_solver'if backend=='native'else'atlas.js'))
  if backend=='wasm':
   self.stderr=(directory/'wasm.stderr').open('w');self.child=subprocess.Popen(['node',str(MIX/'rpc.mjs'),self.exe],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
 def call(self,request):
  request=copy.deepcopy(request);before=copy.deepcopy(request)
  if self.child:
   line=json.dumps({k:request[k]for k in ['function','types','args']});self.child.stdin.write(line+'\n');self.child.stdin.flush()
   if not select.select([self.child.stdout],[],[],30)[0]:raise TimeoutError('Wasm response timeout')
   stdout=self.child.stdout.readline();raw={'backend':self.backend,'request':request,'stdout':stdout,'stderr':'','returncode':None,'pid':self.child.pid}
  else:
   cmd=[self.exe,*request['cli']];run=subprocess.run(cmd,capture_output=True,text=True,timeout=30);stdout=run.stdout;raw={'backend':self.backend,'request':request,'stdout':stdout,'stderr':run.stderr,'returncode':run.returncode,'command':cmd}
  index=self.count;self.count+=1;dump(self.directory/'receipts'/f'{index:04d}.json',raw)
  response=json.loads(stdout)
  if self.child:
   assert response.get('inputs_unchanged')is True and 'transport_error'not in response,response;response=response['response']
  assert request==before
  return {'request':request,'response':response,'receipt':index}
 def close(self):
  if self.child:
   self.child.stdin.close();self.child.wait(timeout=10);self.stderr.close();assert self.child.returncode==0

def rate_request(row):
 z=csv(row['initial']);p=csv(row['parameters']);d=csv(row['strain']);return {'function':'atlas_evaluate','types':['string']*5,'args':[row['model'],p,z,z,d],'cli':['--model',row['model'],'--mode','evaluate','--parameters',p,'--initial',z,'--current',z,'--strain',d]}
def lab_request(s):
 p=csv(s['parameters']);z=csv(s['initial']);sett=settings(s['integration_settings']);common=[s['model'],p,z,s['protocol']];cli=['--model',s['model'],'--parameters',p,'--initial',z,'--protocol',str(s['protocol']),'--response-contract','stress-scope-0.1','--integration-settings',sett]
 if 'loading'in s:
  controls=','.join(s['loading']['controls_bits']);return {'function':'atlas_run_controls_scope_with_settings','types':['string','string','string','number','string','string'],'args':common+[controls,sett],'cli':cli+['--mode','run-controls','--laboratory-controls-file','@CONTROLS@'],'controls_wire':controls}
 return {'function':'atlas_run_scope_with_settings','types':['string','string','string','number','number','number','number','string'],'args':common+[s['target'],s['steps'],s['cycles'],sett],'cli':cli+['--mode','run','--target',format(s['target'],'.17g'),'--steps',str(s['steps']),'--cycles',str(s['cycles'])]}
def execute(backend,destination):
 for file in ['freeze.json','dependencies.json']:
  for name,h in read(HERE/file)['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,name
 for path,h in read(MIX/(backend+'-artifacts.json'))['artifacts'].items():assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==h,path
 if backend=='wasm':assert read(HERE/'native-assessment.json')['qualification_pass']is True
 destination.mkdir(parents=True,exist_ok=False);(destination/'receipts').mkdir();c=Client(backend,destination);data={'backend':backend,'rates':[],'laboratory':[],'guards':[],'transport_error':None,'stopped':None}
 def lab(s):
  request=lab_request(s)
  if backend=='native'and 'controls_wire'in request:
   file=destination/'wire-controls.txt';file.write_text(request['controls_wire']);request['cli']=[str(file)if x=='@CONTROLS@'else x for x in request['cli']]
  return c.call(request)
 try:
  data['descriptor']=c.call({'function':'atlas_describe','types':[],'args':[],'cli':['--describe']})
  for r in read(HERE/'rate-references.json'):
   item=c.call(rate_request(r));data['rates'].append({'id':r['id'],'call':item})
   if item['response'].get('ok')is not True:raise RuntimeError('required rate rejected: '+r['id'])
  for row in read(HERE/'laboratory-requests.json'):
   item=lab(row['specification']);data['laboratory'].append({'id':row['id'],'call':item})
   if item['response'].get('ok')is not True:data['stopped']=row['id'];break
  if data['stopped']is None:
   control=read(HERE/'laboratory-requests.json')[0]['specification'];data['clean']=lab(control)
   for row in read(BASE/'guard-cases.json'):data['guards'].append({'id':row['id'],'call':lab(row['specification']),'recovery':lab(control)})
   data['failure']={'call':lab(read(BASE/'failure-case.json')['specification']),'recovery':lab(control)}
 except Exception as exc:data['transport_error']=repr(exc)
 finally:
  try:c.close()
  except Exception as exc:data['transport_error']=repr(exc)
  dump(destination/'result.json',data)
 return 0 if data['transport_error']is None and data['stopped']is None else 2
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('backend',choices=['native','wasm']);a.add_argument('destination',type=Path);s=a.parse_args();raise SystemExit(execute(s.backend,s.destination))
