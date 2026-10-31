"""Independent Decimal characteristic-cubic reference, exact binary64 Mandel inputs."""
import decimal as dec, json, math, sys, hashlib
from pathlib import Path
D=dec.Decimal
ROOT=Path(__file__).resolve().parent

def mat(v,s2):return [[v[0],v[3]/s2,v[5]/s2],[v[3]/s2,v[1],v[4]/s2],[v[5]/s2,v[4]/s2,v[2]]]
def eye():return [[D(i==j)for j in range(3)]for i in range(3)]
def add(a,b):return [[a[i][j]+b[i][j]for j in range(3)]for i in range(3)]
def sc(a,k):return [[x*k for x in row]for row in a]
def sub(a,b):return add(a,sc(b,D(-1)))
def mm(a,b):return [[sum((a[i][k]*b[k][j]for k in range(3)),D(0))for j in range(3)]for i in range(3)]
def tr(a):return sum((a[i][i]for i in range(3)),D(0))
def det(a):return a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])-a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])+a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])
def norm(a):return max(abs(x)for row in a for x in row)
def txt(x):return format(x,'.72E')if x else '0'
def enc(a):return [[txt(x)for x in row]for row in a]
def root_cubic(a,precision):
 I=eye();scale=norm(a)
 if not scale:return [D(0)]*3,'zero'
 if all(not a[i][j]for i in range(3)for j in range(3)if i!=j):return sorted((a[i][i]for i in range(3)),reverse=True),'diagonal-exact'
 b=sc(a,1/scale);m=tr(b)/3;c=sub(b,sc(I,m));q=tr(mm(c,c))/6;r=det(c)/2
 if q<=0:raise ArithmeticError('non-diagonal stationary range unresolved')
 z=q.sqrt();f=lambda x:(x*x-3*q)*x-2*r
 intervals=[(-2*z,-z),(-z,z),(z,2*z)];roots=[]
 for lo,hi in intervals:
  flo=f(lo);fhi=f(hi)
  if not flo:roots.append((lo+m)*scale);continue
  if not fhi:roots.append((hi+m)*scale);continue
  if flo*fhi>0:raise ArithmeticError('cubic endpoint signs unresolved')
  for k in range(precision*4):
   mid=(lo+hi)/2;fm=f(mid)
   if not fm:lo=hi=mid;break
   if (flo>0)==(fm>0):lo=mid;flo=fm
   else:hi=mid
   if hi-lo < D(10)**(-(precision-18)):break
  else:raise ArithmeticError('bisection budget')
  roots.append(((lo+hi)/2+m)*scale)
 return sorted(roots,reverse=True),'centered-cubic-stationary-brackets'
def project(a,vals,i):
 if all(not a[r][c]for r in range(3)for c in range(3)if r!=c):
  # Exact coordinate projector for a mathematically isolated diagonal value.
  return [[D(r==c and a[r][r]==vals[i])for c in range(3)]for r in range(3)]
 js=[j for j in range(3)if j!=i];I=eye()
 return sc(mm(sub(a,sc(I,vals[js[0]])),sub(a,sc(I,vals[js[1]]))),1/((vals[i]-vals[js[0]])*(vals[i]-vals[js[1]])))
