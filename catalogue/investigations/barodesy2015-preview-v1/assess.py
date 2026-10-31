"""Frozen software-preview gates; independent volume/control checks, no admission."""
from pathlib import Path
import hashlib,json,math,struct
STUDY=Path(__file__).resolve().parent

def unique(pairs):
 out={}
 for key,value in pairs:
  if key in out:raise ValueError('duplicate JSON key: '+key)
  out[key]=value
 return out

def decode(blob):return json.loads(blob,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('nonfinite JSON: '+x)))
def read(path):return decode(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def bits(x):return struct.pack('>d',float(x)).hex()
def same(a,b):
 if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
 if finite(a)and finite(b):return a==b
 if type(a)is not type(b):return False
 if type(a)is dict:return set(a)==set(b)and all(same(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b

def assess(study=STUDY):
 s=Path(study);errors=[]
 def check(ok,why):
  if not ok:errors.append(why)
 for name,pin in read(s/'manifest.json').items():
  if sha(s/name)!=pin:raise ValueError('changed frozen input: '+name)
 policy=read(s/'protocol.json')['policy'];requests=read(s/'requests.json')
 definitions=[read(p)for p in sorted((s/'models').glob('*.json'))]
 catalogue_hash=hashlib.sha256(canonical(definitions)).hexdigest();model=next(m for m in definitions if m['id']=='barodesy-sand')
 parsed={};maxvolume=0.;maxparity=0.;callerpoints={}
 for backend in ('native','wasm'):
  receipt=read(s/backend/'receipt.json');journal=read(s/backend/'journal.json')
  check(receipt.get('completed')is True,backend+' complete execution')
  check(receipt['manifest_sha256']==sha(s/'manifest.json')and receipt['journal_sha256']==sha(s/backend/'journal.json'),backend+' source/raw receipt binding')
  check(all(c['exit_code']==0 for c in receipt['commands']if c['label']in('configure','build','toolchain')),backend+' successful build')
  check([row['id']for row in journal]==['describe']+[r['id']for r in requests],backend+' ordered calls')
  if len(journal)!=len(requests)+1:continue
  desc=decode(journal[0]['raw']);check(same(desc.get('models'),definitions)and desc.get('sha256')==catalogue_hash,backend+' complete descriptor identity')
  for compiled,source in zip(desc['models'],definitions):check(list(compiled['parameters'])==list(source['parameters']),backend+' positional parameter order')
  parsed[backend]=[];controls={};callerpoints[backend]=0
  for req,row in zip(requests,journal[1:]):
   tag=backend+'/'+req['id'];check(same(row.get('request'),req),tag+' literal controls')
   response=decode(row['raw']);parsed[backend].append(response)
   check(response.get('ok')is req['expected_ok'],tag+' expected status')
   if not req['expected_ok']:
    check(type(response.get('message'))is str and bool(response['message']),tag+' failure message');continue
   check(response.get('message')=='',tag+' success message')
   if response.get('ok')is not True:continue
   initial=[float(v)for v in req['initial'].split(',')]
   if req['mode']=='integrate':
    check(len(response['state'])==7 and all(finite(x)for x in response['state']),tag+' finite state')
    check(list(map(bits,response['state']))==list(map(bits,initial)),tag+' exact zero-update identity');continue
   check(response.get('model')==model['id']and response.get('catalogue_hash')==catalogue_hash,tag+' response identity')
   check(same(response.get('parameters'),[float(v)for v in req['parameters'].split(',')])and same(response.get('initial'),initial),tag+' echoed inputs')
   points=response.get('points',[]);check(len(points)==req['steps']+1,tag+' complete points');callerpoints[backend]+=len(points)
   for i,point in enumerate(points):
    state=point['state'];strain=point['strain'];channels=state+strain+[point[k]for k in ('p','q','q_signed','u','control')]
    check(len(state)==7 and len(strain)==6 and all(finite(x)for x in channels),tag+' finite shape')
    if not all(finite(x)for x in channels):continue
    check(min(state[:3])>0 and state[6]>model['parameters']['emin']['default'],tag+' interior state')
    exact=(1+initial[6])*math.exp(-math.fsum(strain[:3]))-1
    err=abs(state[6]-exact);maxvolume=max(maxvolume,err);check(err<=policy['volume_absolute_budget'],tag+' independent volume closure')
    target=(req['target']*math.sin(2*math.pi*req['cycles']*i/req['steps'])if req['cycles']else req['target']*i/req['steps'])
    check(abs(point['control']-target)<=policy['control_relative_budget']*max(1,abs(target)),tag+' caller target')
    protocol=req['protocol'];relative=policy['control_relative_budget'];absolute=policy['control_absolute_budget_Pa']
    if protocol in(0,1,2,4):check(abs(strain[0]-target)<=relative,tag+' axial control')
    if protocol==0:check(abs(strain[1])+abs(strain[2])<=relative,tag+' oedometer')
    if protocol in(2,3):check(abs(math.fsum(strain[:3]))<=relative,tag+' zero volume')
    if protocol==4:check(max(strain[:3])-min(strain[:3])<=relative,tag+' isotropic strain')
    if protocol==1:check(abs((state[1]+state[2]-initial[1]-initial[2])/2)<=absolute+relative*max(abs(initial[1]),abs(initial[2])),tag+' fixed radial stress')
    q=state[0]-(state[1]+state[2])/2
    check(abs(point['q_signed']-q)<=absolute,tag+' independent q channel')
    if protocol==3:check(abs(q-(initial[0]-(initial[1]+initial[2])/2)-target)<=absolute+relative*abs(target),tag+' signed-q control')
   if 'recovery_of'in req:
    check(same(points,controls[req['recovery_of']]),tag+' repeated known-state points')
   controls[req['id']]=points
 if set(parsed)=={'native','wasm'}:
  for req,n,w in zip(requests,parsed['native'],parsed['wasm']):
   if not req['expected_ok']or n.get('ok')is not True or w.get('ok')is not True:continue
   extract=(lambda d:[d['state']])if req['mode']=='integrate'else(lambda d:[p['state']+p['strain']+[p[k]for k in('p','q','q_signed','u','control')]for p in d['points']])
   ns,ws=extract(n),extract(w);check(len(ns)==len(ws),req['id']+' parity points')
   for a,b in zip(ns,ws):
    check(len(a)==len(b),req['id']+' parity shape')
    for x,y in zip(a,b):
     error=abs(x-y)/max(1.,abs(x),abs(y));maxparity=max(maxparity,error);check(error<=policy['parity_scaled_budget'],req['id']+' channel parity')
 return {'version':'barodesy2015-preview-assessment-v1','pass':not errors,'errors':errors,'requests_per_backend':len(requests),'caller_points_per_backend':callerpoints,'maximum_void_error':maxvolume,'maximum_scaled_backend_difference':maxparity,'scientific_admission':False,'experimental_validation':False,'material_tangent':False,'deployment':False}
if __name__=='__main__':
 result=assess();print(json.dumps(result,indent=2,allow_nan=False));raise SystemExit(0 if result['pass']else 1)
