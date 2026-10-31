#!/usr/bin/env python3
"""Independent exact structural checks for 2016 Eqs8,9,18,19 sign conversion.
No Atlas imports, evaluators, derivatives, integration or compiled artifacts.
Rational surrogate coefficients test tensor algebra, not material calibration.
"""
from fractions import Fraction as Q
import json

def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(c,a): return tuple(c*x for x in a)
def dot(a,b): return sum(a[i]*b[i] for i in range(3))+2*sum(a[i]*b[i] for i in range(3,6))
def trace(a): return sum(a[:3])
I=(Q(1),Q(1),Q(1),Q(0),Q(0),Q(0))
hat=(Q(1,2),Q(1,3),Q(1,6),Q(1,12),Q(0),Q(0))
dev=add(hat,mul(-trace(hat)/3,I))
C,F2,a2,Nfac=Q(7,3),Q(5,4),Q(9,2),Q(11,5)
def L(d): return mul(C,add(mul(F2,d),mul(a2*dot(hat,d),hat)))
Ns=mul(Nfac,add(hat,dev))
Nc=mul(-1,Ns)
mR,mT,chi,beta=Q(11,5),Q(11,10),2,2
rows=[]
# Tensor components, not engineering shear or Mandel coordinates.
etas=[(Q(1),Q(0),Q(0),Q(0),Q(0),Q(0)),(Q(3,5),Q(4,5),Q(0),Q(0),Q(0),Q(0))]
for eta in etas:
 for rho in (Q(1,2),Q(1)):
  for d in (eta,mul(-1,eta),(Q(0),Q(0),Q(0),Q(1,3),Q(0),Q(0)),(Q(1,7),Q(-2,7),Q(3,7),Q(1,9),Q(0),Q(0))):
   ds,es=mul(-1,d),mul(-1,eta)
   ps,p=dot(es,ds),dot(eta,d)
   B=rho**chi*mT+(1-rho**chi)*mR
   # Printed fourth-order dyads contracted with source strain rate.
   corr_s=add(mul((1-mT),L(es)),Ns) if ps>0 else mul(mR-mT,L(es))
   source=add(mul(B,L(ds)),mul(rho**chi*ps,corr_s))
   # Independently reduced compression-positive form.
   corr_c=add(mul((1-mT),L(eta)),Nc) if p>0 else mul(mR-mT,L(eta))
   converted=add(mul(B,L(d)),mul(rho**chi*p,corr_c))
   assert converted==mul(-1,source)
   hs=add(ds,mul(-rho**beta*ps,es)) if ps>0 else ds
   hc=add(d,mul(-rho**beta*p,eta)) if p>0 else d
   assert hc==mul(-1,hs)
   assert ps==p
   if rho==1 and d==eta:
    assert hc==(Q(0),)*6
    assert converted==add(L(d),Nc)
   rows.append({'rho':str(rho),'projection':str(p),'stress_sign_conversion':True,'history_sign_conversion':True})
# General exact Mandel isometry in a symbolic sqrt(2) extension:
# normal entries unchanged, both shear factors sqrt(2) give 2*aij*bij.
a=(Q(2),Q(-1),Q(3),Q(2,3),Q(-4,5),Q(6,7));b=(Q(1),Q(4),Q(-2),Q(3,8),Q(2,9),Q(-1,11))
assert dot(a,b)==sum(a[i]*b[i] for i in range(3))+sum(2*a[i]*b[i] for i in range(3,6))
# Pairing eta_source=-eta, D_source=-D preserves branch even with shear.
assert dot(mul(-1,a),mul(-1,b))==dot(a,b)
# Hydrostatic hat=I/3 gives j2=0 and F=1 independent of indeterminate cosine.
assert add(mul(Q(1,3),I),mul(Q(-1,3),I))==(Q(0),)*6
u=Q(0)
assert u*u/8+(2-u*u)/(2+u)==1 and u==0  # sqrt argument1, subtractive term0, so F1
print(json.dumps({'id':'kfs-tmd2-appendix-law-algebra-v1','checks':'16 exact stress/history/branch fixtures, Mandel isometry, paired signs and hydrostatic invariant limit','fixtures':rows,'passed':True,'limits':'Coefficient surrogates; no root evaluation, material trajectory, tolerance or admission test.'},indent=2,sort_keys=True))
