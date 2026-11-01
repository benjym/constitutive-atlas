"""Saved-only diagnostic checks; never run a solver."""
from pathlib import Path
import json,gzip,hashlib,math
P=Path(__file__).resolve().parent;ROOT=P.parents[2]
read=lambda name:json.loads((P/name).read_text())
packed=lambda name:json.loads(gzip.decompress((P/name).read_bytes()))
for rel,h in read('manifest.json')['files'].items():assert hashlib.sha256((P/rel).read_bytes()).hexdigest()==h,rel
for rel,h in read('freeze.json')['source_files'].items():assert hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()==h,rel
for rel,h in read('freeze.json')['diagnostic_files'].items():
 raw=gzip.decompress((P/(rel+'.gz')).read_bytes())if rel.endswith('.log')else(P/rel).read_bytes()
 assert hashlib.sha256(raw).hexdigest()==h,rel
assert hashlib.sha256((P/'native_stages.py').read_bytes()).hexdigest()==read('stage-freeze.json')['script_sha256']
fd=read('fd-interpreter.json');assert len(fd)==12 and sum(x['components'] for x in fd)==104
invalid=[(x['model'],p)for x in fd for p in x['invalid_fd_probes']];assert len(invalid)==1 and invalid[0][1]['failed_domain']==['Omega >= 0'] and invalid[0][1]['value']==-1e-6
raw=packed('observations.json.gz');assert len(raw)==8
for row in raw:
 assert row['signal'] is None and row['error'] is None and row['stderr']==''
 n=json.loads(row['native_raw']);w=json.loads(row['wasm_raw']);assert row['status']==(0 if n['ok']else 1);assert n['ok']==w['ok']
 def compare(a,b):
  if isinstance(b,bool)or b is None or isinstance(b,str):assert a==b
  elif isinstance(b,(int,float)):assert math.isfinite(a)and abs(a-b)<=1e-10*max(1,abs(a),abs(b))
  elif isinstance(b,list):assert len(a)==len(b);[compare(u,v)for u,v in zip(a,b)]
  else:
   assert set(a)==set(b)
   for k in b:
    if k!='elapsed_ms':compare(a[k],b[k])
 compare(n,w)
recorded=json.loads(raw[6]['native_raw']);direct=json.loads(raw[7]['native_raw']);assert recorded['ok'] is False and recorded['failed_knot']==1 and len(recorded['points'])==1
assert direct['ok'] is False and direct['diagnostics']['substeps']==0 and direct['diagnostics']['rejected']==15
req=read('requests.json');assert direct['state']==req['original_recorded']['initial']
x=packed('native-stages.json.gz');assert len(x['calls'])==156 and len(x['rows'])==15
for row in x['calls']:assert row['stderr']=='' and row['status']==(0 if json.loads(row['stdout'])['ok']else 1)
scales=[100000]*6+[1]+[.0001]*6+[1];last=x['rows'][-1]['midpoints'];errors=[max(abs(last[0]['end'][i]-last[2]['end'][i]),abs(last[1]['defect'][i]),abs(last[2]['defect'][i]))/scales[i]for i in range(14)]
assert errors.index(max(errors))==7 and math.isclose(max(errors),3.521071401228803e-6,rel_tol=1e-12)and max(errors)>1e-6
print('PASS: original invalid FD domain, exact recorded/direct rollback,156stage receipts and depth14error exceedance; no gate relaxed.')
