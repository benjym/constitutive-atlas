"""Independent isotropic body-law reference; stdlib, no Atlas imports.

Medicus/Fellin2017 body Eqs1-10, Table1/2 and incompressible-grain closure.
Compression-positive, zero spin, dimensionless v=int tr(de). Not admission.
"""
import argparse,hashlib,json,math
from decimal import Decimal,localcontext
from pathlib import Path
VERSION='barodesy2017-isotropic-reference-v1'
SOURCE_SHA256='bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15'
REVIEWED_DEPENDENCIES={'models/research/barodesy2017/body-zero-spin.json': '16e0ef4de35ea1b47c4dc9122f01a264c56993d6851ba2387e974c0ff5f0af4f', 'docs/models/barodesy2017-implementation-checklist.md': '7c5d79c002e71865357314176fa78ae5799c2a747950f0e693a401ab58d95ce4', 'tools/reference_barodesy2017.py': '10c2dff77152a80abad3e8ad6b3b3965be7550b46e1154e7283712b0b2284f67'}
PARAMETER_NAMES=['phi_c','N','lambda_star','kappa_star','sigma_star']
SOILS={'London':dict(phi_c=math.radians(22.6),N=1.375,lambda_star=.11,kappa_star=.016),'Dresden':dict(phi_c=math.radians(35),N=.622,lambda_star=.038,kappa_star=.008),'Weald':dict(phi_c=math.radians(24),N=.8,lambda_star=.059,kappa_star=.018)}
PRESSURES=(25000.,100000.,400000.)
VOLUMETRIC_KNOTS=(0.,.005,.015,.03)
MATRIX=((1e-4,1),(1e-6,1),(1e-8,1),(1e-4,7),(1e-8,7))
# Global empirical acceptance suggestions, distinct from solver local tolerances.
PROPOSED_ENDPOINT_BOUNDS={1e-4:5e-3,1e-6:3e-4,1e-8:2e-5}

def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def finite(x):
 try:return type(x)in(int,float)and math.isfinite(x)
 except OverflowError:return False
def parameters(soil):return SOILS[soil].copy()
def validate(p,e,pars):
 if not finite(p)or p<=0 or not finite(e)or e<0:raise ValueError('research support p>0,e>=0')
 if type(pars)is not dict or set(pars)!=set(SOILS['London'])or not all(finite(v)for v in pars.values()):raise ValueError('four explicit finite parameters required')
 if not 0<pars['phi_c']<math.pi/2 or not 0<pars['kappa_star']<pars['lambda_star']:raise ValueError('parameter support')
def coefficients(pars):
 validate(1.,0.,pars);s=math.sin(pars['phi_c']);c5=(1+s)/(1-s);t=c5*pars['lambda_star'];rt3=math.sqrt(3.)
 c3=rt3*(1/pars['kappa_star']-1/pars['lambda_star'])/(math.expm1(t*math.log(2))+math.expm1(-t*math.log(500)))
 if not all(math.isfinite(v)for v in[c5,t,c3])or c5<=0:raise ValueError('coefficient arithmetic')
 return c5,t,c3

def scalar_slope(p,e,pars,direction):
 """d(log p)/dv for nonzero isotropic compression(+1)/expansion(-1)."""
 validate(p,e,pars)
 if type(direction)is not int or direction not in(-1,1):raise ValueError('direction must be integer +/-1')
 c5,t,c3=coefficients(pars);B=math.exp(t*math.log(2));K=c3/math.sqrt(3.)
 z=math.exp(c5*(math.log1p(e)-pars['N']+pars['lambda_star']*math.log(2*p/1000.)))
 result=1/pars['lambda_star']+K*(z-B) if direction>0 else 1/pars['kappa_star']-K*(B+z-2)
 if not math.isfinite(result):raise ValueError('nonfinite scalar slope')
 return result

def scalar_rate(p,e,dv,pars):
 validate(p,e,pars)
 if not finite(dv):raise ValueError('finite volumetric loading required')
 if dv==0:return dict(sigma_rhs=[0.]*6,e_rhs=0.)
 dp=p*dv*scalar_slope(p,e,pars,1 if dv>0 else-1);de=-(1+e)*dv
 if not all(math.isfinite(v)for v in[dp,de]):raise ValueError('nonfinite scalar rate')
 return dict(sigma_rhs=[dp]*3+[0.]*3,e_rhs=de)

def D(x):return Decimal.from_float(float(x))
def decimal_sin(x):
 term=x;total=x;k=1
 while True:
  term=-term*x*x/((2*k)*(2*k+1));previous=total;total+=term
  if total==previous:return total
  k+=1
  if k>1000:raise ValueError('Decimal sine budget')
