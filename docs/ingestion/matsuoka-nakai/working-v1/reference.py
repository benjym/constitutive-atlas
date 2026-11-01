"""Independent Cartesian/principal-value differential reference, NumPy only.
No Atlas imports; solves candidate augmented compliance systems, integrates RK4.
"""
import math
import numpy as np
R2=math.sqrt(2.)
I=np.array([1.,1.,1.,0.,0.,0.])
DEFAULT=dict(p_ref=98000.,Cc=.0508,Ce=.0112,e_ref=.83,Rcs=3.5,beta=1.5,a_density=500.,nu=.2)

def matrix(v):
    x,y,z,u,vv,w=v
    return np.array([[x,u/R2,w/R2],[u/R2,y,vv/R2],[w/R2,vv/R2,z]])

def mandel(a):return np.array([a[0,0],a[1,1],a[2,2],R2*a[0,1],R2*a[1,2],R2*a[0,2]])

def terms(stress,rho,p=DEFAULT):
    smat=matrix(np.array(stress)/p['p_ref']);s,q=np.linalg.eigh(smat)
    if min(s)<=0:raise ValueError('nonpositive principal stress')
    i1=sum(s);i2=s[0]*s[1]+s[1]*s[2]+s[2]*s[0];i3=math.prod(s);c=i3/i2
    av=np.sqrt(c/s);tv=av*s;tn=sum(av*tv);xd=tv/tn-av;x2=float(xd@xd)
    r=math.sqrt(p['Rcs']);xc=math.sqrt(2)/3*(r-1/r);yc=(1-r)/(math.sqrt(2)*(r+.5))
    mp=xc**p['beta']+xc**(p['beta']-1)*yc
    # Exact hydro continuation; do not approximate a physical near-hydro state as hydro.
    if max(s)==min(s):
        x2=0.;co=0.;grad=np.zeros(3)
    else:
        co=x2**(p['beta']/2-1)/mp
        grad=np.array([(x2+1)*(1/i1+(i1-si)/i2-1/si) for si in s])
    mdiag=(av+co*(xd-x2*av))/tn
    nl=np.array([1/si-(i1-si)/i2 for si in s])
    nd=nl+co*grad/2
    tr=lambda d:mandel(q@np.diag(d)@q.T)
    m=tr(mdiag);n=tr(nd);dtn=tr(tn*nl)
    cp=p['Cc']-p['Ce'];hp=(sum(mdiag)+p['a_density']*rho*rho/tn)/cp
    icmod=(1+p['a_density']*rho*rho/sum(av))/cp
    size=tn*math.exp(x2**(p['beta']/2)/(p['beta']*mp))
    mean=i1/3;young=3*(1-2*p['nu'])*mean/p['Ce']
    compliance=(1+p['nu'])/young*np.eye(6)-p['nu']/young*np.outer(I,I)
    return dict(a=tr(av),m=m,n=n,dtn=dtn,tn=tn,X2=x2,hp=hp,icmod=icmod,size=size,C=compliance)

def rate(z,de,p=DEFAULT,diagnostics=False):
    t=terms(z[:6],z[6],p);C=t['C'];n=t['n'];m=t['m'];h=t['hp'];b=t['dtn'];size=t['size'];H=t['icmod']
    trial=np.linalg.solve(C,de)
    if n@trial<=0:
        ds=trial;dp=np.zeros(6);branch='elastic'
    else:
        def solve(branch):
            # Independent augmented stress/compliance and two scalar flow equations.
            a=np.zeros((8,8));a[:6,:6]=C;a[:6,6]=m;a[:6,7]=I/3
            rhs=np.zeros(8);rhs[:6]=de
            if branch=='softening' or branch=='AF':
                a[6,:6]=-n;a[6,6]=h;a[7,7]=1
            elif branch=='AF_IC':
                a[6,:6]=-n+b/size;a[6,6]=h
                a[7,:6]=-b/size;a[7,7]=H
            else:
                a[6,6]=1;a[7,:6]=-n;a[7,7]=H
            return np.linalg.solve(a,rhs)
        if h<0:
            out=solve('softening');branch='softening'
        else:
            candidates=[]
            for branch0 in ['AF','AF_IC','IC_only']:
                out0=solve(branch0);ds0=out0[:6];af=n@ds0-max(b@ds0,0)/size
                eps=2e-12*max(1.,np.linalg.norm(de))
                if branch0=='AF' and b@ds0<=eps and out0[6]>=-eps:candidates.append((out0,branch0))
                if branch0=='AF_IC' and b@ds0>=-eps and af>=-eps and out0[6]>=-eps:candidates.append((out0,branch0))
                if branch0=='IC_only' and b@ds0>=-eps and af<=eps:candidates.append((out0,branch0))
            if not candidates:raise ValueError('no consistent source branch')
            out,branch=candidates[0]
        ds=out[:6];dp=out[6]*m+out[7]*I/3
    drho=(1+p['e_ref'])*(sum(dp[:3])-(p['Cc']-p['Ce'])*(n@ds))
    value=np.r_[ds*p['p_ref'],drho,-(1+p['e_ref'])*sum(de[:3])]
    return (value,branch) if diagnostics else value

def rk4(initial,total,n,p=DEFAULT):
    z=np.array(initial,dtype=float);de=np.array(total,dtype=float)/n
    for _ in range(n):
        a=rate(z,de,p);b=rate(z+a/2,de,p);c=rate(z+b/2,de,p);d=rate(z+c,de,p)
        z+=(a+2*b+2*c+d)/6
    return z

def augmented_state(z,p=DEFAULT):return list(z[:8])+list(terms(z[:6],z[6],p)['a'])+[0.,0.]

def initial(pressure=98000.,rho=0.,e=.83):return [pressure]*3+[0.]*3+[rho,e]
