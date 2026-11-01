"""Prospective tensor, critical/hold/reversal, and smooth tangent qualification."""
import argparse,hashlib,importlib.util,json,math,subprocess
from pathlib import Path
B=Path(__file__).resolve().parent;D=B.parent/'control-selection-v1'
def module(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
ref=module('occ_oracle',D/'independent-review/candidate-review-v2-check.py')
rot=module('occ_parent_rotation',D/'check_candidate_v3.py')
base=module('occ_execution',B/'backend_study.py')
def freeze():
 req=json.loads((B/'requests.json').read_text());cases=[]
 def case(name,z,de):
  z,de=list(z),list(de);cases.append(dict(name=name,initial=z,de=de,expected=ref.expected(z,de)))
 for i,c in enumerate(req['cases'][::33]):case('tensor-rotation-'+str(i),rot.rotate(c['initial'][:6])+(c['initial'][6],),rot.rotate(c['de']))
 p=50000.;v=2.5+.16*(1-math.log(100))-.04*math.log(50)
 z=[p+1000,p-500,p-500,200,-300,100,v]
 case('nonisotropic-exact-hold',z,[0.]*6)
 for s in (-1,1):
  case('signed-shear-'+str(s),z,[0.,0.,0.,s*.001,0.,0.])
  case('signed-axial-'+str(s),z,[s*.001,-s*.0005,-s*.0005,0.,0.,0.])
 compression=list(ref.expected(z,[.001,-.0005,-.0005,0.,0.,0.]))
 case('axial-history-reversal',compression,[-.001,.0005,.0005,0.,0.,0.])
 p=1000*math.exp(4);v=2.5-.2*4;q=1.2*p
 case('critical-mechanism',[p+2*q/3,p-q/3,p-q/3,0,0,0,v],[.01,-.005,-.005,0,0,0])
 v=2.5+.16-.2*4-.16*1.1;q=1.2*p*1.1
 case('dry-side-softening',[p+2*q/3,p-q/3,p-q/3,0,0,0,v],[.01,-.005,-.005,0,0,0])
 # Strict smooth nonzero-distortion points, away from min/projection switches.
 tangent=[]
 for name,de in [('smooth',[.001,-.0005,-.0005,.0003,.0001,-.0002]),('corner',[.02,.02,.02,.0001,0,0])]:
  z=req['cases'][10]['initial'];columns=[];coarse=[]
  for h in (1e-7,1e-8):
   cols=[]
   for j in range(6):
    u=de.copy();l=de.copy();u[j]+=h;l[j]-=h
    up,lo=ref.expected(z,u),ref.expected(z,l);cols.append([(a-b)/(2*h) for a,b in zip(up,lo)])
   (coarse if h==1e-7 else columns).extend(cols)
  conv=max(abs(a-b)/max(1e5 if i<6 else 1.,abs(b)) for u,w in zip(coarse,columns) for i,(a,b) in enumerate(zip(u,w)))
  assert conv<1e-5
  tangent.append(dict(name=name,initial=z,de=de,expected=ref.expected(z,de),expected_columns=columns,reference_refinement_error=conv))
 base.dump(B/'supplement-requests.json',dict(identity='occ-execution-supplement-v1',cases=cases,tangents=tangent,policy=dict(state_budget=2e-10,tangent_budget=1e-5,tangent_stress_floor=1e5,tangent_volume_floor=1.,finite_difference_steps=[1e-7,1e-8]),oracle_sha256=base.sha(D/'independent-review/candidate-review-v2-check.py')))
 print('frozen',len(cases),'supplement cases and',len(tangent),'smooth tangent cases')
def native(binary):
 req=json.loads((B/'supplement-requests.json').read_text())
 def call(c,mode):
  args=[str(binary),'--mode',mode,'--model',base.MODEL,'--parameters',base.csv(base.PARAMS),'--initial',base.csv(c['initial']),'--strain',base.csv(c['de']),'--integration-settings',base.SETTINGS]
  r=subprocess.run(args,capture_output=True,text=True);return dict(args=args[1:],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)
 base.dump(B/'native-supplement-raw.json',dict(backend='native',request_sha256=base.sha(B/'supplement-requests.json'),cases=[call(c,'integrate') for c in req['cases']],tangents=[call(c,'linearize') for c in req['tangents']]))
def assess(path):
 req=json.loads((B/'supplement-requests.json').read_text());raw=json.loads(path.read_text());assert raw['request_sha256']==base.sha(B/'supplement-requests.json')
 assert len(raw['cases'])==len(req['cases']) and len(raw['tangents'])==len(req['tangents'])
 errs=[];terr=[]
 for c,r in zip(req['cases']+req['tangents'],raw['cases']+raw['tangents']):
  o=json.loads(r['stdout']);assert o['ok'],(c['name'],o)
  assert len(o['state'])==7 and all(math.isfinite(x) for x in o['state'])
  error=max(abs(a-b)/max(1000. if i<6 else 1.,abs(b)) for i,(a,b) in enumerate(zip(o['state'],c['expected'])));errs.append(error);assert error<=req['policy']['state_budget']
  if c['name']=='nonisotropic-exact-hold':assert o['state']==c['initial']
 for c,r in zip(req['tangents'],raw['tangents']):
  o=json.loads(r['stdout']);assert o['tangent_ok'],o
  ac=o['state_tangent'];assert len(ac)==7 and all(len(row)==6 and all(math.isfinite(x) for x in row) for row in ac)
  error=max(abs(ac[i][j]-c['expected_columns'][j][i])/max(1e5 if i<6 else 1.,abs(c['expected_columns'][j][i])) for i in range(7) for j in range(6));terr.append(error);assert error<=req['policy']['tangent_budget'],error
 report=dict(passed=True,backend=raw['backend'],raw_sha256=base.sha(path),supplemental_cases=len(req['cases']),tangent_cases=len(req['tangents']),worst_state_error=max(errs),tangent_errors=terr)
 base.dump(path.with_name(path.stem+'-assessment.json'),report);print(json.dumps(report,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('mode',choices=['freeze','native','assess']);p.add_argument('path',nargs='?');a=p.parse_args()
 if a.mode=='freeze':freeze()
 elif a.mode=='native':native(Path(a.path))
 else:assess(Path(a.path))
