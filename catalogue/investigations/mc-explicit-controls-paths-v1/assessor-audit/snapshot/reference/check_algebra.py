"""Exact rational identities independent of Decimal path implementation."""
from fractions import Fraction as F
import json,random
random.seed(140503);checks=0
for k in range(1000):
 K,G=F(random.randrange(1,101),7),F(random.randrange(1,101),11);s,d=F(random.randrange(1,100),100),F(random.randrange(1,100),100);L=K-2*G/3;E=9*K*G/(3*K+G);nu=(3*K-2*G)/(2*(3*K+G))
 C=lambda x,y:((L+2*G)*x+2*L*y,L*x+(2*L+2*G)*y)
 for side in('compression','extension'):
  u,v=(1-d,-(1+d)/2)if side=='compression'else(-1-d,(1-d)/2);ca,cr=C(u,v)
  den=(1-s)*ca-(1+s)*cr if side=='compression'else(1-s)*cr-(1+s)*ca
  source=4*K*d*s+G*(3-s-d+s*d/3)if side=='compression'else 4*K*d*s+G*(3+s+d+s*d/3)
  assert den==source>0;checks+=1
  assert u+2*v==-2*d;checks+=1
  assert ca-cr==(G*(3-d)if side=='compression'else-G*(3+d));checks+=1
  gamma=F(random.randrange(1,100),101);dq=F(random.randrange(-100,101),29)
  ea=(dq+(ca-cr)*gamma)/(3*G);er=-ea/2;da,dr=C(ea,er)
  assert da-dr-gamma*(ca-cr)==dq;checks+=1
  assert (da+2*dr-gamma*(ca+2*cr))/3==2*K*d*gamma;checks+=1
  xe,xp=F(random.randrange(-100,101),71),F(random.randrange(-100,101),73)
  er=-nu*xe+(v/u)*xp;da,dr=C(xe+xp,er);gam=xp/u
  assert dr-gam*cr==0 and da-gam*ca==E*xe;checks+=1
print(json.dumps({'identity':'mc-axisymmetric-exact-rational-algebra-v1','checks':checks,'passed':True,'candidate_calls':0,'compiled_observations':0},indent=2))
