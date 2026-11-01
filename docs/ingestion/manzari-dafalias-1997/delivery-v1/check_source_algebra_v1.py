"""Source-derived Cartesian algebra; never imports production model/compiler."""
import json, math
from pathlib import Path
import numpy as np
I=np.eye(3)
def dev(x): return x-np.trace(x)*I/3
# Source cone is Euclidean distance of deviatoric stress from p*alpha.
def cone(sigma,alpha,m):
 p=np.trace(sigma)/3
 return np.linalg.norm(dev(sigma)-p*alpha)-math.sqrt(2/3)*m*p
cases=[]
alpha=np.array([[.02,.007,-.004],[.007,-.013,.003],[-.004,.003,-.007]])
base=np.array([[190000,13000,-9000],[13000,105000,4000],[-9000,4000,125000]],float)
for multiplier in [.25,.5,1,2,4]:
 sigma=base*multiplier
 p=np.trace(sigma)/3; v=dev(sigma)-p*alpha; n=v/np.linalg.norm(v)
 grad=n-(np.sum(n*alpha)+math.sqrt(2/3)*.05)*I/3
 for i in range(6):
  direction=np.zeros((3,3))
  if i<3: direction[i,i]=p
  else:
   a,b=[(0,1),(1,2),(0,2)][i-3];direction[a,b]=direction[b,a]=p/math.sqrt(2)
  h=1e-6
  numeric=(cone(sigma+h*direction,alpha,.05)-cone(sigma-h*direction,alpha,.05))/(2*h)
  exact=np.sum(grad*direction)
  error=abs(numeric-exact)/max(1,abs(exact))
  cases.append(dict(kind='cone-normal',scale=multiplier,direction=i,error=error,tolerance=3e-7,passed=error<3e-7))
# Hydrostatic source8: d epsilon_v/dp=1/K(p), integrated analytically.
pat=100000.;K0=31400000.
def primitive(p,a):
 if a==1:return pat/K0*math.log(p/pat)
 return pat/K0*((p/pat)**(1-a))/(1-a)
for a in [0,.5,.6,1]:
 for p in [40000.,80000.,160000.,320000.]:
  h=p*1e-5
  numeric=(primitive(p+h,a)-primitive(p-h,a))/(2*h)
  exact=1/(K0*(p/pat)**a)
  error=abs(numeric/exact-1)
  cases.append(dict(kind='elastic-primitive',a=a,p=p,error=error,tolerance=2e-8,passed=error<2e-8))
def cosine(n):return math.sqrt(6)*np.trace(n@n@n)
def interp(z,c):return 2*c/(1+c-(1-c)*z)
# Opposite triaxial directions, independently normalized in Cartesian basis.
n=np.diag([2.,-1.,-1.])/math.sqrt(6)
rot=np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
for sign in [-1,1]:
 x=sign*n;z=cosine(x)
 cases.append(dict(kind='lode-endpoint',sign=sign,error=abs(z-sign),tolerance=3e-14,passed=abs(z-sign)<3e-14))
 for c in [.5,.712,1.,1.4]:
  expected=1 if sign==1 else c
  error=abs(interp(z,c)-expected)
  cases.append(dict(kind='interpolation-endpoint',c=c,sign=sign,error=error,tolerance=3e-14,passed=error<3e-14))
  error=abs(interp(cosine(rot@x@rot.T),c)-interp(z,c))
  cases.append(dict(kind='lode-coordinate-covariance',c=c,sign=sign,error=error,tolerance=3e-13,passed=error<3e-13))
result=dict(identity='md1997-source-algebra-v1',scope='Provisional equations8–10,16–18; full visual-source reconciliation pending',production_imports=False,compiled_execution=False,total=len(cases),passed=int(sum(c['passed'] for c in cases)),cases=cases)
path=Path(__file__).with_name('source-algebra-results-v1.json');path.write_text(json.dumps(result,indent=2,default=lambda value:value.item())+'\n')
print(json.dumps({k:result[k] for k in ['identity','total','passed','scope']}))
raise SystemExit(0 if result['passed']==result['total'] else 1)
