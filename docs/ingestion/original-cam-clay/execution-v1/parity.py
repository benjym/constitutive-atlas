"""Prospective all-state native/Wasm parity assessor; backend gates remain separate."""
import hashlib,json,math
from pathlib import Path
B=Path(__file__).resolve().parent
req=json.loads((B/'requests.json').read_text())
a,b=[json.loads((B/f'{s}-raw.json').read_text()) for s in ('native','wasm')]
assert a['requests_sha256']==b['requests_sha256']==hashlib.sha256((B/'requests.json').read_bytes()).hexdigest()
worst=0.;count=0;transport=[]
def compare(x,y,exception=False):
 global worst,count
 x,y=json.loads(x['stdout']),json.loads(y['stdout'])
 if x['ok']!=y['ok']:
  assert exception
  transport.append({'native_ok':x['ok'],'wasm_ok':y['ok']});return
 assert x['ok']==y['ok']
 if 'state' in x or 'state' in y:
  assert len(x['state'])==len(y['state'])==7
  for i,(v,w) in enumerate(zip(x['state'],y['state'])):
   assert math.isfinite(v) and math.isfinite(w)
   error=abs(v-w)/max(1000. if i<6 else 1.,abs(v),abs(w));worst=max(worst,error);count+=1
   assert error<=req['policy']['parity_relative_budget']
for key in ('cases','negatives','paths'):
 assert [r['id'] for r in a[key]]==[r['id'] for r in b[key]]==[r['id'] for r in req[key]]
for c,x,y in zip(req['cases'],a['cases'],b['cases']):
 assert c['id']==x['id']==y['id']
 for u,v in zip(x['calls'],y['calls']):compare(u,v,c['allow_transport_rejection'])
for x,y in zip(a['negatives'],b['negatives']):
 assert x['id']==y['id'];compare(x['bad'],y['bad']);compare(x['recovery'],y['recovery'])
for x,y in zip(a['paths'],b['paths']):
 assert x['id']==y['id'] and len(x['calls'])==len(y['calls']) and len(x['restart'])==len(y['restart'])
 for u,v in zip(x['calls'],y['calls']):compare(u['call'],v['call'])
 for u,v in zip(x['restart'],y['restart']):compare(u,v)
report={'passed':True,'all_state_scalar_comparisons':count,'worst_relative_error':worst,'transport_differences':transport,'native_sha256':hashlib.sha256((B/'native-raw.json').read_bytes()).hexdigest(),'wasm_sha256':hashlib.sha256((B/'wasm-raw.json').read_bytes()).hexdigest()}
(B/'parity-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
