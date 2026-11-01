"""Source-only centered-middle design: exact invariant predicate and direct-matrix Sturm oracle."""
from fractions import Fraction as F
from pathlib import Path
import importlib.util,math,itertools
SOURCE=Path(__file__).parents[1]/'certified-spectral-range-v1/exact.py'
s=importlib.util.spec_from_file_location('centered_field_arithmetic',SOURCE);field=importlib.util.module_from_spec(s);s.loader.exec_module(field);Q=field.Q

def finite(x):
 if isinstance(x,bool)or not isinstance(x,(int,float)):raise ValueError('finite binary64 input required')
 try:v=float(x)
 except (OverflowError,ValueError):raise ValueError('finite binary64 input required')
 if not math.isfinite(v):raise ValueError('finite binary64 input required')
 return F(v)
def inputs(mandel,width):
 if not isinstance(mandel,(list,tuple))or len(mandel)!=6:raise ValueError('six Mandel components required')
 x=list(map(finite,mandel));w=finite(width)
 if w<0:raise ValueError('nonnegative width required')
 return x,w
def invariant_middle_gt(mandel,width):
 x,w=inputs(mandel,width);t=sum(x[:3]);a,b,c=[3*v-t for v in x[:3]];u,v,z=[3*y for y in x[3:]]
 J=(a*a+b*b+c*c+u*u+v*v+z*z)/2
 D=Q(a*b*c-(a*v*v+b*z*z+c*u*u)/2,u*v*z/2)
 return 3*w*w<J and (D+J*w-w*w*w).sign()<0

# Independent route: build det(xI-B) directly by matrix permutations.
# No centered-invariant coefficients or determinant-sign classification are used.
def add(p,q):
 out=[Q()for _ in range(max(len(p),len(q)))]
 for i,v in enumerate(p):out[i]=out[i]+v
 for i,v in enumerate(q):out[i]=out[i]+v
 return trim(out)
def mul(p,q):
 out=[Q()for _ in range(max(0,len(p)+len(q)-1))]
 for i,a in enumerate(p):
  for j,b in enumerate(q):out[i+j]=out[i+j]+a*b
 return trim(out)
def trim(p):
 while p and not p[-1]:p.pop()
 return p
def derivative(p):return [p[i]*i for i in range(1,len(p))]
def remainder(p,q):
 p=list(p)
 while p and len(p)>=len(q):
  shift=len(p)-len(q);factor=p[-1]/q[-1]
  for i,c in enumerate(q):p[i+shift]=p[i+shift]-factor*c
  trim(p)
 return p
def gcd(p,q):
 while q:p,q=q,remainder(p,q)
 return [c/p[-1]for c in p]if p else []
def evaluate(p,x):
 v=Q()
 for c in reversed(p):v=v*x+c
 return v
def right_sign_at_zero(p):
 # First nonzero ascending coefficient is the sign immediately right of zero.
 return next((c.sign()for c in p if c),0)
def variations(signs):
 signs=[s for s in signs if s];return sum(a!=b for a,b in zip(signs,signs[1:]))
def positive_distinct(p):
 if len(p)<=1:return 0
 chain=[p,derivative(p)]
 while True:
  r=trim([-c for c in remainder(chain[-2],chain[-1])])
  if not r:break
  chain.append(r)
 return variations([right_sign_at_zero(q)for q in chain])-variations([q[-1].sign()for q in chain])
def positive_with_multiplicity(p):
 if len(p)<=1:return 0
 # Sturm counts distinct roots. Recursively count repeated factors as well.
 return positive_distinct(p)+positive_with_multiplicity(gcd(p,derivative(p)))
def characteristic(matrix):
 result=[]
 for permutation in itertools.permutations(range(3)):
  inversions=sum(permutation[i]>permutation[j]for i in range(3)for j in range(i+1,3));term=[Q(-1 if inversions%2 else 1)]
  for i,j in enumerate(permutation):term=mul(term,[-matrix[i][j],Q(1)]if i==j else [-matrix[i][j]])
  result=add(result,term)
 return result
def sturm_middle_gt_matrix(matrix,width):
 w=Q.of(width);trace=sum((matrix[i][i]for i in range(3)),Q());B=[[3*matrix[i][j]-(trace+w if i==j else Q())for j in range(3)]for i in range(3)]
 return positive_with_multiplicity(characteristic(B))>=2
def sturm_middle_gt(mandel,width):
 x,w=inputs(mandel,width);a,b,c,u,v,z=x;h=Q(0,F(1,2));matrix=[[Q(a),h*u,h*z],[h*u,Q(b),h*v],[h*z,h*v,Q(c)]]
 return sturm_middle_gt_matrix(matrix,w)
