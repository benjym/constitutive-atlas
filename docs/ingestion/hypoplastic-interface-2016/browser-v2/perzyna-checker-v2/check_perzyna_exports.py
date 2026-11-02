"""Prospective offline verifier of supplied Perzyna UI downloads; no engine/browser calls."""
from pathlib import Path
import argparse,hashlib,json,math,re,sys
MODEL='perzyna-comsol63-mises-perfect-zero-spin-ode'
REVISION='4e60096f3ab4535c53fd48ee92acb094b5682f4d'
ROOT=Path(__file__).resolve().parents[5]
POLICY=ROOT/'docs/ingestion/perzyna-comsol63/interface-v2/POLICY.json'
CASES=ROOT/'docs/ingestion/perzyna-comsol63/execution-v2/cases.json'
# Frozen from the exact committed source; populated before any new browser observation.
POLICY_SHA='6d60f8aead16f9c5c2b2c8c8baa8a637f115825a277ddace53ffa30d8dc6a629'
CASES_SHA='c7aa93e7533ba4b29279f41a83f4a18e29f1966129bb11794be55a15454b563e'
STABLE_IDENTITY_SHA='a6eea1eb28e0beebeaaacbc3e388c3ba0cddbac6af5fd93e0b51ff4eb2600317'
DEFAULTS={'mode':'relaxation','duration':2,'samples':4,'start':0,'parameters':[20e6,10e6,100000,.002,2],'initial':[.01,-.004,-.006,.002,-.001,.003,0,0,0,0,0,0,0],'rates':[.001,-.0002,.0003,.0007,-.0006,.0005]}
def require(ok,message):
 if not ok:raise ValueError(message)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stable_hash(identity):
 return hashlib.sha256(json.dumps({k:v for k,v in identity.items() if k!='release_revision'},sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def finite(x):return type(x) in (int,float) and math.isfinite(x)
def vector(x,n):return type(x) is list and len(x)==n and all(finite(v) for v in x)
def same(a,b):
 if type(a) in (int,float) and type(b) in (int,float):return finite(a) and finite(b) and a==b
 if type(a)!=type(b):return False
 if type(a) is dict:return set(a)==set(b) and all(same(a[k],b[k]) for k in a)
 if type(a) is list:return len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
 return a==b

def load(path):
 def pairs(items):
  d={}
  for k,v in items:require(k not in d,'Duplicate JSON key: '+k);d[k]=v
  return d
 def number(s):
  v=float(s);require(math.isfinite(v),'Nonfinite JSON number');return v
 def integer(s):
  v=int(s);require(abs(v)<=9007199254740991,'Unsafe JSON integer');return v
 return json.loads(path.read_text(),object_pairs_hook=pairs,parse_float=number,parse_int=integer,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Nonfinite JSON token: '+x)))

def frozen_inputs(source_root=ROOT):
 policy_path=source_root/POLICY.relative_to(ROOT);cases_path=source_root/CASES.relative_to(ROOT)
 require(digest(policy_path)==POLICY_SHA and digest(cases_path)==CASES_SHA,'Frozen policy/reference bytes changed')
 policy=load(policy_path);cases=load(cases_path)['cases']
 require(policy['accuracy']=={'state_absolute':3e-7,'stress_absolute_pa':3,'relative':2e-5},'Frozen numerical gate changed')
 return policy,{mode:next(c for c in cases if c['id']=='public-'+mode) for mode in ['relaxation','creep','rate']}

def validate_identity(identity,revision):
 require(type(identity) is dict and re.fullmatch('[0-9a-f]{40}',revision) is not None,'Expected exact source revision')
 require(identity.get('release_revision')==revision,'Package release_revision differs from requested source revision')
 require(stable_hash(identity)==STABLE_IDENTITY_SHA,'Accepted model/source/review/engine/component identities differ')

def check_package(package,revision):
 identity=load(package/'engine-perzyna/identity.json');validate_identity(identity,revision)
 files={'perzyna.mjs':'module_sha256','perzyna.wasm':'wasm_sha256','models.json':'catalogue_file_sha256',MODEL+'.json':'model_sha256','approval.json':'approval_sha256','review.json':'review_sha256','review.html':'review_html_sha256','source-receipts.json':'source_receipts_sha256','build-receipt.json':'build_receipt_sha256'}
 pins=[]
 for name,field in files.items():
  p=package/'engine-perzyna'/name;require(digest(p)==identity[field],'Package asset hash differs: '+name);pins.append({'path':'engine-perzyna/'+name,'sha256':digest(p)})
 for name,h in identity['component_sha256'].items():
  require(Path(name).name==name and re.fullmatch(r'[A-Za-z0-9._-]+\.mjs',name) is not None,'Unsafe component filename')
  require(digest(package/name)==h,'Package component hash differs: '+name);pins.append({'path':name,'sha256':h})
 return identity,pins

def validate_run(run,mode,identity,policy,reference):
 require(type(run) is dict and set(run)=={'controls','kind','provenance','request','result'},mode+': export shape')
 require(run['kind']=='atlas-perzyna-laboratory-v1' and same(run['provenance'],identity),mode+': kind/provenance differs')
 controls=dict(DEFAULTS,mode=mode);require(same(run['controls'],controls),mode+': exact public controls differ')
 spec=reference['specification'];require(same(controls['parameters'],spec['parameters']) and same(controls['initial'],spec['initial']),mode+': frozen controls/reference differ')
 request=run['request'];require(type(request) is dict and set(request)=={'function','args'} and request['function']=='atlas_run_schedule',mode+': request shape/function')
 args=request['args'];expected=list(reference['args'])
 # Exact UI transport (including zero pre-event strain rates), not the Python driver's17digit CSV serialization.
 expected[1]='20000000,10000000,100000,0.002,2'
 expected[2]='0.01,-0.004,-0.006,0.002,-0.001,0.003,0,0,0,0,0,0,0'
 expected[3]='0.01,-0.004,-0.006,0.002,-0.001,0.003';expected[4]='0,0,0,0,0,0'
 expected[5]='2,4,'+(','.join(['1,0,0' if mode=='creep' else '0,0,0']*6) if mode!='rate' else '0,1,0.001,0,1,-0.0002,0,1,0.0003,0,1,0.0007,0,1,-0.0006,0,1,0.0005')
 require(type(args) is list and len(args)==15 and all(type(v) is str for v in args[:7]) and all(finite(v) for v in args[7:]) and same(args,expected),mode+': exact full UI request differs')
 r=run['result'];keys={'ok','schema_version','units','model','catalogue_hash','message','start_time','parameters','initial','initial_strain','initial_strain_rate','solver','segments','points'}
 require(type(r) is dict and set(r)==keys and r['ok'] is True and r['message']=='',mode+': complete successful result required')
 require(r['model']==MODEL and r['catalogue_hash']==identity['catalogue_hash'] and r['units']=='SI' and r['schema_version']=='0.2',mode+': result identity/schema')
 for k in ['start_time','parameters','initial','initial_strain','segments']:require(same(r[k],spec[k]),mode+': result '+k+' differs')
 require(vector(r['initial_strain_rate'],6) and same(r['initial_strain_rate'],[0]*6),mode+': UI initial strain rate must be zero before segment-right event')
 require(same(r['solver'],dict(policy['solver'],maximum_depth=40)),mode+': solver differs')
 points=r['points'];require(type(points) is list and len(points)==6,mode+': complete six-point history required')
 checks=[];errors={'state':0.,'stress':0.}
 pointkeys={'time','segment','side','state','strain','strain_rate','observables','iterations','substeps','rejected','temporal_error_norm','nonlinear_residual_norm'}
 for i,p in enumerate(points):
  require(type(p) is dict and set(p)==pointkeys,mode+': point shape')
  time=0 if i<2 else (i-1)*.5
  require(finite(p['time']) and p['time']==time and type(p['segment']) is int and p['segment']==(-1 if i==0 else 0) and p['side']==('right' if i==1 else 'left'),mode+': point time/event')
  require(vector(p['state'],13) and vector(p['observables'],6) and vector(p['strain'],6),mode+': finite full state/stress/strain required')
  unresolved=i==1 and mode=='creep' and same(p['strain_rate'],[None]*6)
  require(unresolved or vector(p['strain_rate'],6),mode+': finite strain-rate or documented unresolved creep event required')
  # SchedulePoint initial_rate is the UI's zero vector; transition_controls then applies strain rates.
  if i==0 or mode=='relaxation':require(same(p['strain_rate'],[0]*6),mode+': prescribed initial/hold strain rate differs')
  elif mode=='rate':require(same(p['strain_rate'],controls['rates']),mode+': prescribed segment strain rate differs')
  elif mode=='creep' and i==1:require(unresolved,mode+': stress-controlled right event must expose six unresolved null rates')
  # Subsequent creep rates have no frozen independent rate oracle; retain strict finite shape only.
  require(same(p['strain'],p['state'][:6]),mode+': strain/state binding')
  require(p['state'][12]>=0 and abs(sum(p['state'][6:9]))<=1e-10,mode+': alpha/isochoric memory')
  if i<2:require(same(p['state'],controls['initial']),mode+': initial event changes history')
  for k in ['iterations','substeps','rejected']:require(type(p[k]) is int and p[k]>=0,mode+': invalid integer diagnostics')
  for k in ['temporal_error_norm','nonlinear_residual_norm']:require(finite(p[k]) and p[k]>=0,mode+': invalid finite diagnostics')
  matches=[v for v in reference['references'] if v['time']==time];require(len(matches)==1,mode+': frozen reference time ambiguous')
  for key,refkey,absolute,label in [('state','state',policy['accuracy']['state_absolute'],'state'),('observables','stress',policy['accuracy']['stress_absolute_pa'],'stress')]:
   want=matches[0][refkey];require(vector(want,13 if key=='state' else 6),mode+': invalid frozen vector')
   for j,(actual,target) in enumerate(zip(p[key],want)):
    error=abs(actual-target);tol=max(absolute,policy['accuracy']['relative']*abs(target));require(error<=tol,f'{mode}/point{i}/{key}{j}: error{error} exceeds{tol}')
    errors[label]=max(errors[label],error);checks.append({'point':i,'field':key,'component':j,'error':error,'tolerance':tol})
 return {'mode':mode,'points':6,'comparisons':len(checks),'max_errors':errors,'checks':checks}

def assess(identity,runs,revision,policy,references):
 validate_identity(identity,revision)
 require(set(runs)=={'relaxation','creep','rate','reset','replay'},'Require all five downloads')
 modes=[validate_run(runs[m],m,identity,policy,references[m]) for m in ['relaxation','creep','rate']]
 require(same(runs['relaxation'],runs['reset']) and same(runs['relaxation'],runs['replay']),'Fresh full parsed default/reset/replay differs')
 require(sum(x['comparisons'] for x in modes)==342,'Incomplete component comparison count')
 return {'status':'passed-offline-supplied-export-check','model':MODEL,'source_revision':revision,'modes':modes,'frozen_component_comparisons':342,'exact_default_reset_replay':True,'browser_provenance_established':False,'compiled_material_browser_calls':0,'scope':'Supplied-byte verification only; actual download provenance, visible controls, concurrency, network and live delivery require independent browser evidence.'}

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--package',required=True,type=Path);p.add_argument('--revision',default=REVISION);p.add_argument('--source-root',type=Path,default=ROOT,help='Source tree containing the exact frozen policy/references')
 for name in ['relaxation','creep','rate','reset','replay']:p.add_argument('--'+name,required=True,type=Path)
 p.add_argument('--output',required=True,type=Path);a=p.parse_args();require(not a.output.exists(),'Refuse to overwrite prior report')
 policy,references=frozen_inputs(a.source_root);identity,pins=check_package(a.package,a.revision)
 runs={k:load(getattr(a,k)) for k in ['relaxation','creep','rate','reset','replay']};report=assess(identity,runs,a.revision,policy,references)
 report.update(package_identity_sha256=digest(a.package/'engine-perzyna/identity.json'),checked_package_assets=pins,policy_sha256=POLICY_SHA,references_sha256=CASES_SHA,inputs={k:{'path':str(getattr(a,k).resolve()),'sha256':digest(getattr(a,k))} for k in runs})
 text=json.dumps(report,indent=2,allow_nan=False)+'\n'
 with a.output.open('x') as f:f.write(text)
 print(text,end='')
if __name__=='__main__':
 try:main()
 except (ValueError,KeyError,TypeError,OSError,StopIteration) as error:print('FAIL: '+str(error),file=sys.stderr);sys.exit(1)
