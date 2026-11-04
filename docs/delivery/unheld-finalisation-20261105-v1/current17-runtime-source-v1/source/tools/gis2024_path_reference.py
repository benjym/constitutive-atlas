"""Fixed-step independent Cartesian GIS2024 path diagnostics, not an integrator API.

Only stdlib and the independently coded coupled rate/its stdlib HP dependency.
No Atlas DSL, common solver, native/Wasm execution or experimental validation.
"""
import argparse,hashlib,json,math
from pathlib import Path
from tools import reference_gis2024_coupled as reference
SOURCE_SHA256='39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3'
RESOLUTIONS=(16,32,64)
Q=((1/3,2/3,2/3),(2/3,1/3,-2/3),(-2/3,2/3,-1/3))
R2=math.sqrt(2)
PARAMETERS=dict(phi=34*math.pi/180,hs=111746000.,ei0=1.027,ec0=.893,ed0=.520,n=.346,alpha=.15,beta=2.2,R=1e-4,m_R=5.,m_T=2.5,beta_R=.1,chi_R=4.,gamma_chi=1.7,chi_0=.8,chi_max=1.5,C_Omega=45.,gamma_Omega=1.)

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def cart(v):
 x,y,z,u,v,w=v
 return [[x,u/R2,w/R2],[u/R2,y,v/R2],[w/R2,v/R2,z]]
def mand(a):return [a[0][0],a[1][1],a[2][2],R2*a[0][1],R2*a[1][2],R2*a[0][2]]
def rotate(v):
 a=cart(v)
 return mand([[sum(Q[i][k]*a[k][l]*Q[j][l]for k in range(3)for l in range(3))for j in range(3)]for i in range(3)])
def rotate_state(y):return rotate(y[:6])+[y[6]]+rotate(y[7:13])+[y[13]]
def state_dict(y):return dict(sigma=y[:6],e=y[6],h=y[7:13],Omega=y[13])
def cases():
 sigma=[180000.,100000.,70000.,12000.,-8000.,4000.]
 h=[2e-5,-1e-5,.5e-5,.8e-5,-.4e-5,.3e-5]
 initial=sigma+[.595]+h+[.25]
 paths=[('noncoaxial',[[1.5e-5,-.3e-5,.2e-5,.4e-5,-.2e-5,.3e-5],[.7e-5,.3e-5,-.1e-5,.6e-5,.1e-5,-.2e-5],[.8e-5,-.2e-5,.3e-5,-.1e-5,-.3e-5,.4e-5]]),
 ('shear-reversal',[[0.,0.,0.,.8e-5,-.3e-5,.2e-5],[0.,0.,0.,-.5e-5,.2e-5,-.1e-5],[0.,0.,0.,-.3e-5,.1e-5,-.2e-5]])]
 out=[dict(id=name,initial=initial[:],increments=[d[:]for d in path],parameters=PARAMETERS.copy())for name,path in paths]
 for base in out[:]:out.append(dict(id=base['id']+'-rotated',initial=rotate_state(initial),increments=[rotate(d)for d in base['increments']],parameters=PARAMETERS.copy(),rotated_from=base['id']))
 return out

