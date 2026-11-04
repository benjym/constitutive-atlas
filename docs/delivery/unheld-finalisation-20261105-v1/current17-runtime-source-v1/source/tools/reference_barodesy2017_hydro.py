"""Own stdlib Decimal zero-spin body-law local hydro derivative reference.
No Atlas or existing rate/operator implementation imports. Not full-domain code.
"""
import math
from decimal import Decimal,localcontext
P={'phi_c':math.radians(22.6),'N':1.375,'lambda_star':.11,'kappa_star':.016}
def dec(x):return x if isinstance(x,Decimal)else Decimal.from_float(float(x))
def sin(x):
 term=x;out=x;n=1
 while True:
  term=-term*x*x/((2*n)*(2*n+1));old=out;out+=term
  if out==old:return out
  n+=1
  if n>1000:raise ValueError('sin convergence')
def constants(p):
 phi,N,la,ka=(dec(p[k])for k in('phi_c','N','lambda_star','kappa_star'));rt2=Decimal(2).sqrt();rt3=Decimal(3).sqrt();sp=sin(phi)
 c2=-Decimal('1.5')*(rt2+1);c1=(1-sp)/(2*c2*c2*sp);c5=(1+sp)/(1-sp);t=c5*la;A=(t*Decimal(2).ln()).exp();B=(t*(Decimal(1)/500).ln()).exp();c3=rt3*(1/ka-1/la)/(A+B-2);c6=1/(2*(-rt3/(c3*ka)+A-1))
 return dict(c1=c1,c2=c2,c3=c3,c5=c5,c6=c6,la=la,ka=ka,N=N,A=A)
def norm(v):return sum(x*x for x in v).sqrt()
def cart(v):
 x,y,z,xy,yz,xz=v;r=Decimal(2).sqrt();return [[x,xy/r,xz/r],[xy/r,y,yz/r],[xz/r,yz/r,z]]
def matmul(a,b):return [[sum(a[i][k]*b[k][j]for k in range(3))for j in range(3)]for i in range(3)]
def normalized_exp(v):
 a=cart(v);I=[[Decimal(int(i==j))for j in range(3)]for i in range(3)];n=max(sum(abs(x)for x in row)for row in a);s=0
 while n>Decimal('.125'):n/=2;s+=1
 a=[[x/(2**s)for x in row]for row in a];out=[row[:]for row in I];term=[row[:]for row in I]
 for k in range(1,2000):
  term=[[x/k for x in row]for row in matmul(term,a)];fresh=[[out[i][j]+term[i][j]for j in range(3)]for i in range(3)]
  if fresh==out:break
  out=fresh
 else:raise ValueError('exponential convergence')
 for _ in range(s):out=matmul(out,out)
 n=sum(x*x for row in out for x in row).sqrt();r=Decimal(2).sqrt();return [out[0][0]/n,out[1][1]/n,out[2][2]/n,r*out[0][1]/n,r*out[1][2]/n,r*out[0][2]/n]
def evaluate(sig,e,E,parameters=P,precision=100):
 with localcontext()as ctx:
  ctx.prec=precision;sig=list(map(dec,sig));E=list(map(dec,E));e=dec(e);c=constants(parameters);r=norm(E);rt3=Decimal(3).sqrt();p=sum(sig[:3])/3
  if not(r>0 and p>0 and e>=0):raise ValueError('local positive loading/pressure/void support')
  mean=sum(E[:3])/3;Z=[E[i]-(mean if i<3 else 0)for i in range(6)];z=norm(Z);delta=-3*mean/r;q=z/r
  if z==0:Pdir=[1/rt3]*3+[Decimal(0)]*3
  else:
   m=Decimal('1.5').sqrt()*3*mean/z;x=c['c1']*(m-c['c2'])**2
   if x<=0:raise ValueError('K0')
   a=-(1+1/x).ln()/(Decimal('1.5').sqrt()*q)
   # Shift away exact spherical exponent: normalized exp ignores this term.
   Pdir=normalized_exp([-a*v/r for v in Z])
  Lam=(c['la']+c['ka'])/2-(c['la']-c['ka'])*delta/(2*rt3);beta=-1/(c['c3']*Lam)+(c['A']-1)/rt3;f=c['c6']*beta*delta-Decimal('.5');density=(1+e)*(-c['N']+c['la']*(2*p/1000).ln()).exp();d5=(c['c5']*density.ln()).exp();g=(1-c['c6'])*beta*delta+d5-Decimal('.5');ns=norm(sig)
  F=[c['c3']*r*(f*ns*Pdir[i]+g*sig[i])for i in range(6)]+[-(1+e)*sum(E[:3])]
  return {'rate':F,'P':Pdir,'delta':delta,'r':r,'Z':Z,'z':z,'derived':c|{'f':f,'g':g,'d5':d5,'p':p,'ns':ns}}
