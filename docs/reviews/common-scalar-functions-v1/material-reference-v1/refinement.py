"""Independent scalar quadratic midpoint recurrence versus source hyperbola.
No Atlas imports. Constant confinement, no material backend observations.
"""
from decimal import Decimal as Q,localcontext
from pathlib import Path
import json
from reference import q,sin
B=Path(__file__).resolve().parent

def calculate(p,eps,N,precision):
    with localcontext() as c:
        c.prec=precision;c0=Q(100000);sp=sin(q(p['phi']));F=2*c0*sp/(1-sp);Ei=q(p['K'])*q(p['pa'])*(c0/q(p['pa']))**q(p['n']);b=q(p['Rf'])/F
        de=float(eps/N);dt=q(de);x=Q(1)
        for _ in range(N):
            y=2*x/(1+(1+2*b*Ei*dt*x).sqrt());x=2*y-x
        D=(1-x)/b;exact=Ei*q(eps)/(1+b*Ei*q(eps));return D,exact,F

def build():
    refs=json.loads((B/'references.json').read_text());params={label:next(x['parameters'] for x in refs['cases'] if x['id'].startswith(label)) for label in ('dense','loose')};rows=[]
    for label,p in params.items():
        for eps in (.001,.003,.005):
            group=[]
            for N in (16,32,64,128):
                r1=calculate(p,eps,N,100);r2=calculate(p,eps,N,160);assert max(abs(x-y) for x,y in zip(r1,r2))<Q('1e-70')
                D,exact,F=r2;error=abs(D-exact)/max(F,Q(100000));de=eps/N
                group.append(dict(id=f'{label}-hyperbola-{eps}-{N}',parameters=p,initial=[100000.]*3+[0.]*4,de=[de,-p['nu']*de,-p['nu']*de,0.,0.,0.],steps=N,expected_D=str(D),hyperbola_D=str(exact),F=str(F),normalized_error=str(error)))
            assert Q(group[-1]['normalized_error'])<=Q('1e-3')
            assert Q(group[-2]['normalized_error'])/Q(group[-1]['normalized_error'])>=Q('1.5')
            rows+=group
    return dict(identity='duncan-source-hyperbola-refinement-v1',rows=rows,pass_=True,method='closed positive quadratic root for midpoint primary law; compare source Eq4 continuous hyperbola; strain rounds to exact binary64 per partition')
if __name__=='__main__':
    out=build();(B/'refinement-references.json').write_text(json.dumps(out,indent=2)+'\n');print('24 refinement references pass convergence and source budgets')
