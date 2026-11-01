"""Independent continuous hydrostatic source-recovery refinement study."""
import argparse,json,math,subprocess
from pathlib import Path
from supplement import base
B=Path(__file__).resolve().parent
def freeze():
 z=[100000.]*3+[0.]*3+[2.5+.16-.2*math.log(100)]
 base.dump(B/'hydro-requests.json',dict(identity='occ-elastic-hydro-source-refinement-v1',parameters=base.PARAMS,model=base.MODEL,settings=base.SETTINGS,paths=[dict(id='elastic-hydro-'+str(n),initial=z,de=[-.001/n]*3+[0.]*3,count=n,total_volumetric_strain=-.003) for n in (32,64,128,256)],policy=dict(minimum_refinement_ratio=1.8,finest_pressure_relative_error_budget=3e-6,exact_specific_volume_log_pressure_relation_budget=2e-10)))
def native(binary):
 req=json.loads((B/'hydro-requests.json').read_text());rows=[]
 for p in req['paths']:
  z=p['initial'];calls=[]
  for _ in range(p['count']):
   args=[str(binary),'--mode','integrate','--model',req['model'],'--parameters',base.csv(req['parameters']),'--initial',base.csv(z),'--strain',base.csv(p['de']),'--integration-settings',req['settings']]
   r=subprocess.run(args,capture_output=True,text=True);rr=dict(args=args[1:],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr);calls.append(rr);o=json.loads(r.stdout)
   if not o['ok']:break
   z=o['state']
  rows.append(dict(id=p['id'],calls=calls))
 base.dump(B/'native-hydro-raw.json',dict(backend='native',request_sha256=base.sha(B/'hydro-requests.json'),paths=rows))
def assess(path):
 req=json.loads((B/'hydro-requests.json').read_text());raw=json.loads(path.read_text());assert raw['request_sha256']==base.sha(B/'hydro-requests.json');assert [x['id'] for x in raw['paths']]==[x['id'] for x in req['paths']]
 errors=[];elastic=[]
 for p,row in zip(req['paths'],raw['paths']):
  assert len(row['calls'])==p['count'];worst=0.;bal=0.;v0=p['initial'][6]
  for i,r in enumerate(row['calls']):
   o=json.loads(r['stdout']);assert o['ok'];z=o['state'];assert len(z)==7 and all(math.isfinite(x) for x in z)
   pressure=sum(z[:3])/3;volume=v0*math.exp(-p['total_volumetric_strain']*(i+1)/p['count']);exact=100000*math.exp((v0-volume)/.04)
   worst=max(worst,abs(pressure-exact)/100000,abs(z[6]-volume));bal=max(bal,abs(z[6]+.04*math.log(pressure/100000)-v0))
   assert z[0]==z[1]==z[2] and z[3:6]==[0.,0.,0.]
  errors.append(worst);elastic.append(bal)
 ratios=[a/b for a,b in zip(errors,errors[1:])];assert min(ratios)>=1.8 and errors[-1]<=3e-6 and max(elastic)<=2e-10
 report=dict(passed=True,backend=raw['backend'],raw_sha256=base.sha(path),source_errors=errors,refinement_ratios=ratios,log_pressure_volume_balance_errors=elastic)
 base.dump(path.with_name(path.stem+'-assessment.json'),report);print(json.dumps(report,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['freeze','native','assess']);a.add_argument('path',nargs='?');x=a.parse_args()
 if x.mode=='freeze':freeze()
 elif x.mode=='native':native(Path(x.path))
 else:assess(Path(x.path))
