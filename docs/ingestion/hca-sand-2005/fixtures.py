"""Independent source-distinguishing HCA polarization/filter algebra, stdlib only.
Not a constitutive implementation or selected correction to the 2005 manuscript.
"""
import argparse,hashlib,json,math
from pathlib import Path
SOURCE_SHA256='ecf856384f0c77d5440a2aeb28c96420e609ed7cefffab9f19a0b8e141a796ce'
VERSION='hca2005-polarization-filter-reconciliation-v1'

def eye(n):return [[float(i==j)for j in range(n)]for i in range(n)]
def outer(a,b):return [[x*y for y in b]for x in a]
def inner(a,b):return math.fsum(x*y for r,s in zip(a,b)for x,y in zip(r,s))
def norm(a):return math.sqrt(inner(a,a))
def combine(a,b,u,v):return [[u*x+v*y for x,y in zip(r,s)]for r,s in zip(a,b)]
def scale(a,k):return [[k*x for x in r]for r in a]
def add(a,b):return combine(a,b,1,1)
def unit(a):return scale(a,1/norm(a))
def basis():
 # Orthonormal Cartesian row-major second-order tensor coordinates.
 # Symmetric order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz, then skew xy,yz,xz.
 out=[]
 for i in (0,4,8):v=[0.]*9;v[i]=1.;out.append(v)
 for i,j in ((1,3),(5,7),(2,6)):
  v=[0.]*9;v[i]=v[j]=1/math.sqrt(2);out.append(v)
 for i,j in ((1,3),(5,7),(2,6)):
  v=[0.]*9;v[i]=1/math.sqrt(2);v[j]=-1/math.sqrt(2);out.append(v)
 return out

def reduce22(pi):
 b=basis();B=[[math.fsum(x*pi[i][j]*y for i,x in enumerate(u)for j,y in enumerate(v))for v in b[:6]]for u in b[:6]]
 c=math.fsum(math.fsum(x*pi[i][j]*y for i,x in enumerate(v)for j,y in enumerate(v))for v in b[6:])/3
 return B,c

def expand22(B,c):
 b=basis();out=[[0.]*9 for _ in range(9)]
 for i in range(6):
  for j in range(6):out=add(out,scale(outer(b[i],b[j]),B[i][j]))
 for v in b[6:]:out=add(out,scale(outer(v,v),c))
 return out

def toward_by_angle_law(pi,A,h):
 """Derived consequence of Eq24+unit inner product; not literal Eq26 selection."""
 cosine=inner(pi,A)
 if cosine==1:return [r.copy()for r in pi]
 if not 0<=cosine<1:raise ValueError('unit-state angle support')
 alpha=math.acos(cosine);new=alpha*math.exp(-h)
 u=math.sin(new)/math.sin(alpha);v=math.sin(alpha-new)/math.sin(alpha)
 return combine(pi,A,u,v)

def literal26(pi,A,delta):
 """Conventional left action of printed outer-product operator, normalized mu/nu."""
 mu=unit(add(A,pi));nu=unit(combine(A,pi,1,-1))
 return add(pi,add(scale(add(scale(mu,inner(mu,pi)),scale(nu,inner(nu,pi))),math.cos(delta)-1),scale(combine(nu,mu,inner(mu,pi),-inner(nu,pi)),math.sin(delta))))

def decision(epsilon_R,delta,kind):
 if len(epsilon_R)!=6 or len(delta)!=6:raise ValueError('six symmetric coordinates')
 if any(type(v)not in(int,float)or not math.isfinite(v)for v in epsilon_R+delta):raise ValueError('finite numerical components')
 radius=math.hypot(*epsilon_R);step=math.hypot(*delta)
 if radius<=1e-5:return False # Strict norm condition fails before angular normalization.
 if step==0:return None # Printed unit current increment undefined; no invented decision.
 cosine=math.fsum(x*y for x,y in zip(epsilon_R,delta))/(radius*step)
 if not -1<=cosine<=1:raise ValueError('angle roundoff; no clipping')
 if kind=='eq36':return cosine>.9
 if kind=='figure22':return math.acos(cosine)>math.pi/18
 raise ValueError('named source rule required')