def ncl_initial(soil,p0):
 pars=parameters(soil)
 if not finite(p0)or p0<=0:raise ValueError('positive finite pressure')
 with localcontext()as ctx:
  ctx.prec=100;q=(D(pars['N'])-D(pars['lambda_star'])*(D(p0)/1000).ln()).exp();e=float(q-1)
 validate(p0,e,pars);return [p0]*3+[0.]*3+[e]
def ncl_state(soil,p0,v,initial_e=None,precision=100):
 """Ideal NCL exponential trajectory from binary64 p0/e0; tiny initial
 manifold residual is preserved, not silently reset. Output is rounded once.
 """
 pars=parameters(soil);e0=ncl_initial(soil,p0)[6]if initial_e is None else initial_e
 validate(p0,e0,pars)
 if not finite(v)or type(precision)is not int or not 60<=precision<=180:raise ValueError('finite v; precision60..180')
 with localcontext()as ctx:
  ctx.prec=precision;vol=D(v);p=D(p0)*(vol/D(pars['lambda_star'])).exp();q=(1+D(e0))*(-vol).exp();e=q-1
  if e<0:raise ValueError('selected trajectory leaves e>=0 support')
  return [float(p)]*3+[0.]*3+[float(e)]
def rounded_initial_compression(soil,p0,e0,v,precision=100):
 """Exact scalar compression solution for actual rounded initial p0/e0.

 Uses the independent Bernoulli reduction of body isotropic ODE. This is
 NOT a general tensor update. Source coefficients use high-precision sin.
 """
 pars=parameters(soil);validate(p0,e0,pars)
 if not finite(v)or v<0 or type(precision)is not int or not 60<=precision<=180:raise ValueError('nonnegative v; precision60..180')
 with localcontext()as ctx:
  ctx.prec=precision;phi,N,la,ka=[D(pars[k])for k in('phi_c','N','lambda_star','kappa_star')];s=decimal_sin(phi);c5=(1+s)/(1-s);t=c5*la;B=(t*Decimal(2).ln()).exp();rt3=Decimal(3).sqrt()
  c3=rt3*(1/ka-1/la)/(B+(-t*Decimal(500).ln()).exp()-2);K=c3/rt3;vol=D(v)
  logz=c5*((1+D(e0)).ln()-N+la*(2*D(p0)/1000).ln());z0=logz.exp()
  bracket=1+(1-z0/B)*((t*K*B*vol).exp()-1)
  if bracket<=0:raise ValueError('scalar solution leaves positive pressure branch')
  p=D(p0)*(vol/la-bracket.ln()/t).exp();q=(1+D(e0))*(-vol).exp();e=q-1
  if e<0:raise ValueError('scalar solution leaves e>=0 support')
  return [float(p)]*3+[0.]*3+[float(e)]
def ncl_residual(state,pars):
 validate(sum(state[:3])/3,state[6],pars)
 with localcontext()as ctx:
  ctx.prec=100;p=sum((D(v)for v in state[:3]),Decimal(0))/3
  return float((1+D(state[6])).ln()+D(pars['lambda_star'])*(p/1000).ln()-D(pars['N']))

def rk4_scalar(initial,volumetric_increments,pars,steps_per_segment):
 """Independent scalar log-pressure RK4; exact volume closure at every stage.

 Each signed segment selects its own loading branch. Integrates actual
 initial p/e, no NCL reset; retains every original segment endpoint.
 """
 if type(initial)is not list or len(initial)!=7 or not all(finite(x)for x in initial)or initial[:3]!=[initial[0]]*3 or initial[3:6]!=[0.]*3:raise ValueError('isotropic7state required')
 p0=initial[0];e0=initial[6];validate(p0,e0,pars)
 if type(steps_per_segment)is not int or not 1<=steps_per_segment<=4096:raise ValueError('steps1..4096')
 if not isinstance(volumetric_increments,(list,tuple))or not volumetric_increments or not all(finite(v)and v!=0 for v in volumetric_increments):raise ValueError('nonzero finite signed segments')
 y=math.log(p0);v=0.;min_e=e0;min_p=p0;calls=0;trajectory=[dict(segment=0,v=0.,state=initial.copy())]
 for j,dv in enumerate(volumetric_increments,1):
  direction=1 if dv>0 else-1;h=dv/steps_per_segment;base=v
  def f(position,logp):
   nonlocal min_e,min_p,calls
   p=math.exp(logp);e=math.expm1(math.log1p(e0)-position);validate(p,e,pars);min_e=min(min_e,e);min_p=min(min_p,p);calls+=1
   return scalar_slope(p,e,pars,direction)
  for i in range(steps_per_segment):
   x=base+i*h;k1=f(x,y);k2=f(x+h/2,y+h*k1/2);k3=f(x+h/2,y+h*k2/2);k4=f(x+h,y+h*k3);y+=h*(k1+2*k2+2*k3+k4)/6
  v=base+dv;p=math.exp(y);e=math.expm1(math.log1p(e0)-v);validate(p,e,pars)
  trajectory.append(dict(segment=j,v=v,state=[p]*3+[0.]*3+[e]))
 return dict(steps_per_segment=steps_per_segment,trajectory=trajectory,stage_domains=dict(minimum_pressure=min_p,minimum_e=min_e,evaluations=calls))

