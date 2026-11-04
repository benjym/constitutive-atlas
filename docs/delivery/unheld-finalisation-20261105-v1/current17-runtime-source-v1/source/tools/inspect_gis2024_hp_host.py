"""Typed instantaneous HP/extracted-ASBS host fragment; no state integration."""
import json,math
from pathlib import Path
from atlas.dsl import Sym,I,Type,dimensions,infer,parse,ValidationError
from atlas.history import _evaluate as evaluate
ROOT=Path(__file__).resolve().parents[1]
def load_fragment():return json.loads((ROOT/'catalogue/source-audits/gis-2024-hp-extracted-asbs-host.json').read_text())
def real(x):
 try:good=type(x) in (int,float) and math.isfinite(x) and float(x)==x
 except (ValueError,OverflowError):good=False
 if not good:raise ValidationError('expected finite real, excluding bool')
 return float(x)
def finite(x):
 for v in x.v if isinstance(x,Sym) else (x,):real(v)
 return x
def validate_fragment(f):
 if f.get('id')!='hp-2024-extracted-asbs-supplied-gis-host' or f.get('candidate_id')!='hypoplastic-generalized-igs-2024':raise ValidationError('wrong host fragment identity')
 if f['source']['sha256']!='39ec8356a26b82ae651be8feb4cdb3e49bb86ded9a850adc4c7eee5e9ec3bdc3' or f['source']['doi']!='10.1016/j.compgeo.2024.106480':raise ValidationError('wrong host source identity')
 expected={'sigma','e','phi','hs','ei0','ec0','ed0','n','alpha','beta'}
 if set(f['inputs'])!=expected or f['outputs']!=['m','C','S','f'] or set(f['actions'])!={'L','L_inverse','E'}:raise ValidationError('incorrect host input/output/action names')
 symbols={'I':Type('sym')}
 for n,s in f['inputs'].items():
  typ=Type(s['shape'],dimensions(s['unit']))
  wanted=Type('sym' if n=='sigma' else 'scalar',dimensions('Pa' if n in ('sigma','hs') else '1'))
  if typ!=wanted:raise ValidationError('incorrect host input type: '+n)
  symbols[n]=typ
 for t in f['terms']:
  typ=infer(parse(t['expression']),symbols)
  if typ!=Type(t['shape'],dimensions(t['unit'])):raise ValidationError('term typing: '+t['name'])
  if t['name'] in symbols:raise ValidationError('duplicate name')
  symbols[t['name']]=typ
 for name,spec in f['actions'].items():
  if spec['argument']!={'name':'X','shape':'sym','unit':'1'} or Type(spec['shape'],dimensions(spec['unit']))!=Type('sym',dimensions('Pa' if name=='E' else '1')):raise ValidationError('incorrect host action type')
  arg=spec['argument'];typ=infer(parse(spec['expression']),symbols|{arg['name']:Type(arg['shape'],dimensions(arg['unit']))})
  if typ!=Type(spec['shape'],dimensions(spec['unit'])):raise ValidationError('action typing')
 return f

def host(f,**values):
 validate_fragment(f)
 if set(values)!=set(f['inputs']):raise ValidationError('exact explicit host inputs required')
 env={'I':I}
 for n,s in f['inputs'].items():
  x=values[n]
  if s['shape']=='sym':
   if not isinstance(x,Sym) or len(x.v)!=6:raise ValidationError('six Mandel components required')
   x=Sym(tuple(real(v) for v in x.v))
  else:x=real(x)
  env[n]=x
 if not (env['hs']>0 and 0<env['n']<1 and 0<env['phi']<math.pi/2 and env['alpha']>0 and env['beta']>=0 and 0<env['ed0']<env['ec0']<env['ei0'] and env['e']>0):raise ValidationError('outside audit parameter domain')
 positive={'p','Q','Fden','Frad','F','compression','ei','ec','ed','fd','fsden','fs','inverse_den','Bnorm','asbs_norm','fdAstar','C','S'}
 try:
  for t in f['terms']:
   name=t['name'];env[name]=finite(evaluate(parse(t['expression']),env))
   if name in positive and env[name]<=0:raise ValueError(name+' must be positive')
   if name=='j2' and env[name]==0 and not (env['sigma'].v[0]==env['sigma'].v[1]==env['sigma'].v[2] and all(x==0 for x in env['sigma'].v[3:])):raise ValueError('nonisotropic stress invariant underflow')
   if name=='cos3theta' and not -1-64*math.ulp(1.)<=env[name]<=1+64*math.ulp(1.):raise ValueError('unresolved Lode cosine')
   if name=='ed' and not env['ed']<env['e']<env['ei']:raise ValueError('void ratio outside selected audit domain')
   if name=='asbs_den' and env[name]==0:raise ValueError('Eq31 denominator zero')
 except (ArithmeticError,ValueError,TypeError) as exc:raise ValidationError('host arithmetic/domain failure: '+str(exc)) from exc
 def action(name,X):
  if not isinstance(X,Sym) or len(X.v)!=6:raise ValidationError('action requires Sym')
  X=Sym(tuple(real(v) for v in X.v))
  try:return finite(evaluate(parse(f['actions'][name]['expression']),env|{'X':X}))
  except (ArithmeticError,ValueError,TypeError) as exc:raise ValidationError('action arithmetic failure') from exc
 columns=[action('E',Sym(tuple(float(i==j) for i in range(6)))).v for j in range(6)]
 return dict(env=env,action=action,E=[[columns[j][i] for j in range(6)] for i in range(6)],**{n:env[n] for n in ('m','C','S','f')})
