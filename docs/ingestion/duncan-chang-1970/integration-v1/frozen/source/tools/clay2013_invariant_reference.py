"""Independent Decimal Cartesian invariant/direction identities; no production DSL."""
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
from pathlib import Path
import hashlib,json,math

def trace(a):return sum(a[i][i] for i in range(3))
def matmul(a,b):return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def det(a):return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def matrix(diag):return [[v if i==j else D(0) for j in range(3)] for i,v in enumerate(diag)]
def decimal_fraction(x):return D(x.numerator)/D(x.denominator)
def textify(x):
 if isinstance(x,D):return str(x)
 if isinstance(x,list):return [textify(v) for v in x]
 if isinstance(x,dict):return {k:textify(v) for k,v in x.items()}
 return x

def inspect(sigma):
 S=trace(sigma);T=[[-x for x in r] for r in sigma];I1=trace(T)
 I2=(sum(x*x for r in T for x in r)-I1*I1)/2;I3=det(T)
 r=[[x/S for x in row] for row in sigma]
 # Pairwise diagonal differences avoid falsely spherical residual in exact iso.
 a=[[((2*r[i][i]-sum(r[j][j] for j in range(3) if j!=i))/3 if i==k else r[i][k]) for k in range(3)] for i in range(3)]
 j2=sum(x*x for row in a for x in row);j3=trace(matmul(matmul(a,a),a))
 numerator=j2-3*j3;denominator=D(8)/27-(j2+j3)/3
 original=(9*I3+I1*I2)/(I3+I1*I2)
 stable=numerator/denominator
 iso=all(sigma[i][j]==0 for i in range(3) for j in range(3) if i!=j) and sigma[0][0]==sigma[1][1]==sigma[2][2]
 # phi=30deg: sin(phi)=1/2 exactly; xi=1.7+3.9/4=2.675.
 sine=D('.5');xi=D('2.675');power=(xi*sine.ln()).exp()
 if iso:
  cosine=None;direction=matrix([-1/D(3).sqrt()]*3)
 else:
  cosine=-D(6).sqrt()*j3/(j2*j2.sqrt())
  c=(D(2)/3-(cosine+1)*(stable.ln()/4).exp()/4)*(((xi/2*stable.ln()).exp()-power)/(1-power))
  dA=[[-a[i][j]+(c if i==j else 0) for j in range(3)] for i in range(3)]
  length=sum(x*x for row in dA for x in row).sqrt();direction=[[x/length for x in row] for row in dA]
 spherical=matrix([-1/D(3).sqrt()]*3)
 distance=sum((direction[i][j]-spherical[i][j])**2 for i in range(3) for j in range(3)).sqrt()
 return dict(sigma=sigma,source_invariants=dict(I1=I1,I2=I2,I3=I3),j2=j2,j3=j3,
  Fm_direct=original,Fm_stable=stable,absolute_formula_difference=abs(original-stable),denominator=denominator,
  isotropic=iso,lode_cosine=cosine,direction=direction,direction_distance_to_isotropic=distance)

def generate():
 with localcontext() as c:
  c.prec=180
  cases=[]
  for p in ['.1','.3','100000','1e-80','1e80']:
   cases.append(dict(name='isotropic-'+p,**inspect(matrix([D(p)]*3))))
  for sign in [1,-1]:
   for exponent in [2,4,8,16,32,45]:
    t=D(sign)*D(10)**(-exponent)
    cases.append(dict(name=f'axisymmetric-{sign}-1e-{exponent}',deviation=t,
      **inspect(matrix([1+2*t,1-t,1-t]))))
  # Rational orthogonal Householder rotation; Cartesian no Mandel helper.
  q=[[F(int(i==j))-F(2*(i+1)*(j+1),14) for j in range(3)] for i in range(3)]
  q=[[decimal_fraction(x) for x in row] for row in q]
  for diag in [[D(1),D(2),D(4)],[D('1e-30'),D(1),D(2)]]:
   sigma=matmul(matmul(q,matrix(diag)),q)
   cases.append(dict(name='rotated-SPD-'+str(diag[0]),**inspect(sigma)))
  float_edges=[]
  for p in [.1,.3,1.,100000.]:
   S=p+p+p;r=p/S;d=r-(r+r+r)/3;j2=3*d*d;j3=3*d*d*d
   cosine=-math.sqrt(6)*j3/(j2*math.sqrt(j2)) if j2 else None
   float_edges.append(dict(p=p,r_diag=r,ordinary_dev_diagonal=d,j2=j2,lode_cosine=cosine))
  data=dict(scope='Independent Decimal Cartesian identities and explicit proposed limiting branch, not full source-rate/model validation',
    precision=180,definitions=dict(a='sigma/tr(sigma)-I/3 (mathematically deviatoric)',j2='a:a',j3='tr(a^3)',
      source_Fm='(9I3+I1I2)/(I3+I1I2)',stable_Fm='(j2-3j3)/(8/27-(j2+j3)/3)',
      source_sign='T=-sigma',I2='(T:T-tr(T)^2)/2',direction_parameters='sin(phi_c)=1/2,xi=2.675'),
    fixtures=cases,float_exact_isotropic_edges=float_edges,
    generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
  return textify(data)
if __name__=='__main__':
 import argparse
 parser=argparse.ArgumentParser()
 parser.add_argument('--output',required=True,type=Path)
 args=parser.parse_args()
 args.output.write_text(json.dumps(generate(),sort_keys=True,indent=2,allow_nan=False)+'\n')