def study():
 cases=[]
 for soil in SOILS:
  pars=parameters(soil)
  for p0 in PRESSURES:
   initial=ncl_initial(soil,p0);increments=[[float(b-a)/3]*3+[0.]*3 for a,b in zip(VOLUMETRIC_KNOTS,VOLUMETRIC_KNOTS[1:])];vs=[0.];total=Decimal(0)
   with localcontext()as ctx:
    ctx.prec=100
    for inc in increments:total+=sum((D(x)for x in inc[:3]),Decimal(0));vs.append(float(total))
   data=dict(id=f'{soil.lower()}-ncl-{int(p0)}pa',soil=soil,p0=p0,initial=initial,parameters=[pars[k]for k in PARAMETER_NAMES[:-1]]+[1000.],increments=increments,volumetric_knots=vs)
   exact=[]
   for i,v in enumerate(vs):
    state=ncl_state(soil,p0,v,initial[6]);actual=rounded_initial_compression(soil,p0,initial[6],v)
    exact.append(dict(segment=i,v=v,state=state,rounded_initial_exact=actual,ncl_residual=ncl_residual(state,pars),rounding_correction_stress=max(abs(a-b)for a,b in zip(state[:6],actual[:6]))))
   cases.append(dict(input=data,input_sha256=digest(data),exact=exact))
 scalar=[]
 for soil in SOILS:
  for kind,segments,mult in [('off-ncl-compression',[.005,.01,.015],.9),('ncl-reversal',[.01,-.002,.005],1.)]:
   initial=ncl_initial(soil,100000.);initial[6]=(1+initial[6])*mult-1;pars=parameters(soil);grids=[rk4_scalar(initial,segments,pars,n)for n in(16,32,64)]
   differences=[]
   for a,b in zip(grids,grids[1:]):differences.append(max(abs(x['state'][0]-y['state'][0])for x,y in zip(a['trajectory'],b['trajectory'])))
   scalar.append(dict(id=soil.lower()+'-'+kind,initial=initial,parameters=[pars[k]for k in PARAMETER_NAMES[:-1]]+[1000.],volumetric_increments=segments,grids=grids,successive_pressure_differences=differences,observed_ratio=differences[0]/differences[1]if differences[1]>0 else None))
 return dict(contract=VERSION,source_sha256=SOURCE_SHA256,reviewed_dependency_sha256=REVIEWED_DEPENDENCIES,source_locators=['bodyEqs1-10 pp366-367','Table1 p367','Table2 p368','Eq8 body2p distinct from NCLp and App41 6p','footnote13 p374 incompressible grains'],generator_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),reference_numerical_floor=dict(stress_pa=1e-7,e=1e-14),public_admission=False,full_model=False,parameter_names=PARAMETER_NAMES,state_layout=['sigma_xx','sigma_yy','sigma_zz','sigma_xy_mandel','sigma_yz_mandel','sigma_xz_mandel','e'],basis='symmetric_mandel',compression_positive=True,zero_spin=True,coordinate=dict(name='v',unit='1',meaning='integrated_compression_positive_volumetric_stretching'),matrix=[dict(tolerance=t,partitions=n)for t,n in MATRIX],proposed_endpoint_scaled_bounds=[dict(tolerance=t,bound=b)for t,b in PROPOSED_ENDPOINT_BOUNDS.items()],cases=cases,scalar_diagnostics=scalar,limits=['Ideal NCL exponential solution is exact mathematically; input/output binary64 rounding is retained and measured separately.','Rounded-initial compression correction solves only the independent scalar isotropic ODE.','RK4 grid differences/ratios are observed indicators, not rigorous error bounds.','Reversal does not generally follow NCL nor universal unloading1/kappa.','No native integration, nonisotropic finite paths, finite spin, experiments or model admission.'])
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.write_text(json.dumps(study(),indent=2,allow_nan=False)+'\n')
