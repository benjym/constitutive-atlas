"""Independent exact checks of source algebra; no Atlas or vendor imports."""
from fractions import Fraction as Q
from decimal import Decimal,localcontext
import json,sys
from pathlib import Path

def check():
    rows=[]
    def keep(name,values):rows.append(dict(check=name,status='passed',values=values))
    # Rational source envelope at a=1/2, mb=2,s=1,sci=100. Sampling
    # x=150 gives sqrt(1+2*x/100)=2, exact slope3/2 and intercept125.
    sci,mb,s,x=map(Q,[100,2,1,150]);a=Q(1,2);rad=Q(2)
    H=x+sci*rad;N=1+a*mb/rad;B=H-N*x
    assert (H,N,B)==(350,Q(3,2),125)
    assert N*x+B==H
    # Derivative follows implicit square identity (H-x)^2=sci^2+mb*sci*x.
    assert 2*(H-x)*(N-1)==mb*sci
    keep('exact tangent value and independently implicit derivative',dict(H=str(H),N=str(N),B=str(B)))
    for xp,rp in [(Q(0),Q(1)),(Q(400),Q(3))]:
        assert rp*rp==1+mb*xp/sci
        curved=xp+sci*rp;tangent=N*xp+B
        assert tangent-curved==25
    keep('finite tangent-envelope mismatch retained',{'trial_sampling_x':'150','residual_at_x0':'25','residual_at_x400':'25','meaning':'exact nonlinear return and frozen tangent return cannot be substituted at finite step'})
    K,G=Q(1000),Q(600);A1,A2=K+4*G/3,K-2*G/3;Np,Nps=Q(3),Q(2);p=[Q(500),Q(120),Q(50)];b=Q(100)
    F=p[0]-Np*p[2]-b;lam=F/((A1-A2*Nps)+(A1*Nps-A2)*Np)
    dep=[lam,Q(0),-lam*Nps]
    elastic=lambda e:[A1*e[i]+A2*sum(e[j] for j in range(3) if i!=j) for i in range(3)]
    Cdep=elastic(dep);final=[pi-ci for pi,ci in zip(p,Cdep)]
    assert final[0]-Np*final[2]-b==0 and lam>0
    # Independently apply negative-compression MC Eq14 then flip stress sign.
    t=[-v for v in p];tn=[t[0]+lam*(A1-A2*Nps),t[1]+lam*A2*(1-Nps),t[2]+lam*(-A1*Nps+A2)]
    assert [-v for v in tn]==final
    assert sum(dep)==lam*(1-Nps)<0
    keep('MC sign/order/elastic-flow conversion',dict(multiplier=str(lam),plastic_volume=str(sum(dep)),final=[str(v) for v in final]))
    # A deviatoric projection cannot by itself represent the dilatant total flow.
    mean=sum(dep)/3;dev=[v-mean for v in dep];assert sum(dev)==0 and sum(dep)!=0
    keep('total versus deviatoric increment diagnostic',{'total_volume':str(sum(dep)),'deviatoric_volume':'0','meaning':'not a correction to printed HB Eq12; its tensor meaning must be resolved'})
    ks2=sum((v-mean)**2 for v in dep)/2
    assert ks2==lam**2*(1+Nps+Nps*Nps)/3
    keep('SSoft shear measure independent invariant reduction',{'kappa_s_squared':str(ks2),'scope':'single homogeneous principal plastic increment; zone averaging not replaced'})
    # Tensor stress/strain sign conversion preserves work exactly.
    assert sum(pi*ei for pi,ei in zip(p,dep))==sum((-pi)*(-ei) for pi,ei in zip(p,dep))
    keep('work conjugacy under simultaneous sign conversion',{'work':str(sum(pi*ei for pi,ei in zip(p,dep)))})
    # Tension bound at zero confinement: N=2,B=100,c/tan(phi)=B/(N-1).
    N0=1+a*mb;sci0=sci;cap=s*sci/mb;apex=sci0/(N0-1)
    assert (N0,cap,apex,min(Q(70),cap,apex))==(2,50,100,50)
    keep('zero-confinement tangent and tension cap',dict(N=str(N0),intrinsic_cap=str(cap),apex_cap=str(apex),capped_tension='50'))
    assert Q(2)/Q(2)==1 and Q(2)/Q(4)==Q(1,2)
    keep('calibration geometry scaling',{'Lc_m':'2','Vz8m3_factor':'1','Vz64m3_factor':'1/2','scope':'requires host geometry, not a material constant'})
    with localcontext() as ctx:
        ctx.prec=60;D=Decimal;gsi=D(100);disturb=D(0);mi=D(12)
        mb0=mi*((gsi-100)/(28-14*disturb)).exp();s0=((gsi-100)/(9-3*disturb)).exp();a0=D('.5')+((-gsi/15).exp()-(-D(20)/3).exp())/6
        assert mb0==mi and s0==1 and a0==D('.5')
    keep('GSI100 intact limiting identity',{'mb':'mi','s':'1','a':'1/2'})
    return {'kind':'source-algebra-diagnostics-not-candidate-qualification','checks':rows,'groups':len(rows),'material_calls':0,'scope':'constant scalar tangent and smooth single-plane checks only; no full HB update, curves, softening, rotation, branch, derivative, or vendor equivalence claim'}
if __name__=='__main__':
    result=check();text=json.dumps(result,indent=2)+'\n'
    if len(sys.argv)>1:Path(sys.argv[1]).write_text(text)
    else:print(text,end='')
