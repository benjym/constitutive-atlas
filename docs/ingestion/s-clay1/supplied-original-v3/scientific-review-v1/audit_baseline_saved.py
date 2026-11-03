"""Replay unchanged fixture assertions on saved JSON only; no compiled execution."""
from pathlib import Path
import hashlib,importlib.util,json,math,unittest,io
O=Path(__file__).resolve().parent.parent;R=O.parents[3]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=json.loads((O/'backend-completion.json').read_text())
for p,h in receipt['evidence'].items():assert sha(O/p)==h,p
for p,h in receipt['artifacts'].items():assert sha(R/receipt['artifact_root']/p)==h,p
r=json.loads((O/'baseline-fixture-results.json').read_text());assert sha(R/r['fixture_path'])==r['fixture_sha256']
for n,h in r['definition_hashes'].items():assert sha(R/'models'/f'{n}.json')==h
calls=json.loads((O/'baseline-fixture-calls.json').read_text());assert len(calls)==6
spec=importlib.util.spec_from_file_location('savedfixtures',R/r['fixture_path']);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
index=0
def savedrun(model,**kwargs):
 global index
 c=calls[index];index+=1;assert c['model']==model and c['kwargs']==kwargs
 return c['result']
m.run=savedrun;m.NumericalTests.__unittest_skip__=False
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream).run(unittest.TestSuite(m.NumericalTests(n) for n in r['tests']))
assert result.wasSuccessful(),stream.getvalue();assert index==6
rows=[json.loads(s) for s in (O/'wasm-baseline-v1/calls.jsonl').read_text().splitlines()];assert len(rows)==6
count=0;maximum=0

def scalar(x,y,scale):
 global count,maximum
 assert math.isfinite(x) and math.isfinite(y)
 e=abs(x-y)/scale;assert e<=2e-8;maximum=max(maximum,e);count+=1

def vec(a,b):
 assert len(a)==len(b)
 for i,(x,y) in enumerate(zip(a,b)):scalar(x,y,20000 if i<6 or i==13 else 1)
for c,row in zip(calls,rows):
 a=c['result'];b=row['actual'];assert a['ok']==b['ok']
 assert row['argv'][row['argv'].index('--model')+1]==c['model']
 for k in ['state','values']:
  assert (k in a)==(k in b)
  if k in a:vec(a[k],b[k])
 if 'points' in a:
  assert len(a['points'])==len(b['points'])
  for x,y in zip(a['points'],b['points']):
   vec(x['state'],y['state'])
   for k in ['p','q','q_signed','u']:
    if k in x:scalar(x[k],y[k],20000)
w=json.loads((O/'wasm-baseline-v1/results.json').read_text());assert count==w['comparisons'] and maximum==w['maximum_scaled_difference']
print(json.dumps({'ok':True,'unchanged_fixture_tests':result.testsRun,'saved_native_calls':index,'saved_wasm_calls':len(rows),'wasm_comparisons':count,'maximum_scaled_difference':maximum,'backend_evidence_hashes':len(receipt['evidence']),'backend_artifact_hashes':len(receipt['artifacts']),'scope':'Saved data only; no compiled execution. Baseline inherited scope label bounded by BASELINE_SCOPE_ADDENDUM.md.'},indent=2))
