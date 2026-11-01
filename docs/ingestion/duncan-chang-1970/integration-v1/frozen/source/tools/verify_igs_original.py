"""Python-only instantaneous comparison with Niemunis–Herle 1997 Eqs. 14–15, 23–31.

Constructs the full Cartesian fourth-order operator from the original paper.
Does not import the existing host oracle, integrate trajectories or execute binaries.
"""
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.model import load, interpret


def cart(v):
    x,y,z,u,v,w = v
    return [[x,u/math.sqrt(2),w/math.sqrt(2)],
            [u/math.sqrt(2),y,v/math.sqrt(2)],
            [w/math.sqrt(2),v/math.sqrt(2),z]]


def mandel(a):
    return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],
            math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]


def original(state, strain, p):
    """Original physical history ball only; compression-positive conversion.

    Appendix A has no free beta. Its density product is Eq. 29 directly.
    """
    if p['beta'] != 1.:
        raise ValueError('original seven-parameter host requires beta=1')
    S,H,D = cart(state['sigma']),cart(state['h']),cart(strain)
    tr = sum(S[i][i] for i in range(3)); e=state['e']
    A=[[S[i][j]/tr for j in range(3)] for i in range(3)]
    B=[[A[i][j]-(i==j)/3 for j in range(3)] for i in range(3)]
    b2=sum(x*x for row in B for x in row)
    b3=sum(B[i][j]*B[j][k]*B[k][i] for i in range(3) for j in range(3) for k in range(3))
    cosine=-math.sqrt(6)*b3/b2**1.5 if b2 else 0.
    u=math.sqrt(3*b2)
    F=math.sqrt(u*u/8+(2-u*u)/(2+math.sqrt(2)*u*cosine))-u/(2*math.sqrt(2))
    a=math.sqrt(3)*(3-math.sin(p['phi']))/(2*math.sqrt(2)*math.sin(p['phi']))
    reduction=math.exp(-(tr/p['hs'])**p['n'])
    ed,ec,ei=[p[n]*reduction for n in ['ed0','ec0','ei0']]
    density=(e-ed)/(ec-ed)
    factor=(p['hs']/p['n']*(1+ei)/e*(tr/p['hs'])**(1-p['n']) /
            (3+a*a-a*math.sqrt(3)*((p['ei0']-p['ed0'])/(p['ec0']-p['ed0']))**p['alpha']))
    aa=sum(x*x for row in A for x in row)
    # Symmetric fourth-order identity, with full Cartesian shear contractions.
    L=[[[[factor/aa*(F*F*((i==k)*(j==l)+(i==l)*(j==k))/2+
                       a*a*A[i][j]*A[k][l]) for l in range(3)]
          for k in range(3)] for j in range(3)] for i in range(3)]
    N=[[-density**p['alpha']*factor*F*a/aa*(A[i][j]+B[i][j])
        for j in range(3)] for i in range(3)]
    magnitude=math.sqrt(sum(x*x for row in H for x in row))
    rho=magnitude/p['R']
    if rho>1+1e-14: raise ValueError('outside original history ball')
    eta=[[x/magnitude if magnitude else 0. for x in row] for row in H]
    projection=sum(eta[i][j]*D[i][j] for i in range(3) for j in range(3))
    weight=rho**p['chi']
    base=weight*p['mT']+(1-weight)*p['mR']
    # Assemble M first, then contract. This differs from the DSL's contracted form.
    M=[[[[base*L[i][j][k][l]+weight*eta[k][l]*(
          ((1-p['mT']) if projection>0 else (p['mR']-p['mT']))*
          sum(L[i][j][a][b]*eta[a][b] for a in range(3) for b in range(3))+
          (N[i][j] if projection>0 else 0.)) for l in range(3)]
          for k in range(3)] for j in range(3)] for i in range(3)]
    stress=[[sum(M[i][j][k][l]*D[k][l] for k in range(3) for l in range(3))
             for j in range(3)] for i in range(3)]
    history=[[D[i][j]-(eta[i][j]*rho**p['beta_r']*projection if projection>0 else 0.)
              for j in range(3)] for i in range(3)]
    return mandel(stress)+[-(1+e)*sum(D[i][i] for i in range(3))]+mandel(history)


def check():
    model_path=ROOT/'models/hypoplastic-sand-igs97.json'
    model=load(model_path)
    # Original Table I, p. 292, converting MPa and degrees to SI. beta=1
    # is the derived specialization of the current eight-parameter host.
    p={n:d['default'] for n,d in model['parameters'].items()}
    p.update(phi=math.radians(33),hs=1e9,n=.25,ec0=.95,ed0=.55,ei0=1.05,
             alpha=.25,beta=1.,R=1e-4,mR=5.,mT=2.,beta_r=.5,chi=6.)
    directions=[[1.,0.,0.,0.,0.,0.],[0.,0.,0.,1.,0.,0.],
                [0.,0.,0.,0.,1.,0.],[0.,0.,0.,0.,0.,1.],
                [.4,-.7,.2,.3,-.6,.5],[1.,1.,1.,0.,0.,0.]]
    haxis=[.4,-.7,.2,.3,-.6,.5]; length=math.sqrt(sum(x*x for x in haxis))
    haxis=[x/length for x in haxis]
    cases=[]
    for pressure in [1e4,1e5,1e6]:
        for shape in [[1.,1.,1.,0.,0.,0.],[1.4,.8,.8,.1,-.05,.07]]:
            for void in [.65,.8]:
                for rho in [0.,.3,.9,1.]:
                    state={'sigma':[pressure*x for x in shape], 'e':void,
                           'h':[rho*p['R']*x for x in haxis]}
                    for index,d in enumerate(directions):
                        for sign in [-1,1]:
                            strain=[sign*1e-4*x for x in d]
                            ref=original(state,strain,p)
                            result=interpret(model,state,state,strain,p)
                            actual=list(result['sigma'].v)+[result['e']]+list(result['h'].v)
                            # Declared before execution: stress Pa, void/history dimensionless.
                            absolute=[1e-7]*6+[1e-14]*7;relative=2e-11
                            ratio=max(abs(a-b)/(t+relative*abs(b)) for a,b,t in zip(actual,ref,absolute))
                            cases.append(dict(pressure_Pa=pressure,shape=shape,void_ratio=void,
                                              rho=rho,direction=index,sign=sign,passed=ratio<=1,
                                              max_tolerance_ratio=ratio))
    return dict(record_version=1,kind='python-interpreter-original-equation-comparison',
                source_receipt='catalogue/source-audits/original-papers-2026-10-31.json',
                source_sha256='8fd75de38a5f2c89dcc2cf40c6c2daff03a87153a9e5161c3dfdb91e7a536d8d',
                model_sha256=hashlib.sha256(model_path.read_bytes()).hexdigest(),
                verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                parameters=p,stress_absolute_tolerance_Pa=1e-7,
                dimensionless_absolute_tolerance=1e-14,relative_tolerance=2e-11,
                count=len(cases),passed=sum(c['passed'] for c in cases),
                scope='Instantaneous equations only, zero spin, original host beta=1, rho<=1. No integration, native/Wasm, external code, independent authorship or experimental validation.',
                independent_review='pending',cases=cases)


if __name__=='__main__':
    result=check()
    if len(sys.argv)>1: Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['count','passed','scope']}))
    sys.exit(0 if result['passed']==result['count'] else 1)
