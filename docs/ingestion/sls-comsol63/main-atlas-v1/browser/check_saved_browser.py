"""Saved integrated main-atlas exports against unchanged frozen independent references."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
def read(name):return json.loads((HERE/(name+'.json')).read_text())
cases=json.loads((ROOT/'docs/ingestion/sls-comsol63/execution-v1/cases.json').read_text())['cases'];comparisons=0
for name,caseid in [('default','relax-schedule'),('creep','creep-schedule'),('rate','load-hold-reverse')]:
 data=read(name);case=next(c for c in cases if c['id']==caseid)
 assert data['result']['ok'] and len(data['result']['points'])==6
 for point in data['result']['points']:
  ref=next(r for r in case['references'] if r['time']==point['time']);assert len(point['state'])==12 and len(point['observables'])==6
  for i,(actual,expected) in enumerate(zip(point['state'],ref['state'])):
   assert abs(actual-expected)<=(3e-8 if i<6 else 1),(name,point['time'],i);comparisons+=1
  for actual,expected in zip(point['observables'],ref['stress']):assert abs(actual-expected)<=1;comparisons+=1
assert read('default')==read('reset')==read('replayed')
custom=read('custom')['controls'];assert custom['parameters']==[20e6,8e6,12e6,3];assert custom['initial']==[.003,.002,-.002,.0006,-.0005,.0004,4000,-1000,-3000,800,-300,200]
for path,expected in read('implementation-freeze').items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
result=dict(ok=True,fullStateStressComparisons=comparisons,exactResetReplay=True,customAllStateAndParameterEcho=True,implementationFreezeUnchanged=True)
(HERE/'browser-assessment.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
