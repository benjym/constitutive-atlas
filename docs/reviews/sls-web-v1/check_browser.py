"""Read saved real-browser exports against existing frozen independent references."""
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
cases = json.loads((ROOT/'docs/ingestion/sls-comsol63/execution-v1/cases.json').read_text())['cases']
read = lambda name: json.loads((HERE/(name+'.json')).read_text())
count = 0
for name,caseid in [('browser-default','relax-schedule'),('browser-creep','creep-schedule'),('browser-rate','load-hold-reverse')]:
    data = read(name)
    case = next(c for c in cases if c['id']==caseid)
    for point in data['result']['points']:
        ref = next(r for r in case['references'] if r['time']==point['time'])
        for i,(actual,expected) in enumerate(zip(point['state'],ref['state'])):
            assert abs(actual-expected)<=(3e-8 if i<6 else 1),(name,point['time'],i,actual,expected)
            count += 1
        for actual,expected in zip(point['observables'],ref['stress']):
            assert abs(actual-expected)<=1,(name,point['time'],actual,expected)
            count += 1
assert read('browser-default') == read('browser-replayed') == read('browser-reset')
custom=read('browser-custom')['request']
assert custom['parameters']==[20e6,8e6,12e6,3]
assert custom['initial']==[.003,.002,-.002,.0006,-.0005,.0004,4000,-1000,-3000,800,-300,200]
freeze=json.loads((HERE/'implementation-freeze-v4.json').read_text())
for path,expected in freeze.items():
    assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==expected,path
result=dict(ok=True,browser_reference_comparisons=count,exact_export_import_reset_replay=True,custom_parameter_and_all_state_echo=True,implementation_freeze_unchanged=True)
(HERE/'browser-assessment.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
