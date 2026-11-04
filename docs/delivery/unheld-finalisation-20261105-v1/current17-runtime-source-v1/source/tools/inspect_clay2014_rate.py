"""Generic DSL evaluation of pinned2014 base-rate transcription; no material kernel."""
import json,math
from pathlib import Path
from atlas.dsl import FUNCTIONS,I,Sym,Type,ValidationError,dimensions,infer,parse
from atlas.history import _evaluate
from atlas.model import ROOT
FRAGMENT_PATH=ROOT/'catalogue/source-audits/clay-hypoplasticity-2014-base-rate.json'
SOURCE_SHA256='2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202'
PARAMETERS=('phi_c','lambda_star','kappa_star','N','nu_pp','alpha_G','alpha_E','alpha_nu','n1','n2','n3')
CONSTANTS={'p_ref':1000,'source_a':.3,'lode_roundoff_allowance':64*math.ulp(1.),'orientation_allowance':64*math.ulp(1.),'stress_interior_margin':64*math.ulp(1.)}

def scalar(x):
 try:
  if type(x)not in(int,float)or not math.isfinite(x)or float(x)!=x:raise ValidationError('finite binary64 real required')
  return float(x)
 except(OverflowError,ValueError)as error:raise ValidationError('finite binary64 real required')from error
def sym(x):
 v=x.v if isinstance(x,Sym)else x
 if not isinstance(v,(list,tuple))or len(v)!=6:raise ValidationError('six finite Mandel components required')
 return Sym(tuple(scalar(a)for a in v))
def validate_fragment(f):
 if f.get('fragment_version')!='clay2014-base-rate-0.1'or f.get('model_id')!='hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane':raise ValidationError('wrong explicit2014variant')
 if f['source']['sha256']!=SOURCE_SHA256 or f['source']['doi']!='10.1680/geot.13.P.065':raise ValidationError('wrong source')
 if set(f['inputs'])!={'sigma','stretching','e',*PARAMETERS}or set(f['constants'])!=set(CONSTANTS):raise ValidationError('explicit inputs/constants required')
 symbols={'I':Type('sym')}
 for n,spec in f['inputs'].items():
  want=Type('sym'if n in('sigma','stretching')else'scalar',dimensions('Pa'if n=='sigma'else'1'))
  actual=Type(spec['shape'],dimensions(spec['unit']))
  if want!=actual:raise ValidationError('wrong input type '+n)
  symbols[n]=actual
 for n,spec in f['constants'].items():
  if type(spec['value'])not in(int,float)or spec['value']!=CONSTANTS[n]:raise ValidationError('fixed source/numerical constant changed')
  actual=Type(spec['shape'],dimensions(spec['unit']));want=Type(dim=dimensions('Pa'if n=='p_ref'else'1'))
  if actual!=want:raise ValidationError('constant type')
  symbols[n]=actual
 for t in f['terms']:
  n=t['name']
  if n in symbols or n in FUNCTIONS or not n.isidentifier():raise ValidationError('duplicate/reserved term')
  actual=Type(t['shape'],dimensions(t['unit']))
  if infer(parse(t['expression']),symbols)!=actual:raise ValidationError('term type '+n)
  symbols[n]=actual
  if not t.get('locator','').strip():raise ValidationError('source locator required')
  for c in t.get('checks',[]):
   if infer(parse(c),symbols)!=Type('bool'):raise ValidationError('Boolean term check required')
 if f['outputs']!=['stress_rate','e_rate','linear_stress_rate','Am','Am_trace','Am_discrepancy','alpha_f']:raise ValidationError('required source diagnostics')
 return f

def load_fragment(path=FRAGMENT_PATH):return validate_fragment(json.loads(Path(path).read_text()))
def evaluate_rate(fragment,sigma,stretching,e,**parameters):
 """All typed terms; no state update, normalization, spin, IGS or hidden calibration."""
 validate_fragment(fragment)
 if set(parameters)!=set(PARAMETERS):raise ValidationError('exact explicit parameter set required')
 p={n:scalar(v)for n,v in parameters.items()};e=scalar(e);sigma=sym(sigma);stretching=sym(stretching)
 if not(e>=0 and p['lambda_star']>p['kappa_star']>0 and -1<p['nu_pp']<.5 and 0<p['phi_c']<math.pi/2 and min(p[n]for n in('alpha_G','alpha_E','alpha_nu'))>0):raise ValidationError('outside selected parameter support')
 if any(abs(p[n])>1 for n in('n1','n2','n3')):raise ValidationError('axis component outside[-1,1]')
 env=dict(I=I,sigma=sigma,stretching=stretching,e=e,**p,**CONSTANTS)
 exact_iso=sigma.v[0]==sigma.v[1]==sigma.v[2]and all(x==0 for x in sigma.v[3:])
 try:
  for t in fragment['terms']:
   n=t['name'];env[n]=_evaluate(parse(t['expression']),env)
   if n=='j2'and env[n]==0 and not exact_iso:raise ValidationError('nonisotropic invariant underflow; no spherical substitution')
   for c in t.get('checks',[]):
    if _evaluate(parse(c),env)is not True:raise ValidationError('domain at '+n)
 except(ArithmeticError,ValueError,TypeError)as error:raise ValidationError('undefined clay2014rate: '+str(error))from error
 return {t['name']:env[t['name']]for t in fragment['terms']}
