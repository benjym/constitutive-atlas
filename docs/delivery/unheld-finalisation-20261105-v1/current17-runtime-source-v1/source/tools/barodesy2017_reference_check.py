"""Fresh independent source-body reference checks; no DSL/model imports."""
import hashlib,json,math
from decimal import Decimal,localcontext
from tools.retain_barodesy2017_reference import cases as fresh_cases
from tools.reference_barodesy2017 import rate,UnsupportedDomain

def require(ok,message):
 if not ok:raise ValueError(message)
def digest(value):
 try:return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
 except (TypeError,ValueError,OverflowError) as exc:raise ValueError('invalid reference encoding') from exc

def verify_reference(reference):
 # Recreate explicit canonical inputs, source metadata, all80/140digit results,
 # derived diagnostics and rejected cases. A report hash alone cannot do this.
 fresh=fresh_cases()
 require(digest(reference)==digest(fresh),'reference differs from fresh independent80/140digit corpus')
 maximum=Decimal(0)
 for case in reference['cases']:
  q=case['request'];hi=rate(q['state'],q['increment'],q['parameters'],160)
  old=case['oracle']
  require(hi['sigma_rhs']==old['sigma_rhs'] and hi['e_rhs']==old['e_rhs'],'160digit refinement changes rounded rates')
  if hi['expm'] is not None:
   with localcontext() as ctx:
    ctx.prec=180
    error=max(abs(Decimal(x)-Decimal(y)) for x,y in zip(hi['expm']['decimal_normalized'],old['expm']['decimal_normalized']))
    require(error<Decimal('1e-110'),'140/160digit exponential refinement')
    maximum=max(maximum,error)
 for case in reference['rejected_cases']:
  q=case['request']
  try:rate(q['state'],q['increment'],q['parameters'],160)
  except UnsupportedDomain as exc:require(str(exc)==case['message'],'rejected diagnostic identity')
  else:raise ValueError('previously rejected actual binary64 input accepted')
 return {'cases':111,'rejected':3,'fresh_precisions':[80,140,160],'maximum_140_160_normalized_expm_difference':str(maximum),'scope':'Scalar body-law arithmetic binary64; Decimal refinement of actual rounded exponential argument only; no AD/integration/admission'}
