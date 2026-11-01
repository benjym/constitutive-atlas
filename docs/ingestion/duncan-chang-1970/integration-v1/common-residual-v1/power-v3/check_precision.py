"""Independent Decimal oracle on exact binary64 power inputs, no engine calls."""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib,json,math
p=Path(__file__).parent
assert not (p/'precision-results.json').exists()
a=json.loads((p/'requests.json').read_text())['cases'];r=json.loads((p/'results.json').read_text())['results']; rows=[]
for c,v in zip(a,r):
 assert c['id']==v['id']; par=c['parameters']; assert par[2]*par[1]==1 and par[3]*par[1]==1 and par[8]==0
 assert c['previous']==c['current'] and c['strain']==[0,0,0,1,0,0]
 x=c['current'][0]/par[1];n=par[4];vals=[]
 for precision in (100,160):
  with localcontext() as ctx:
   ctx.prec=precision; value=Decimal.from_float(x)**Decimal.from_float(n);vals.append(value)
 assert float(vals[0])==float(vals[1]),c['id']
 with localcontext() as ctx:
  ctx.prec=160;ref=vals[1];ulp=Decimal.from_float(math.ulp(float(ref)))
  errors={b:str((Decimal.from_float(-v[b]['response']['values'][3])-ref)/ulp) for b in ['baseline','no_contraction','wasm']}
 rows.append(dict(id=c['id'],base_hex=x.hex(),exponent_hex=n.hex() if isinstance(n,float) else float(n).hex(),reference_160=str(ref),rounded_reference=float(ref),backend_error_ulps=errors))
(p/'precision-results.json').write_text(json.dumps({'scope':'Decimal100/160 exact-binary64 input oracle; converged rounding required. Fractional Decimal power is almost always correctly rounded, so precision convergence is evidence, not a formal proof. No trajectory/source/refinement gate replaced.','rows':rows},indent=2)+'\n')
print('36 exact-input reference roundings converge at100/160digits')
for row in rows:
 if '/point2/' in '/'+row['id'] and 'n-0.54' in row['id']:print(json.dumps(row,indent=2))
