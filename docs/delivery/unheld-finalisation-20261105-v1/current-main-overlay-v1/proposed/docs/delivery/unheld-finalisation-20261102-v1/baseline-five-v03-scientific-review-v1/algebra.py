"""Independent source algebra only: no atlas/model/engine imports or execution."""
import json, math
from pathlib import Path
checks=[]
def close(a,b,label,rel=1e-12,abs_=1e-12):
 assert math.isclose(a,b,rel_tol=rel,abs_tol=abs_),(label,a,b)
 checks.append(label)
def norm(x):return math.sqrt(sum(a*a for a in x))
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def tr(a):return sum(a[:3])
def dev(a):return [x-tr(a)/3 if i<3 else x for i,x in enumerate(a)]
I=[1,1,1,0,0,0]
# Independent Lame identities and Cartesian/Mandel shear norm.
for nu in [-.99,-.2,.25,.49,.499]:
 E=3e7;G=E/(2*(1+nu));K=E/(3*(1-2*nu));lam=E*nu/((1+nu)*(1-2*nu))
 close(K,lam+2*G/3,f'elastic Lame identity nu={nu}')
 assert K>0 and G>0;checks.append(f'elastic energy positivity nu={nu}')
 de=[.001,-.0002,.0001,math.sqrt(2)*.0003,0,0]
 for i in range(6):
  a=K*tr(de)*I[i]+2*G*dev(de)[i];b=lam*tr(de)*I[i]+2*G*de[i]
  close(a,b,f'elastic isotropic stress component {i} nu={nu}',abs_=1e-8)
close(dot([1,2,3,math.sqrt(2)*4,math.sqrt(2)*5,math.sqrt(2)*6],[1,2,3,math.sqrt(2)*4,math.sqrt(2)*5,math.sqrt(2)*6]),1+4+9+2*(16+25+36),'Mandel Frobenius contraction')
# OGS void bookkeeping is an Atlas addition. It composes exactly by volume.
v0=1.7;a=.001;b=-.0003
close(v0*math.exp(-a)*math.exp(-b),v0*math.exp(-(a+b)),'exponential total volume composition')
assert v0*math.exp(-a)<v0;checks.append('compression decreases void ratio')
# DP source convention conversion from OpenSees sqrt(s:s)+rho tr(T)-sqrt(2/3)*sy.
rho=.2;rhobar=.04;sy=10000;p=80000;q=40000
M=3*math.sqrt(1.5)*rho;Md=3*math.sqrt(1.5)*rhobar
close(math.sqrt(1.5)*(q/math.sqrt(1.5)-3*rho*p-math.sqrt(2/3)*sy),q-M*p-sy,'DP source yield normalization')
gO=.002;gA=math.sqrt(2/3)*gO;K=2e7;G=1.2e7
close(3*K*rhobar*gO,K*Md*gA,'DP source volumetric multiplier normalization')
close(2*G*gO*math.sqrt(1.5),3*G*gA,'DP source deviator multiplier normalization')
# Independent scalar returns: smooth, apex and elastic. Complementarity separate.
M=1.2;Md=.2;c=10000
for pt,qt,kind in [(1e5,3e5,'smooth'),(-2e5,1000,'apex'),(1e5,1000,'elastic')]:
 ft=qt-M*pt-c
 if ft<=0:g=0;qn=qt;pn=pt
 else:
  gs=ft/(3*G+M*K*Md)
  g=gs if gs<=qt/(3*G) else (-c/M-pt)/(K*Md)
  qn=max(qt-3*G*g,0);pn=pt+K*Md*g
 f=qn-M*pn-c
 assert g>=0 and f<1e-7;checks.append(f'DP {kind} feasibility')
 close(g*f,0,f'DP {kind} complementarity',abs_=1e-8)
 close(math.sqrt(g*g+(f/1e5)**2)-g+f/1e5,0,f'DP {kind} Fischer Burmeister',abs_=1e-12)
 if kind=='apex':assert g>=qt/(3*G);checks.append('DP apex subgradient threshold')
