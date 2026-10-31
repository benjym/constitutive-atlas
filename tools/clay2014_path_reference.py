"""Independent fixed-plane clay2014 finite paths; stdlib Cartesian RK4 only.
No DSL/compiler/common solver imports. The sole constitutive dependency is the
frozen literal-four-index tools.reference_clay2014_cartesian rate oracle.
"""
import copy
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
from tools import reference_clay2014_cartesian as source

SOURCE_ORACLE_SHA256='0bc6e129d836fbe9f17b176eb1bcfe6728c4a9293db37c3449d67a39d044465c'
Q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
POLICY={
 'reference':'all caller points from original initial; independent full-state fixed-step RK4',
 'tolerances':[1e-4,1e-6,1e-8],
 'stress_relative_budgets':[2e-3,1e-4,8e-6],
 'void_absolute_budgets':[5e-6,3e-7,2e-8],
 'stress_scale':'max(1 Pa,Frobenius original supplied stress), fixed per case',
 'reference_budget_fraction':.1,
 'reference_uncertainty':'max finest-minus-middle and middle-minus-coarse, observed only; no rigorous bound',
 'reference_shrink':'finest-middle <= .35*(middle-coarse) unless both below roundoff floor',
 'stress_roundoff_floor_relative':5e-12,
 'void_roundoff_floor_absolute':5e-13,
 'covariance_stress_relative':2e-10,
 'covariance_void_absolute':2e-12,
 'volume_absolute':2e-12,
 'caller_partition_shrink':'tight endpoint n1/n7 discrepancy <= .35*loose + 2*roundoff floor; no reference uncertainty term',
 'compiled_refinement':'each successor <= .65*predecessor and tight <= .35*loose, each plus 2*(roundoff floor + observed reference uncertainty)',
 'support':'every RK4 stage and returned state must pass the independent source domain; no clipping/projection',
 'admission':False,
}

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def exact(v):
 f=Fraction(v);return {'numerator':str(f.numerator),'denominator':str(f.denominator)}
def unexact(v):return Fraction(int(v['numerator']),int(v['denominator']))
def split_increment(increment,n):
 if type(n)is not int or n not in(1,7):raise ValueError('caller partitions1or7')
 if len(increment)!=6 or any(type(v)not in(int,float)or not math.isfinite(v)for v in increment):raise ValueError('finite loading6')
 pieces=[[float(x/n)for x in increment]for _ in range(n-1)]
 residual=[]
 for j,x in enumerate(increment):
  f=Fraction(x)-sum((Fraction(p[j])for p in pieces),Fraction())
  v=float(f)
  if not math.isfinite(v)or Fraction(v)!=f:raise ValueError('residual not exactly representable; do not repair path')
  residual.append(v)
 return pieces+[residual]

def schedule(increments,n):
 cumulative=[Fraction()for _ in range(6)];out=[]
 for segment,inc in enumerate(increments,1):
  for caller,piece in enumerate(split_increment(inc,n),1):
   cumulative=[a+Fraction(b)for a,b in zip(cumulative,piece)]
   out.append({'segment':segment,'caller':caller,'increment':piece,'cumulative_loading_exact':[exact(x)for x in cumulative]})
 return out

def inputs():
 p=source.default_parameters();z=[120000.,90000.,80000.,3000.,-2000.,1000.,.65]
 incs=[[.006,-.002,.001,.002,-.001,.0015],[-.004,.001,-.0005,-.001,.0008,-.001],[.001,.003,-.001,-.001,.0015,.0007]]
 base=[{'id':'vertical-nonproportional','parameters':p,'initial':z,'increments':incs}]
 p2=p|dict(n1=1/3,n2=2/3,n3=2/3)
 base.append({'id':'oblique-reversal','parameters':p2,'initial':z.copy(),'increments':copy.deepcopy(incs)})
 rotated_p=p2|dict(zip(('n1','n2','n3'),[math.fsum(Q[i][j]*p2[f'n{j+1}']for j in range(3))for i in range(3)]))
 rot=lambda v:source.to_mandel(source.rotate(source.from_mandel(v),Q))
 base.append({'id':'rotated-oblique-reversal','parameters':rotated_p,'initial':rot(z[:6])+[z[6]],'increments':[rot(v)for v in incs],'rotation_of':'oblique-reversal','rotation':Q})
 pi=p|dict(alpha_G=1.,alpha_E=1.,alpha_nu=1.,nu_pp=0.)
 base.append({'id':'isotropic-ratios-hydro-reversal','parameters':pi,'initial':[1e5]*3+[0.]*3+[.65], 'increments':[[.003]*3+[0.]*3,[-.002]*3+[0.]*3,[.0015]*3+[0.]*3],'scalar_isotropic':True})
 for case in base:case['parameters']['p_scale']=max(1.,math.hypot(*case['initial'][:6]))
 return copy.deepcopy(base)

def cartesian_state(state):
 a=source.from_mandel(state[:6]);return[a[0][0],a[1][1],a[2][2],a[0][1],a[1][2],a[0][2],state[6]]