def integrate(case,n):
 if type(n)is not int or n<1 or n>4096:raise ValueError('integer steps1..4096 required')
 y=case['initial'][:];rows=[dict(segment=0,state=y[:])];step=1/n
 margins=dict(e_min=math.inf,radius_gap_min=math.inf,rho_min=math.inf,Omega_min=math.inf,one_minus_Omega_min=math.inf,pressure_min_Pa=math.inf,S_min=math.inf,fdAstar_min=math.inf)
 segments=[];evaluations=0
 def rhs(z,d,qvalues):
  nonlocal evaluations
  if len(z)!=14 or not all(type(x)in(int,float)and math.isfinite(x)for x in z):raise ValueError('finite14state required')
  result=reference.coupled_rates(state_dict(z),d,case['parameters']);evaluations+=1
  if len(result['derivative'])!=14:raise ValueError('reference derivative shape mismatch')
  diag=result['diagnostics'];rho=diag['rho'];Omega=z[13]
  values=dict(e_min=z[6],radius_gap_min=1-rho,rho_min=rho,Omega_min=Omega,one_minus_Omega_min=1-Omega,pressure_min_Pa=sum(z[:3])/3,S_min=diag['S'],fdAstar_min=diag['fdAstar'])
  if any(not math.isfinite(v)or v<=0 for v in values.values()):raise ValueError('stage left selected strictly interior path domain')
  for k,v in values.items():margins[k]=min(margins[k],v)
  if diag['q']is not None:qvalues.append(diag['q'])
  return result['derivative']
 for segment,d in enumerate(case['increments'],1):
  qs=[]
  for _ in range(n):
   a=rhs(y,d,qs);b=rhs([v+.5*step*k for v,k in zip(y,a)],d,qs)
   c=rhs([v+.5*step*k for v,k in zip(y,b)],d,qs);f=rhs([v+step*k for v,k in zip(y,c)],d,qs)
   y=[v+step*(k1+2*k2+2*k3+k4)/6 for v,k1,k2,k3,k4 in zip(y,a,b,c,f)]
  rhs(y,d,qs)
  rows.append(dict(segment=segment,state=y[:]))
  segments.append(dict(segment=segment,q_min=min(qs),q_max=max(qs),branch_crossing_observed=min(qs)<0<max(qs)))
 return dict(steps_per_segment=n,trajectory=rows,stage_diagnostics=dict(evaluations=evaluations,minima=margins,segments=segments))

def differences(a,b):
 if len(a)!=len(b)or[r['segment']for r in a]!=[r['segment']for r in b]:raise ValueError('trajectory labels differ')
 return {name:max(abs(x-y)for ra,rb in zip(a,b)for x,y in zip(ra['state'][lo:hi],rb['state'][lo:hi]))for name,lo,hi in [('stress',0,6),('e',6,7),('h',7,13),('Omega',13,14)]}
def volume_errors(case,trajectory):
 total=0.;errors=[]
 for row in trajectory:
  j=row['segment']
  if j:total+=math.fsum(case['increments'][j-1][:3])
  expected=(1+case['initial'][6])*math.exp(-total)-1
  errors.append(abs(row['state'][6]-expected))
 return errors

def study():
 results=[]
 for case in cases():
  grids=[integrate(case,n)for n in RESOLUTIONS]
  for g in grids:g['exact_volume_absolute_errors']=volume_errors(case,g['trajectory'])
  coarse=differences(grids[0]['trajectory'],grids[1]['trajectory']);fine=differences(grids[1]['trajectory'],grids[2]['trajectory'])
  ratio={k:coarse[k]/fine[k]if fine[k]else None for k in fine}
  results.append(dict(input=case,input_sha256=digest(case),grids=grids,coarse_difference=coarse,fine_difference=fine,refinement_ratio=ratio,richardson_estimate={k:fine[k]/15 for k in fine},richardson_assumption='conditional fourth-order smooth asymptotic estimate; not rigorous bound; roundoff-sized channels do not resolve order'))
 covariance=[]
 for base,rot in zip(results[:2],results[2:]):
  expected=[dict(segment=r['segment'],state=rotate_state(r['state']))for r in base['grids'][-1]['trajectory']]
  covariance.append(dict(case=base['input']['id'],difference=differences(expected,rot['grids'][-1]['trajectory'])))
 deps={'tools/gis2024_path_reference.py':sha(__file__),'tools/reference_gis2024_coupled.py':sha(reference.__file__),'tools/reference_gis2024_hp_host.py':sha(reference.hp.__file__)}
 return dict(contract='gis2024-independent-cartesian-path-reference-v1',basis='Mandel xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz; state sigma6,e,h6,Omega',coordinate='each full6 piecewise-constant strain segment0..1; not physical time',zero_spin=True,source_sha256=SOURCE_SHA256,source_url='https://publikationen.bibliothek.kit.edu/1000171366/153009465',source_doi='10.1016/j.compgeo.2024.106480',source_locators=['p3 Eqs8-12','p4 Eqs26-32','p5 Eq33','p6 Eqs34-35,39','p7 Eqs40-43','p12 AppendixB'],resolutions=list(RESOLUTIONS),rotation=[list(r)for r in Q],cases=results,covariance=covariance,dependency_sha256=deps,scope='Strictly interior fixed-step independent numerical references; no preparation, native/Wasm/common-engine comparison, experimental validation or scientific admission')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(study(),indent=2,allow_nan=False)+'\n')
if __name__=='__main__':main()
