"""Collect standard C API through a native shared library, without constitutive logic."""
from pathlib import Path
import ctypes,json,sys,hashlib,struct
B=Path(__file__).resolve().parent;req=json.loads((B/'requests.json').read_text());lib=ctypes.CDLL(sys.argv[1]);paramnames=list(req['cases'][0]['parameters'])
def csv(v):return ','.join(format(float(x),'.17g') for x in v)
def params(c):return c.get('parameters_csv',csv([c['parameters'][k] for k in paramnames]) if 'parameters' in c else '')
def call(name,types,args):
 f=getattr(lib,name);f.argtypes=types;f.restype=ctypes.c_char_p;raw=f(*[x.encode() if isinstance(x,str) else x for x in args]).decode();return dict(args=args,stdout=raw,response=json.loads(raw,parse_int=float))
S=ctypes.c_char_p;settings=csv(req['settings']);model=req['model']
def integrate(c,z=None,de=None,setting=None):return call('atlas_integrate_with_settings',[S]*5,[model,params(c),c.get('initial_csv',csv(z if z is not None else c.get('initial',[]))),c.get('de_csv',csv(de if de is not None else c.get('de',[]))),csv(setting) if setting is not None else settings])
def admissible(c,z):return call('atlas_study_admissible',[S]*2,[csv(z),params(c)])
def evaluate(c,z,zn,de):return call('atlas_evaluate',[S]*5,[model,params(c),csv(z),csv(zn),csv(de)])
base=req['cases'][0];recovery=lambda:integrate(base)
out=dict(backend='native',artifact_sha256=hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),requests_sha256=hashlib.sha256((B/'requests.json').read_bytes()).hexdigest(),describe=call('atlas_describe',[],[]))
out['cases']=[]
for c in req['cases']:
 a=integrate(c);b=integrate(c);r=a['response'];out['cases'].append(dict(id=c['id'],calls=[a,b],admissible=admissible(c,r['state']) if r['ok'] else None,residual=evaluate(c,r['state'],c['initial'],c['de']) if r['ok'] else None))
out['paths']=[]
for p in req['paths']:
 z=p['initial'];calls=[];holds=[];constraints=[]
 for de in p['increments']:
  a=integrate(p,z=z,de=de);calls.append(a);r=a['response']
  if not r['ok']:break
  z=r['state'];constraints.append(admissible(p,z));holds.append(integrate(p,z=z,de=[0.]*6))
 half=len(calls)//2;z=calls[half-1]['response']['state'] if half and calls[half-1]['response']['ok'] else p['initial'];restart=[]
 for de in p['increments'][half:]:
  a=integrate(p,z=z,de=de);restart.append(a)
  if not a['response']['ok']:break
  z=a['response']['state']
 out['paths'].append(dict(id=p['id'],calls=calls,holds=holds,constraints=constraints,restart=restart,restart_index=half))
out['transactions']=[dict(id=c['id'],call=integrate(c,setting=c['settings']),recovery=recovery()) for c in req['transactions']]
out['invalids']=[dict(id=c['id'],call=integrate(c),recovery=recovery()) for c in req['invalids']]
out['diagnostics']=[dict(id=c['id'],call=evaluate(c,c['current'],c['previous'],c['de'])) for c in req['diagnostics']]
out['derivatives']=[dict(id=c['id'],call=call('atlas_study_jacobian',[S]*4,[csv(c['current']),csv(c['previous']),csv(c['de']),params(c)])) for c in req['derivatives']]
def runpreset(c,initial=None,target=None,steps=None):return call('atlas_run_with_settings',[S,S,S,ctypes.c_int,ctypes.c_double,ctypes.c_int,ctypes.c_int,S],[model,params(c),csv(c['initial'] if initial is None else initial),c['protocol'],c['target'] if target is None else target,c['steps'] if steps is None else steps,c['cycles'],settings])
out['presets']=[]
for c in req['presets']:
 a=runpreset(c);points=a['response'].get('points',[]);half=c['steps']//2;mid=points[half]['state'] if len(points)>half else c['initial'];end=points[-1]['state'] if points else c['initial'];bad=c|{'parameters':c['parameters']|{'p_ref':0.}}
 out['presets'].append(dict(id=c['id'],call=a,replay=runpreset(c),hold=integrate(c,z=end,de=[0.]*6),restart=runpreset(c,mid,c['target']/2,half),invalid=runpreset(bad),recovery=runpreset(c)))
Path(sys.argv[2]).write_text(json.dumps(out,indent=2,allow_nan=False)+'\n');print('Saved native material API observations')
