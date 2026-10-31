"""Source-only exact Mandel range design; no Atlas/runtime imports."""
from fractions import Fraction as F
import math

class Q:
    """Ordered field Q(sqrt(2)); independent Python oracle arithmetic."""
    def __init__(self,a=0,b=0): self.a,self.b=F(a),F(b)
    @staticmethod
    def of(x): return x if isinstance(x,Q) else Q(x)
    def __add__(self,x):
        x=Q.of(x);return Q(self.a+x.a,self.b+x.b)
    __radd__=__add__
    def __neg__(self):return Q(-self.a,-self.b)
    def __sub__(self,x):return self+-Q.of(x)
    def __rsub__(self,x):return Q.of(x)+-self
    def __mul__(self,x):
        x=Q.of(x);return Q(self.a*x.a+2*self.b*x.b,self.a*x.b+self.b*x.a)
    __rmul__=__mul__
    def __truediv__(self,x):
        x=Q.of(x);d=x.a*x.a-2*x.b*x.b
        if not d:raise ZeroDivisionError()
        return self*Q(x.a/d,-x.b/d)
    def sign(self):
        a,b=self.a,self.b
        if not a:return (b>0)-(b<0)
        if not b or (a>0)==(b>0):return (a>0)-(a<0)
        d=a*a-2*b*b;return ((a>0)-(a<0))*((d>0)-(d<0))
    def __bool__(self):return bool(self.a or self.b)
    def __eq__(self,x):
        x=Q.of(x);return self.a==x.a and self.b==x.b

def finite(x):
    if not isinstance(x,(float,int)) or not math.isfinite(x):raise ValueError('finite binary64 input required')
    return F(float(x))

def invariants(v,width):
    if len(v)!=6:raise ValueError('six Mandel components required')
    x=list(map(finite,v));w=finite(width)
    if w<0:raise ValueError('nonnegative width required')
    t=sum(x[:3]);a,b,c=[3*y-t for y in x[:3]];u,v,z=[3*y for y in x[3:]]
    j2=(a*a+b*b+c*c+u*u+v*v+z*z)/2
    j3=Q(a*b*c-(a*v*v+b*z*z+c*u*u)/2,u*v*z/2)
    return j2,j3,(3*w)**2

def range_le(v,width):
    j2,j3,s=invariants(v,width)
    if s<3*j2:return False
    if s>=4*j2:return True
    h=Q(s**3-6*j2*s*s+9*j2*j2*s-4*j2**3)+27*j3*j3
    return h.sign()>=0

# Independent Sturm algorithm: no largest-root bounds or h-sign decision.
# Coefficients ascending; signed exact Euclidean remainders handle multiplicities.
def trim(p):
    while p and not p[-1]:p.pop()
    return p

def remainder(p,q):
    p=list(p)
    while len(p)>=len(q) and p:
        k=len(p)-len(q);c=p[-1]/q[-1]
        for i,x in enumerate(q):p[i+k]=p[i+k]-c*x
        trim(p)
    return p

def value(p,x):
    out=Q()
    for c in reversed(p):out=out*x+c
    return out

def variations(signs):
    s=[x for x in signs if x];return sum(a!=b for a,b in zip(s,s[1:]))

def right_sign(p,x):
    while p:
        y=value(p,x).sign()
        if y:return y
        p=[p[i]*i for i in range(1,len(p))]
    return 0

def sturm_range_le(v,width):
    j2,j3,s=invariants(v,width)
    h=[Q(-4*j2**3)+27*j3*j3,Q(9*j2*j2),Q(-6*j2),Q(1)]
    chain=[h,[h[i]*i for i in range(1,len(h))]]
    while True:
        q=trim([-c for c in remainder(chain[-2],chain[-1])])
        if not q:break
        chain.append(q)
    above=variations([right_sign(q,s)for q in chain])-variations([q[-1].sign()for q in chain])
    return above==0
