"""Proposal diagnostic only; production must remain declarative/common-engine.

Check the eliminated formula against finite-law equations and the previously
frozen continuous source solution. This helper is NOT the independent oracle;
that separately authored constrained-equation review lives in independent-review/.
"""
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
P = dict(M=1.2, lam=.2, kappa=.04, Gamma=2.5, pref=1000.)


def mean(a):
    return math.fsum(a[:3])/3


def dev(a):
    p = mean(a)
    return tuple(x-(p if i<3 else 0) for i,x in enumerate(a))


def direction(a):
    """Scaled vector direction: never square an unscaled tiny component."""
    scale = max(map(abs,a))
    if scale == 0:
        return (0.,)*6, 0.
    z = tuple(x/scale for x in a)
    n = math.hypot(*z)
    return tuple(x/n for x in z), scale*n


def preparation(p=100000., q=0., pc=100000., pars=P):
    d=pars['lam']-pars['kappa']
    w=pars['Gamma']+d*(1-math.log(pc/pars['pref']))
    v=w-pars['kappa']*math.log(p/pars['pref'])
    return (p+2*q/3,p-q/3,p-q/3,0.,0.,0.,v)


def update(z,de,pars=P):
    if len(z)!=7 or len(de)!=6 or not all(math.isfinite(x) for x in (*z,*de)):
        raise ValueError('finite complete state and strain required')
    M,la,ka,G,pref=(pars[k] for k in ('M','lam','kappa','Gamma','pref'))
    if not (M>0 and la>ka>0 and pref>0 and z[6]>0 and mean(z)>0):
        raise ValueError('outside material domain')
    if max(map(abs,de)) == 0:
        return tuple(z), dict(branch='hold', L=0., r=0., Ev=0.)
    E=math.fsum(de[:3])
    if 1+E<=0:
        raise ValueError('BE volume denominator is nonpositive')
    v=z[6]/(1+E)
    # Normalize before dev to preserve tiny pure diagonal directions too.
    ds=max(map(abs,de)); dn=dev(tuple(x/ds for x in de))
    unit, mag=direction(dn)
    r=ds*mag*math.sqrt(2/3)
    r_nonzero=max(map(abs,dn))>0
    xn=math.log(mean(z)/pref)
    alpha=ka/v; beta=M*r/(la-ka)
    xc=(G+la-ka-v)/la
    xs=(E+alpha*xn+beta*(G-v))/(alpha+beta*la)
    x=min(xs,xc); p=pref*math.exp(x)
    Q=max(0.,M*p*la/(la-ka)*(xc-x))
    if xs>=xc:
        s=(0.,)*6; L=(E-alpha*(xc-xn))/M; branch='corner'
    elif r_nonzero:
        s=tuple(math.sqrt(2/3)*Q*a for a in unit); L=r; branch='smooth'
    else:
        oldunit,oldmag=direction(dev(z[:6])); oldq=math.sqrt(1.5)*oldmag
        factor=math.sqrt(2/3)*min(oldq,Q)
        s=tuple(factor*a for a in oldunit); L=0.; branch='elastic-projection'
    return tuple(s[i]+(p if i<3 else 0) for i in range(6))+(v,),dict(branch=branch,L=L,r=r,Ev=E)


def residuals(old,new,diag,pars=P):
    M,la,ka,G,pref=(pars[k] for k in ('M','lam','kappa','Gamma','pref'))
    pn,p=mean(old),mean(new);vn,v=old[6],new[6]
    xn,x=math.log(pn/pref),math.log(p/pref)
    wn,w=vn+ka*xn,v+ka*x
    c=1+(G-w)/(la-ka)
    q=math.sqrt(1.5)*math.hypot(*dev(new[:6])); F=q+M*p*(x-c)
    A=M*(1+x-c);L=diag['L']; E=diag['Ev'];r=diag['r']
    vals=[abs(v-vn+v*E),abs(E-ka/v*(x-xn)-L*A),abs(w-wn+v*L*A),max(0.,F)/max(p,pref),abs(L*F)/max(p,pref)]
    if diag['branch']=='smooth':
        vals += [abs(L-r), abs(F)/max(p,pref)]
    if diag['branch']=='corner':
        vals += [max(0.,r-L),q/max(p,pref),abs(x-c)]
    return max(vals)


