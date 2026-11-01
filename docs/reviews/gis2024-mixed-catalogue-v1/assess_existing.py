"""Apply the prospectively frozen compatibility policy to retained API results."""
from pathlib import Path
import importlib.util,json,math
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
def read(p):return json.loads(Path(p).read_text())
def mod(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def compare_old(rows,backend):
 expected=read(P/'old-nine-baseline-responses.json');requests=read(P/'old-nine-requests.json');policy=read(P/'policy.json')['old_nine'];failures=[];fields=0
 assert len(rows)==len(expected)==len(requests)==policy['request_count']
 absolute=policy[backend+'_absolute'];relative=policy[backend+'_relative'];catalogue_hash=read(P/'generated-eleven/models.json')['sha256']
 def compare(a,b,path):
  nonlocal fields
  if isinstance(b,dict):
   if not isinstance(a,dict)or set(a)!=set(b):failures.append({'path':path,'reason':'object shape'});return
   for key in b:
    if key=='elapsed_ms':continue
    if key=='catalogue_hash':
     if a[key]!=catalogue_hash:failures.append({'path':path,'reason':'candidate catalogue hash'})
    else:compare(a[key],b[key],path+'/'+key)
  elif isinstance(b,list):
   if not isinstance(a,list)or len(a)!=len(b):failures.append({'path':path,'reason':'array shape'});return
   for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+'/'+str(i))
  elif isinstance(b,bool)or b is None or isinstance(b,str):
   if type(a)is not type(b)or a!=b:failures.append({'path':path,'reason':'exact scalar'})
  elif isinstance(b,(int,float)):
   fields+=1
   if not isinstance(a,(int,float))or isinstance(a,bool)or not math.isfinite(a)or abs(a-b)>absolute+relative*abs(b):failures.append({'path':path,'reason':'numeric mismatch','actual':a,'expected':b})
   if path.rsplit('/',1)[-1]in ('iterations','substeps','rejected')and a!=b:failures.append({'path':path,'reason':'diagnostics changed'})
  else:raise TypeError(type(b))
 failures_expected=0;rollbacks=0
 for actual,wanted,request in zip(rows,expected,requests):
  assert actual['label']==wanted['label']==request['label']
  compare(actual['response'],wanted['response'],wanted['label'])
  if wanted['response'].get('ok')is False:failures_expected+=1
  if actual['response'].get('ok')is False and 'state'in actual['response']:
   original=[float(v)for v in request['args'][2].split(',')]
   if actual['response']['state']!=original:failures.append({'path':request['label'],'reason':'failure did not retain incoming full state'})
   rollbacks+=1
 return {'qualification_pass':not failures,'requests':len(rows),'numeric_fields':fields,'expected_failures':failures_expected,'full_rollback_checks':rollbacks,'failures':failures}

def assess():
 lab=mod('mixed_lab_assessor',P/'assess_laboratory.py');history=mod('mixed_history_assessor',P/'assess_history.py');out={}
 for b in ['native','wasm']:
  old=compare_old(read(P/(b+'-old-nine-responses.json')),b)
  l=lab.assess(read(P/(b+'-laboratory-responses.json')),read(P/'laboratory-inputs.json'),read(P/'laboratory-references.json'),read(P/'laboratory-policy.json'),ROOT)
  h=history.assess(read(P/(b+'-history-responses.json')),read(P/'history-inputs.json'),ROOT)
  out[b]={'old_nine':old,'tresca_laboratory':l,'tresca_api_restart_history':h,'qualification_pass':old['qualification_pass']and l['qualification_pass']and h['qualification_pass']}
 out['overall_pass']=all(out[b]['qualification_pass']for b in ['native','wasm']);return out
if __name__=='__main__':print(json.dumps(assess(),indent=2))
