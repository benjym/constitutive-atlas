"""Independent wider body-law paths; no Atlas/model/compiler/native imports.
Scalar exact branch reduction + full7state fixed-grid RK4 of Cartesian oracle.
"""
import copy,hashlib,json,math,pathlib
from decimal import Decimal,localcontext
from tools import reference_barodesy2017 as cartesian
from tools import barodesy2017_isotropic_reference as scalar
VERSION='barodesy2017-wider-path-independent-v1'
SOURCE_SHA256='bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15'
D=Decimal.from_float
GRIDS=(8,16,32,64)
def finite(x):
 try:return type(x)in(int,float)and math.isfinite(x)
 except OverflowError:return False
def validate_initial(initial):
 if type(initial)is not list or len(initial)!=7 or not all(finite(x)for x in initial):raise ValueError('seven finite binary64 initial values')
 # Existing independent Cartesian rate performs SPD/local arithmetic checks.
 return initial

def _scalar_segment_decimal(initial,v,parameters):
 phi,N,la,ka=[D(float(parameters[k]))for k in('phi_c','N','lambda_star','kappa_star')];sp=scalar.decimal_sin(phi);c5=(1+sp)/(1-sp);t=c5*la;B=(t*Decimal(2).ln()).exp();Cext=(-t*Decimal(500).ln()).exp();K=(1/ka-1/la)/(B+Cext-2)
 if v==0:return initial[:]
 z0=(c5*((1+initial[6]).ln()-N+la*(2*initial[0]/1000).ln())).exp();equilibrium=B if v>0 else Cext;exponent=(t*K*equilibrium if v>0 else -t*K*equilibrium)*v;bracket=1+(1-z0/equilibrium)*(exponent.exp()-1)
 if bracket<=0:raise ValueError('scalar positive-pressure branch failed')
 p=initial[0]*(v/la-bracket.ln()/t).exp();e=(1+initial[6])*(-v).exp()-1
 if p<=0 or e<0:raise ValueError('scalar endpoint outside positivepressure/e>=0 support')
 return [p]*3+[Decimal(0)]*3+[e]
def scalar_segment(initial,dv,parameters,precision=100):
 """Exact signed scalar branch from actual rounded initial values, rounded once."""
 validate_initial(initial)
 if initial[:3]!=[initial[0]]*3 or initial[3:6]!=[0.]*3:raise ValueError('isotropic initial stress')
 scalar.validate(initial[0],initial[6],parameters)
 if not finite(dv)or type(precision)is not int or not 80<=precision<=180:raise ValueError('finite dv and precision80..180')
 if dv==0:return initial.copy()
 with localcontext()as ctx:
  ctx.prec=precision;return list(map(float,_scalar_segment_decimal(list(map(lambda x:D(float(x)),initial)),D(float(dv)),parameters)))
def scalar_path(initial,increments,parameters,precision=100):
 scalar_segment(initial,0.,parameters,precision)
 if not isinstance(increments,(list,tuple))or not all(finite(x)for x in increments):raise ValueError('finite scalar increments')
 with localcontext()as ctx:
  ctx.prec=precision;state=list(map(lambda x:D(float(x)),initial));rows=[initial.copy()]
  for dv in increments:state=_scalar_segment_decimal(state,D(float(dv)),parameters);rows.append(list(map(float,state)))
  return rows

def scalar_path_actual_mandel(initial,increments,parameters,precision=100):
 scalar_segment(initial,0.,parameters,precision)
 with localcontext()as ctx:
  ctx.prec=precision;state=list(map(lambda x:D(float(x)),initial));rows=[initial.copy()]
  for inc in increments:
   if type(inc)is not list or len(inc)!=6 or inc[:3]!=[inc[0]]*3 or inc[3:]!=[0.]*3 or not all(finite(x)for x in inc):raise ValueError('actual isotropic Mandel increments')
   vol=sum((D(float(x))for x in inc[:3]),Decimal(0));state=_scalar_segment_decimal(state,vol,parameters);rows.append(list(map(float,state)))
  return rows

def scalar_cases():
 out=[]
 for soil,pars in cartesian.SOILS.items():
  initial=scalar.ncl_initial(soil,100000.);initial[6]=(1+initial[6])*.9-1
  for name,segments in [('off-ncl-compression',[.005,.01,.015]),('off-ncl-reversal',[.01,-.004,.006])]:out.append(dict(id=soil.lower()+'-'+name,initial=initial,parameters=pars,volumetric_increments=segments,increments=[[v/3]*3+[0.]*3 for v in segments],initial_preparation='p0=100000Pa; e0 roundedNCL then binary64(1+e0)*0.9−1; supplied state, no hidden path'))
 return out

def tensor_cases():
 p=cartesian.SOILS['London'];initial=[120000.,80000.,100000.,2000.,-3000.,4000.,.8]
 inc=[[.004,-.001,-.001,.0008,-.0004,.0003],[.001,.002,-.001,-.0005,.0002,.0004],[-.002,.0005,.0005,-.0004,.0002,-.00015]]
 q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
 return [dict(id='london-nonproportional',initial=initial,parameters=p,increments=inc),dict(id='london-nonproportional-rotated',initial=cartesian.rotate(initial[:6],q)+[initial[6]],parameters=p,increments=[cartesian.rotate(x,q)for x in inc])]

