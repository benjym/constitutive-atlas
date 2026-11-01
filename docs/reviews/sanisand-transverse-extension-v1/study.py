"""Independent Decimal transverse-mode study; no Atlas or candidate integration."""
from decimal import Decimal as D, localcontext
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
REF=ROOT/'docs/references/sanisand-project-monotonic-v1'
spec=importlib.util.spec_from_file_location('cartesian_sanisand_reference',REF/'reference.py');law=importlib.util.module_from_spec(spec);spec.loader.exec_module(law)


def load(path):return json.loads(gzip.decompress(path.read_bytes()) if path.suffix=='.gz' else path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def verify_pins():
 for name,expected in load(HERE/'prospective-freeze.json')['files'].items():
  assert sha(ROOT/name)==expected,name
 for name,expected in load(REF/'manifest.json')['files'].items():assert sha(ROOT/name)==expected,name


def coefficients(y,v,e,k,p0):
 """Analytic antisymmetric yy-minus-zz system on a symmetric diagonal branch."""
 s,a,z=y[:9],y[9:18],y[18:];p=law.tr(s)/3
 r=[x/p for x in law.dev(s)];w=[x-b for x,b in zip(r,a)];norm=law.dot(w,w).sqrt();n=[x/norm for x in w]
 assert s[4]==s[8] and a[4]==a[8] and z[4]==z[8] and all(s[i]==0 for i in [1,2,3,5,6,7])
 c3=D(6).sqrt()*law.dot(n,law.square(n));g=2*k['c']/((1+k['c'])-(1-k['c'])*c3)
 B=1+D('1.5')*(1-k['c'])/k['c']*g*c3;C=3*(D(3)/2).sqrt()*(1-k['c'])/k['c']*g
 f=B-2*C*n[4]
 diag=law.rates(y,v,e,k,True);G,K=law.elastic(p,e,k)
 psi=e-k['e0']+k['lambda_c']*(p/k['p_at'])**k['xi'];ab=(D(2)/3).sqrt()*(g*k['M']*(-k['nb']*psi).exp()-k['m'])
 b0=k['G0']*k['h0']*(1-k['ch']*e)/(p/k['p_at']).sqrt()
 loading=2*G*law.dot(n,v);q=max(D(0),loading/diag['denominator']);L=diag['distance']*q
 A=-2*G*L*f/norm;H=D(2)/3*b0*q;J=H*ab/norm;F=k['cz']*max(D(0),-L*diag['dilatancy'])
 # Coordinates x=(sigma_yy-sigma_zz)/p0, y=alpha_yy-alpha_zz, z=fabric_yy-fabric_zz.
 matrix=[[A/p,-A/p0,D(0)],[J*p0/p,-J-H,D(0)],[-F*k['zmax']*p0/(p*norm),F*k['zmax']/norm,-F]]
 trace=matrix[0][0]+matrix[1][1];det=matrix[0][0]*matrix[1][1]-matrix[0][1]*matrix[1][0]
 discriminant=trace*trace-4*det
 eigen_plus=(trace+discriminant.sqrt())/2 if discriminant>=0 else None
 return matrix,{'flow_transverse_coefficient':f,'transverse_2x2_determinant':det,'transverse_2x2_positive_eigenvalue':eigen_plus,'p':p,'norm':norm}


def starting(case,raw):
 k=law.parameters(raw);p0=D(case['pressure_Pa']);e=D(case['void_ratio']);v=list(map(D,case['direction_cartesian']))
 G,_=law.elastic(p0,e,k);entry=p0*(D(2)/3).sqrt()*k['m']/(2*G*law.dot(v,v).sqrt())
 y=[p0 if i in (0,4,8) else D(0) for i in range(9)]+[D(0)]*18
 for i in range(9):y[i]+=2*G*entry*v[i]
 return k,p0,e,v,entry,y


def advance(y,t,target,h,fn,scales,tolerance,variable_relative=False):
 accepted=rejected=0
 while t<target:
  if accepted+rejected>=20000:raise ValueError('diagnostic attempt budget')
  h=min(h,target-t)
  if h<D('1e-30'):raise ValueError('diagnostic minimum step')
  try:
   high,low=law.rk(y,h,fn)
   error=max(abs(a-b)/(max(scale,abs(a)) if variable_relative and i>=27 else scale) for i,(a,b,scale) in enumerate(zip(high,low,scales)))
  except law.Unsupported:
   rejected+=1;h/=2;continue
  if error>tolerance:rejected+=1;h*=max(D('.1'),D('.9')*(tolerance/error)**D('.2'));continue
  y=high;t+=h;accepted+=1
  h*=2 if error==0 else min(D(2),max(D('.2'),D('.9')*(tolerance/error)**D('.2')))
 return y,t,h,accepted,rejected


def variational(case,raw,precision,tolerance):
 with localcontext() as ctx:
  ctx.prec=precision;k,p0,e,v,t,y=starting(case,raw);end=D(case['end_parameter']);entry=t
  y += [D(1),D(0),D(0)];h=(end-entry)/100;tol=D(tolerance);scales=[p0]*9+[D(1)]*21;samples=[];accepted=rejected=0
  def fn(state):
   matrix,_=coefficients(state[:27],v,e,k,p0)
   return law.rates(state[:27],v,e,k)+[sum(matrix[i][j]*state[27+j] for j in range(3)) for i in range(3)]
  for index in range(17):
   target=entry+(end-entry)*index/16
   if index:
    y,t,h,a,r=advance(y,t,target,h,fn,scales,tol,True);accepted+=a;rejected+=r
   matrix,diag=coefficients(y[:27],v,e,k,p0)
   samples.append({'parameter':str(t),'variation':list(map(str,y[27:])),'matrix':[[str(x) for x in row] for row in matrix],
                   'diagnostics':{key:str(x) if x is not None else None for key,x in diag.items()}})
  return {'case':case['id'],'precision':precision,'tolerance':tolerance,'samples':samples,'accepted':accepted,'rejected':rejected}


def nonlinear(case,raw,epsilon,sign):
 with localcontext() as ctx:
  ctx.prec=100;k,p0,e,v,t,y=starting(case,raw);end=D(case['end_parameter']);entry=t
  perturb=D(sign)*D(epsilon)*p0/2;y[4]+=perturb;y[8]-=perturb
  h=(end-entry)/100;scales=[p0]*9+[D(1)]*18;samples=[];accepted=rejected=0
  for index in range(17):
   target=entry+(end-entry)*index/16
   if index:
    y,t,h,a,r=advance(y,t,target,h,lambda state:law.rates(state,v,e,k),scales,D('1e-12'));accepted+=a;rejected+=r
   d=law.rates(y,v,e,k,True)
   samples.append({'parameter':str(t),'state_cartesian':list(map(str,y)),
                   'scaled_transverse':[str((y[4]-y[8])/p0),str(y[13]-y[17]),str(y[22]-y[26])],
                   'yield_excess_over_p0':str(d['yield_Pa']/p0)})
  return {'case':case['id'],'precision':100,'tolerance':'1e-12','epsilon':epsilon,'sign':sign,'samples':samples,'accepted':accepted,'rejected':rejected}


def tangent_checks(case,raw):
 with localcontext() as ctx:
  ctx.prec=100;k,p0,e,v,t,y=starting(case,raw)
  ref=next(c for c in load(REF/'reference-p80-t12.json.gz')['cases'] if c['id']==case['id'])
  worst=D(0);checks=0
  for sample in ref['samples'][2:]:
   s=list(map(D,sample['state']));y=[]
   for offset in [0,7,13]:
    block=s[offset:offset+6];y+= [block[0],block[3]/D(2).sqrt(),block[5]/D(2).sqrt(),block[3]/D(2).sqrt(),block[1],block[4]/D(2).sqrt(),block[5]/D(2).sqrt(),block[4]/D(2).sqrt(),block[2]]
   matrix,diag=coefficients(y,v,e,k,p0)
   for col,offset,scale in [(0,0,p0),(1,9,D(1)),(2,18,D(1))]:
    eps=D('1e-30');plus=y.copy();minus=y.copy();plus[offset+4]+=eps*scale/2;plus[offset+8]-=eps*scale/2;minus[offset+4]-=eps*scale/2;minus[offset+8]+=eps*scale/2
    rp=law.rates(plus,v,e,k);rm=law.rates(minus,v,e,k)
    for row,off,outscale in [(0,0,p0),(1,9,D(1)),(2,18,D(1))]:
     derivative=((rp[off+4]-rp[off+8])-(rm[off+4]-rm[off+8]))/(2*eps*outscale)
     err=abs(derivative-matrix[row][col])/max(D(1),abs(matrix[row][col]));worst=max(worst,err);checks+=1
  assert worst<D('1e-24'),str(worst)
  return {'case':case['id'],'derivative_components':checks,'maximum_scaled_derivative_difference':str(worst)}


def main(output):
 verify_pins();policy=load(HERE/'policy.json');inputs=load(REF/'inputs.json');by_id={c['id']:c for c in inputs['cases']};rows=[];checks=[]
 for identity in policy['cases']:
  checks.append(tangent_checks(by_id[identity],inputs['parameters']))
  for precision,tolerance in policy['variational_configs']:
   try:r=variational(by_id[identity],inputs['parameters'],precision,tolerance);r['status']='completed'
   except Exception as exc:r={'case':identity,'precision':precision,'tolerance':tolerance,'status':'failed','exception':repr(exc)}
   rows.append(r);print(identity,'variational',precision,tolerance,r['status'],flush=True)
 nonlinear_rows=[]
 for identity in policy['nonlinear_cases']:
  for epsilon in policy['nonlinear_epsilon']:
   for sign in [-1,1]:
    try:r=nonlinear(by_id[identity],inputs['parameters'],epsilon,sign);r['status']='completed'
    except Exception as exc:r={'case':identity,'epsilon':epsilon,'sign':sign,'status':'failed','exception':repr(exc)}
    nonlinear_rows.append(r);print(identity,'perturbation',epsilon,sign,r['status'],flush=True)
 result={'kind':'independent-transverse-diagnosis','candidate_integrations':0,'variational':rows,'nonlinear':nonlinear_rows,'analytic_derivative_checks':checks}
 with output.open('xb') as f:f.write(gzip.compress((json.dumps(result,indent=2)+'\n').encode(),mtime=0))
 if any(r['status']!='completed' for r in rows+nonlinear_rows):raise SystemExit(2)

if __name__=='__main__':main(Path(sys.argv[1]))