def mandel_state(y):return[y[0],y[1],y[2],math.sqrt(2)*y[3],math.sqrt(2)*y[4],math.sqrt(2)*y[5],y[6]]
def rhs(y,de,p,monitor=None):
 a=[[y[0],y[3],y[5]],[y[3],y[1],y[4]],[y[5],y[4],y[2]]]
 out=source.rate(a,source.from_mandel(de),y[6],[p[f'n{i}']for i in(1,2,3)],**{k:p[k]for k in('phi_c','lambda_star','kappa_star','N','nu_pp','alpha_G','alpha_E','alpha_nu','source_a')})
 if monitor is not None:
  norm=math.hypot(*(v for row in a for v in row));b=[[v/norm for v in row]for row in a];d=out['diagnostics']
  metrics={'void_ratio':y[6],'normalized_stress_leading1':b[0][0],'normalized_stress_leading2':b[0][0]*b[1][1]-b[0][1]**2,'normalized_stress_determinant':source.determinant(b),'omega':d['omega'],'fd':d['fd'],'fdA':d['fdA'],'fs':d['fs'],'one_minus_Fm':1-d['Fm']}
  monitor['rate_evaluations']+=1
  for name,value in metrics.items():monitor['minimum'][name]=min(monitor['minimum'].get(name,value),value)
  if min(metrics['normalized_stress_leading1'],metrics['normalized_stress_leading2'],metrics['normalized_stress_determinant'])<=64*math.ulp(1.):raise ValueError('stress leaves declared interior numerical margin')
 r=out['stress_rate'];return[r[0][0],r[1][1],r[2][2],r[0][1],r[1][2],r[0][2],out['e_rate']]
def checked_state(y,p,monitor=None):
 if any(not math.isfinite(v)for v in y):raise ValueError('nonfinite RK4 state')
 rhs(y,[0.]*6,p,monitor)

def rk4(case,n,steps):
 if type(steps)is not int or steps<=0:raise ValueError('positive fixed steps')
 monitor={'rate_evaluations':0,'minimum':{}}
 y=cartesian_state(case['initial']);p=case['parameters'];checked_state(y,p,monitor);trajectory=[]
 for knot in schedule(case['increments'],n):
  de=knot['increment'];h=1/steps
  for _ in range(steps):
   k1=rhs(y,de,p,monitor);k2=rhs([a+h*b/2 for a,b in zip(y,k1)],de,p,monitor)
   k3=rhs([a+h*b/2 for a,b in zip(y,k2)],de,p,monitor);k4=rhs([a+h*b for a,b in zip(y,k3)],de,p,monitor)
   y=[a+h*math.fsum((b,2*c,2*d,e))/6 for a,b,c,d,e in zip(y,k1,k2,k3,k4)]
   checked_state(y,p,monitor)
  trajectory.append({'segment':knot['segment'],'caller':knot['caller'],'state':mandel_state(y)})
 return {'trajectory':trajectory,'stage_domain':monitor}

def scalar_trajectory(case,n):
 """Exact real hydro solution evaluated in binary64; no claim exact rounding."""
 p=case['parameters'];z=case['initial'];la=p['lambda_star'];ka=p['kappa_star'];a=source.evaluate({'parameters':p,'state':z,'increment':[0.]*6})['diagnostics']['alpha_f']
 if any(p[k]!=1 for k in('alpha_G','alpha_E','alpha_nu'))or z[0]!=z[1]or z[1]!=z[2]or any(z[3:6]):raise ValueError('isotropic-ratio/hydro initial required')
 pe0=1000*math.exp((p['N']-math.log1p(z[6]))/la);pressure=z[0];pe=pe0;y=(pe/pressure)**a;volume=Fraction();out=[]
 for knot in schedule(case['increments'],n):
  de=knot['increment']
  if de[0]!=de[1]or de[1]!=de[2]or any(de[3:]):raise ValueError('hydro increments required')
  vf=sum((Fraction(x)for x in de[:3]),Fraction());v=float(vf);s=1 if v>0 else -1 if v<0 else 0
  if s:
   # Stable y+(y-s)*expm1 avoids discarding small represented changes.
   y=y+(y-s)*math.expm1(-a*.5*(1/ka-1/la)*v)
   if not math.isfinite(y)or y<=0:raise ValueError('hydro scalar solution leaves positive y domain')
  volume+=vf;pe=pe0*math.exp(float(volume)/la);pressure=pe*math.exp(-math.log(y)/a)
  e=(1+z[6])*math.exp(-float(volume))-1
  state=[pressure]*3+[0.]*3+[e];checked_state(cartesian_state(state),p)
  out.append({'segment':knot['segment'],'caller':knot['caller'],'state':state})
 return out

def errors(a,b):
 if len(a)!=len(b):raise ValueError('trajectory length')
 out=[]
 for x,y in zip(a,b):
  if(x['segment'],x['caller'])!=(y['segment'],y['caller']):raise ValueError('unaligned trajectories')
  out.append({'segment':x['segment'],'caller':x['caller'],'stress_Pa':math.hypot(*(u-v for u,v in zip(x['state'][:6],y['state'][:6]))),'void_ratio':abs(x['state'][6]-y['state'][6])})
 return out

