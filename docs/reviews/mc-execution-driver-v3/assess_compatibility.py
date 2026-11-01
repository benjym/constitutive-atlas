"""Exact prior-backend compatibility; independent source accuracy is separate."""
from pathlib import Path
import sys,json,struct,math
P=Path(__file__).resolve().parent;R=P.parents[2];C=P.parent/'mc-current-collector-freeze-v3'
sys.path.insert(0,str(C))
from strict_observation_json import loads
from assess_binding import exact
read=lambda p:loads(Path(p).read_bytes())
def same(a,b):
 if type(a)in(int,float)and type(b)in(int,float):
  return math.isfinite(a)and math.isfinite(b)and struct.pack('>d',a)==struct.pack('>d',b)
 if type(a)is not type(b):return False
 if isinstance(a,dict):return a.keys()==b.keys()and all(same(a[k],b[k])for k in a)
 if isinstance(a,list):return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
def physical(x):return{k:v for k,v in x.items()if k not in('elapsed_ms','catalogue_hash')}
def assess(file,role):
 assert role in('native','wasm');data=read(file);assert data['role']==role
 policy=read(C/'compatibility-policy.json');assert not policy['executed']
 base=R/'catalogue/investigations/declared-loading-mixed-v1';requests=read(base/'requests.json');baseline=read(base/('baseline-'+role+'.json'));cat=read(C/'catalogue.json')
 assert len(data['rows'])==len(baseline['rows'])==len(requests)==12 and len(data['calls'])==13
 def call(c,name,args=None):
  assert c['name']==name and ('process'in c)==(role=='native')
  if args is not None:assert same(c['args'],args)
  raw=loads(c['raw'])
  if role=='native':
   v=c['process'];assert type(v['status'])is int and v['status']==(0 if name=='atlas_describe'or raw['ok']else 1)
   assert v['signal']is None and v['error']is None and v['stderr']==''
  return raw
 descriptor=call(data['calls'][0],'atlas_describe',[]);assert exact(descriptor,cat)
 assert [m for m in descriptor['models']if m['id']!='mohr-coulomb']==baseline['descriptor']['models']
 for row,old,request,c in zip(data['rows'],baseline['rows'],requests,data['calls'][1:]):
  assert row['id']==old['id']==request['id'] and row['raw']==c['raw'];s=request['specification']
  args=[s['model'],','.join(str(x)for x in s['parameters']),','.join(str(x)for x in s['initial']),s['protocol'],','.join(s['loading']['controls_bits']),','.join(str(s['integration_settings'][k])for k in ['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'])]
  actual_args=c['args'];assert len(actual_args)==6
  assert type(actual_args[3])is int and actual_args[3]==s['protocol']
  for i in [0,4]:assert actual_args[i]==args[i]
  for i in [1,2,5]:assert all(type(v)is str for v in [actual_args[i],args[i]])and same([float(v)for v in actual_args[i].split(',')],[float(v)for v in args[i].split(',')])
  value=call(c,'atlas_run_controls_scope_with_settings');assert value['catalogue_hash']==cat['sha256']
  assert value['ok']is request['expected_ok']and len(value['points'])==request['expected_points']
  assert same(physical(value),physical(old['result'])),request['id']
 return {'passed':True,'backend':role,'requests':12,'full_response_exact_except_elapsed_and_catalogue_hash':True,'ordinary_GIS_failure_retained':True}
if __name__=='__main__':print(json.dumps(assess(sys.argv[1],sys.argv[2]),indent=2))
