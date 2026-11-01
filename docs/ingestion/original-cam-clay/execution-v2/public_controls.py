"""Prospective ordinary/default-settings controller qualification; failures retained."""
import argparse,json,math,subprocess
from pathlib import Path
from supplement import base,ref
B=Path(__file__).resolve().parent
def freeze():
 z=[100000.]*3+[0.]*3+[2.5+.16-.2*math.log(100)]
 cases=[]
 for p in range(5):
  cases.append(dict(name='ordinary-protocol-'+str(p),protocol=p,target=10000. if p==3 else .01,steps=64,cycles=0,initial=z,parameters=base.PARAMS,settings='',expected_ok=True))
 for p in (0,2,4):cases.append(dict(name='cyclic-strain-'+str(p),protocol=p,target=.002,steps=64,cycles=1,initial=z,parameters=base.PARAMS,settings='',expected_ok=True))
 # Explicit reference-pressure change, conversion Gamma2=Gamma-lambda*log(r2/r1).
 c=json.loads((B/'supplement-requests.json').read_text())['cases'][0]
 params=base.PARAMS.copy();params[0]=100.;params[4]-=.2*math.log(.1)
 base.dump(B/'public-requests.json',dict(identity='occ-default-controls-v1',cases=cases,reference_pressure=dict(initial=c['initial'],de=c['de'],parameters=params,settings='',expected=c['expected']),policy=dict(all_requested_success=True,state_relative_budget=2e-10,controller_relative_budget=2e-8,substeps='Normal default failure subdivision allowed; every accepted increment is independently checked against the finite law only if unsplit. Subdivided path needs separate reference trace and cannot pass this study silently.',max_initial_source_error=2e-10),settings_source_sha256=base.sha(B/'source-snapshot/cpp/include/atlas/settings.hpp')))
 print('frozen',len(cases),'ordinary/default and cyclic controls plus pressure conversion')
def native(binary):
 req=json.loads((B/'public-requests.json').read_text());rows=[]
 for c in req['cases']:
  args=[str(binary),'--mode','run','--model',base.MODEL,'--parameters',base.csv(c['parameters']),'--initial',base.csv(c['initial']),'--protocol',str(c['protocol']),'--target',str(c['target']),'--steps',str(c['steps']),'--cycles',str(c['cycles'])]
  r=subprocess.run(args,capture_output=True,text=True);rows.append(dict(name=c['name'],args=args[1:],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 c=req['reference_pressure'];args=[str(binary),'--mode','integrate','--model',base.MODEL,'--parameters',base.csv(c['parameters']),'--initial',base.csv(c['initial']),'--strain',base.csv(c['de'])]
 r=subprocess.run(args,capture_output=True,text=True)
 base.dump(B/'native-public-raw.json',dict(backend='native',request_sha256=base.sha(B/'public-requests.json'),cases=rows,reference_pressure=dict(args=args[1:],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr)))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['freeze','native']);a.add_argument('path',nargs='?');x=a.parse_args()
 if x.mode=='freeze':freeze()
 else:native(Path(x.path))
