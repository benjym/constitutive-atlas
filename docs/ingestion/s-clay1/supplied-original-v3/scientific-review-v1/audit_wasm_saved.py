"""Check saved actual Wasm replay against frozen native requests; no Wasm calls."""
from pathlib import Path
import hashlib,json,math
O=Path(__file__).resolve().parent.parent;R=O.parents[3]
inputs=[]
for n in ['native-v1','native-v2']:
 inputs.extend(json.loads(s) for s in (O/n/'calls.jsonl').read_text().splitlines())
inputs.extend(json.loads((O/'native-interpreter-calls.json').read_text()))
actual=[json.loads(s) for s in (O/'wasm-v1/calls.jsonl').read_text().splitlines()]
assert len(inputs)==len(actual)==1494
maxerr=0.;checks=0

def compare(a,b,scale):
 global maxerr,checks
 assert isinstance(a,(int,float)) and isinstance(b,(int,float)) and math.isfinite(a) and math.isfinite(b)
 error=abs(a-b)/scale;assert error<=2e-8;maxerr=max(maxerr,error);checks+=1

def vector(a,b):
 assert len(a)==len(b)
 for i,(x,y) in enumerate(zip(a,b)):compare(x,y,20000 if i<6 or i==13 else 1)

for i,(saved,row) in enumerate(zip(inputs,actual),1):
 assert row['call']==i and saved['argv']==row['argv']
 expected=json.loads(saved['stdout']);out=row['actual'];assert type(out['ok']) is bool and out['ok']==expected['ok']
 for key in ['state','values']:
  assert (key in out)==(key in expected),(i,key)
  if key in out: vector(out[key],expected[key])
 assert ('points' in out)==('points' in expected)
 if 'points' in out:
  assert len(out['points'])==len(expected['points'])
  for a,b in zip(out['points'],expected['points']):
   vector(a['state'],b['state'])
   for k in ['p','q','q_signed','u']:
    if k in a:compare(a[k],b[k],20000)
report=json.loads((O/'wasm-v1/results.json').read_text())
assert report['ok'] and report['comparisons']==checks and report['maximum_scaled_difference']==maxerr
binary=R/'.local/s-clay1-delivery-v3/wasm/atlas.wasm'
assert hashlib.sha256(binary.read_bytes()).hexdigest()==report['wasm_sha256']
print(json.dumps({'ok':True,'calls':len(actual),'comparisons':checks,'maximum_scaled_difference':maxerr,'same_outcomes_shapes':True,'binary_sha256':report['wasm_sha256'],'scope':'saved artifact validation only; no compiled or Wasm execution'},indent=2))
