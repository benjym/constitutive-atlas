"""Independent saved-output route audit. No Atlas, DSL, solver or integration imports."""
import argparse,hashlib,json,math,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];BASE=ROOT/'docs/reviews/gis2024-browser-preparation-v1';sys.path.insert(0,str(ROOT))
from tools.reference_gis2024_coupled import coupled_rates
from driver import lab_request,rate_request

def read(p):return json.loads(p.read_bytes())
def require(b,message):
 if not b:raise ValueError(message)
def finite(x):return type(x)in(int,float)and math.isfinite(x)
def vector(v,n):return type(v)is list and len(v)==n and all(finite(x)for x in v)
def bits(x):return struct.pack('>d',x).hex()
def audit(data,directory):
 require(data.get('transport_error')is None and data.get('stopped')is None,'transport or stopped route');require(data['backend']in ['native','wasm'],'backend identity')
 catalogue=read(ROOT/'docs/reviews/gis2024-mixed-catalogue-v1/generated-eleven/models.json');model=next(m for m in catalogue['models']if m['id']==read(BASE/'policy.json')['identity']['model_id']);policy=read(BASE/'policy.json');used=[];receipt_count=len(list((directory/'receipts').glob('*.json')))
 def bound(item,expected):
  require(type(item['receipt'])is int and item['receipt']not in used,'receipt missing/reused');used.append(item['receipt']);raw=read(directory/'receipts'/f"{item['receipt']:04d}.json");actual=item['request']
  # Native exact controls have an explicit per-run file; its literal content is
  # bound in controls_wire. No response or catalogue is projected/relabelled.
  if data['backend']=='native'and 'controls_wire'in expected:
   require(len(actual['cli'])==len(expected['cli']),'native CLI shape');expected=json.loads(json.dumps(expected));i=expected['cli'].index('@CONTROLS@');require(Path(actual['cli'][i]).name=='wire-controls.txt','native controls path');expected['cli'][i]=actual['cli'][i]
  require(actual==expected and raw['request']==actual and raw['backend']==data['backend'],'request/raw binding')
  result=json.loads(raw['stdout'])
  if data['backend']=='wasm':require(result.get('inputs_unchanged')is True and 'transport_error'not in result,'Wasm mutation/transport');result=result['response']
  else:require(raw['returncode']==(0 if actual['function']=='atlas_describe' or item['response'].get('ok')else 1),'native process status')
  require(result==item['response'],'raw response binding');return result
 descriptor=bound(data['descriptor'],{'function':'atlas_describe','types':[],'args':[],'cli':['--describe']});require(descriptor==catalogue,'real eleven-model catalogue identity')
 rates=read(HERE/'rate-references.json');require(len(data['rates'])==len(rates)==26,'rate coverage');rate_max=0.
 for got,row in zip(data['rates'],rates):
  require(got['id']==row['id'],'rate order');r=bound(got['call'],rate_request(row));require(r.get('ok')is True and vector(r.get('values'),14),'rate finite layout')
  for a,b in zip(r['values'],row['expected']):
   err=abs(a-b);rate_max=max(rate_max,err);require(err<=1e-10+1e-10*abs(b),'independent origin/interior rate error')
 params=dict(zip(model['parameters'],rates[0]['parameters']));physical={k:v for k,v in params.items()if k!='p_scale'};maximum_volume=0.;point_count=0
 def positive(item,s,success=True,forced=False):
  nonlocal maximum_volume,point_count
  r=bound(item,lab_request(s));require(r.get('ok')is success,'laboratory outcome')
  require(r.get('catalogue_hash')==catalogue['sha256']and r.get('model')==s['model']and r.get('parameters')==s['parameters']and r.get('initial')==s['initial'],'response identity/history echo')
  require(r.get('schema_version')=='0.1'and r.get('api_version')=='experimental-laboratory-scope-0.1'and r.get('integration_settings')==s['integration_settings'],'response version/settings')
  stress={'source':'state','name':'sigma','measure':'cauchy','scope':'effective','tensor_representation':'mandel','sign':'compression_positive'};require(r.get('stress')==stress and r.get('protocol')==s['protocol']and r.get('steps')==s['steps']and 'research_scope'not in r,'scope/protocol identity')
  pore={'quantity':'change','availability':'reconstructed','assumption':'fixed_radial_total_stress_incompressible_fluid_and_grains'}if s['protocol']in[2,3]else{'quantity':'change','availability':'unavailable','reason':'not_reconstructed_for_protocol'};require(r.get('pore_pressure')==pore,'pore contract')
  if 'loading'in s:
   wanted=s['loading']['controls_bits'];wire=r.get('loading',{});require(wire.get('version')=='laboratory-controls-0.1'and wire.get('encoding')=='ieee754-binary64-hex'and wire.get('controls_bits')==wanted and vector(wire.get('controls'),len(wanted))and [bits(x)for x in wire['controls']]==wanted,'exact loading wire');controls=wire['controls'];require('target'not in r and 'cycles'not in r,'exact/legacy contract confusion')
  else:
   require('loading'not in r and r.get('target')==s['target']and r.get('cycles')==s['cycles'],'legacy loading context');controls=None
  points=r.get('points');expected_count=1 if forced else s['steps']+1;require(type(points)is list and len(points)==expected_count,'committed prefix coverage')
  require(points[0]['state']==s['initial']and points[0]['strain']==[0.]*6 and points[0]['control']==0,'initial point identity')
  budget=max(1.,abs(s['initial'][1]))*1e-8+2e-8;previous=None
  for index,p in enumerate(points):
   point_count+=1;z=p.get('state');e=p.get('strain');require(vector(z,14)and vector(e,6)and all(finite(p.get(k))for k in ['control','p','q','q_signed','error']),'finite point layout');require(all(type(p.get(k))is int and p[k]>=0 for k in ['iterations','substeps','rejected']),'diagnostic counters')
   if controls is not None:require(bits(p['control'])==bits(controls[index]),'point exact control')
   elif not s['cycles']:require(abs(p['control']-s['target']*index/s['steps'])<=1e-16*max(1.,abs(s['target'])),'legacy monotonic control')
   elif index:require(abs(p['control'])<=abs(s['target'])*(1+1e-14),'legacy cyclic control range')
   if s['target']==0:require(z==s['initial']and e==[0.]*6,'full14 zero/hold equality')
   coupled_rates({'sigma':z[:6],'e':z[6],'h':z[7:13],'Omega':z[13]},[0.]*6,physical)
   trace=math.fsum(e[:3]);volume=abs(z[6]-((1+s['initial'][6])*math.exp(-trace)-1));maximum_volume=max(maximum_volume,volume);require(volume<=1e-10,'volume closure')
   q=z[0]-.5*(z[1]+z[2]);mean=math.fsum(z[:3])/3;dev=[z[i]-mean if i<3 else z[i]for i in range(6)];magnitude=math.sqrt(1.5*math.fsum(x*x for x in dev));require(abs(p['p']-mean)<=2e-8 and abs(p['q_signed']-q)<=2e-8 and abs(p['q']-magnitude)<=2e-8,'stress observables')
   require(all(abs(x)<=1e-14 for x in e[3:]),'axisymmetric shear strain')
   protocol=s['protocol']
   if protocol in[0,1,2,4]:require(abs(e[0]-p['control'])<=1e-14,'strain control')
   if protocol==0:require(abs(e[1])<=1e-14 and abs(e[2])<=1e-14,'oedometer controller')
   if protocol==1:require(abs(.5*(z[1]+z[2])-.5*(s['initial'][1]+s['initial'][2]))<=budget,'radial stress controller')
   if protocol in[2,3]:require(abs(trace)<=1e-14,'undrained volume controller')
   if protocol==3 and previous is not None:
    old=previous['state'];dq=q-(old[0]-.5*(old[1]+old[2]));require(abs(dq-(p['control']-previous['control']))<=budget,'deviator stress controller')
   if protocol==4:require(max(e[:3])-min(e[:3])<=1e-14,'isotropic strain controller')
   if protocol in[2,3]:require(finite(p.get('u'))and abs(p['u']-(.5*(s['initial'][1]+s['initial'][2])-.5*(z[1]+z[2])))<=2e-8,'reconstructed pore pressure')
   else:require(p.get('u')is None,'unavailable pore pressure')
   previous=p
  return r
 rows=read(HERE/'laboratory-requests.json');require(len(data['laboratory'])==len(rows)==60,'laboratory coverage')
 for got,row in zip(data['laboratory'],rows):require(got['id']==row['id'],'laboratory order');positive(got['call'],row['specification'])
 control=rows[0]['specification'];clean=positive(data['clean'],control);guards=read(BASE/'guard-cases.json');require(len(data['guards'])==len(guards)==8,'guard coverage')
 for got,row in zip(data['guards'],guards):
  require(got['id']==row['id'],'guard order');r=bound(got['call'],lab_request(row['specification']));require(r.get('ok')is False and not r.get('points'),'invalid state committed');recovered=positive(got['recovery'],control);require([p['state']for p in recovered['points']]==[p['state']for p in clean['points']],'recovery full-state mismatch')
 positive(data['failure']['call'],read(BASE/'failure-case.json')['specification'],False,True);recovered=positive(data['failure']['recovery'],control);require([p['state']for p in recovered['points']]==[p['state']for p in clean['points']],'post-failure recovery')
 require(len(used)==receipt_count and sorted(used)==list(range(receipt_count)),'raw receipt coverage');require(used==sorted(used),'request execution order')
 return {'qualification_pass':True,'backend':data['backend'],'rates':26,'laboratory_cases':60,'guards':8,'recoveries':9,'forced_failures':1,'points_checked':point_count,'raw_receipts':receipt_count,'maximum_rate_absolute_error':rate_max,'maximum_volume_error':maximum_volume,'scientific_admission':False}
def assess(directory):return audit(read(directory/'result.json'),directory)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);x=p.parse_args()
 try:result=assess(x.directory)
 except Exception as exc:result={'qualification_pass':False,'failure':str(exc),'scientific_admission':False}
 print(json.dumps(result,indent=2));raise SystemExit(0 if result['qualification_pass']else 1)
