"""Integrity and saved-outcome replay; no candidate artifact execution."""
from pathlib import Path
import json,hashlib,sys
if not __debug__:raise RuntimeError('Required verification checks cannot be optimized away')
s=Path(__file__).parent
read=lambda n:json.loads((s/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for n,h in read('manifest.json').items():assert sha(s/n)==h,n
assert read('prospective-freeze.json')['manifest_sha256']==sha(s/'manifest.json')
for n,h in read('evidence-manifest.json').items():assert sha(s/n)==h,n
assert read('pure/receipt.json')['completed']is True
pure=read('pure/results.json');assert pure['passed']is True and pure['exact_cyclic_controls']==9720 and pure['exact_ramp_samples']==250 and pure['negative_checks']==60
assert read('post/receipt.json')['completed']is False
assert read('post/receipt.json')['commands'][0]['exit_code']==1
for n,h in read('collection-v2/prospective-freeze.json')['files'].items():assert sha(s/n)==h,n
full=read('collection-v2/backend-results.json');assert full['status']=='failed'and len(full['pairs'])==101 and len(full['parity_failures'])==1
raw=iter(read('collection-v2/backend-results.json.raw.json'))
def physical(v):return {k:x for k,x in v.items()if k!='elapsed_ms'}
def consume(role,expected):
 r=next(raw);assert r['role']==role
 assert physical(json.loads(r['raw']))==physical(expected)
errors=[];count=0
for row in full['pairs']:
 consume('native',row['native']);consume('wasm',row['wasm'])
 if row['name'].startswith('legacy/'):
  for role in ['native','wasm']:
   consume(role,row['direct_'+role]);assert physical(row[role])==physical(row['direct_'+role])
 if row['name'].startswith(('legacy/','current/')):consume('wasm',row['wasm']);assert row['roundtrip_replayed']is True
 tol=1e-7 if row['name'].startswith('legacy/')else 1e-10
 def compare(a,b,path='result'):
  global count
  if type(b)in(int,float):
   count+=1
   if abs(a-b)>tol*max(1,abs(a),abs(b)):errors.append((row['name'],path))
  elif isinstance(b,list):
   assert len(a)==len(b)
   for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
  elif isinstance(b,dict):
   assert set(a)==set(b)
   for k,v in b.items():
    if k!='elapsed_ms':compare(a[k],v,path+'.'+k)
  else:assert a==b
 compare(row['native'],row['wasm'])
assert next(raw,None)is None
assert count==163298 and len(errors)==11
for name,path in errors:
 assert name=='current/hypoplastic-sand-igs97/4'and path.endswith('.q')
 row=next(r for r in full['pairs']if r['name']==name);index=int(path.split('points[')[1].split(']')[0])
 for role in ['native','wasm']:
  state=row[role]['points'][index]['state'];assert state[0]==state[1]==state[2]and state[3:6]==[0,0,0]
for name in ['remaining-checks/replay-v2/command.json','remaining-checks/generic-regressions.json']:assert read(name)['exit_code']==0
legacy=read('remaining-checks/replay-v2/results.json');assert legacy['status']=='passed'and len(legacy['pairs'])==17
artifacts=0
if '--artifacts'in sys.argv:
 for role in ['native','wasm']:
  for a in read(role+'/receipt.json')['artifacts'].values():assert sha(Path(a['path']))==a['sha256'];artifacts+=1
print(json.dumps({'evidence_replay_passed':True,'study_outcome':'failed','paired_cases':101,'numeric_comparisons':count,'failed_scalars':len(errors),'isotropic_q_expected':0,'legacy_cases':17,'candidate_calls':0,'local_artifacts_checked':artifacts},indent=2))
