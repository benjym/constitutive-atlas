#!/usr/bin/env python3
"""Small exact source-algebra checks. No Atlas imports or numerical solver."""
from fractions import Fraction as F
import json
from pathlib import Path

def dot(a,b): return sum(x*y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(a,s): return tuple(x*s for x in a)
def linear(d): return tuple((i+1)*x for i,x in enumerate(d))
def overlay(r,eta,d,chi=2,mR=5,mT=2):
    w=r**chi; z=dot(eta,d)
    base=mul(linear(d),w*mT+(1-w)*mR)
    correction=add(mul(linear(eta),1-mT),N) if z>0 else mul(linear(eta),mR-mT)
    return add(base,mul(correction,w*z))
def history(r,eta,d,beta=2):
    return add(d,mul(eta,-r**beta*dot(eta,d))) if dot(eta,d)>0 else d
rows=[]
def check(name,value):
    rows.append({'id':name,'pass':bool(value)})
eta=(F(3,5),F(4,5),F(0)); zero=(F(0),)*3; N=(F(2),F(-3),F(7)); tangent=(F(-4,5),F(3,5),F(0))
check('unit-history-direction',dot(eta,eta)==1)
check('Eq10-saturated-aligned-host',overlay(F(1),eta,eta)==add(linear(eta),N))
check('Eq11-saturated-reversal',overlay(F(1),eta,mul(eta,-1))==mul(linear(mul(eta,-1)),5))
check('Eq12-saturated-neutral',overlay(F(1),eta,tangent)==mul(linear(tangent),2))
check('Eq13-zero-history',overlay(F(0),zero,tangent)==mul(linear(tangent),5))
check('Eq15-aligned-saturation-zero',history(F(1),eta,eta)==zero)
check('Eq15-saturated-tangent-norm-derivative-zero',dot(eta,history(F(1),eta,add(eta,tangent)))==0)
check('Eq15-reversal-unmodified',history(F(1),eta,mul(eta,-1))==mul(eta,-1))
check('Eq15-zero-history',history(F(0),zero,tangent)==tangent)
check('zero-loading-does-not-decay-history',history(F(1,2),eta,zero)==zero)
# Under sigma=-T, d=-D, h=-delta: eta_new=-eta, N_new=-N, L unchanged.
for name,d in [('positive',eta),('negative',mul(eta,-1)),('neutral',tangent)]:
    r=F(2,3); source=overlay(r,eta,d); oldN=N; N=mul(N,-1)
    converted=overlay(r,mul(eta,-1),mul(d,-1)); N=oldN
    check('compression-sign-stress-'+name,converted==mul(source,-1))
    check('compression-sign-history-'+name,history(r,mul(eta,-1),mul(d,-1))==mul(history(r,eta,d),-1))
# Exact Mandel isometry without evaluating sqrt2: product of two Mandel shears=2xy.
a=(F(1),F(2),F(-1),F(3,7),F(-5,9),F(2,3)); b=(F(3),F(-1),F(4),F(2,5),F(1,8),F(-7,4))
A=((a[0],a[5],a[4]),(a[5],a[1],a[3]),(a[4],a[3],a[2]))
B=((b[0],b[5],b[4]),(b[5],b[1],b[3]),(b[4],b[3],b[2]))
cartesian=sum(A[i][j]*B[i][j] for i in range(3) for j in range(3))
mandel=sum(a[i]*b[i]*(1 if i<3 else 2) for i in range(6))
check('orthonormal-Mandel-double-contraction',cartesian==mandel)
ei0,ec0,e,c=F(21,20),F(19,20),F(139,200),F(4,5)
ei,ec=ei0*c,ec0*c
check('AppendixA-beta1-factor-identity',(ei0/ec0)*(1+ei)/ei*(ec/e)==(1+ei)/e)
check('beta2-not-original-host-generally',(ei0/ec0)**2*(1+ei)/ei*(ec/e)**2!=(1+ei)/e)
check('Eq17-mu-not-mR',F(1,5)*F(1,10000)/(1-F(1,2)**2)==F(1,37500))
check('branch-rate-continuity-at-zero-projection',dot(eta,tangent)==0 and overlay(F(1,2),eta,tangent)==mul(linear(tangent),F(17,4)))
report={'task':'AUDIT-igs97-original-equations-v3','scope':'exact illustrative algebra, not a DSL or compiled comparison','status':'pass' if all(x['pass'] for x in rows) else 'fail','checks':rows,'count':len(rows)}
if __name__=='__main__':
    print(json.dumps(report,indent=2))
    if report['status']!='pass': raise SystemExit(1)
