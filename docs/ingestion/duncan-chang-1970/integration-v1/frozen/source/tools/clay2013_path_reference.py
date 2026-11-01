"""Independent Cartesian RK4 clay2013 finite-path reference, no Atlas integration.
Run python -m tools.clay2013_path_reference --output PATH from repository root.
Stored symmetric components use orthonormal Mandel xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz.
"""
import argparse,hashlib,json,math
from pathlib import Path
from tools import reference_clay2013_cartesian as reference
rate=reference.rate
SOURCE_SHA256=reference.SOURCE_SHA256
ROOT=Path(__file__).resolve().parents[1]
PARAMETERS=dict(phi_c=math.pi/6,lambda_star=.12,kappa_star=.025,N=1.1,nu=.2)
R2=math.sqrt(2)
Q=((1/3,2/3,2/3),(2/3,1/3,-2/3),(-2/3,2/3,-1/3))
RESOLUTIONS=(8,16,32)

def cart(v):
 x,y,z,u,v,w=v
 return [[x,u/R2,w/R2],[u/R2,y,v/R2],[w/R2,v/R2,z]]
def mand(a):return [a[0][0],a[1][1],a[2][2],R2*a[0][1],R2*a[1][2],R2*a[0][2]]
def rotate(v):
 a=cart(v)
 return mand([[sum(Q[i][k]*a[k][l]*Q[j][l] for k in range(3) for l in range(3)) for j in range(3)]for i in range(3)])
def cases():
 initial=[14000.,10000.,8000.,1200.,-700.,900.,.8]
 paths=[('noncoaxial',[[.001,-.0002,-.0001,.0004,.0002,-.0003],[-.0001,.0006,-.0002,-.0003,.0005,.0002],[.0002,-.0001,.0001,.0002,-.0004,.0003]]),
        ('shear-reversal',[[0.,0.,0.,.001,.0003,-.0002],[0.,0.,0.,-.001,-.0003,.0002],[0.,0.,0.,-.0006,.0002,.0005]])]
 out=[dict(id=name,initial=initial[:],increments=[[10*x for x in v] for v in inc],parameters=PARAMETERS.copy())for name,inc in paths]
 for base in out[:]:
  out.append(dict(id=base['id']+'-rotated',initial=rotate(initial[:6])+[initial[6]],increments=[rotate(v) for v in base['increments']],parameters=PARAMETERS.copy(),rotated_from=base['id']))
 return out

def rhs(y,d,parameters):
 answer=rate(cart(y[:6]),cart(d),y[6],**parameters)
 return mand(answer['stress_rate'])+[answer['e_rate']]
def integrate(case,n):
 """RK4 in normalized caller-segment coordinate0..1, n equal steps per segment."""
 y=case['initial'][:];rows=[dict(segment=0,state=y[:])];h=1/n
 for segment,d in enumerate(case['increments'],1):
  for _ in range(n):
   k1=rhs(y,d,case['parameters']);k2=rhs([a+.5*h*b for a,b in zip(y,k1)],d,case['parameters'])
   k3=rhs([a+.5*h*b for a,b in zip(y,k2)],d,case['parameters']);k4=rhs([a+h*b for a,b in zip(y,k3)],d,case['parameters'])
   y=[a+h*(b+2*c+2*e+f)/6 for a,b,c,e,f in zip(y,k1,k2,k3,k4)]
   if not all(math.isfinite(v) for v in y):raise ValueError('nonfinite RK4 endpoint')
  # Explicit endpoint domain/rate check, not only intermediate stages.
  rhs(y,[0.]*6,case['parameters']);rows.append(dict(segment=segment,state=y[:]))
 return rows

def differences(a,b):
 return dict(stress=max(abs(x-y)for ra,rb in zip(a,b)for x,y in zip(ra['state'][:6],rb['state'][:6])),
             e=max(abs(ra['state'][6]-rb['state'][6])for ra,rb in zip(a,b)))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def study():
 result=[]
 for case in cases():
  grids=[dict(steps_per_segment=n,trajectory=integrate(case,n))for n in RESOLUTIONS]
  coarse=differences(grids[0]['trajectory'],grids[1]['trajectory']);fine=differences(grids[1]['trajectory'],grids[2]['trajectory'])
  ratios={k:coarse[k]/fine[k] if fine[k] else None for k in coarse}
  result.append(dict(input=case,input_sha256=hashlib.sha256(json.dumps(case,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),grids=grids,coarse_difference=coarse,fine_difference=fine,refinement_ratio=ratios,richardson_estimate={k:fine[k]/15 for k in fine}))
 covariance=[]
 for base,rotated in zip(result[:2],result[2:]):
  expected=[dict(segment=r['segment'],state=rotate(r['state'][:6])+[r['state'][6]])for r in base['grids'][-1]['trajectory']]
  covariance.append(dict(case=base['input']['id'],difference=differences(expected,rotated['grids'][-1]['trajectory'])))
 return dict(contract='clay2013-independent-cartesian-path-reference-v1',basis='Mandel xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz; e',zero_spin=True,coordinate='each piecewise-constant full6 strain segment parameterized0..1; not physical time',source_sha256=SOURCE_SHA256,resolutions=list(RESOLUTIONS),rotation=[list(r)for r in Q],cases=result,covariance=covariance,dependency_sha256={'tools/clay2013_path_reference.py':sha(Path(__file__)),'tools/reference_clay2013_cartesian.py':sha(Path(reference.__file__))},scope='Fixed-step independent rate integration only; convergence estimates not rigorous error bounds; no production/native or experiment validation')
def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(study(),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
