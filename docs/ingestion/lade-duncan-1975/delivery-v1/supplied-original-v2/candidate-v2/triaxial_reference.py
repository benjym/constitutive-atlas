"""Independent stress-driven scalar source compliance quadrature, no Atlas DSL."""
import json,math,hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
P=60000.;PA=101325.
SETS={'dense':dict(k1=103,ft=40,A=.44,rf=.957,M=2.55e-4,l=1.32,Kur=2300,n=.80),'loose':dict(k1=58,ft=33,A=.39,rf=.970,M=6.80e-4,l=1.17,Kur=1600,n=.86)}
def f(r):return (r+2)**3/r
def root_level(level):
    lo,hi=1.,20.
    for _ in range(100):
        mid=(lo+hi)/2
        if f(mid)>level:hi=mid
        else:lo=mid
    return (lo+hi)/2

def quad(fn,lo,hi,tol):
    if lo==hi:return 0.
    def sim(a,b,fa,fm,fb):return (b-a)*(fa+4*fm+fb)/6
    def rec(a,b,fa,fm,fb,total,eps,depth):
        mid=(a+b)/2;l=(a+mid)/2;r=(mid+b)/2;fl,fr=fn(l),fn(r)
        left,right=sim(a,mid,fa,fl,fm),sim(mid,b,fm,fr,fb)
        delta=left+right-total
        if abs(delta)<=15*eps:return left+right+delta/15
        if not depth:raise RuntimeError('quadrature depth exhausted')
        return rec(a,mid,fa,fl,fm,left,eps/2,depth-1)+rec(mid,b,fm,fr,fb,right,eps/2,depth-1)
    a,b=lo,hi;fa,fm,fb=fn(a),fn((a+b)/2),fn(b)
    return rec(a,b,fa,fm,fb,sim(a,b,fa,fm,fb),tol,24)

def reference(params,eps,tol):
    t=root_level(params['ft']);failure=root_level(params['k1']);E=params['Kur']*PA*(P/PA)**params['n'];a=params['M']*PA*(P/PA)**params['l']
    def plastic_compliance_r(r,component):
        # S=P*diag(r,1,1); derivative in r, with frozen-kappa2 gradient.
        level=f(r);k=params['A']*level+27*(1-params['A']);gp=(r+2)**3-k*r
        n1=3*(r+2)**2-k;nr=3*(r+2)**2-k*r
        df=2*(r-1)*(r+2)**2/r**2
        den=1-params['rf']*(level-params['ft'])/(params['k1']-params['ft'])
        return (a/P)*(n1 if component==0 else nr)*df/(3*gp*den**2)
    def axial(r):return P*(r-1)/E+(quad(lambda x:plastic_compliance_r(x,0),t,r,tol) if r>t else 0.)
    if eps>=axial(failure):raise ValueError('requested strain reaches/exceeds failure')
    lo,hi=1.,failure
    for _ in range(65):
        mid=(lo+hi)/2
        if axial(mid)>eps:hi=mid
        else:lo=mid
    r=(lo+hi)/2;level=f(r);x=max(level-params['ft'],0)
    radial=quad(lambda v:plastic_compliance_r(v,1),t,r,tol) if r>t else 0.
    work=a*x/(1-params['rf']*x/(params['k1']-params['ft']))
    return {'axial_strain':eps,'axial_stress':P*r,'radial_stress':P,'radial_strain':radial,'h':max(level,params['ft']),'wp':work,'f':level}
if __name__=='__main__':
    policy=json.loads((HERE/'triaxial-policy.json').read_text());rows=[]
    for name,p in SETS.items():
        for target in policy['targets_axial_strain']:
            coarse,fine=[reference(p,target,t) for t in policy['quadrature_abs_strain_tolerances']]
            ds=abs(coarse['axial_stress']-fine['axial_stress'])/fine['axial_stress'];dr=abs(coarse['radial_strain']-fine['radial_strain'])
            rows.append({'set':name,'reference':fine,'convergence':{'relative_axial_stress':ds,'absolute_radial_strain':dr},'passed':ds<=policy['reference_convergence']['relative_axial_stress'] and dr<=policy['reference_convergence']['absolute_radial_strain']})
    result={'policy_sha256':hashlib.sha256((HERE/'triaxial-policy.json').read_bytes()).hexdigest(),'reference_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':rows,'passed':all(x['passed'] for x in rows)}
    (HERE/'triaxial-reference-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(0 if result['passed'] else 1)