def study():
 b=basis();J=eye(9);I=[[.5*(float(i==k and j==l)+float(i==l and j==k))for k in range(3)for l in range(3)]for i in range(3)for j in range(3)]
 Panti=combine(J,I,1,-1);literal=scale(J,1/3);restricted=scale(I,1/3);normalized=scale(I,1/math.sqrt(6));average6=scale(I,1/6)
 vertical=outer(b[2],b[2]);uniform=scale(I,1/math.sqrt(6));states={'literal_J9_over3':literal,'restricted_I6_over3':restricted,'renormalized_I6_over_sqrt6':normalized,'sphere6_average_I6_over6':average6}
 identities={name:dict(full_norm=norm(pi),symmetric_norm=norm(combine(pi,Panti,1,-inner(pi,Panti)/3)),antisymmetric_norm=abs(inner(pi,Panti))/math.sqrt(3),vertical_contraction=inner(pi,vertical),uniform_symmetric_contraction=inner(pi,uniform),fpi_vertical_Cpi1_4=1+4*(1-inner(pi,vertical)),fpi_uniform_Cpi1_4=1+4*(1-inner(pi,uniform)))for name,pi in states.items()}
 # A finite isotropic second-moment quadrature is exact for this polynomial.
 average=[[0.]*9 for _ in range(9)]
 for v in b[:6]:
  for sign in(-1,1):average=add(average,scale(outer([sign*x for x in v],[sign*x for x in v]),1/12))
 identity_error=norm(combine(average,average6,1,-1))
 pi=literal;steps=[]
 amplitudes=[vertical,unit(add(outer(b[0],b[0]),scale(outer(b[3],b[3]),.4))),unit(outer([math.fsum((u+v,w*.3))for u,v,w in zip(b[1],b[4],b[5])],[math.fsum((u+v,w*.3))for u,v,w in zip(b[1],b[4],b[5])]))]
 for h,A in zip((.7,.2,1.1),amplitudes):
  B,c=reduce22(pi);expected=toward_by_angle_law(pi,A,h);a=math.acos(inner(pi,A));new=a*math.exp(-h);u=math.sin(new)/math.sin(a);v=math.sin(a-new)/math.sin(a);AB,_=reduce22(A)
  reconstructed=expand22(combine(B,AB,u,v),u*c)
  steps.append(dict(h=h,old_angle=a,new_angle=math.acos(inner(expected,A)),full_norm=norm(expected),full_vs_22_error=norm(combine(expected,reconstructed,1,-1)),antisymmetric_coefficient=u*c,reduced_norm=math.sqrt(inner(combine(B,AB,u,v),combine(B,AB,u,v))+3*(u*c)**2)))
  pi=expected
 # Orthogonal positive rank-one polarizations distinguish Eq24 from literal sign.
 pi0=outer(b[0],b[0]);A0=outer(b[1],b[1]);literal_step=literal26(pi0,A0,-.1);angle_step=toward_by_angle_law(pi0,A0,.1/(math.pi/2))
 angle_sign=dict(delta_alpha=-.1,literal_cosine=inner(literal_step,A0),literal_norm=norm(literal_step),literal_angle=math.acos(inner(literal_step,A0)),old_angle=math.pi/2,eq24_integrated_cosine=inner(angle_step,A0),eq24_integrated_angle=math.acos(inner(angle_step,A0)),interpretation='Conventional left action of printed Eq26; no correction chosen')
 filters=[]
 for deg in(0.,9.,11.,15.,25.,30.,90.):
  theta=math.radians(deg);R=[2e-5,0,0,0,0,0];d=[math.cos(theta),math.sin(theta),0,0,0,0]
  filters.append(dict(angle_degrees=deg,eq36=decision(R,d,'eq36'),figure22=decision(R,d,'figure22')))
 return dict(version=VERSION,source_sha256=SOURCE_SHA256,identities=identities,exact_second_moment_quadrature_error=identity_error,full9_vs22_piecewise_angle_law=steps,angle_sign_witness=angle_sign,filter_witnesses=filters,undefined_or_boundary_filters=dict(zero_current_increment=decision([2e-5,0,0,0,0,0],[0.]*6,'eq36'),exact_radius_threshold=decision([1e-5,0,0,0,0,0],[1.,0,0,0,0,0],'eq36')),claims=dict(full_constitutive_implementation=False,source_correction_selected=False,scientific_admission=False))

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(study(),indent=2,allow_nan=False)+'\n')