def hydro_jacobian(sig,e,s,parameters=P,precision=100):
 with localcontext()as ctx:
  ctx.prec=precision;sig=list(map(dec,sig));e=dec(e);s=dec(s);out=evaluate(sig,e,[s]*3+[0]*3,parameters,precision);d=out['derived'];r=out['r'];P0=out['P'];j=[[Decimal(0)for _ in range(13)]for _ in range(7)]
  for i in range(6):
   for k in range(6):j[i][k]=d['c3']*r*(d['f']*sig[k]/d['ns']*P0[i]+d['g']*int(i==k)+sig[i]*d['d5']*d['c5']*d['la']*(1 if k<3 else 0)/(3*d['p']))
   j[i][6]=d['c3']*r*sig[i]*d['d5']*d['c5']/(1+e)
   for k in range(7,10):j[i][k]=out['rate'][i]/(3*s)
  j[6][6]=-3*s
  for k in range(7,10):j[6][k]=-(1+e)
  return j

SOILS={
 'London':dict(phi_c=math.radians(22.6),N=1.375,lambda_star=.11,kappa_star=.016),
 'Dresden':dict(phi_c=math.radians(35),N=.622,lambda_star=.038,kappa_star=.008),
 'Weald':dict(phi_c=math.radians(24),N=.8,lambda_star=.059,kappa_star=.018)}
VERSION='barodesy2017-exact-hydro-decimal-reference-v1'
def exact_hydro(sig,e,loading,parameters,precision=160):
 """Only exact nonzero hydro; no arbitrary near-hydro numerical claim."""
 def finite(x):
  try:return type(x)in(int,float)and math.isfinite(x)
  except OverflowError:return False
 if type(sig)is not list or len(sig)!=6 or not all(finite(x)for x in sig)or not finite(e):raise ValueError('finite six stress/void')
 if type(loading)is not list or len(loading)!=6 or not all(finite(x)for x in loading):raise ValueError('finite six loading')
 if not(loading[0]==loading[1]==loading[2]and loading[0]!=0 and loading[3:]==[0,0,0]):raise ValueError('exact nonzero hydro only')
 if type(parameters)is not dict or set(parameters)!={'phi_c','N','lambda_star','kappa_star'}or not all(finite(x)for x in parameters.values()):raise ValueError('four finite soil parameters')
 if type(precision)is not int or not 80<=precision<=300:raise ValueError('precision80..300')
 # This local reference's comparisons use explicitly interior SPD stress.
 with localcontext()as ctx:
  ctx.prec=precision;a=cart(list(map(dec,sig)))
  det=a[0][0]*(a[1][1]*a[2][2]-a[1][2]**2)-a[0][1]*(a[0][1]*a[2][2]-a[0][2]*a[1][2])+a[0][2]*(a[0][1]*a[1][2]-a[0][2]*a[1][1])
  if not(a[0][0]>0 and a[0][0]*a[1][1]-a[0][1]**2>0 and det>0 and e>=0):raise ValueError('local SPD/void support')
 out=evaluate(sig,e,loading,parameters,precision)
 return {'values':out['rate'],'jacobian':hydro_jacobian(sig,e,loading[0],parameters,precision)}
