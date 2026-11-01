"""Prospectively specified accepted-prefix/failure rollback and recovery."""
import argparse,json,math,subprocess
from pathlib import Path
from supplement import base
B=Path(__file__).resolve().parent
def freeze():
 r=json.loads((B/'requests.json').read_text());z=r['paths'][0]['initial'];c=r['recovery']
 base.dump(B/'transaction-requests.json',dict(identity='occ-partial-rollback-v1',cases=[dict(name='accepted-prefix-then-fail',initial=z,de=[-.999,-.999,-.999,0,0,0],settings='1e-11,1e-6,60,2,4,20',expected_ok=False,require_accepted_prefix=True),dict(name='subsequent-recovery',initial=c['initial'],de=c['de'],expected=c['expected'],settings=r['settings'],expected_ok=True,require_accepted_prefix=False)],policy=dict(exact_rollback=True,minimum_accepted_prefix_substeps=1,recovery_relative_budget=2e-10)))
def native(binary):
 req=json.loads((B/'transaction-requests.json').read_text());rows=[]
 for c in req['cases']:
  args=[str(binary),'--mode','integrate','--model',base.MODEL,'--parameters',base.csv(base.PARAMS),'--initial',base.csv(c['initial']),'--strain',base.csv(c['de']),'--integration-settings',c['settings']]
  r=subprocess.run(args,capture_output=True,text=True);rows.append(dict(name=c['name'],args=args[1:],returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
 base.dump(B/'native-transaction-raw.json',dict(backend='native',request_sha256=base.sha(B/'transaction-requests.json'),cases=rows))
def assess(path):
 req=json.loads((B/'transaction-requests.json').read_text());raw=json.loads(path.read_text());assert raw['request_sha256']==base.sha(B/'transaction-requests.json');assert [x['name'] for x in raw['cases']]==[x['name'] for x in req['cases']]
 for c,r in zip(req['cases'],raw['cases']):
  o=json.loads(r['stdout']);assert o['ok']==c['expected_ok'],o
  assert len(o['state'])==7 and all(math.isfinite(x) for x in o['state'])
  if c['require_accepted_prefix']:assert o['state']==c['initial'] and o['diagnostics']['substeps']>=1,o
  else:assert max(abs(a-b)/max(1000. if i<6 else 1.,abs(b)) for i,(a,b) in enumerate(zip(o['state'],c['expected'])))<=2e-10
 report=dict(passed=True,backend=raw['backend'],raw_sha256=base.sha(path),exact_partial_failure_rollback=True,subsequent_recovery=True)
 base.dump(path.with_name(path.stem+'-assessment.json'),report);print(json.dumps(report,indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('mode',choices=['freeze','native','assess']);a.add_argument('path',nargs='?');x=a.parse_args()
 if x.mode=='freeze':freeze()
 elif x.mode=='native':native(Path(x.path))
 else:assess(Path(x.path))
