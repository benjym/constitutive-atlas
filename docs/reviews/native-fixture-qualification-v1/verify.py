from pathlib import Path
import json,gzip,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda p:json.loads((P/p).read_text())
for rel,h in read('manifest.json')['files'].items():assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==h,rel
for name in ['preflight-freeze.json','preflight-v2-freeze.json','preflight-v3-freeze.json']:
 for rel,h in read(name)['files'].items():assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==h,rel
r=read('results.json');assert r['status']=='failed'and r['installed']is False and r['new_builds']==0
for rel,h in r['original_native_sources'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
for version in [1,2,3]:
 x=json.loads(gzip.decompress((P/f'preflight-v{version}-failed.json.gz').read_bytes()));assert x['status']=='failed'
 for row in x['raw']:
  if row['role']=='native':assert row['signal']is None and row['error']is None and row['stderr']==''and row['status']==(0 if json.loads(row['raw'])['ok']else 1)
x=json.loads(gzip.decompress((P/'preflight-v3-failed.json.gz').read_bytes()));assert len(x['cases'])==2
for c in x['cases']:
 for role in ['native','wasm']:
  assert c[role]['ok']and len(c[role]['points'])==5
  assert c[role]['points'][3]['state']==c[role]['points'][2]['state']
  assert c['restart_'+role]['ok']
a,b=x['cases'];assert a['passed']and len(a['direct'])==3
for role in ['native','wasm']:
 assert a[role]['state']==a['restart_'+role]['state']
 assert b[role]['state']!=b['restart_'+role]['state']
 changed=[i for i,(u,v)in enumerate(zip(b[role]['state'],b['restart_'+role]['state']))if u!=v];assert changed==[7,8,9]
 assert max(abs(u-v)for u,v in zip(b[role]['state'],b['restart_'+role]['state']))<1e-20
 scale=max(100000,*map(abs,b['restart_'+role]['initial'][:6]));assert scale==100000.0000027397
print('PASS: retained unqualified fixture study; two completed physical paths, exact all-strain restart, failed exact drained restart, unchanged sources; no installation.')
