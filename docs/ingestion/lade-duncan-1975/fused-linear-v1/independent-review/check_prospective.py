"""Source pins and independent fused binary64 fixtures; no project artifact calls."""
from pathlib import Path
import json,hashlib,math
P=Path(__file__).resolve().parents[1];ROOT=P.parents[3];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();old=P.with_name('outer-predictor-v1')
f=P/'freeze-v2.json';d=json.loads(f.read_text())
for name,s in d['files'].items():assert h(ROOT/name)==s,name
for name in ['model.json','POLICY.json','SUPPLEMENT_POLICY.json','triaxial-policy.json','triaxial-reference-results.json','check_wasm_source.py']:assert (P/name).read_bytes()==(old/name).read_bytes(),name
for name in ['check_native_domain.py','check_native_triaxial.py','check_native_triaxial_fixed.py','check_native_lifecycle.py','check_native_legacy.py','check_domain_supplement.py','check_wasm_bounded.mjs','check_wasm_chains_bounded.mjs']:
 assert (P/name).read_text().replace('fused-linear-v1','outer-predictor-v1')==(old/name).read_text(),name
for row in json.loads((P/'linear-system-reference.json').read_text()):
 a=[r.copy() for r in row['matrix']];b=row['rhs'].copy();n=len(b)
 for k in range(n):
  pivot=max(range(k,n),key=lambda i:abs(a[i][k]));a[k],a[pivot]=a[pivot],a[k];b[k],b[pivot]=b[pivot],b[k]
  for i in range(k+1,n):
   q=a[i][k]/a[k][k]
   for j in range(k+1,n):a[i][j]=math.fma(-q,a[k][j],a[i][j])
   b[i]=math.fma(-q,b[k],b[i])
 x=[0.]*n
 for i in reversed(range(n)):
  s=b[i]
  for j in range(i+1,n):s=math.fma(-a[i][j],x[j],s)
  x[i]=s/a[i][i]
 assert [v.hex() for v in x]==[v.hex() for v in row['fused_expected']]
out={'freeze_sha256':h(f),'verified_files':len(d['files']),'independent_8x8_FMA_fixtures':2,'gates_and_reference_unchanged':True,'compiled_execution':False}
(P/'independent-review/prospective-check-results.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
