"""Independent instantaneous Cartesian body-law research oracle; stdlib only.

Medicus/Fellin DOI10.1007/s11440-016-0458-4, body Eqs1–10 (not App41).
Zero spin, incompressible grains; no integration or author-code equivalence.
"""
from decimal import Decimal, localcontext
import math

VERSION='barodesy2017-body-cartesian-decimal-v1'
SOILS={
 'London':dict(phi_c=math.radians(22.6),N=1.375,lambda_star=.11,kappa_star=.016),
 'Dresden':dict(phi_c=math.radians(35),N=.622,lambda_star=.038,kappa_star=.008),
 'Weald':dict(phi_c=math.radians(24),N=.8,lambda_star=.059,kappa_star=.018)}
class UnsupportedDomain(ValueError):pass

def number(x):
 try:return type(x) in (int,float) and math.isfinite(x)
 except OverflowError:return False
def vector(v):
 if not isinstance(v,(list,tuple))or len(v)!=6 or not all(number(x) for x in v):raise UnsupportedDomain('six finite real Mandel components required')
 return [float(x)for x in v]
def cart(v):
 x,y,z,u,v,w=vector(v);s=math.sqrt(2)
 return [[x,u/s,w/s],[u/s,y,v/s],[w/s,v/s,z]]
def mandel(a):
 s=math.sqrt(2);return [a[0][0],a[1][1],a[2][2],s*(a[0][1]+a[1][0])/2,s*(a[1][2]+a[2][1])/2,s*(a[0][2]+a[2][0])/2]
