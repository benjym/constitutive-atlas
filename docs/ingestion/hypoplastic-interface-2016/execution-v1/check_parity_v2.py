"""Prospective exact layouts and frozen scaled native/Wasm component parity."""
from pathlib import Path
import json,math,hashlib,sys
P=Path(__file__).resolve().parent
plan=json.loads((P/'source-freeze-v2.json').read_text());native,wasm,output=[Path(x) for x in sys.argv[1:]] if len(sys.argv)==4 else [P/'native-results.json',P/'wasm-results.json',P/'parity-results-v2.json'];a=json.loads(native.read_text());b=json.loads(wasm.read_text());assert a['request_sha256']==b['request_sha256'];assert len(a['rows'])==len(b['rows'])==59
rows=[]
for x,y in zip(a['rows'],b['rows']):
 assert x['id']==y['id'] and x['status']==y['status']
 assert len(x['state'])==len(y['state'])==5 and len(x['observables'])==len(y['observables'])==8
 assert x['coordinate']==y['coordinate'] and math.isfinite(x['coordinate'])
 maximum=0
 for key,scales in [('state',plan['state_scales']),('observables',plan['observable_scales'])]:
  for av,bv,scale in zip(x[key],y[key],scales):
   assert type(av) in (float,int) and type(bv) in (float,int) and math.isfinite(av) and math.isfinite(bv)
   error=abs(av-bv)/scale;maximum=max(maximum,error);assert error<=plan['parity_scaled_absolute'],(x['id'],key,error)
 rows.append({'id':x['id'],'max_scaled_error':maximum})
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
output.write_text(json.dumps({'passed':True,'requests':59,'scaled_absolute_limit':plan['parity_scaled_absolute'],'inputs':{p.name:sha(p) for p in [native,wasm,P/'source-freeze-v2.json']},'rows':rows},indent=2)+'\n')
print('59 full-state/observable parity rows passed')
