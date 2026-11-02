"""Reviewer-owned exact sparse-polynomial identities; no Atlas/symbolic packages."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib,importlib.util,json
N=12
class P:
 def __init__(self,v=0):self.d={tuple([0]*N):Q(v)} if v else {}
 @staticmethod
 def var(i):
  p=P();key=[0]*N;key[i]=1;p.d[tuple(key)]=Q(1);return p
 def __add__(self,b):
  b=b if isinstance(b,P) else P(b);p=P();p.d=self.d.copy()
  for k,v in b.d.items():p.d[k]=p.d.get(k,0)+v
  p.d={k:v for k,v in p.d.items() if v};return p
 __radd__=__add__
 def __neg__(self):return self*-1
 def __sub__(self,b):return self+-b
 def __rsub__(self,b):return -self+b
 def __mul__(self,b):
  b=b if isinstance(b,P) else P(b);p=P()
  for k,v in self.d.items():
   for l,w in b.d.items():
    m=tuple(x+y for x,y in zip(k,l));p.d[m]=p.d.get(m,0)+v*w
  p.d={k:v for k,v in p.d.items() if v};return p
 __rmul__=__mul__
 def __eq__(self,b):return self.d==(b.d if isinstance(b,P) else P(b).d)
def embed(x):
 a,b,c,d=x;return [[a,c,d],[c,b,P()],[d,P(),b]]
def mul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def tr(a):return sum(a[i][i] for i in range(3))
def colon(a,b):return sum(a[i][j]*b[i][j] for i in range(3) for j in range(3))
def rt(x):return x[0]+2*x[1]
def rc(x,y):return x[0]*y[0]+2*sum(x[i]*y[i] for i in range(1,4))
def prod(x,y):
 a,b,c,d=x;e,f,g,h=y;return [a*e+c*g+d*h,b*f+c*g,a*g+c*f,d*e+b*h]
def cubic(x):a=embed(x);return tr(mul(mul(a,a),a))
def run():
 x=[P.var(i) for i in range(4)];y=[P.var(i) for i in range(4,8)];a,b,c,d=x
 checks=0
 def check(v):
  nonlocal checks;assert v;checks+=1
 defect=rt(x)*(c*c-d*d)
 check(rt(prod(prod(x,x),x))-cubic(x)==defect)
 check(rt(prod(x,prod(x,x)))-cubic(x)==defect)
 z=[-2*b,b,c,d]
 check(rt(prod(prod(z,z),z))==cubic(z));check(rt(prod(z,prod(z,z)))==cubic(z))
 rot=[-2*b,b,Q(3,5)*c-Q(4,5)*d,Q(4,5)*c+Q(3,5)*d]
 check(cubic(rot)==cubic(z));check(rc(rot,rot)==rc(z,z))
 check(rc(x,y)==colon(embed(x),embed(y)));check(rt(x)==tr(embed(x)))
 # Any scalar host coefficients: identity action, stress dyad, nonlinear X/Z terms.
 # Hence proof applies to full VW96 coefficients rather than a single test state.
 k1,k2,k3,k4=[P.var(i) for i in range(8,12)]
 v=[y[0],P(),y[2],y[3]];z=[x[0]-Q(1,3),x[1]-Q(1,3),x[2],x[3]]
 reduced=[k1*v[i]+k2*x[i]*rc(x,v)+k3*x[i]+k4*z[i] for i in range(4)]
 X=embed(x);V=embed(v);Z=embed(z)
 cart=[[k1*V[i][j]+k2*X[i][j]*colon(X,V)+k3*X[i][j]+k4*Z[i][j] for j in range(3)] for i in range(3)]
 for i in range(3):
  for j in range(3):check(embed(reduced)[i][j]==cart[i][j])
 check(cart[1][1]==cart[2][2]);check(cart[1][2]==0)
 # T -> -sigma, D -> -DA: normalized T unchanged; linear terms negate,
 # norm is even; negating stress rate restores linear signs and negates norm term.
 r=[k1*v[i]+k2*x[i]*rc(x,v)-k3*x[i]-k4*z[i] for i in range(4)]
 source=[k1*(-v[i])+k2*x[i]*rc(x,[-u for u in v])+k3*x[i]+k4*z[i] for i in range(4)]
 for i in range(4):check(r[i]==-source[i])
 root=Path(__file__).resolve().parents[4]
 source=root/'docs/ingestion/hypoplastic-interface-2016/source-v2/check_reduced_cubic.py'
 spec=importlib.util.spec_from_file_location('author_cubic',source);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);author=m.run();assert author['exact_checks']==702 and author['passed']
 return dict(passed=True,reviewer_exact_polynomial_identities=checks,author_rational_checks_replayed=author['exact_checks'],all_symbolic_coefficients=True,cubic_intermediate_nonclosure_not_denied=True,subspace_rate_preserved=True,sign_conversion_checked=True,compiled_calls=0,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
if __name__=='__main__':print(json.dumps(run(),indent=2))