def rotate(v,q):
 a=cart(v);return mandel([[sum(q[i][k]*a[k][l]*q[j][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)])
def decimal_exponential(v,precision=100):
 """Actual binary64 Mandel input; adaptive Decimal matrix power series.

 Scale Cartesian infinity norm to<=1/8, stop after3tiny consecutive terms,
 then square. No production fixed-degree polynomial/DSL/kernel imports.
 """
 v=vector(v)
 if type(precision)is not int or not 60<=precision<=300:raise ValueError('precision60..300 required')
 with localcontext()as ctx:
  ctx.prec=precision;d=[Decimal.from_float(x)for x in v];rt2=Decimal(2).sqrt()
  if sum(x*x for x in d)>Decimal(4096):raise UnsupportedDomain('operator support: exact input Frobenius exceeds64')
  x,y,z,u,vv,w=d;b=[[x,u/rt2,w/rt2],[u/rt2,y,vv/rt2],[w/rt2,vv/rt2,z]]
  def mul(a,b):return [[sum((a[i][k]*b[k][j]for k in range(3)),Decimal(0))for j in range(3)]for i in range(3)]
  squares=0
  while max(sum(abs(x)for x in row)for row in b)>Decimal(1)/8:
   b=[[x/2 for x in row]for row in b];squares+=1
  term=[[Decimal(i==j)for j in range(3)]for i in range(3)];total=[r[:]for r in term]
  tiny=Decimal(10)**(-precision+20);count=0
  for k in range(1,4097):
   term=[[x/k for x in row]for row in mul(term,b)]
   total=[[total[i][j]+term[i][j]for j in range(3)]for i in range(3)]
   count=count+1 if max(abs(x)for row in term for x in row)<tiny else 0
   if count==3:break
  else:raise UnsupportedDomain('Decimal exponential convergence budget')
  for _ in range(squares):total=mul(total,total)
  out=[total[0][0],total[1][1],total[2][2],rt2*(total[0][1]+total[1][0])/2,rt2*(total[1][2]+total[2][1])/2,rt2*(total[0][2]+total[2][0])/2]
  n=sum(x*x for x in out).sqrt()
  return dict(normalized=[float(x/n)for x in out],decimal_normalized=[str(+(x/n))for x in out],squares=squares,terms=k,precision=precision)

def constants(parameters):
 if not isinstance(parameters,dict)or set(parameters)!={'phi_c','N','lambda_star','kappa_star'}or not all(number(x)for x in parameters.values()):raise UnsupportedDomain('exact four finite parameters required')
 phi,N,la,ka=[parameters[n]for n in ('phi_c','N','lambda_star','kappa_star')]
 if not 0<phi<math.pi/2 or not 0<ka<la:raise UnsupportedDomain('research parameter support:0<phi<pi/2,lambda>kappa>0')
 s=math.sin(phi);c2=-1.5*(math.sqrt(2)+1);c1=(1-s)/(2*c2*c2*s);c5=(1+s)/(1-s);t=c5*la
 try:
  c3=math.sqrt(3)*(1/ka-1/la)/(math.exp(t*math.log(2))+math.exp(t*math.log(1/500))-2)
  c6=1/(2*(-math.sqrt(3)/(c3*ka)+math.expm1(t*math.log(2))))
 except(OverflowError,ZeroDivisionError,ValueError)as e:raise UnsupportedDomain('parameter coefficient arithmetic')from e
 out=dict(c1=c1,c2=c2,c3=c3,c4=1.,c5=c5,c6=c6)
 if not all(math.isfinite(x)for x in out.values())or c1<=0:raise UnsupportedDomain('nonfinite parameter coefficients')
 return out

def rate(state,increment,parameters,precision=100):
 """Return seven instantaneous rates and inspectable derived quantities.

 Research support: SPD compressive stress,e>=0; operatorFrobenius<=64.
 These restrictions are not asserted as the full paper physical domain.
 """
 c=constants(parameters)
 if not isinstance(state,dict)or set(state)!={'sigma','e'}or not number(state['e'])or state['e']<0:raise UnsupportedDomain('research state support requires sigma and finite e>=0')
 sig=vector(state['sigma']);de=vector(increment);e=float(state['e']);a=cart(sig)
 det=a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
 if not(a[0][0]>0 and a[0][0]*a[1][1]-a[0][1]**2>0 and det>0 and math.isfinite(det)):raise UnsupportedDomain('research support requires SPD compression-positive stress')
 p=sum(sig[:3])/3;r=math.hypot(*de);la=parameters['lambda_star'];ka=parameters['kappa_star']
 try:
  critical_plus_one=math.exp(parameters['N']-la*math.log(2*p/1000.))
  density=(1+e)/critical_plus_one;density_power=density**c['c5']
 except(OverflowError,ZeroDivisionError,ValueError)as err:raise UnsupportedDomain('bodyEq8density arithmetic')from err
 if not all(math.isfinite(x)and x>0 for x in (p,critical_plus_one,density,density_power)):raise UnsupportedDomain('nonfinite bodyEq8density')
 if r==0:return dict(sigma_rhs=[0.]*6,e_rhs=0.,branch='zero-continuation',P=None,derived=c|dict(p=p,density=density),expm=None)
 if not math.isfinite(r):raise UnsupportedDomain('nonfinite loading norm')
 u=[x/r for x in de];delta=-sum(u[:3]);rt3=math.sqrt(3);hydro=(de[0]==de[1]==de[2] and de[3:]==[0.,0.,0.])
 if hydro:
  delta=-math.copysign(rt3,de[0]);P=[1/rt3]*3+[0.]*3;meta=None;direction=dict(m=None,K=None,a=None,q=0.);branch='hydrostatic-continuation'
 else:
  dev=u[:];tr=sum(u[:3])/3
  for i in range(3):dev[i]-=tr
  q=math.hypot(*dev)
  if q==0:raise UnsupportedDomain('nonhydrostatic direction lost deviatoric norm')
  m=-math.sqrt(1.5)*delta/q
  try:
   x=c['c1']*(m-c['c2'])**2;K=x/(1+x)
   if not math.isfinite(x)or x<=0:raise UnsupportedDomain('regular branch x must be finite positive; K0 unsupported')
   # log(K) exactly equals log(x)-log1p(x); use reciprocal form
   # for large x so rounded K=1 cannot flatten nearhydrostatic inputs.
   logK=math.log(x)-math.log1p(x) if x<=1 else -math.log1p(1/x)
   aa=logK/(math.sqrt(1.5)*q)
  except(OverflowError,ZeroDivisionError,ValueError)as err:raise UnsupportedDomain('regular directional arithmetic')from err
  meta=decimal_exponential([-aa*z for z in u],precision);P=meta['normalized'];direction=dict(m=m,K=K,a=aa,q=q,x=x,logK=logK,naive_log_rounded_K=math.log(K) if K>0 else None);branch='regular'
 Lambda=(la+ka)/2-(la-ka)*delta/(2*rt3)
 if not math.isfinite(Lambda)or Lambda<=0:raise UnsupportedDomain('nonpositive/nonfinite Lambda')
 beta=-1/(c['c3']*Lambda)+math.expm1(c['c5']*la*math.log(2))/rt3
 f=c['c6']*beta*delta-.5;g=(1-c['c6'])*beta*delta+density_power-.5
 ns=math.hypot(*sig)
 rhs=[c['c3']*r*(f*ns*P[i]+g*sig[i])for i in range(6)];erhs=-(1+e)*sum(de[:3])
 derived=c|direction|dict(p=p,density=density,Lambda=Lambda,beta=beta,f=f,g=g,delta=delta)
 if not all(math.isfinite(x)for x in rhs+[erhs]):raise UnsupportedDomain('nonfinite rate output')
 return dict(sigma_rhs=rhs,e_rhs=erhs,branch=branch,P=P,derived=derived,expm=meta)
