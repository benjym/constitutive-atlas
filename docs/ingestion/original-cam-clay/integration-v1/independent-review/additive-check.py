import hashlib,json,math
from pathlib import Path
root=Path(__file__).resolve().parents[5];b=root/'docs/ingestion/original-cam-clay/integration-v1';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
a=read(root/'protocols/gis2024-small-drained-twelve-v1.json');n=read(root/'protocols/gis2024-small-drained-thirteen-occ-v1.json');pros=read(b/'example-replay-v1/prospective.json');raw=read(b/'example-replay-v1/result.json')
assert a['specification']==n['specification']==pros['specification'];assert raw==n['result'];assert raw['ok'] and len(raw['points'])==9;assert n['catalogue_hash']==raw['catalogue_hash']==pros['new_catalogue']
m0=read(b/'example-replay-v1/manifest-before.json');m1=read(root/'catalogue/laboratory-examples.json')
for e in m1['examples']:
 e['document_path']=m0['examples'][0]['document_path'];e['document_sha256']=m0['examples'][0]['document_sha256']
assert m0==m1
x=read(b/'applicability-before.json');y=read(root/'catalogue/applicability/kfs-development-v1.json');key=next(k for k in y if isinstance(y[k],list) and any(isinstance(z,dict) and z.get('model',{}).get('id')=='original-cam-clay-sw-electronic-log-recovery-v1' for z in y[k]));row=y[key].pop();assert x==y;assert row['assessment']=='not_assessed' and row['scientific_eligibility']=='undetermined';assert sha(root/row['model']['path'])==row['model']['sha256']
for e in row['evidence']:assert sha(root/e['path'])==e['sha256']
assert (root/'tests/test_solver.cpp').read_bytes()==(b/'source-snapshot/tests/test_solver.cpp').read_bytes()
count=0
# Independent recursive comparison of saved backend observations, excluding timing only.
def compare(a,b,tol):
 global count
 if isinstance(b,(int,float)) and not isinstance(b,bool):
  assert isinstance(a,(int,float)) and math.isfinite(a) and math.isfinite(b);assert abs(a-b)<=tol*max(1,abs(a),abs(b));count+=1
 elif isinstance(b,list):
  assert isinstance(a,list) and len(a)==len(b)
  for v,w in zip(a,b):compare(v,w,tol)
 elif isinstance(b,dict):
  assert a.keys()==b.keys()
  for k in b:
   if k!='elapsed_ms':compare(a[k],b[k],tol)
 else:assert a==b
s=read(b/'scoped-parity.json');assert s['status']=='passed' and len(s['cases'])==35
for c in s['cases']:compare(c['native'],c['wasm'],1e-10)
w=read(b/'browser-loading.json');assert w['status']=='passed' and len(w['pairs'])==145 and sum(bool(c.get('roundtrip_replayed')) for c in w['pairs'])==120
for c in w['pairs']:compare(c['native'],c['wasm'],1e-7 if c['name'].startswith('legacy/') else 1e-10)
for f in ['scoped-parity-process.json','browser-loading-process.json','wasm-regressions-process.json']:assert read(b/f)['returncode']==0
paths=['protocols/gis2024-small-drained-twelve-v1.json','protocols/gis2024-small-drained-thirteen-occ-v1.json','catalogue/laboratory-examples.json','catalogue/applicability/kfs-development-v1.json','.github/workflows/verify.yml']
paths += ['docs/ingestion/original-cam-clay/integration-v1/'+s for s in ['example-replay-v1/prospective.json','example-replay-v1/result.json','example-replay-v1/manifest-before.json','applicability-before.json','scoped-parity-process.json','browser-loading-process.json','wasm-regressions-process.json','scoped-parity.json','browser-loading.json']]
result={'status':'passed','compiled_calls':0,'independent_saved_scalar_comparisons':count,'hashes':{p:sha(root/p) for p in paths}}
(b/'independent-review/additive-results.json').write_text(json.dumps(result,indent=2)+'\n');print('Additive review checks pass; compared',count,'saved scalars; zero compiled calls')
