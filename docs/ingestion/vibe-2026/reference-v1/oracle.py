"""Independent Cartesian Decimal oracle for the published explicit Appendix A VIBE law.
No production expressions/imports, author code or compiled material calls.
"""
from decimal import Decimal as Q, localcontext
from pathlib import Path
import json
D=Q
ZERO=D(0);ONE=D(1)
PI=D('3.14159265358979323846264338327950288419716939937510582097494459230781640628620899862803482534211706798214808651')
class DomainError(ValueError):pass
def require(ok,why):
 if not ok:raise DomainError(why)
def power(x,y):return (D(y)*x.ln()).exp() if x else ZERO
def sin(x):
 term=x;s=x;k=1
 while True:
  term=-term*x*x/D((2*k)*(2*k+1));n=s+term
  if n==s:return s
  s=n;k+=1
def cos(x):
 term=ONE;s=ONE;k=1
 while True:
  term=-term*x*x/D((2*k-1)*(2*k));n=s+term
  if n==s:return s
  s=n;k+=1
def eye():return [[D(int(i==j)) for j in range(3)] for i in range(3)]
def add(A,B):return [[A[i][j]+B[i][j] for j in range(3)] for i in range(3)]
def scale(c,A):return [[c*x for x in row] for row in A]
def trace(A):return sum(A[i][i] for i in range(3))
def dot(A,B):return sum(A[i][j]*B[i][j] for i in range(3) for j in range(3))
def matmul(A,B):return [[sum(A[i][k]*B[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def det(A):return sum(A[0][j]*(A[1][(j+1)%3]*A[2][(j+2)%3]-A[1][(j+2)%3]*A[2][(j+1)%3]) for j in range(3))
def tensor(v):
 rt=D(2).sqrt();a,b,c,d,e,f=v
 return [[a,d/rt,f/rt],[d/rt,b,e/rt],[f/rt,e/rt,c]]
def mandel(A):
 rt=D(2).sqrt();return [A[0][0],A[1][1],A[2][2],rt*A[0][1],rt*A[1][2],rt*A[0][2]]
def solve(A,b):
 n=len(b);R=[list(A[i])+[b[i]] for i in range(n)]
 for k in range(n):
  pivot=max(range(k,n),key=lambda i:abs(R[i][k]));R[k],R[pivot]=R[pivot],R[k]
  require(R[k][k]!=0,'singular direct B solve')
  v=R[k][k];R[k]=[x/v for x in R[k]]
  for i in range(n):
   if i!=k:
    v=R[i][k];R[i]=[R[i][j]-v*R[k][j] for j in range(n+1)]
 return [R[i][-1] for i in range(n)]
def params(branch=False):
 raw=json.loads((Path(__file__).parent.parent/'source-v2/parameters.json').read_text(),parse_float=str,parse_int=str)
 p={k:D(str(v['value'])) for group in ['material_parameters','hidden_parameters'] for k,v in raw[group].items()}
 if branch:p.update(ns=D('.02'),ls=D('.005'),lT=D('.01'))
 return p

def algebra(y,s,T,sd,p):
 require(all(x.is_finite() for x in y+[s,T,sd]),'nonfinite state/control')
 e=y[6];ah=y[7];require(s>0,'suction must be strictly positive');require(T>0,'temperature must be positive');require(0<=ah<=1,'scanning state outside [0,1]')
 I=eye();sig=scale(-ONE,tensor(y[:6]));pm=-trace(sig)/3+s
 require(pm>0,'micro pressure must be positive')
 fac=p['a']+p['b']*T;facref=p['a']+p['b']*p['Tr'];require(fac>0 and facref>0,'thermal multiplier nonpositive')
 em=p['em0']*(-power(pm/p['hms'],p['nm'])).exp()*fac/facref
 require(e>em>0,'require e>em>0');eM=(e-em)/(1+em)
 sen=p['se0']*p['eM0']/eM*fac/facref;se=sen*(p['ae']+ah-p['ae']*ah)
 u=power(se/s,p['lp']);tail=(-u).exp();S=1-tail;require(0<S<1,'retention interior lost')
 sigM=add(sig,scale(-S*s,I));pM=-trace(sigM)/3;require(pM>0,'macro pressure nonpositive')
 f=ah if sd>0 else 1-ah if sd<0 else ZERO;r=D('.1')+D('.9')*f**3
 DsS=-r/s*tail*p['lp']*u;Dse=tail*p['lp']*u/se;Demse=-se/eM;DTse=se*p['b']/fac
 Dp=-em*p['nm']/pm*power(pm/p['hms'],p['nm']);DTm=em*p['b']/fac
 Nst=p['N']-p['ns']/p['lp']*S.ln()+p['nT']*(T/p['Tr']).ln();lam=p['lambda']-p['ls']/p['lp']*S.ln()+p['lT']*(T/p['Tr']).ln();require(lam>0,'lambda nonpositive')
 Aact=Dse*se/(p['lp']*S)*(p['ns']-p['ls']*(pM/p['pr']).ln())
 aden=eM*(1+em)-Aact*(1+e);require(aden!=0,'active slope denominator zero')
 lact=(eM*(1+em)*lam+Aact*Dp*pM*(1+eM))/aden;require(lact>0,'active slope nonpositive')
 pe=p['pr']*((Nst-(1+e).ln())/lam).exp();OI=pe/pM
 hydro=(sigM[0][0]==sigM[1][1]==sigM[2][2] and sigM[0][1]==sigM[0][2]==sigM[1][2]==0)
 if hydro:Fm=ZERO;shat=[[ZERO for _ in range(3)] for _ in range(3)];c3=ZERO
 else:
  I1=trace(sigM);I2=(dot(sigM,sigM)-I1**2)/2;I3=det(sigM);require(I3+I1*I2!=0,'invariant denominator zero');Fm=(9*I3+I1*I2)/(I3+I1*I2)
  shat=add(scale(1/I1,sigM),scale(-ONE/3,I));ss=dot(shat,shat);c3=-D(6).sqrt()*trace(matmul(matmul(shat,shat),shat))/(ss*ss.sqrt())
 require(0<=Fm<1,'Fm outside [0,1)')
 phi=p['phi']*PI/180;sp=sin(phi);omega=-(cos(phi)**2).ln()/p['Oc'].ln()+D('.3')*(Fm-sp**2);require(omega!=0,'omega zero')
 OA=OI*power(1-Fm,1/omega);require(OA>=1,'state outside selected ASBS domain')
 eA=((1+e).ln()+lam*OA.ln()).exp()-1;require(eA!=em,'density denominator zero');re=(e-em)/(eA-em);fm=1-power(re,p['m'])
 fs=3*pM/2*(lact+p['kappa'])/(lact*p['kappa'])*(1-2*p['nu'])/(1+p['nu']);Iv=D('.004')+p['IvT']*(T-p['Tr'])**3*D('1e-8');require(Iv>0,'Iv nonpositive')
 ci=((lact+p['kappa'])*(power(OI,p['alpha_f'])-1)+2*p['kappa'])/((lact+p['kappa'])*(power(OI,p['alpha_f'])-power(OA,p['alpha_f']))+2*p['kappa']*power(OA,p['alpha_f']))
 DsP=-pe*DsS/(p['lp']*S*lam)*(p['ns']-p['ls']*(pe/p['pr']).ln());DTP=pe/(T*lam)*(p['nT']-p['lT']*(pe/p['pr']).ln())
 # A12: only the product involving the undefined hydrostatic Lode angle is extended.
 coef=(D(2)/3-(c3+1)/4*power(Fm,D('.25')))*(power(Fm,p['xi']/2)-power(sp,p['xi']))/(1-power(sp,p['xi']))
 dA=add(scale(-ONE,shat),scale(coef,I));dn=dot(dA,dA).sqrt();require(dn>0,'direction norm zero');direction=scale(1/dn,dA)
 bB=-Dse*Demse*s*(1+eM)*Dp/(3*(1+em));cB=-fs*fm*Dp/(9*(1+em));dB=p['nu']/(1-2*p['nu'])
 require(1+3*(bB+cB+3*cB*dB)!=0,'B singular')
 return locals()

def rate(y,s,T,sd,Td,mech,p,observables=False):
 q=algebra(y,s,T,sd,p);I=q['I'];sigM=q['sigM'];fs=q['fs'];fm=q['fm'];em=q['em'];eM=q['eM'];Dp=q['Dp'];NE=None
 def L(X):return add(X,scale(p['nu']/(1-2*p['nu'])*trace(X),I))
 # Build B from its original fourth-order composition (body Eq42), then direct 6x6 solve.
 def B(X):
  JX=scale(trace(X),I)
  return add(add(X,scale(q['bB'],JX)),scale(q['cB'],L(JX)))
 columns=[]
 for k in range(6):
  v=[ZERO]*6;v[k]=ONE;columns.append(mandel(B(tensor(v))))
 Bmatrix=[[columns[j][i] for j in range(6)] for i in range(6)]
 def A(X):return add(scale(fs,L(X)),scale(trace(X)/q['lact'],sigM))
 Ad=A(q['direction']);NE=scale((p['vf']-1)*power(q['OA'],-p['alpha_f']),Ad)
 NV=scale(-p['vf']*power(q['OA'],-1/q['Iv']),Ad)
 def Hprime(Pdot,control):
  sign=ONE if Pdot<0 else -ONE if Pdot>0 else ZERO
  H=ONE if -Pdot*control>=0 else ZERO
  return scale(q['ci']*Pdot/q['pe']*sign*H,sigM)
 Hls=add(scale(-Dp*fs*fm/(3*(1+em)),L(I)),scale(q['DsS']*s+q['S']-Dp*q['Dse']*q['Demse']*s*(1+eM)/(1+em),I))
 Hns=add(scale(power(q['OA'],-p['m']),Hprime(q['DsP'],sd)),scale(-D(3).sqrt()*p['frm']*fm/3*abs(Dp)/(1+em),NE))
 Hlt=add(scale(-p['alpha_s']*fs*fm/3,L(I)),scale(q['Dse']*s*(q['DTse']-q['Demse']*q['DTm']*(1+eM)/(1+em)),I))
 Hnt=add(scale(power(q['OA'],-p['m']),Hprime(q['DTP'],Td)),scale(-D(3).sqrt()*p['frm']*fm/3*abs(p['alpha_s']),NE))
 strain=scale(-ONE,tensor(mech));LEd=add(scale(fs,L(strain)),scale(q['Dse']*q['Demse']*s*(1+eM)*trace(strain),I))
 rhs=LEd
 for coeff,X in [(dot(strain,strain).sqrt(),NE),(p['Dr'],NV),(sd,Hls),(abs(sd),Hns),(Td,Hlt),(abs(Td),Hnt)]:rhs=add(rhs,scale(coeff,X))
 out=[-x for x in solve(Bmatrix,mandel(rhs))]+[(1+y[6])*trace(strain),q['se']/q['sen']*(1-q['r'])/(s*(1-p['ae']))*sd]
 require(all(x.is_finite() for x in out),'nonfinite rate')
 if observables:return out,{k:q[k] for k in ['em','eM','S','Sr','OA','re','Fm','DsP','DTP'] if k in q}|{'Sr':q['S']+q['em']/y[6]*(1-q['S'])}
 return out

def initial(p,scan=D('.35'),dry=False,anisotropic=False):
 e=D('.725');s=D(100000000) if dry else D(10000000);T=D(294)
 if dry:net=D(1000);scan=ZERO
 else:
  lo=D(1);hi=D(30000000);target=D('1.005')
  # Only initialization root search uses unrestricted OA calculation via choosing a temporary target-neutral algebra route.
  # Compute source hydrostatic OI directly; no stress-rate evaluations are used in this bisection.
  def oi(net):
   pm=net+s;em=p['em0']*(-power(pm/p['hms'],p['nm'])).exp();eM=(e-em)/(1+em);se=p['se0']*p['eM0']/eM*(p['ae']+scan-p['ae']*scan)
   S=1-(-power(se/s,p['lp'])).exp();lam=p['lambda']-p['ls']/p['lp']*S.ln();Nst=p['N']-p['ns']/p['lp']*S.ln();pe=p['pr']*((Nst-(1+e).ln())/lam).exp();return pe/(net+S*s)
  require(oi(lo)>target>oi(hi),'initial root bracket missing')
  for _ in range(400):
   mid=(lo+hi)/2
   if oi(mid)>target:lo=mid
   else:hi=mid
  net=(lo+hi)/2
 y=[net,net,net,ZERO,ZERO,ZERO,e,scan]
 if anisotropic:y=[a+D(b) for a,b in zip(y,[2000,-1000,-1000,3000,-2000,1000,0,0])]
 return y,s,T

def stringify(v):
 if isinstance(v,D):return str(v)
 if isinstance(v,dict):return {k:stringify(x) for k,x in v.items()}
 if isinstance(v,list):return [stringify(x) for x in v]
 return v