assert -2e5 < -c/M;checks.append('DP Md0 beyond tensile apex unsolvable hydrostatic volume')
# MCC: exact critical point, printed conflict, associated derivative and log hardening.
M=1.2;pc=2e5;p=pc/2;q=M*pc/2
close(q*q+M*M*p*(p-pc),0,'MCC M squared critical ellipse witness',abs_=1e-5)
assert abs(q*q+M*p*(p-pc))>1e6;checks.append('MCC printed single M conflict remains')
close(M*M*(2*p-pc),0,'MCC critical associated plastic volume zero')
e=.7;kappa=.04;lam=.2;gamma=.001
for p in [60000,140000]:
 pv=gamma*M*M*(2*p-pc)/pc;pc1=pc*math.exp((1+e)*pv/(lam-kappa))
 close(math.log(pc1/pc),(1+e)*pv/(lam-kappa),f'MCC BE log pc normalization p={p}')
 assert (pc1>pc)==(p>pc/2);checks.append(f'MCC wet harden dry soften p={p}')
phi=1/3;rate=.01
close((1+phi)*rate,1/75,'MCC printed Eq7 porosity witness')
close((1-phi)*rate,1/150,'MCC Eqs8-9 porosity witness')
# VW96 isotropic F, sign transformation and degree-one positive homogeneity.
close(math.sqrt((2-0)/(2+0))-0,1,'VW96 exact isotropic F')
hat=[.45,.33,.22,.01,-.02,.03];D=[.001,-.0002,.0001,.0004,-.0001,.0002];a=3;fac=1e7;fd=.8;F=.9
L=lambda x:[fac*(F*F*x[i]+a*a*dot(hat,x)*hat[i]) for i in range(6)]
N=[fac*fd*a*F*(hat[i]+dev(hat)[i]) for i in range(6)]
A=[L(D)[i]-N[i]*norm(D) for i in range(6)]
Ts=[L([-x for x in D])[i]+N[i]*norm(D) for i in range(6)]
for i in range(6):close(A[i],-Ts[i],f'VW96 double sign reversal component{i}')
for s in [.25,3]:
 for i in range(6):close(L([s*x for x in D])[i]-N[i]*norm([s*x for x in D]),s*A[i],f'VW96 positive path homogeneity {s} component{i}',abs_=1e-8)
# NH97 Eq14/15 limiting branches for a general linear operator and N.
mR=5;mT=2;eta=[1,0,0,0,0,0];Ne=[-x for x in N]
def overlay(r,D):
 proj=dot(eta,D);rc=r**6;base=rc*mT+(1-rc)*mR
 return [base*L(D)[i]+rc*((1-mT)*L(eta)[i]+Ne[i])*proj if proj>0 else base*L(D)[i]+rc*(mR-mT)*L(eta)[i]*proj for i in range(6)]
for D,label,expected in [(eta,'monotonic',[L(eta)[i]+Ne[i] for i in range(6)]),([-x for x in eta],'reverse',[mR*x for x in L([-x for x in eta])]),([0,1,0,0,0,0],'neutral',[mT*x for x in L([0,1,0,0,0,0])])]:
 for i in range(6):close(overlay(1,D)[i],expected[i],f'NH97 saturated {label} component{i}',abs_=1e-8)
for i in range(6):close(overlay(0,D)[i],mR*L(D)[i],f'NH97 zero history stiffness component{i}',abs_=1e-8)
for r in [0,.3,1]:
 dh=[eta[i]-r**.5*eta[i]*dot(eta,eta) for i in range(6)]
 close(dot(eta,dh),1-r**.5,f'NH97 proportional history evolution rho={r}')
assert min(1.005,1)==1 and 1.005>1;checks.append('NH97 capped numerical overshoot distinct from physical rho<=1')
result={'kind':'independent source-derived algebra; no atlas or material model execution','checks':len(checks),'passed':True,'labels':checks,'scientific_admission':False,'compiled_calls':0}
p=Path(__file__).with_name('algebra-results.json');p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='labels'}))
