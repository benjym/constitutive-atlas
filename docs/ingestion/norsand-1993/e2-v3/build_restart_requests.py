"""Generate explicit midpoint/restart contexts for prospective compiled requests."""
from pathlib import Path
import sys,json,hashlib
HERE=Path(__file__).resolve().parent;sys.path.insert(0,'/private/tmp/atlas-norsand-path-v1')
from atlas.model import load
from atlas.path import initialize,advance,evaluate_stage,stage_inputs,Settings

def main():
 model=load('/private/tmp/atlas-norsand-path-v1/candidate.json');reqs=json.loads((HERE/'interpreter-requests-v1.json').read_text());settings=Settings(**json.loads((HERE/'reference_policy-v2.json').read_text())['candidate_settings']);rows=[]
 for r in reqs['cases']:
  start=r['controls_start'];end=r['controls_end'];mid={n:(start[n]+end[n])/2 for n in start};parent=initialize(model,r['state'],r['coordinate'],start,r['parameters']);left=advance(model,parent,.08,start,mid,settings);right=advance(model,initialize(model,left.state,left.coordinate,left.controls,left.parameters),.08,mid,end,settings)
  _,lo=evaluate_stage(model,left.state,left.parameters,stage_inputs(model,left.coordinate,start,mid,1,.08));_,ro=evaluate_stage(model,right.state,right.parameters,stage_inputs(model,right.coordinate,mid,end,1,.08))
  rows.append(dict(id=r['id'],left=dict(state=left.state,coordinate=left.coordinate,controls=mid,observables=lo),right=dict(state=right.state,coordinate=right.coordinate,controls=end,observables=ro)))
  print(r['id'],'restart contexts retained',flush=True)
 (HERE/'restart-contexts-v1.json').write_text(json.dumps(dict(script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),rows=rows),indent=2)+'\n')
if __name__=='__main__':main()
