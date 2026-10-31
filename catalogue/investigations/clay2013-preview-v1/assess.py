"""Frozen settings-aware preview acceptance; no experimental/scientific admission."""
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
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def bits(x):return struct.pack('>d',float(x)).hex()
def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def same(a,b):
 if isinstance(a,bool)or isinstance(b,bool):return type(a)is type(b)and a==b
 if finite(a)and finite(b):return a==b
 if type(a)is not type(b):return False
 if type(a)is dict:return set(a)==set(b)and all(same(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b

def physical(response,mode):
 if mode=='integrate':return [response['state']]
 return [p['state']+p['strain']+[p[k]for k in ('p','q','q_signed','u','control')]for p in response['points']]

def spd_interior(sigma):
 scale=max(abs(x)for x in sigma)
 if not scale:return False
 a,b,c,xy,yz,xz=[x/scale for x in sigma]
 # Atlas Mandel order xx,yy,zz,sqrt2*xy,sqrt2*yz,sqrt2*xz.
 xy,yz,xz=xy/math.sqrt(2),yz/math.sqrt(2),xz/math.sqrt(2)
 return min(a,b,c,a*b-xy*xy,a*c-xz*xz,b*c-yz*yz,a*b*c+2*xy*yz*xz-a*yz*yz-b*xz*xz-c*xy*xy)>0

def assess(study=STUDY):
 s=Path(study);errors=[]
 def check(ok,why):
  if not ok:errors.append(why)
 for name,pin in read(s/'manifest.json').items():
  if sha(s/name)!=pin:raise ValueError('changed frozen input: '+name)
 policy=read(s/'acceptance.json');requests=read(s/'requests.json')
 definitions=[read(p)for p in sorted((s/'models').glob('*.json'))]
 model=next(m for m in definitions if m['id']=='hypoplastic-clay-2013')
 catalogue_hash=hashlib.sha256(canonical(definitions)).hexdigest()
 channels={};maxvolume=0.;maxparity=0.;callerpoints={}
 for backend in ('native','wasm'):
  receipt=read(s/backend/'receipt.json');journal=read(s/backend/'journal.json')
  check(receipt.get('completed')is True,backend+' completed execution')
  check(receipt['manifest_sha256']==sha(s/'manifest.json')and receipt['journal_sha256']==sha(s/backend/'journal.json'),backend+' source/raw binding')
  check(all(c['exit_code']==0 for c in receipt['commands']if c['label']in('toolchain','configure','build')),backend+' successful build')
  check([row['id']for row in journal]==['describe']+[r['id']for r in requests],backend+' complete ordered calls')
  if len(journal)!=len(requests)+1:continue
  descriptor=decode(journal[0]['raw'])
  check(same(descriptor.get('models'),definitions)and descriptor.get('sha256')==catalogue_hash,backend+' complete descriptor identity')
  for compiled,source in zip(descriptor['models'],definitions):check(list(compiled['parameters'])==list(source['parameters']),backend+' positional parameter layout')
  controls={};channels[backend]=[];callerpoints[backend]=0
  for req,row in zip(requests,journal[1:]):
   tag=backend+'/'+req['id'];check(same(row.get('request'),req),tag+' literal controls')
   response=decode(row['raw']);check(response.get('ok')is req['expected_ok'],tag+' status')
   values=None;channels[backend].append(values)
   if not req['expected_ok']:
    check(type(response.get('message'))is str and bool(response['message']),tag+' failure message')
    if req.get('returned_state')=='bitwise_identical_to_incoming':
     incoming=list(map(float,req['initial'].split(',')));returned=response.get('state',[])
     check(len(returned)==7 and all(finite(x)for x in returned),tag+' rollback shape')
     if len(returned)==7 and all(finite(x)for x in returned):check(list(map(bits,returned))==list(map(bits,incoming)),tag+' exact invalid-integrate rollback')
    continue
   check(response.get('message')=='',tag+' success message')
   if response.get('ok')is not True:continue
   initial=list(map(float,req['initial'].split(',')));parameters=list(map(float,req['parameters'].split(',')))
   expected_settings={'version':'incremental-settings-0.1','norm':'scaled_component_max'}
   setting_values=list(map(float,req['integration_settings'].split(',')))
   for key,value in zip(policy['settings_order'],setting_values):expected_settings[key]=value
   check(same(response.get('integration_settings'),expected_settings),tag+' exact numerical settings')
   check(response.get('model')==model['id']and response.get('catalogue_hash')==catalogue_hash,tag+' model/catalogue identity')
   check(same(response.get('initial'),initial)and same(response.get('parameters'),parameters),tag+' echoed state/parameters')
   if req['mode']=='integrate':
    returned=response.get('state',[]);check(len(returned)==7 and all(finite(x)for x in returned),tag+' finite state')
    check(same(response.get('strain'),list(map(float,req['strain'].split(',')))),tag+' echoed strain')
    if len(returned)==7 and all(finite(x)for x in returned):check(list(map(bits,returned))==list(map(bits,initial)),tag+' exact zero-update')
   else:
    for key in('protocol','target','steps','cycles'):check(same(response.get(key),req[key]),tag+' echoed '+key)
    points=response.get('points',[]);callerpoints[backend]+=len(points)
    check(len(points)==req['steps']+1,tag+' point count')
    if points:
     check(list(map(bits,points[0]['state']))==list(map(bits,initial)),tag+' exact initial row')
     check(points[0]['strain']==[0]*6 and points[0]['control']==0,tag+' zero initial control/strain')
    for i,point in enumerate(points):
     state=point['state'];strain=point['strain'];vector=state+strain+[point[k]for k in('p','q','q_signed','u','control')]
     check(len(state)==7 and len(strain)==6 and all(finite(x)for x in vector),tag+' finite shape')
     if len(state)!=7 or len(strain)!=6 or not all(finite(x)for x in vector):continue
     check(state[6]>=0 and point['p']>0 and spd_interior(state[:6]),tag+' independent interior checks')
     exact=(1+initial[6])*math.exp(-math.fsum(strain[:3]))-1
     error=abs(state[6]-exact);maxvolume=max(maxvolume,error);check(error<=1e-6,tag+' independent volume closure')
     target=req['target']*math.sin(2*math.pi*req['cycles']*i/req['steps'])if req['cycles']else req['target']*i/req['steps']
     check(abs(point['control']-target)<=1e-12*max(1,abs(target)),tag+' caller target')
     p=req['protocol'];strain_budget=policy['success_gates']['strain_controls_absolute']
     if p in(0,1,2,4):check(abs(strain[0]-target)<=strain_budget,tag+' axial control')
     if p==0:check(max(abs(strain[1]),abs(strain[2]))<=strain_budget,tag+' oedometer')
     if p in(2,3):check(abs(math.fsum(strain[:3]))<=strain_budget,tag+' zero volume')
     if p==4:check(max(strain[:3])-min(strain[:3])<=strain_budget,tag+' isotropic strain')
     check(abs(strain[1]-strain[2])<=strain_budget and max(map(abs,strain[3:]))<=strain_budget,tag+' axisymmetric strain')
     radial=(state[1]+state[2])/2;reference=(initial[1]+initial[2])/2
     if p==1:check(abs(radial-reference)<=.002+1e-8*max(1,abs(reference)),tag+' drained radial stress')
     q=state[0]-radial
     if p==3:check(abs(q-(initial[0]-reference)-target)<=.002+i*1e-8*max(1,abs(reference)),tag+' signed-q control')
     mean=math.fsum(state[:3])/3
     deviator=[v-mean for v in state[:3]]+state[3:6]
     reconstructed={'p':mean,'q':math.sqrt(1.5)*math.hypot(*deviator),'q_signed':q,'u':reference-radial if p in(2,3)else 0.}
     for key,value in reconstructed.items():check(abs(point[key]-value)<=1e-10*max(1,abs(value)),tag+' independent '+key+' channel')
   values=physical(response,req['mode']);channels[backend][-1]=values
   if 'same_result_as'in req:
    prior=controls.get(req['same_result_as'])
    check(prior is not None and len(values)==len(prior)and all(len(a)==len(b)and list(map(bits,a))==list(map(bits,b))for a,b in zip(values,prior)),tag+' bitwise physical recovery')
   controls[req['id']]=values
 if set(channels)=={'native','wasm'}:
  for req,n,w in zip(requests,channels['native'],channels['wasm']):
   if n is None or w is None:continue
   check(len(n)==len(w),req['id']+' parity shape')
   for a,b in zip(n,w):
    check(len(a)==len(b),req['id']+' parity channels')
    for x,y in zip(a,b):
     error=abs(x-y)/max(1,abs(x),abs(y));maxparity=max(maxparity,error);check(error<=policy['parity']['scaled_absolute_budget'],req['id']+' channel parity')
 return {'version':'clay2013-preview-assessment-v1','pass':not errors,'errors':errors,'requests_per_backend':len(requests),'caller_points_per_backend':callerpoints,'maximum_void_error':maxvolume,'maximum_scaled_backend_difference':maxparity,'scientific_admission':False,'experimental_validation':False,'update_tangent':False,'deployment':False}
if __name__=='__main__':
 result=assess();print(json.dumps(result,indent=2,allow_nan=False));raise SystemExit(0 if result['pass']else 1)
