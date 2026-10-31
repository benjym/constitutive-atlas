"""Independent exact v2 rearrangement identities; no Atlas imports."""
from fractions import Fraction as Q
import itertools,json
checks=0
for (s,cp),d,K,G,c in itertools.product([(Q(3,5),Q(4,5)),(Q(5,13),Q(12,13))],[Q(1,100),Q(1,3),Q(99,100)],[Q(1,1000),Q(2,3),Q(1000)],[Q(1)],[Q(5)]):
 h=2*c*cp;D=4*K*d*s
 for m,x,y in itertools.product([-Q(10)**300,-Q(10),Q(0),Q(1),Q(10)**300],[Q(0),Q(1,100),Q(1),Q(10)**300],[Q(0),Q(1,100),Q(1),Q(10)**300]):
  t=(m+x+y,m+y,m);F=(1+s)*t[0]-(1-s)*t[2]-h
  old=(Q(2,3)*s*sum(t)-h)/D
  new=(F-(1+s/3)*x-(1-s/3)*y)/D
  assert old==new
  assert (t[0]+t[1]-2*t[2])/(2*G*(3-d))==(x+2*y)/(2*G*(3-d))
  assert (2*t[0]-t[1]-t[2])/(2*G*(3+d))==(2*x+y)/(2*G*(3+d))
  assert (1+s)*(t[0]+t[1])/2-(1-s)*t[2]-h==F-(1+s)*x/2
  assert (1+s)*t[0]-(1-s)*(t[1]+t[2])/2-h==F-(1-s)*y/2
  if x==y==0:assert new==F/D
  checks+=1
print(json.dumps({'identity':'mc-gap-classifier-v2-exact-identities-v1','cases':checks,'algebraic_identities_per_case':5,'hydrostatic_identity_checked':True,'failed':0,'compiled_observations':0,'candidate_executed':False},indent=2,sort_keys=True))
