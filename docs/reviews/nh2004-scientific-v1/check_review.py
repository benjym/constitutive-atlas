"""Independent scientific diagnostics; no Atlas/working-reference imports."""
import gzip, hashlib, json, math
from collections import Counter
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PACK=ROOT/'docs/ingestion/matsuoka-nakai/working-v1'
I=np.eye(3); Cc=.0508; Ce=.0112; Cp=Cc-Ce; er=.83

def terms(s,rho=0.,nu=.2):
    w,Q=np.linalg.eigh(s)
    i1=sum(w);i2=w[0]*w[1]+w[1]*w[2]+w[2]*w[0];i3=np.prod(w)
    av=np.sqrt(i3/i2/w);a=(Q*av)@Q.T;t=a@s;tn=np.sum(t*a)
    x=t/tn-a;x2=np.sum(x*x)
    xc=math.sqrt(2)/3*(math.sqrt(3.5)-1/math.sqrt(3.5))
    yc=(1-math.sqrt(3.5))/(math.sqrt(2)*(math.sqrt(3.5)+.5))
    mp=xc**1.5+xc**.5*yc
    co=x2**(-.25)/mp if x2>1e-30 else 0.
    m=(a+co*(x-x2*a))/tn
    inv=np.linalg.inv(s)
    nlog=inv-(i1*I-s)/i2
    # Derivative from product I1*I2/(9 I3), independent of deviator expression.
    gx=(x2+1)*(I/i1+(i1*I-s)/i2-inv)
    n=nlog+co*gx/2
    h=(np.trace(m)+500*rho*rho/tn)/Cp
    p=i1/3;K=p/Ce;G=3*K*(1-2*nu)/(2*(1+nu))
    D=lambda v:K*np.trace(v)*I+2*G*(v-np.trace(v)*I/3)
    f=math.log(tn)+x2**.75/(1.5*mp)
    return dict(a=a,t=t,tn=tn,x2=x2,m=m,n=n,h=h,D=D,f=f,
                denominator=h+np.sum(n*D(m)),dtn=tn*nlog,size=math.exp(f))

def matrix(v):
    a,b,c,d,e,f=v
    return np.array([[a,d/math.sqrt(2),f/math.sqrt(2)], [d/math.sqrt(2),b,e/math.sqrt(2)], [f/math.sqrt(2),e/math.sqrt(2),c]])

def H(v):
    s=matrix(v[:6])/98000.;g=terms(s)
    return v[7]+v[6]+(1+er)*(Cp*g['f']+Ce*math.log(np.trace(s)/3))

