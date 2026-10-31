"""Exact policy-semantics witness, not a candidate floating computation."""
from fractions import Fraction as Q
import json
from check_classifier import Law,enc
law=Law(Q(1),Q(1),Q(3,5),Q(1,3),Q(5),Q(4,5))
eps=Q(1,2**52);delta=256*eps*8
t=(5+delta*Q(5,8),Q(1),Q(0))
assert max(law.h,abs(t[0]),abs(t[2]))==8
assert law.data(t)[0]['face']==delta
branch,g,r=law.check(t);assert branch=='face'and g>0
jump=tuple(t[i]-r[i]for i in range(3))
v=(1+law.d,Q(0),-1+law.d);cv=tuple(2*law.G*x+(law.K-Q(2,3)*law.G)*sum(v)for x in v)
f=(1+law.s,Q(0),-1+law.s)
source_tangent=[[Q(i==j)-cv[i]*f[j]/law.den['face']for j in range(3)]for i in range(3)]
zone_tangent=[[Q(i==j)for j in range(3)]for i in range(3)]
assert source_tangent!=zone_tangent
print(json.dumps(enc({'identity':'mc-prospective-elastic-zone-exact-semantics-v1','compiled_observations':0,'candidate_executed':False,'epsilon':eps,'delta':delta,'source_trial':t,'exact_source_branch':branch,'source_gamma':g,'exact_source_return':r,'prospective_zone_return':t,'upper_zone_discontinuity_vector':jump,'source_principal_tangent':source_tangent,'zone_principal_tangent':zone_tangent,'meaning':'A distinct F<=delta zone intentionally returns elastic for a source-plastic state and chooses identity tangent. Its boundary jump is nonzero; this is declared numerical policy, not exact source equality.'}),indent=2,sort_keys=True))
