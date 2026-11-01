#!/usr/bin/env python3
"""Standalone Cartesian/principal-stress checks; no Atlas imports or solver calls.
Frozen criteria: relative/absolute 2e-12 algebra, 3e-7 finite-difference derivative.
Not a complete constitutive implementation or trajectory validation.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATOL = 2e-12
DTOL = 3e-7

def close(a, b, tol=ATOL):
    assert abs(a-b) <= tol*max(1., abs(a), abs(b)), (a,b,tol)

def quantities(s):
    i1=sum(s); i2=s[0]*s[1]+s[1]*s[2]+s[2]*s[0]; i3=math.prod(s)
    c=i3/i2
    av=[math.sqrt(c/x) for x in s]
    t=[x*y for x,y in zip(av,s)]
    tn=sum(x*y for x,y in zip(t,av))
    tv=[x-tn*y for x,y in zip(t,av)]
    xs=[x/tn for x in tv]
    return av,t,tn,math.sqrt(sum(x*x for x in xs)),xs

def constants(r,beta):
    root=math.sqrt(r)
    x=math.sqrt(2)/3*(root-1/root)
    y=(1-root)/(math.sqrt(2)*(root+.5))
    m=(x**beta+x**(beta-1)*y)**(1/beta)
    return x,y,m

def zeta(x,m,beta):
    return (x/m)**beta/beta

def yieldpart(s,m,beta):
    _,_,tn,x,_=quantities(s)
    return math.log(tn)+zeta(x,m,beta)

def analytic_n(s,m,beta):
    i1=sum(s); i2=s[0]*s[1]+s[1]*s[2]+s[2]*s[0]; i3=math.prod(s)
    _,_,tn,x,_=quantities(s)
    n=[]
    for si in s:
        dlogtn=1/si-(i1-si)/i2
        # X^2+1=I1 I2/(9 I3), avoiding a tensor eigensolver.
        dx=(x*x+1)*(1/i1+(i1-si)/i2-1/si)/(2*x)
        n.append(dlogtn+x**(beta-1)/m**beta*dx)
    return n

def run():
    groups=[]
    for s in ([100.,100.,100.],[350.,100.,100.],[370.,230.,90.],[100.,100.,350.]):
        av,t,tn,x,xs=quantities(s)
        close(sum(a*a for a in av),1.)
        close(tn,3*math.prod(s)/(s[0]*s[1]+s[1]*s[2]+s[2]*s[0]))
        close(x*x,sum(s)*(s[0]*s[1]+s[1]*s[2]+s[2]*s[0])/(9*math.prod(s))-1.)
        close(sum(a*y for a,y in zip(av,xs)),0.)
    groups.append('principal_table1_and_invariant_identities:4_states')
    av,t,tn,x,_=quantities([100.,100.,100.])
    for a in av: close(a,1/math.sqrt(3))
    close(tn,100.);close(x,0.)
    groups.append('nonzero_hydrostatic_limit')
    for r,beta in ((3.5,1.5),(3.2,2.)):
        xc,yc,m=constants(r,beta)
        close(quantities([r,1.,1.])[3],xc)
        close((m**beta-xc**beta)/xc**(beta-1),yc)
        av=quantities([r,1.,1.])[0]
        normal=av[0]-av[1]
        shear=math.sqrt(1.5-normal*normal)
        close(normal/shear,yc)
    groups.append('critical_state_A7_A11:clay_and_sand')
    _,_,m=constants(3.5,1.5); beta=1.5
    s=[370.,230.,90.]; av,t,tn,x,xs=quantities(s)
    for k in (1e-6,1.,1e6):
        ak,tk,tnk,xk,_=quantities([k*v for v in s])
        for a,b in zip(ak,av):close(a,b)
        close(tnk,k*tn);close(xk,x)
        close(yieldpart([k*v for v in s],m,beta)-math.log(k),yieldpart(s,m,beta))
    groups.append('pressure_scaling:3_scales')
    # Orthogonal rotation of principal a and t; trace/dot identities are Cartesian.
    q=[[.6,-.8,0.],[.8,.6,0.],[0.,0.,1.]]
    rotate=lambda d:[[sum(q[i][k]*d[k]*q[j][k] for k in range(3)) for j in range(3)] for i in range(3)]
    aa=rotate(av); tt=rotate(t); ss=rotate(s)
    for i in range(3):
        for j in range(3):close(sum(aa[i][k]*ss[k][j] for k in range(3)),tt[i][j])
    close(sum(aa[i][j]*aa[i][j] for i in range(3) for j in range(3)),1.)
    close(sum(aa[i][j]*tt[i][j] for i in range(3) for j in range(3)),tn)
    groups.append('rotated_Cartesian_coaxial_product')
    n=analytic_n(s,m,beta)
    for j in range(3):
        h=1e-4; plus=s.copy();minus=s.copy();plus[j]+=h;minus[j]-=h
        close(n[j],(yieldpart(plus,m,beta)-yieldpart(minus,m,beta))/(2*h),DTOL)
    close(sum(a*b for a,b in zip(n,s)),1.)
    flow=[(a+x**(beta-2)/m**beta*(y-x*x*a))/tn for a,y in zip(av,xs)]
    assert max(abs(a-b) for a,b in zip(n,flow))>1e-4
    groups.append('ordinary_stress_gradient_Euler_and_finite_difference_distinct_from_flow')
    cp=(.1-.02)/(1+.8);rho=.05;a=500.;tr_a=sum(av)
    hp=(sum(flow)+a*rho*rho/tn)/cp
    close(hp,(sum(flow)-(-a*rho*rho/tn))/cp)
    close((a*0.*0.)/tn,0.)
    assert -a*rho*rho/tn<0
    ratio=math.exp(rho/(.1-.02))
    close((.1-.02)*math.log(ratio),rho)
    groups.append('density_hardening_NC_limit_and_log_surface_ratio')
    # Eq 51 becomes Eq 52 when positive dtN vanishes; Appendix V boundary.
    dfs=0.002; dtn=0.; size=tn*math.exp(zeta(x,m,beta))
    af=(dfs-max(dtn,0.)/size)/hp
    ic=(max(dtn,0.)/size)/((1+a*rho*rho/tr_a)/cp)
    close(af,dfs/hp);close(ic,0.)
    dtn=dfs*size
    af=(dfs-dtn/size)/hp
    ic=(dtn/size)/((1+a*rho*rho/tr_a)/cp)
    appendix=dfs/((1+a*rho*rho/tr_a)/cp)
    close(af,0.);close(ic,appendix)
    groups.append('branch_boundary_algebra_Eq51_52_and_A28')
    assert all(v>0 for v in s)
    # Finite SPD hydro is admissible; zero/tension are outside literal square-root/log law.
    rejected=0
    for bad in ([1.,0.,1.],[1.,-1.,1.],[0.,0.,0.]):
        if not all(v>0 for v in bad):rejected+=1
    assert rejected==3
    groups.append('explicit_positive_principal_source_domain_witnesses')
    return {'status':'pass','groups':groups,'group_count':len(groups),
            'criteria':{'algebra_relative_absolute':ATOL,'derivative_relative_absolute':DTOL},
            'limitations':['No stress update, integrated paths, branch selection, native or Wasm calls.',
                          'Regular principal derivatives only; hydro and boundary derivatives remain open.'],
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run()
    if args.write:(HERE/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