def study():
 if digest(source.__file__)!=SOURCE_ORACLE_SHA256:raise ValueError('frozen constitutive oracle hash mismatch')
 cases=[]
 for inp in inputs():
  scale=max(1.,math.hypot(*inp['initial'][:6]))
  for n in(1,7):
   steps=[28,56,112]if n==1 else[4,8,16]
   grids=[{'steps_per_piece':s,'nominal_steps_per_segment':s*n,**rk4(inp,n,s)}for s in steps]
   coarse=errors(grids[0]['trajectory'],grids[1]['trajectory']);fine=errors(grids[1]['trajectory'],grids[2]['trajectory'])
   scalar=scalar_trajectory(inp,n)if inp.get('scalar_isotropic')else None
   volume=[]
   for knot,obs in zip(schedule(inp['increments'],n),grids[-1]['trajectory']):
    V=sum((unexact(x)for x in knot['cumulative_loading_exact'][:3]),Fraction());target=(1+inp['initial'][6])*math.exp(-float(V))-1
    volume.append(abs(obs['state'][6]-target))
   cases.append({'id':inp['id']+'-n'+str(n),'input':inp,'caller_partitions':n,'caller_points':schedule(inp['increments'],n),'stress_scale_Pa':scale,'grids':grids,'coarse_middle':coarse,'middle_fine':fine,'scalar_reference':scalar,'scalar_finest_errors':errors(grids[-1]['trajectory'],scalar)if scalar else None,'max_volume_error':max(volume)})
 covariance=[]
 for n in(1,7):
  a=next(c for c in cases if c['input']['id']=='oblique-reversal'and c['caller_partitions']==n)
  b=next(c for c in cases if c['input']['id']=='rotated-oblique-reversal'and c['caller_partitions']==n)
  rot=[o|{'state':source.to_mandel(source.rotate(source.from_mandel(o['state'][:6]),Q))+[o['state'][6]]}for o in a['grids'][-1]['trajectory']]
  covariance.append({'caller_partitions':n,'errors':errors(rot,b['grids'][-1]['trajectory']),'caveat':'rounded rotated initial/loading define slightly different exact binary64 inputs; empirical covariance check'})
 return {'cases':cases,'covariance':covariance}

def validate(result):
 for c in result['cases']:
  for coarse,fine in zip(c['coarse_middle'],c['middle_fine']):
   for k,floor in [('stress_Pa',POLICY['stress_roundoff_floor_relative']*c['stress_scale_Pa']),('void_ratio',POLICY['void_roundoff_floor_absolute'])]:
    if fine[k]>.35*coarse[k]and max(fine[k],coarse[k])>floor:raise ValueError('reference not shrinking above roundoff floor')
    budget=(POLICY['stress_relative_budgets'][-1]*c['stress_scale_Pa']if k=='stress_Pa'else POLICY['void_absolute_budgets'][-1])
    if max(fine[k],coarse[k])>POLICY['reference_budget_fraction']*budget:raise ValueError('reference differences exceed declared budget fraction')
  if c['max_volume_error']>POLICY['volume_absolute']:raise ValueError('volume closure')
  for e in c.get('scalar_finest_errors')or[]:
   if e['stress_Pa']>POLICY['covariance_stress_relative']*c['stress_scale_Pa']or e['void_ratio']>POLICY['volume_absolute']:raise ValueError('scalar solution discrepancy')
 for row in result['covariance']:
  scale=next(c['stress_scale_Pa']for c in result['cases']if c['input']['id']=='oblique-reversal')
  if any(e['stress_Pa']>POLICY['covariance_stress_relative']*scale or e['void_ratio']>POLICY['covariance_void_absolute']for e in row['errors']):raise ValueError('covariance')
 return result

def build_reference():
 out=validate(study())
 return {'version':'clay2014-fixed-plane-path-reference-v1','source_sha256':source.SOURCE_SHA256,'source_oracle_sha256':SOURCE_ORACLE_SHA256,'generator_sha256':digest(__file__),'input_sha256':hashlib.sha256(json.dumps(inputs(),sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),'policy_sha256':hashlib.sha256(json.dumps(POLICY,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest(),'dependencies':{'tools/reference_clay2014_cartesian.py':SOURCE_ORACLE_SHA256},'source_locators':['PDFp2Eqs2-6','PDFp3Eqs7-15','PDFp9Eqs34-47','PDFp10Eqs48-50'],'parameter_order':source.PARAMETER_ORDER,'basis':'symmetric_mandel','compression_positive':True,'zero_spin':True,'policy':POLICY,'rotation':Q,'claims':{'scientific_admission':False,'finite_common_solver_validated':False,'rigorous_error_bound':False,'material_axis_transport':False},**out}

def checked_reference(document):
 """Exact current replay; not a portable archive resolver or numerical comparator."""
 fresh=build_reference()
 dump=lambda d:json.dumps(d,sort_keys=True,separators=(',',':'),allow_nan=False)
 if dump(document)!=dump(fresh):raise ValueError('reference differs from fresh pinned independent replay')
 return document

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 args.output.write_text(json.dumps(build_reference(),indent=2,allow_nan=False)+'\n')
