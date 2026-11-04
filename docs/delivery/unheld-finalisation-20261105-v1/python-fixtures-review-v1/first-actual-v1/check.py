from pathlib import Path
import json,hashlib,ast,re
O=Path(__file__).resolve().parent;N=O.parents[1];P=N/'python-explicit-fixtures-actual-v1';R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'plan.json')=='c62e57204ac72fc1001d120a2741a3302b39c562e03ebad8b960cab4c95e21ab'
plan=json.loads((P/'plan.json').read_text());assert sha(Path(plan['observer']))==plan['observer_sha256']=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e'
assert sha(N/'python-fixtures-review-v1/first-decision.json')==plan['review_sha256']=='25ecb38ccca651069a26a1473be90604cebdc53132d87a406506ab0eefba9639'
assert sha(Path(plan['env']['ATLAS_SOLVER']))==plan['runtime_sha256']=='606852e570c5d9082cec8b7281096ca352397de7b9c029e0630b5dca26c90747'
for x in plan['source_delta']['files']:
 assert sha(R/x['path'])==x['sha256'];assert sha(P/'preimages'/x['path'])==x['preimage_sha256']
r=json.loads((P/'observer/receipt.json').read_text());assert r['returncode']==r['reaped_returncode']==0 and r['mandatory_reap'] and r['status']=='passed' and r['cleanup_errors']==[]
assert r['argv']==plan['argv'] and r['cwd']==plan['cwd']
for key in ['stdout','stderr','executable']:
 x=r[key];assert sha(Path(x['path']))==x['sha256'] and Path(x['path']).stat().st_size==x['bytes']
output=(P/'observer/stderr.raw').read_text();assert re.search(r'Ran 43 tests in [0-9.]+s\n\nOK\n',output)
actual=re.findall(r'^test_\w+ \(([^)]+)\) \.\.\. ok$',output,re.M);expected=[]
for filename in ['test_atlas','test_capacity','test_history_legacy']:
 for c in ast.parse((R/'tests'/(filename+'.py')).read_text()).body:
  if isinstance(c,ast.ClassDef):
   for f in c.body:
    if isinstance(f,ast.FunctionDef) and f.name.startswith('test_'):expected.append('tests.'+filename+'.'+c.name+'.'+f.name)
assert len(actual)==43 and set(actual)==set(expected) and len(expected)==43
print('PASS: exact43testnames, source/preimage/runtime/plan/rawpins and genuine exit0/reap')
