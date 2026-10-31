from pathlib import Path
from fractions import Fraction as F
import json,struct,hashlib,math
from reference import square,passes_exact_accuracy,certify_rounding
P=Path(__file__).parent;checks=[]
def check(n,b):
 checks.append({'name':n,'passed':b})
 if not b:raise AssertionError(n)
freeze=json.loads((P/'prospective-freeze.json').read_text())
for n,h in freeze['files'].items():check('frozen '+n,hashlib.sha256((P/n).read_bytes()).hexdigest()==h)
inputs=json.loads((P/'inputs.json').read_text())['cases'];refs=json.loads((P/'references.json').read_text())['cases'];check('35 input/reference IDs',len(inputs)==len(refs)==35 and [x['id']for x in inputs]==[x['id']for x in refs])
for c,r in zip(inputs,refs):
 vals=[struct.unpack('>d',bytes.fromhex(b))[0]for b in c['input_bits']];v=[F.from_float(x)for x in vals];a,b,d,u,w,z=v;t=a+b+d
 alternative=F(3,2)*(a*a+b*b+d*d-t*t/3+u*u+w*w+z*z)
 qsq=F(int(r['q_squared_numerator']),int(r['q_squared_denominator']));q=struct.unpack('>d',bytes.fromhex(r['q_rounded_bits']))[0]
 check(c['id']+' exact algebra identity',alternative==square(v)==qsq)
 check(c['id']+' finite bounded reference',all(math.isfinite(x)and abs(x)<=1e300 for x in vals)and math.isfinite(q)and q>=0)
 check(c['id']+' exact rounding cell',certify_rounding(qsq,q))
 check(c['id']+' frozen accuracy positive fixture',passes_exact_accuracy(q,qsq))
 bad=q+max(1.,q)*1e-4
 check(c['id']+' oversized error rejected',not passes_exact_accuracy(bad,qsq))
 if qsq==0:check(c['id']+' exact isotropic positive zero',r['q_rounded_bits']=='0000000000000000' and not passes_exact_accuracy(-0.,qsq)and not passes_exact_accuracy(1e-10,qsq))
for bad in [-1.,math.inf,math.nan]:check('invalid candidate rejected '+str(bad),not passes_exact_accuracy(bad,F(1)))
(P/'checks.json').write_text(json.dumps({'passed':True,'checks':checks,'candidate_calls':0,'compiled_calls':0},indent=2)+'\n');print(len(checks),'independent exact algebra/rounding/policy checks passed')
