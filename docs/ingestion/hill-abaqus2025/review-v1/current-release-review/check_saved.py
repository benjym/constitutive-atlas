"""Reassess actual browser exports and fresh-runtime saved evidence, zero compiled calls."""
from pathlib import Path
import hashlib,importlib.util,json,subprocess
ROOT=Path(__file__).resolve().parents[5]
BASE=ROOT/'docs/ingestion/hill-abaqus2025'
def read(p):return json.loads(p.read_text())
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
oracle=load('review_source_oracle',BASE/'source-v1/check_algebra.py')
assessor=load('review_saved_assessor',BASE/'execution-v1/qualify.py')
keys=['p_ref','K','Gmod','sigma_y','F','Gh','Hh','L','M','N']
browser=BASE/'delivery-v1/browser-v2';worst=[0.,0.];comparisons=0;exports={}
for kind in ['preset','changed','initial','reset','replay','shear']:
 doc=read(browser/f'hill-browser-{kind}.json');exports[kind]=doc
 assert doc['ok'];r=doc['request'];state=r['initial'][:6]
 assert doc['points'][0]['state']==r['initial']
 for de,row,record in zip(r['increments'],doc['points'][1:],doc['records']):
  expected=oracle.endpoint(dict(zip(keys,r['parameters'])),state,de,precision=100)
  assert row['state']==record['response']['state'];assert record['response']['ok']
  for i,(a,b) in enumerate(zip(row['state'],expected)):
   b=float(b);err=abs(a-b);assert err<=(.01+1e-10*abs(b) if i<6 else 1e-9)
   worst[i==6]=max(worst[i==6],err);comparisons+=1
  state=expected[:6]
assert exports['preset']==exports['reset'];assert exports['changed']==exports['replay']
report=read(browser/'report.json');assert len(report['checks'])==22 and all(report['checks'].values());assert report['preset']==exports['preset']
assert not report['page_errors']
fresh={}
for be in ['native','wasm']:
 path=Path('/private/tmp/atlas-hill-current-ci-'+be+'-v1')
 fresh[be]=assessor.assess(read(path/(be+'-raw.json')))
 saved=read(path/'report.json');assert saved['passed'] and saved['calls']==82
 for k,v in fresh[be].items():assert saved[k]==v
 rollback=read(path/(be+'-rollback-raw.json'));assert rollback['before']==rollback['after'];assert rollback['before']['ok'];assert not rollback['failed']['ok'];assert rollback['failed']['state']==rollback['failed']['initial']
 negatives=read(path/(be+'-negative-raw.json'));assert len(negatives)==5
 for row in negatives:assert not row['failed']['ok'] and row['recovered']['ok']
 assert saved['model_sha256']==report['identity']['model_sha256']
# Retain the exact additive release diff for reviewers without touching git/worktree state.
release=Path('/private/tmp/atlas-hill-release-v2');diffs={}
import difflib
for f in ['web/app.js','tools/build_web.py','.github/workflows/verify.yml']:
 original=subprocess.check_output(['git','show','0cd28fc2:'+f],cwd=ROOT,text=True)
 final=(release/f).read_text();diffs[f]='\n'.join(difflib.unified_diff(original.splitlines(),final.splitlines(),fromfile='0cd28fc2/'+f,tofile='Hill additive/'+f))+'\n'
output=dict(passed=True,compiled_calls=0,browser_exports=6,state_comparisons=comparisons,max_stress_error_Pa=worst[0],max_gamma_error=worst[1],browser_report_checks=22,exact_reset=True,exact_changed_replay=True,fresh_runtime_saved_assessments=fresh,base_revision='0cd28fc2a18dea9a496795ad149a58afed809930',actual_final_release_browser='pending additional v3 evidence, including latest-request/tampered replay/timed peer/startup errors')
print(json.dumps(output,indent=2))
if __name__=='__main__':
 (Path(__file__).parent/'additive-diff.txt').write_text('\n'.join(diffs.values()))