def checks():
    policy=json.loads((BASE/'prospective.json').read_text())
    cases=[]
    def add(name,z,de):
        out,d=update(z,de);res=residuals(z,out,d)
        assert res<=policy['physical_residual_relative_budget'], (name,res)
        cases.append(dict(name=name,old=z,de=de,new=out,diagnostics=d,maximum_scaled_finite_residual=res))
        return out,d
    nc=preparation();oc=preparation(p=50000,pc=100000,q=10000)
    add('interior hold',oc,[0.]*6)
    add('elastic compression',oc,[.001]*3+[0.]*3)
    add('elastic recovery',oc,[-.001]*3+[0.]*3)
    add('deviator capacity projection',preparation(p=50000,pc=100000,q=40000),[-.1]*3+[0.]*3)
    for sign in [1,-1]:
        for r in [.00001,.001,.01]:
            add(f'smooth signed {sign} {r}',nc,[sign*r,-sign*r/2,-sign*r/2,0.,0.,0.])
    add('isotropic corner',nc,[.002]*3+[0.]*3)
    add('mixed corner',nc,[.0022,.0019,.0019,.0002,0.,0.])
    add('dry-side dilution',preparation(p=20000,q=35000,pc=20000*math.exp(35000/(1.2*20000))),[.002,-.001,-.001,0.,0.,0.])
    critical=preparation(p=50000,q=60000,pc=math.e*50000)
    add('critical undrained',critical,[.001,-.0005,-.0005,0.,0.,0.])
    zz,_=add('first shear',oc,[.001,-.0005,-.0005,0.,0.,0.])
    add('reverse shear',zz,[-.001,.0005,.0005,0.,0.,0.])
    tiny,_=add('tiny nonzero shear',preparation(p=50000,pc=100000),[0.,0.,0.,1e-200,0.,0.])
    assert abs(tiny[3])>1000 and math.sqrt(sum(x*x for x in [1e-200]))==0
    try:
        update(nc,[-1.,-1.,-1.,0.,0.,0.])
    except ValueError:
        pass
    else:
        raise AssertionError('invalid volume accepted')
    assert update(oc,[0.]*6)[0]==oc
    # Continuous analytical virgin-undrained path; only the closed solution seeds
    # the post-vertex state, then repeated finite-equation updates are compared.
    v0=nc[6];Lam=1-P['kappa']/P['lam'];a=P['M']*v0/(P['kappa']*Lam)
    def exact(t):
        p=100000*math.exp(-Lam+Lam*math.exp(-a*t))
        q=P['M']*p*(-math.expm1(-a*t))
        return preparation(p=p,q=q,pc=p*math.exp(q/(P['M']*p)))
    ref=policy['undrained_reference'];studies=[]
    for n in ref['steps']:
        z=exact(ref['start_distortion']);h=(ref['end_distortion']-ref['start_distortion'])/n
        err=0.
        for i in range(n):
            z,_=update(z,[h,-h/2,-h/2,0.,0.,0.]);target=exact(ref['start_distortion']+(i+1)*h)
            err=max(err,max(abs(z[j]-target[j])/100000 for j in range(6)),abs(z[6]-target[6]))
        studies.append(dict(steps=n,maximum_scaled_error=err))
    improvements=[a['maximum_scaled_error']/b['maximum_scaled_error'] for a,b in zip(studies,studies[1:])]
    assert min(improvements)>=ref['minimum_adjacent_error_improvement'],improvements
    assert studies[-1]['maximum_scaled_error']<=ref['finest_scaled_error_budget'],studies
    # Reference-pressure invariance, without modifying the physical old state.
    converted=dict(P,pref=10000.,Gamma=P['Gamma']-P['lam']*math.log(10))
    for case in cases:
        zz,_=update(case['old'],case['de'],converted)
        err=max(abs(a-b)/max(1.,abs(a)) for a,b in zip(zz,case['new']))
        assert err<policy['reference_pressure_relative_budget'],(case['name'],err)
    return dict(passed=True,scope='proposal Python diagnostics, not backend or independent oracle',cases=cases,undrained_refinement=studies,adjacent_improvements=improvements,naive_tiny_norm_false_zero_retained=True)


if __name__=='__main__':
    (BASE/'prototype-results.json').write_text(json.dumps(checks(),indent=2,allow_nan=False)+'\n')
