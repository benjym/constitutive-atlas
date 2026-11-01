"""Independent saved raw-response parity coverage and artifact audit."""
from pathlib import Path
import json,hashlib,math
P=Path(__file__).resolve().parent;B=P.parents[1]/'execution-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
n=json.loads((B/'native-results.json').read_text());w=json.loads((B/'wasm-results.json').read_text())
for saved,replay in [('wasm-assessment.json','wasm-assessment-replay.json'),('wasm-partition-assessment.json','wasm-partition-replay.json'),('parity-results.json','parity-replay.json')]:
 assert json.loads((B/saved).read_text())==json.loads((P/replay).read_text())
assert w['requests_sha256']==sha(B/'requests.json')
artifact=Path('/private/tmp/atlas-duncan-material-v2/wasm/duncan.js');binary=artifact.with_suffix('.wasm')
assert sha(artifact)==w['artifact_sha256'] and sha(binary)==w['wasm_sha256']
worst=(0.,'');count=0;rawcalls=0
def responses(a,b,label):
 global count,worst
 if isinstance(a,dict) and isinstance(b,dict):
  if 'state' in a and 'state' in b and isinstance(a['state'],list) and all(isinstance(x,(int,float)) for x in a['state']):
   x=a['state'];y=b['state'];assert len(x)==len(y)==7
   if all(math.isfinite(t) for t in x+y):
    for i,(u,v) in enumerate(zip(x,y)):
     d=abs(u-v)/1e5;assert d<=4e-8,(label,i,d)
     count+=1
     if d>worst[0]:worst=(d,label+'/state/'+str(i))
  for key in sorted(a.keys()&b.keys()):
   if key!='state':responses(a[key],b[key],label+'/'+key)
 elif isinstance(a,list) and isinstance(b,list):
  assert len(a)==len(b),(label,'coverage')
  for i,(x,y) in enumerate(zip(a,b)):responses(x,y,label+'/'+str(i))
def walk(a,b,label):
 global rawcalls
 if isinstance(a,dict) and isinstance(b,dict):
  if 'stdout' in a and 'stdout' in b:
   rawcalls+=1
   x=json.loads(a['stdout'],parse_int=float);y=json.loads(b['stdout'],parse_int=float)
   assert x.get('ok')==y.get('ok'),label
   responses(x,y,label)
  else:
   for key in sorted(a.keys()&b.keys()):walk(a[key],b[key],label+'/'+key)
 elif isinstance(a,list) and isinstance(b,list):
  assert len(a)==len(b),(label,'coverage')
  for i,(x,y) in enumerate(zip(a,b)):walk(x,y,label+'/'+str(i))
walk(n,w,'')
print(json.dumps({'identity':'independent-wasm-raw-state-parity-v2','pass':True,'raw_responses_checked':rawcalls,'all_finite_state_components_checked':count,'worst_normalized_state_difference':worst[0],'worst_location':worst[1],'budget':4e-8,'compiled_calls':0,'artifacts':{str(x):sha(x) for x in [artifact,binary]}},indent=2))