def main():
    checks=[]
    def check(label,error,bound):
        checks.append(dict(name=label,error=float(error),bound=bound,pass_=bool(error<=bound)))
    Q=np.array([[.6,-.8,0],[.8,.6,0],[0,0,1.]])
    for k,w in enumerate([[1,1,1],[3.5,1,1],[1.4,.9,.7],[6,.5,.5]]):
        s=Q@np.diag(w)@Q.T;g=terms(s)
        inv=np.linalg.inv(s);target=inv/np.trace(inv)
        check(f'{k}:positive SMP square',np.max(abs(g['a']@g['a']-target)),1e-11)
        check(f'{k}:SMP unit',abs(np.sum(g['a']**2)-1),1e-11)
        i1=sum(w);i2=w[0]*w[1]+w[1]*w[2]+w[2]*w[0];i3=math.prod(w)
        check(f'{k}:tn identity',abs(g['tn']-3*i3/i2),1e-11)
        check(f'{k}:X identity',abs(g['x2']-(i1*i2/(9*i3)-1)),1e-11)
        # full Cartesian symmetric directional derivative
        V=np.array([[.3,.2,-.1],[.2,-.4,.15],[-.1,.15,.5]])
        if k:
            dt=1e-6
            fd=(terms(s+dt*V)['f']-terms(s-dt*V)['f'])/(2*dt)
            check(f'{k}:ordinary loading gradient',abs(fd-np.sum(g['n']*V)),2e-6)
        vm=[s[0,0],s[1,1],s[2,2],math.sqrt(2)*s[0,1],math.sqrt(2)*s[1,2],math.sqrt(2)*s[0,2]]
        check(f'{k}:Mandel norm',abs(np.dot(vm,vm)-np.sum(s*s)),1e-11)
    cs=terms(np.diag([3.5,1,1]))
    check('critical state trace m',abs(np.trace(cs['m'])),1e-11)
    # Table1 projection for axisymmetric plastic vector (1,-1/2,-1/2).
    a=np.diag(cs['a']);ep=np.array([1,-.5,-.5]);proj=ep@a
    yc=proj/np.linalg.norm(ep-proj*a)
    check('Table1 Ycs Eq18',abs(yc-(1-math.sqrt(3.5))/(math.sqrt(2)*(math.sqrt(3.5)+.5))),1e-11)
    witnesses=[]
    for R in [2,3.5,6,10,20,50,100,1000]:
      for rho in [0,.01,.03]:
       for nu in [-.9,-.5,0,.2,.49]:
        g=terms(np.diag([float(R),1.,1.]),rho,nu)
        if g['h']<0 and g['denominator']<=0:
            witnesses.append(dict(R=R,rho=rho,nu=nu,h=g['h'],denominator=g['denominator'],
                trial=float(np.sum(g['n']**2)),gamma=float(np.sum(g['n']**2)/g['denominator'])))
    saved=json.loads(gzip.decompress((PACK/'qualification.json.gz').read_bytes()))
    paths=[]
    for p in saved['paths']:
        grids=[]
        coverage=Counter()
        for grid in p['native_grids']:
            tr=grid['trajectory'];hs=[H(v) for v in tr]
            for old,cur in zip(tr,tr[1:]):
                g=terms(matrix(cur[:6])/98000.,cur[6]);de=matrix(np.array(p['total_strain'])/grid['steps']);ds=matrix(np.array(cur[:6])-np.array(old[:6]))/98000.
                trial=np.sum(g['n']*g['D'](de));fsig=np.sum(g['n']*ds);ic=max(np.sum(g['dtn']*ds),0)/g['size']
                branch='elastic' if trial<0 else ('softening' if g['h']<0 else ('IC_only' if fsig-ic<0 else ('AF_IC' if ic>0 else 'AF')))
                coverage[branch]+=1
            grids.append(dict(steps=grid['steps'],H_initial=hs[0],H_final=hs[-1],H_max_drift=max(abs(x-hs[0]) for x in hs),rho_min=min(v[6] for v in tr),rho_max=max(v[6] for v in tr),saved_endpoint_error=grid['scaled_endpoint_error']))
        paths.append(dict(name=p['name'],grids=grids,endpoint_branch_diagnostics=dict(coverage)))
    labs=json.loads(gzip.decompress((PACK/'laboratory-responses.json.gz').read_bytes()))
    laboratory=[]
    for i,r in enumerate(labs):
        tr=[p['state'] for p in r['points']];hs=[H(v) for v in tr]
        aux=[matrix(v[8:14]) for v in tr]
        aux_min=min(float(np.min(np.linalg.eigvalsh(a))) for a in aux)
        aux_error=max(float(np.max(abs(a@a-np.linalg.inv(matrix(v[:6]))/np.trace(np.linalg.inv(matrix(v[:6])))))) for a,v in zip(aux,tr))
        laboratory.append(dict(protocol=i,auxiliary_min_eigenvalue=aux_min,auxiliary_square_max_error=aux_error,H_initial=hs[0],H_final=hs[-1],H_max_drift=max(abs(x-hs[0]) for x in hs),rho_min=min(v[6] for v in tr),rho_max=max(v[6] for v in tr)))
    result=dict(algebra=checks,algebra_pass=all(x['pass_'] for x in checks),softening_negative_multiplier_witnesses=witnesses,finite_paths=paths,laboratory=laboratory,
      initialization_reference_examples=[dict(pressure=p,rho=r,e=e,H=H([p,p,p,0,0,0,r,e])) for p,r,e in [(98000,0,.83),(98000,.03,.8),(98000,.03,.83),(196000,0,.83)]])
    (HERE/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(algebra_pass=result['algebra_pass'],algebra_checks=len(checks),softening_witness_count=len(witnesses),first_witness=witnesses[:1],initialization_reference_examples=result['initialization_reference_examples'],laboratory=laboratory),indent=2))
    assert result['algebra_pass']
if __name__=='__main__':main()
