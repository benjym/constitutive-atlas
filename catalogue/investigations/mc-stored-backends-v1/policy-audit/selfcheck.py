from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal as D,localcontext
import json,random,sys
sys.path.insert(0,str(Path(__file__).parent));import classify as c
p=Path(__file__).parent;d=json.loads((p/'policy-table.json').read_text());checks=0
assert d['counts']=={'conditional-numerical-coverage-gap':27,'required-success':113};checks+=1
for row in d['cases']:
 assert row['canonical_branch']in row['eligible_branches'];checks+=1
 for b in row['branches'].values():assert len(b['direction_norm_budgets'])==38 and all(D(x)>0 for x in b['direction_norm_budgets']);checks+=1
 if row['id'].startswith('mixed-scale-middle/'):assert row['mixed_component_gate']is not None;checks+=1
s=json.loads((p/'supplemental/check-results.json').read_text());assert s['passed']and not s['failures'];checks+=1
random.seed(76319)
with localcontext()as ctx:
 ctx.prec=160
 for k in range(2000):
  a=F(random.randrange(-100000,100001),2**random.randrange(0,40));b=F(random.randrange(1,100001),2**random.randrange(0,40));x,y=D(a.numerator)/D(a.denominator),D(b.numerator)/D(b.denominator)
  for actual,box in((a+b,c.I(x)+c.I(y)),(a-b,c.I(x)-c.I(y)),(a*b,c.I(x)*c.I(y)),(a/b,c.I(x)/c.I(y))):
   exact=D(actual.numerator)/D(actual.denominator);assert box.a<=exact<=box.b;checks+=1
r={'identity':'mc-backend-source-policy-selfcheck-v1','checks':checks,'passed':True,'candidate_calls':0,'compiled_observations':0};print(json.dumps(r,indent=2))