def rk4_tensor(initial,increments,parameters,steps_per_segment,precision=100):
 validate_initial(initial)
 if type(steps_per_segment)is not int or not 1<=steps_per_segment<=4096:raise ValueError('steps1..4096')
 if type(increments)is not list or not increments or any(type(x)is not list or len(x)!=6 or not all(finite(v)for v in x)for x in increments):raise ValueError('explicit finite six-component increments')
 state=initial.copy();rows=[state.copy()];actual_loading=[];calls=0;minimum_e=state[6];minimum_pressure=sum(state[:3])/3;minimum_sylvester=[math.inf]*3
 def slope(z,inc):
  nonlocal calls,minimum_e,minimum_pressure
  validate_initial(z);out=cartesian.rate({'sigma':z[:6],'e':z[6]},inc,parameters,precision);calls+=1;minimum_e=min(minimum_e,z[6]);minimum_pressure=min(minimum_pressure,sum(z[:3])/3)
  a=cartesian.cart(z[:6]);minors=[a[0][0],a[0][0]*a[1][1]-a[0][1]**2,a[0][0]*(a[1][1]*a[2][2]-a[1][2]**2)-a[0][1]*(a[0][1]*a[2][2]-a[0][2]*a[1][2])+a[0][2]*(a[0][1]*a[1][2]-a[0][2]*a[1][1])]
  for i,v in enumerate(minors):minimum_sylvester[i]=min(minimum_sylvester[i],v)
  return out['sigma_rhs']+[out['e_rhs']]
 for inc in increments:
  step=[v/steps_per_segment for v in inc]
  with localcontext()as ctx:
   ctx.prec=100;totals=[D(float(x))*steps_per_segment for x in step];actual_loading.append({'step':step,'segment_totals_decimal':list(map(str,totals)),'target_residual_decimal':[str(D(float(v))-x)for v,x in zip(inc,totals)]})
  for _ in range(steps_per_segment):
   a=slope(state,step);b=slope([x+y/2 for x,y in zip(state,a)],step);c=slope([x+y/2 for x,y in zip(state,b)],step);d=slope([x+y for x,y in zip(state,c)],step)
   candidate=[x+(a[i]+2*b[i]+2*c[i]+d[i])/6 for i,x in enumerate(state)]
   slope(candidate,[0.]*6) # Validate full endpoint as well as RK stages, no commit on failure.
   state=candidate
  rows.append(state.copy())
 with localcontext()as ctx:
  ctx.prec=100;vol=sum((sum((Decimal(x)for x in row['segment_totals_decimal'][:3]),Decimal(0))for row in actual_loading),Decimal(0));exact_void=float((1+D(float(initial[6])))*(-vol).exp()-1)
 return dict(steps_per_segment=steps_per_segment,trajectory=rows,actual_loading=actual_loading,cumulative_volumetric_decimal=str(vol),exact_final_void_actual_loading=exact_void,stage_support=dict(minimum_pressure=minimum_pressure,minimum_e=minimum_e,minimum_cartesian_leading_minors=minimum_sylvester,evaluations=calls))

def study():
 scalar_rows=[]
 for c in scalar_cases():
  with localcontext()as ctx:
   ctx.prec=100;actual=[sum((D(float(x))for x in inc[:3]),Decimal(0))for inc in c['increments']]
  actual64=list(map(float,actual));exact100=scalar_path_actual_mandel(c['initial'],c['increments'],c['parameters'],100);exact160=scalar_path_actual_mandel(c['initial'],c['increments'],c['parameters'],160);grids=[scalar.rk4_scalar(c['initial'],actual64,c['parameters'],n)for n in GRIDS]
  scalar_rows.append(c|{'actual_volumetric_decimal':list(map(str,actual)),'scalar_RK4_volumetric_inputs':actual64,'scalar_RK4_trace_rounding_discrepancy_decimal':[str(x-D(float(y)))for x,y in zip(actual,actual64)],'branch_exact_100':exact100,'branch_exact_160':exact160,'scalar_rk4_grids':grids,'maximum_exact_precision_difference':max(abs(a-b)for x,y in zip(exact100,exact160)for a,b in zip(x,y))})
 tensor_rows=[]
 for c in tensor_cases():
  grids=[rk4_tensor(c['initial'],c['increments'],c['parameters'],n)for n in GRIDS];differences=[]
  for a,b in zip(grids,grids[1:]):differences.append(max(math.hypot(*(x-y for x,y in zip(s[:6],t[:6])))for s,t in zip(a['trajectory'],b['trajectory'])))
  total=sum(sum(inc[:3])for inc in c['increments']);void_exact=math.expm1(math.log1p(c['initial'][6])-total)
  tensor_rows.append(c|{'grids':grids,'successive_stress_endpoint_differences_pa':differences,'observed_last_ratio':differences[-2]/differences[-1]if differences[-1]>0 else None,'exact_void_at_nominal_binary64_total':void_exact,'final_RK4_void_errors':[abs(g['trajectory'][-1][6]-g['exact_final_void_actual_loading'])for g in grids]})
 return dict(version=VERSION,dependency_sha256={name:hashlib.sha256(pathlib.Path(module.__file__).read_bytes()).hexdigest()for name,module in [('tools/reference_barodesy2017.py',cartesian),('tools/barodesy2017_isotropic_reference.py',scalar)]},generator_sha256=hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),protocol_sha256=hashlib.sha256((pathlib.Path(__file__).resolve().parents[1]/'catalogue/investigations/barodesy2017-wider-reference-v1/protocol.json').read_bytes()).hexdigest(),source_url='https://doi.org/10.1007/s11440-016-0458-4',source_sha256=SOURCE_SHA256,source_locators=['bodyEqs1-10 pp366-367','Table2 p368','footnote13 p374; incompressible-grain void closure'],basis='symmetric_mandel',scope='Independent source mathematics and fixed-grid reference; not compiled integration/AD/admission',scalar_cases=scalar_rows,tensor_cases=tensor_rows)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--output',type=pathlib.Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(study(),indent=2,allow_nan=False)+'\n')