def record(case,precision):
 with dec.localcontext() as ctx:
  ctx.prec=precision;s2=D(2).sqrt();a=mat([D.from_float(float.fromhex(x))for x in case['mandel_hex']],s2);hs=[mat([D.from_float(float.fromhex(x))for x in h],s2)for h in SEEDS]
  vals,method=root_cubic(a,precision);ps={};rows={};I=eye();scale=max(norm(a),D(1))
  residuals=[]
  for i,name in enumerate(('max','mid','min')):
   if any(vals[i]==vals[j]for j in range(3)if i!=j):rows[name]={'status':'repeated-selected-no-classical-derivative'};continue
   p=project(a,vals,i);ps[i]=p
   residuals.extend([norm(sub(mm(a,p),sc(p,vals[i])))/scale,norm(sub(mm(p,p),p)),abs(tr(p)-1)])
   ders=[]
   # Resolvent on orthogonal complement, using polynomial projectors if simple;
   # a repeated complementary pair has one shared denominator and group projector.
   others=[j for j in range(3)if j!=i]
   for h in hs:
    dl=tr(mm(p,h))
    if vals[others[0]]==vals[others[1]]:
     c=sub(I,p);dp=sc(add(mm(mm(c,h),p),mm(mm(p,h),c)),1/(vals[i]-vals[others[0]]))
    else:
     dp=[[D(0)]*3 for _ in range(3)]
     for j in others:
      pj=project(a,vals,j);dp=add(dp,sc(add(mm(mm(pj,h),p),mm(mm(p,h),pj)),1/(vals[i]-vals[j])))
    residuals.extend([norm(sub(add(mm(p,dp),mm(dp,p)),dp))/max(norm(dp),D(1)),abs(tr(dp))/max(norm(dp),D(1))])
    ders.append({'eigenvalue':txt(dl),'projector':enc(dp)})
   rows[name]={'status':'isolated','projector':enc(p),'directions':ders}
  sums={}
  for name,ids,complement in [('upper',(0,1),2),('lower',(1,2),0)]:
   if complement not in ps:sums[name]={'value':txt(vals[ids[0]]+vals[ids[1]]),'status':'repeated-complement-no-classical-derivative'}
   else:sums[name]={'value':txt(vals[ids[0]]+vals[ids[1]]),'status':'isolated-complement','directions':[txt(tr(mm(sub(I,ps[complement]),h)))for h in hs]}
  return {'id':case['id'],'method':method,'eigenvalues':[txt(x)for x in vals],'selected':rows,'pair_sums':sums,'maximum_internal_normalized_residual':txt(max(residuals,default=D(0)))}

def hx(v):return [float(x).hex()for x in v]
def tensor_rotate(vals,q):return [[sum(q[i][k]*vals[k]*q[j][k]for k in range(3))for j in range(3)]for i in range(3)]
def stored(a):return [a[0][0],a[1][1],a[2][2],math.sqrt(2)*a[0][1],math.sqrt(2)*a[1][2],math.sqrt(2)*a[0][2]]
def corpus():
 cases=[]
 def put(name,v):cases.append({'id':name,'mandel_hex':hx(v)})
 for name,v in [('zero',[0]*6),('hydro',[3,3,3,0,0,0]),('upper-repeat',[4,4,1,0,0,0]),('lower-repeat',[4,1,1,0,0,0]),('distinct',[7,2,-3,0,0,0]),('negative',[-1,-3,-8,0,0,0]),('mixed-scale',[1e300,1,-1e300,0,0,0]),('subnormal',[math.ulp(0.),2*math.ulp(0.),3*math.ulp(0.),0,0,0]),('huge',[float.fromhex('0x1.fffffffffffffp+1023'),1,0,0,0,0])]:put(name,v)
 q=[[1/9,8/9,4/9],[8/9,1/9,-4/9],[-4/9,4/9,-7/9]]
 bases=[('dense',[3,-2,1,.7,-.4,1.2]),('rotated-distinct',stored(tensor_rotate([7,2,-3],q))),('rotated-upper-pair-encoding',stored(tensor_rotate([4,4,1],q))),('rotated-lower-pair-encoding',stored(tensor_rotate([4,1,1],q)))]
 for name,v in bases:
  for sign,power in [(1,0),(-1,0),(1,400),(1,-400),(-1,400),(-1,-400)]:put(f'{name}-sign{sign}-p{power}',[math.ldexp(sign*x,power)for x in v])
 for k in (8,24,40,48):
  put(f'near-upper-{k}',[1+2**(-k),1,-2,0,0,0]);put(f'near-lower-{k}',[2,1,1-2**(-k),0,0,0])
  put(f'rotated-gap-{k}',stored(tensor_rotate([1+2**(-k),1,-2],q)))
 return cases
SEEDS=[hx([1 if i==j else 0 for i in range(6)])for j in range(6)]+[hx([(((j+1)*(k+3))%17-8)/(1+(j+k)%5)for k in range(6)])for j in range(32)]
if __name__=='__main__':
 precision=int(sys.argv[1]);cases=corpus();output={'identity':'stored-binary64-Mandel-independent-Decimal-v1','precision':precision,'cartesian_shear':'exact stored binary64 / mathematical sqrt(2), approximated at declared Decimal precision','seeds_mandel_hex':SEEDS,'cases':[],'unresolved':[]}
 for case in cases:
  try:output['cases'].append({'input':case,'reference':record(case,precision)})
  except ArithmeticError as e:output['unresolved'].append({'input':case,'reason':str(e)})
 print(json.dumps(output,sort_keys=True,separators=(',',':')))
