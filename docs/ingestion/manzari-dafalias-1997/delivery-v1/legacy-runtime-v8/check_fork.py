"""Read-only exact literal fork proof and current source preflight."""
import ast,hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
D=Path(__file__).resolve().parent;P=D.parent
sys.path.insert(0,str(D))
from frozen_logic import frozen,load,sha
frozen();proof=json.loads((D/'fork-proof.json').read_text())
assert sha(P/'raw-link-v7/manifest.json')==proof['accepted_original_manifest_sha256']
for row in proof['files']:
 original=(D/'originals'/row['file']).read_text();adapted=(D/row['file']).read_text()
 assert sha(P/'raw-link-v7'/row['file'])==row['original_sha256']==sha(D/'originals'/row['file'])
 text=original
 for step in row['substitutions']:
  assert text.count(step['original'])==step['count']
  text=text.replace(step['original'],step['replacement'])
 assert text==adapted and sha(D/row['file'])==row['fork_sha256'];text=adapted
 for step in reversed(row['substitutions']):
  a,b=step['original'],step['replacement'];positions=[p+i*(len(b)-len(a))for i,p in enumerate(step['original_positions'])]
  for p in reversed(positions):assert text[p:p+len(b)]==b;text=text[:p]+a+text[p+len(b):]
 assert text==original,'exact reverse fork'
 ast.parse(adapted)
assert sha(P/'resolution-study-v4/run_native.py')==sha(P/'execution-v3/run_native.py')
plan=json.loads((P/'execution-v3/requests.json').read_text());assert sha(P/'execution-v3/requests.json')=='2365a2d8e175a88273747da6fd7c56afa0fe9f67ffb71aa1ea13c5efbf6ac0f5'
assert len(plan['cases'])==35
paths=[c for c in plan['cases']if c['group']in ['axis','interior']]
assert len(paths)==28 and {c['resolution']for c in paths}=={128,512}
assert sha(P/'execution-v1/requests.json')==sha(P/'execution-v3/requests.json')
current=load('runtime-rebind-v5/preflight.py').check()
if (D/'pre-observation-freeze.json').exists():
 for name,h in json.loads((D/'pre-observation-freeze.json').read_text())['files'].items():assert sha(D/name)==h
print(json.dumps(dict(identity='md1997-legacy-fork-source-check-v8',passed=True,compiled_calls=0,source_files=current['source_files'],cases=35,paths=14,resolutions=[128,512],fork_files=len(proof['files']),source_accuracy_checkers_unchanged=True)))
