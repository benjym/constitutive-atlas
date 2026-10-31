#!/usr/bin/env python3
"""Independent algebra of the inspected author Figure1; no Atlas/author imports."""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json

def run():
    checks=[]
    def check(name,ok):
        if not ok: raise AssertionError(name)
        checks.append(name)
    # Work conjugacy and signed invariant inversion, exactly rational.
    for dv,ds,p,q in [(F(1,5),F(-2,7),F(13),F(-5)),(F(-3,4),F(2,9),F(17),F(11)),(F(0),F(0),F(1),F(0))]:
        d=[dv/3+ds,dv/3-ds/2,dv/3-ds/2]
        s=[p+2*q/3,p-q/3,p-q/3]
        check('trace-and-signed-rate-'+str(len(checks)),sum(d)==dv and F(2,3)*(d[0]-d[1])==ds)
        check('work-conjugacy-'+str(len(checks)),sum(a*b for a,b in zip(d,s))==p*dv+q*ds)
    with localcontext() as ctx:
        ctx.prec=80
        D=Decimal; K=D('13e9'); G=D('5e9'); phi=D('.423'); pe=D('100000')
        for ratio in ['-1','-.73','0','.73','1']:
            qe=pe*D(ratio)
            discr=1-K/(3*G)*(qe/pe)**2
            ev=(pe/(K*phi**6)*(1+discr.sqrt())).sqrt()
            es=qe/(3*G*phi**6*ev)
            rp=phi**6*(K*ev**2+3*G*es**2)/2
            rq=3*G*phi**6*ev*es
            check('positive-stable-root-q-over-p='+ratio,abs(rp-pe)<D('1e-65') and abs(rq-qe)<D('1e-65') and K*ev**2>=3*G*es**2)
        # Deliberately outside real elastic initialization; do not clip.
        check('outside-elastic-cone',1-K/(3*G)*D('2')**2<0)
        alpha=gamma=D('600000'); Gamma=D('.001'); T=D('.0001'); dv=D('6e-5'); ds=D('-2e-5')
        qe=D('-20000'); pv=2*alpha*T*dv/Gamma; qv=2*gamma*T*ds/Gamma; pt=T*T/Gamma
        P=pe+pv+pt; Q=qe+qv
        check('captured-total-stress-recovers-both-hold-rates',Gamma*(P-pe-pt)/(2*alpha*T)==dv and Gamma*(Q-qe)/(2*gamma*T)==ds)
        check('hold-rate-jacobian-positive-at-positive-T',4*alpha*gamma*T*T/(Gamma*Gamma)>0)
        check('hold-rate-jacobian-singular-at-zero-T',4*alpha*gamma*D(0)**2/(Gamma*Gamma)==0)
        check('Gamma-kPa-to-Pa',D(1)/1000==Gamma)
        p1=1000/D('.267')**10
        check('rounded-presets-remain-distinct',abs(p1-D('543000000'))>D('100000'))
    return {'version':'terracotta-figure1-algebra-v1','checks':len(checks),'failures':0,'passed':checks,'scope':'independent rational/80-digit decimal algebra; not journal verification, integration, author-code or compiled execution'}

if __name__=='__main__': print(json.dumps(run(),indent=2))
