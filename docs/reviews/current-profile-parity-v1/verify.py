"""Saved-only release evidence; no compiled execution."""
from pathlib import Path
import json,gzip,hashlib
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).parent
load=lambda p:json.loads(p.read_text())
f=load(HERE/'freeze.json')
for p,h in f['source_files'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
for p,h in load(HERE/'manifest.json')['files'].items():assert hashlib.sha256((HERE/p).read_bytes()).hexdigest()==h,p
read=lambda name:json.loads(gzip.decompress((HERE/name).read_bytes()))
a=read('profile-loading.json.gz');b=read('scoped.json.gz')
assert a['status']==b['status']=='passed'
assert len(a['pairs'])==134 and a['same_instance_wasm_export_import_replays']==110
assert sum(x.get('expected_contract_rejection',False) for x in a['pairs'])==11
assert sum(x.get('expected_ordinary_failure',False) for x in a['pairs'])==1
assert len(b['cases'])==26 and len({x['specification']['model'] for x in b['cases']})==12
assert all(x['passed'] for x in b['cases']) and b['maximum_budget_fraction']<=1
assert b['wrong_scope_rejected_before_compiled_call']
raw=read('scoped.json.raw.json.gz')
for x in raw:
 if x['role']=='native':
  assert x['signal'] is None and x['error'] is None and x['stderr']==''
  result=json.loads(x['raw']);assert x['status']==(0 if x['name']=='atlas_describe' or result['ok'] else 1)
print('Saved profile release evidence verified: 134 loading pairs, 110 replays, 26 scoped cases/all12models; no execution.')
