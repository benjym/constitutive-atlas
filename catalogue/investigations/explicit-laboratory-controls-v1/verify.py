"""Integrity and saved-result replay; never executes a candidate binary."""
from pathlib import Path
import hashlib,json,struct,sys
stage=Path(__file__).resolve().parent
root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else stage.parents[2]
def require(ok,message):
    if not ok:raise RuntimeError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text(),parse_int=float)
def bits(x):return struct.pack('>d',x).hex()
def physical(r):return {k:v for k,v in r.items() if k!='elapsed_ms'}
def snapshot_bits_match(values,expected):
    # JSON.stringify preserves nonzero numeric values but canonicalizes -0 to0.
    return len(values)==len(expected) and all(bits(x)==b or (b=='8000000000000000' and x==0) for x,b in zip(values,expected))
manifest=json.loads((stage/'manifest.json').read_text())
for name,digest in manifest['files'].items():require(sha(stage/name)==digest,'manifest '+name)
freeze=json.loads((stage/'prospective-freeze.json').read_text())
for name,digest in freeze['source_files'].items():require(sha(stage/'frozen'/name)==digest,'frozen source '+name)
for name,digest in freeze['local_files'].items():require(sha(stage/name)==digest,'frozen study '+name)
correction=stage/'test-json-signed-zero-v2';v2=json.loads((correction/'prospective-freeze.json').read_text())
for name,digest in v2['files'].items():require(sha(correction/name)==digest,'v2 freeze '+name)
require(sha(stage/'check-command-2.json')==v2['original_check_receipt_sha256'],'original failure binding')
for role in ['native','wasm']:
 for i in range(2):require(load(stage/f'{role}-command-{i}.json')['returncode']==0,'build failure')
for i in [0,1]:require(load(stage/f'check-command-{i}.json')['returncode']==0,'primary check failure')
require(load(stage/'check-command-2.json')['returncode']==1,'original test failure not retained')
require(load(correction/'check-command.json')['returncode']==0,'correction check failure')
require('Ran 4 tests' in load(correction/'check-command.json')['stderr'],'four tests missing')
require(json.loads((stage/'native-artifacts.json').read_text())['atlas_solver']==v2['unchanged_native_artifact'],'same native artifact')
observations=load(stage/'observations.json')
for key,value in {'passed':True,'legacy_backend_runs':90,'explicit_legacy_equivalences':90,'analytic_backend_points':40,'negative_cases':33}.items():require(observations[key]==value,'summary '+key)
require(len(observations['legacyJournals'])==90 and len(observations['journals'])==147,'journal counts')
for i,legacy in enumerate(observations['legacyJournals']):
 require(physical(legacy['prior'])==physical(legacy['current']),'legacy regression')
 explicit=observations['journals'][i];require(explicit['backend']==legacy['backend'] and explicit['specification']==legacy['specification'],'request correspondence')
 response=explicit['result'];require(response['points']==legacy['prior']['points'],'explicit replay regression')
 expected=[bits(p['control']) for p in legacy['prior']['points']]
 require(explicit['wire'].split(',')==expected==response['loading']['controls_bits'],'regression exact input bits')
for row in observations['journals']:
 response=row['result']
 if 'loading' not in response:continue
 expected=row['wire'].split(',');require(response['loading']['controls_bits']==expected,'full wire echo')
 require(snapshot_bits_match(response['loading']['controls'],expected),'numeric wire echo')
 require(len(response['points'])<=len(expected),'committed prefix length')
 require(snapshot_bits_match([x['control'] for x in response['points']],expected[:len(response['points'])]),'committed control bits')
 if response['ok']:require(len(response['points'])==len(expected),'successful point count')
rawdir=stage/'raw-signed-zero-v1';rawfreeze=json.loads((rawdir/'prospective-freeze.json').read_text())
for name,digest in rawfreeze['files'].items():require(sha(rawdir/name)==digest,'raw capture freeze '+name)
require(load(rawdir/'check-command.json')['returncode']==0,'raw capture failed')
raw=load(rawdir/'observations.json')
for backend in ['native','wasm']:
 response=json.loads(raw[backend]['raw'],parse_int=float)
 require([bits(x) for x in response['loading']['controls']]==raw['expected'],'raw numeric signed zero')
 require([bits(x['control']) for x in response['points']]==raw['expected'],'raw point signed zero')
 require(response['loading']['controls_bits']==raw['expected'],'raw authoritative bits')
# Current checkout compatibility allows exactly the separately frozen test-reader correction.
if root.exists() and (root/'cpp/main.cpp').exists():
 for name,digest in freeze['source_files'].items():
  expected=v2['files']['test_laboratory_controls.py'] if name=='tests/test_laboratory_controls.py' else digest
  require(sha(root/name)==expected,'current source '+name)
checked=missing=0
for role in ['native','wasm']:
 for receipt in json.loads((stage/f'{role}-artifacts.json').read_text()).values():
  p=Path(receipt['path'])
  if p.exists():require(sha(p)==receipt['sha256'],'local artifact '+str(p));checked+=1
  else:missing+=1
print(json.dumps({'passed':True,'legacy_saved_runs':90,'explicit_saved_records':147,'original_failed_test_preserved':True,'corrected_tests':4,'local_artifact_hashes_checked':checked,'local_artifacts_absent':missing,'raw_signed_zero_backends':2,'candidate_executions':0}))
