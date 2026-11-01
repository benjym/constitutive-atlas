#!/usr/bin/env python3
"""Independent Hill algebra and Decimal return oracle; no Atlas imports."""
from decimal import Decimal, localcontext
from pathlib import Path
import hashlib
import json
import math


def matrix(p):
    f, g, h, l, m, n = (p[k] for k in ('F', 'Gh', 'Hh', 'L', 'M', 'N'))
    z = f * 0
    return [[g+h,-h,-g,z,z,z],[-h,f+h,-f,z,z,z],[-g,-f,f+g,z,z,z],
            [z,z,z,n,z,z],[z,z,z,z,l,z],[z,z,z,z,z,m]]


def action(a, s):
    return [sum(x*y for x,y in zip(row,s)) for row in a]


def square(a, s):
    return sum(x*y for x,y in zip(s,action(a,s)))


def solve3(a, b):
    """Decimal partial-pivot Gaussian elimination, separate from production Newton."""
    work = [list(row)+[v] for row,v in zip(a,b)]
    for col in range(3):
        pivot = max(range(col,3), key=lambda j: abs(work[j][col]))
        work[col],work[pivot] = work[pivot],work[col]
        divisor = work[col][col]
        if not divisor:
            raise ArithmeticError('singular positive-definite oracle matrix')
        work[col] = [v/divisor for v in work[col]]
        for j in range(col+1,3):
            factor=work[j][col]
            work[j]=[v-factor*w for v,w in zip(work[j],work[col])]
    x=[b[0]*0]*3
    for i in range(2,-1,-1):
        x[i]=work[i][3]-sum(work[i][j]*x[j] for j in range(i+1,3))
    return x


def endpoint(parameters, sigma_n, de, precision=80):
    """Return Decimal stress6+gamma, one unsplit mathematical BE step.

    Inputs may be float, string, or Decimal; decimals use their supplied string
    values. No schema/model loading, clipping, production code or time integration.
    Persistent parent stress must already be admissible.
    """
    with localcontext() as ctx:
        ctx.prec=precision
        d=lambda x: Decimal(str(x))
        p={k:d(v) for k,v in parameters.items()}
        a=matrix(p); sn=list(map(d,sigma_n)); e=list(map(d,de))
        y=p['sigma_y']; mu=p['Gmod']; bulk=p['K']
        if any(p[k]<=0 for k in ('sigma_y','Gmod','K','F','Gh','Hh','L','M','N')):
            raise ValueError('outside positive convex scope')
        if len(sn)!=6 or len(e)!=6 or not all(v.is_finite() for v in sn+e):
            raise ValueError('finite six-component inputs required')
        ev=sum(e[:3]); third=Decimal(1)/3
        t=[sn[i]+2*mu*(e[i]-ev*third if i<3 else e[i])+(bulk*ev if i<3 else 0) for i in range(6)]
        if square(a,t)<=y*y:
            return t+[Decimal(0)]
        def at(gamma):
            c=2*mu*gamma/y
            normal=solve3([[Decimal(i==j)+c*a[i][j] for j in range(3)] for i in range(3)],t[:3])
            return normal+[t[i]/(1+c*a[i][i]) for i in range(3,6)]
        lo=Decimal(0); hi=Decimal(1)
        while square(a,at(hi))>y*y:
            hi*=2
        for _ in range(precision*4):
            mid=(lo+hi)/2
            if mid==lo or mid==hi:
                break
            if square(a,at(mid))>y*y:
                lo=mid
            else:
                hi=mid
        gamma=(lo+hi)/2
        return at(gamma)+[gamma]


def checks():
    p=dict(F=.7,Gh=.5,Hh=.3,L=1.2,M=1.7,N=2.,Gmod=12e6,K=20e6,sigma_y=60000.)
    a=matrix(p); count=0; worst=0.
    def close(x,y,tol=1e-9):
        nonlocal count,worst
        error=abs(x-y)/max(1.,abs(x),abs(y));worst=max(worst,error)
        assert error<tol,(x,y,error)
        count+=1
    # Six known-axis yields; Mandel shear includes sqrt(2).
    coeff=[p['Gh']+p['Hh'],p['F']+p['Hh'],p['F']+p['Gh'],p['N'],p['L'],p['M']]
    for i,c in enumerate(coeff):
        s=[0.]*6;s[i]=p['sigma_y']/math.sqrt(c)
        close(math.sqrt(square(a,s)),p['sigma_y'])
    samples=[[35000.,-21000.,44000.,17000.,-33000.,29000.],[-12000.,52000.,21000.,-19000.,13000.,-37000.]]
    for s in samples:
        q=math.sqrt(square(a,s));n=[v/q for v in action(a,s)]
        close(sum(s[i]*n[i] for i in range(6)),q)
        close(sum(n[:3]),0.)
        close(square(a,[v+120000 if i<3 else v for i,v in enumerate(s)]),q*q)
        close(square(a,[-v for v in s]),q*q)
        for i in range(6):
            left=s.copy();right=s.copy();left[i]-=.01;right[i]+=.01
            grad=(math.sqrt(square(a,right))-math.sqrt(square(a,left)))/.02
            close(grad,n[i],2e-8)
        active=[v*p['sigma_y']/q for v in s]
        close(square(a,active),p['sigma_y']**2)
        for x,y in zip(action(a,active),action(a,s)):
            close(x/p['sigma_y'],y/q)
    iso=dict(p,F=.5,Gh=.5,Hh=.5,L=1.5,M=1.5,N=1.5)
    for s in samples:
        mean=sum(s[:3])/3
        dev=[v-mean if i<3 else v for i,v in enumerate(s)]
        close(square(matrix(iso),s),1.5*sum(v*v for v in dev))
    # Scalar-bisection oracle hydrostatic, elastic and anisotropic endpoint checks.
    for e in ([.0001]*3+[0]*3,[.00001,-.00002,.00001,0,0,0],[.01,-.003,.002,.004,-.002,.003]):
        out=endpoint(p,[0]*6,e);s=out[:6];gamma=out[6]
        with localcontext() as ctx:
            ctx.prec=70;pd={k:Decimal(str(v)) for k,v in p.items()};ad=matrix(pd)
            q2=square(ad,s)
            assert gamma>=0
            assert q2<=pd['sigma_y']**2+Decimal('1e-55')
            if gamma>0:
                assert abs(q2-pd['sigma_y']**2)<Decimal('1e-55')
            count+=2
    return {'status':'pass','checks':count,'largest_normalized_float_error':worst,
            'decimal_precision':80,'compiled_calls':0,'atlas_imports':0,
            'scope':'Independent algebra and mathematical BE oracle self-check; no experimental or backend claim'}


if __name__=='__main__':
    result=checks(); result['script_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
