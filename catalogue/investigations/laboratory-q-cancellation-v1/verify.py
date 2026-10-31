"""Replay saved evidence only; optional local artifact hashing, no candidate calls."""
from pathlib import Path
import json,hashlib,sys,subprocess,math
if not __debug__:raise RuntimeError('Required verification checks cannot be optimized away')
s=Path(__file__).parent
read=lambda n:json.loads((s/n).read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for manifest in ['manifest.json','evidence-manifest.json']:
 for name,h in read(manifest).items():assert sha(s/name)==h,name
assert read('prospective-freeze.json')['manifest_sha256']==sha(s/'manifest.json')
assert read('prospective-freeze.json')['compiled_calls_at_freeze']==0
artifacts=0
for role in ['native','wasm','post']:
 receipt=read(role+'/receipt.json');assert receipt['completed']is True
 assert receipt['manifest_sha256']==sha(s/'manifest.json')
 assert all(c['exit_code']==0 for c in receipt['commands'])
 if '--artifacts'in sys.argv:
  for a in receipt['artifacts'].values():assert sha(Path(a['path']))==a['sha256'];artifacts+=1
for role in ['native','wasm']:
 subprocess.run([sys.executable,'-B',str(s/'assess_probe.py'),str(s/role/'probe.json')],check=True)
subprocess.run([sys.executable,'-B',str(s/'assess_invariance.py'),str(s/'post/backend-results.json')],check=True)
report=read('post/backend-results.json');assert report['status']=='passed'and len(report['pairs'])==101
journal=iter(read('post/backend-results.json.raw.json'))
physical=lambda r:{k:v for k,v in r.items()if k!='elapsed_ms'}
comparisons=0
for row in report['pairs']:
 # Bind raw result order and values; exact arguments are independently checked against all382baseline calls.
 for role in ['native','wasm']:
  r=next(journal);assert r['role']==role;assert physical(json.loads(r['raw']))==physical(row[role])
 if row['name'].startswith('legacy/'):
  for role in ['native','wasm']:
   r=next(journal);assert r['role']==role;assert physical(json.loads(r['raw']))==physical(row['direct_'+role]);assert physical(row['direct_'+role])==physical(row[role])
 if row['name'].startswith(('current/','legacy/')):
  r=next(journal);assert r['role']=='wasm'and row['roundtrip_replayed']is True
  assert physical(json.loads(r['raw']))==physical(row['wasm'])
 tol=1e-7 if row['name'].startswith('legacy/')else 1e-10
 def compare(a,b,path='response'):
  global comparisons
  if type(b)in(int,float):
   comparisons+=1;assert type(a)in(int,float)and math.isfinite(a)and math.isfinite(b)
   assert abs(a-b)<=tol*max(1,abs(a),abs(b)),(row['name'],path,a,b)
  elif isinstance(b,list):
   assert isinstance(a,list)and len(a)==len(b)
   for i,(x,y)in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
  elif isinstance(b,dict):
   assert isinstance(a,dict)and set(a)==set(b)
   for k,v in b.items():
    if k!='elapsed_ms':compare(a[k],v,path+'.'+k)
  else:assert type(a)is type(b)and a==b
 compare(row['native'],row['wasm'])
assert next(journal,None)is None and comparisons==163298
assert report['backend_runs']==202 and report['same_instance_wasm_export_import_replays']==90
legacy=read('post/legacy-results.json');assert legacy['status']=='passed'and len(legacy['pairs'])==17
print(json.dumps({'evidence_replay_passed':True,'paired_cases':101,'numeric_comparisons':comparisons,'raw_calls':382,'legacy_pairs':17,'probe_cases_per_backend':35,'candidate_calls':0,'local_artifacts_checked':artifacts},indent=2))
