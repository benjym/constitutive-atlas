"""Independent caller-point references; source-only, no generated-state inputs."""
import hashlib,json,math,pathlib
from decimal import Decimal,localcontext,Inexact
from fractions import Fraction
from tools import reference_barodesy2017_wider_paths as base
ROOT=pathlib.Path(__file__).resolve().parents[1]
PROTOCOL=ROOT/'catalogue/investigations/barodesy2017-wider-caller-reference-v1/protocol.json'
FROZEN=ROOT/'catalogue/investigations/barodesy2017-wider-caller-reference-v1/reference.json'
VERSION='barodesy2017-independent-caller-points-v1'
STRESS_BOUNDS=(.005,.0003,.00002)
VOID_BOUNDS=(5e-5,3e-6,2e-7)
GRIDS=(4,8,16)
def exact_decimal(q):
 # Binary64-derived fractions terminate in base10. Bound precision from the
 # exact integers, trapping accidental rounding rather than claiming exactness.
 with localcontext()as ctx:
  ctx.prec=len(str(abs(q.numerator)))+q.denominator.bit_length()+10
  ctx.traps[Inexact]=True
  return str(Decimal(q.numerator)/Decimal(q.denominator))
def split_path(increments,partitions):
 if type(partitions)is not int or partitions not in(1,7):raise ValueError('predeclared partitions1or7')
 pieces=[];points=[];cumulative=[Fraction(0)]*6
 for j,inc in enumerate(increments,1):
  if type(inc)is not list or len(inc)!=6 or not all(base.finite(x)for x in inc):raise ValueError('six finite actualincrements')
  first=[float(x)/partitions for x in inc]
  remaining=[Fraction.from_float(float(x))-(partitions-1)*Fraction.from_float(y)for x,y in zip(inc,first)]
  last=list(map(float,remaining))
  if any(Fraction.from_float(x)!=y for x,y in zip(last,remaining)):raise ValueError('exactresidualsplitnotrepresentable')
  for k in range(1,partitions+1):
   piece=last[:]if k==partitions else first[:];pieces.append(piece)
   for i,v in enumerate(piece):cumulative[i]+=Fraction.from_float(v)
   points.append({'original_segment':j,'caller_piece':k,'original_endpoint':k==partitions,'increment':piece[:],'cumulative_strain_decimal':list(map(exact_decimal,cumulative)),'display_strain':list(map(float,cumulative))})
 return pieces,points

def fixed_scale(initial):return max(1.,math.hypot(*initial[:6]))
def eligibility(stress_difference_pa,void_difference,scale):
 stress_limit=.1*min(STRESS_BOUNDS)*scale;void_limit=.1*min(VOID_BOUNDS)
 if not all(base.finite(x)for x in(stress_difference_pa,void_difference,scale))or not(0<=stress_difference_pa<=stress_limit and 0<=void_difference<=void_limit and scale>0):raise ValueError('independentcallerreferenceuncertaintyexceedsbudget')
 return stress_limit,void_limit

def scalar_case(c,n):
 pieces,points=split_path(c['increments'],n);a=base.scalar_path_actual_mandel(c['initial'],pieces,c['parameters'],100);b=base.scalar_path_actual_mandel(c['initial'],pieces,c['parameters'],160)
 stress=max(math.hypot(*(x-y for x,y in zip(a0[:6],b0[:6])))for a0,b0 in zip(a,b));void=max(abs(x[6]-y[6])for x,y in zip(a,b));scale=fixed_scale(c['initial']);sl,vl=eligibility(stress,void,scale)
 return {'id':c['id'],'partitions':n,'initial':c['initial'],'parameters':c['parameters'],'initial_stress_scale_pa':scale,'points':[{'index':0,'state100':a[0],'state160':b[0]}]+[point|{'index':i,'state100':x,'state160':y}for i,(point,x,y)in enumerate(zip(points,a[1:],b[1:]),1)],'maximum_precision_stress_difference_pa':stress,'maximum_precision_void_difference':void,'stress_reference_eligibility_limit_pa':sl,'void_reference_eligibility_limit':vl,'reference_eligible':True}
def tensor_case(c,n):
 pieces,points=split_path(c['increments'],n);grids=[base.rk4_tensor(c['initial'],pieces,c['parameters'],k*7//n)for k in GRIDS];diffs=[];void=[]
 for a,b in zip(grids,grids[1:]):
  diffs.append(max(math.hypot(*(x-y for x,y in zip(z[:6],w[:6])))for z,w in zip(a['trajectory'],b['trajectory'])));void.append(max(abs(z[6]-w[6])for z,w in zip(a['trajectory'],b['trajectory'])))
 scale=fixed_scale(c['initial']);stress_limit,void_limit=eligibility(diffs[-1],void[-1],scale)
 return {'id':c['id'],'partitions':n,'initial':c['initial'],'parameters':c['parameters'],'initial_stress_scale_pa':scale,'points':[{'index':0,'state':grids[-1]['trajectory'][0]}]+[point|{'index':i,'state':z}for i,(point,z)in enumerate(zip(points,grids[-1]['trajectory'][1:]),1)],'grids':grids,'maximum_callerpoint_stress_differences_pa':diffs,'maximum_callerpoint_void_differences':void,'stress_reference_eligibility_limit_pa':stress_limit,'void_reference_eligibility_limit':void_limit,'reference_eligible':True}
def study():
 return {'version':VERSION,'scope':'Independentreferences only; no generatedstate, native/Wasm execution, modeladmission or sourceversionchange','constitutive_dependency_sha256':{name:hashlib.sha256(pathlib.Path(module.__file__).read_bytes()).hexdigest()for name,module in [('tools/reference_barodesy2017.py',base.cartesian),('tools/barodesy2017_isotropic_reference.py',base.scalar)]},'base_reference_script_sha256':hashlib.sha256(pathlib.Path(base.__file__).read_bytes()).hexdigest(),'generator_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'protocol_sha256':hashlib.sha256(PROTOCOL.read_bytes()).hexdigest(),'scalar_cases':[scalar_case(c,n)for c in base.scalar_cases()for n in(1,7)],'tensor_cases':[tensor_case(c,n)for c in base.tensor_cases()for n in(1,7)]}
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(study(),indent=2,allow_nan=False)+'\n')
