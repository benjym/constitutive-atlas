"""Bounded common-engine isotropic Barodesy study; no material solver here.

Independent exact scalar targets, actual caller chaining, source-bound replay.
Rate engine uses explicit midpoint/step-doubling; no AD/tangent admission.
"""
import argparse,copy,hashlib,json,math,subprocess
from pathlib import Path
from atlas.model import ROOT,load
from tools import barodesy2017_isotropic_reference as reference
VERSION='barodesy2017-isotropic-integration-v1'
MODEL_PATH=ROOT/'models/research/barodesy2017/body-zero-spin.json'
REFERENCE_PATH=ROOT/'catalogue/investigations/barodesy2017-isotropic-reference-v1/reference.json'
SOURCE_SHA256='bd049a3fd874c9e4945e1c77f5af5b84ac14c26a08cee1b953428b4312e6af15'
MATRIX=((1e-4,1),(1e-6,1),(1e-8,1),(1e-4,7),(1e-8,7))
ENDPOINT_BOUNDS={1e-4:5e-3,1e-6:3e-4,1e-8:2e-5}
REFERENCE_FLOOR=dict(stress=1e-7,e=1e-14)
PARITY_BOUND=5e-11
# Declared before any compiled run; never replace these with report-provided values.
POLICY=dict(endpoint_scaled_bounds=[dict(tolerance=t,bound=b)for t,b in ENDPOINT_BOUNDS.items()],reference_floor=REFERENCE_FLOOR,volume_fraction=.01,successive_refinement=.65,coarse_to_fine=.35,partition_shrink=.35,parity_scaled_bound=PARITY_BOUND)
PINNED_DEPENDENCIES={'tools/barodesy2017_isotropic_reference.py': '45d8457633482c463ed5310aa99d0fdd3521c84b3325edcf5627a1354c6246cb', 'tools/reference_barodesy2017.py': '10c2dff77152a80abad3e8ad6b3b3965be7550b46e1154e7283712b0b2284f67', 'models/research/barodesy2017/body-zero-spin.json': '16e0ef4de35ea1b47c4dc9122f01a264c56993d6851ba2387e974c0ff5f0af4f', 'docs/models/barodesy2017-implementation-checklist.md': '7c5d79c002e71865357314176fa78ae5799c2a747950f0e693a401ab58d95ce4', 'atlas/compiler.py': '4c7ffb54a59ec2f0ad8afc90e755243ea100d4172790de7ae4466f1e749c9292', 'atlas/dsl.py': 'd98844ee61060aca4ca39198bf261552f29ebc480abcf196cc2e836016e8cb6d', 'atlas/model.py': 'b7ee41dfe6f6d12a87f963256ab5a09f1eb6e66a5a5fb181b14e18fd69614276', 'atlas/scalar_math.py': 'ed29e8ee35045a4de313accf1fc2bae7ae6f8f09af1ab297fe4c21a5582bef89', 'cpp/main.cpp': '88f35705114993bac3eabb3ae33ddadedf27fe4d01b666b7ec5d036dc06cb4e7', 'cpp/include/atlas/solver.hpp': '7842240f542949a1ba547f4a2fea44e4ef1fadf50b35a18fd86f8fe4327164d5', 'cpp/include/atlas/tensor.hpp': '62a7456ed71910033b165df6479b52cd416425614d5aa354f13501228c794a08', 'cpp/include/atlas/expm.hpp': '267a9044b686082ba4faf9777ec271ea91ec9eed3495219abd3d5559a680c85f'}

def require(ok,message):
 if not ok:raise ValueError(message)
def finite(x):
 try:return type(x)in(int,float)and math.isfinite(x)
 except OverflowError:return False
def vector(x,n):return type(x)is list and len(x)==n and all(finite(v)for v in x)
def digest(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(),parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite JSON')))
def csv(v):return ','.join(format(x,'.17g')for x in v)
def settings(r):return dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(('residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),r['settings'])))
def split_increment(d,n):
 used=[0.]*6;parts=[]
 for j in range(n):
  p=[x-u if j==n-1 else x/n for x,u in zip(d,used)];parts.append(p);used=[u+x for u,x in zip(used,p)]
 return parts

def checked_reference(ref=None):
 for path,pin in PINNED_DEPENDENCIES.items():require(sha(ROOT/path)==pin,'current dependency changed: '+path)
 fresh=reference.study();ref=read(REFERENCE_PATH)if ref is None else ref
 require(digest(ref)==digest(fresh),'reference differs from fresh independent replay')
 require(ref.get('source_sha256')==SOURCE_SHA256 and ref.get('contract')==reference.VERSION,'reference source/contract')
 require(ref.get('basis')=='symmetric_mandel'and ref.get('zero_spin')is True and ref.get('compression_positive')is True,'reference conventions')
 cases={}
 for c in ref['cases']:
  require(c['input_sha256']==digest(c['input']),'reference input receipt');name=c['input']['id'];require(name not in cases,'duplicate reference');cases[name]=c
 require(len(cases)==9,'nine cases required');return ref,cases

def validate_model(model,cases):
 require(model['id']=='research-barodesy-clay-2017-body-zero-spin'and model['integration']=='rate','selected rate fragment')
 require([(s['name'],s['shape'],s['unit'],s['scale'])for s in model['state']]==[('sigma','sym','Pa','sigma_star'),('e','scalar','1','1')],'seven physical state layout')
 require(list(model['parameters'])==reference.PARAMETER_NAMES,'parameter order')
 require(model['parameters']['sigma_star']['min']==model['parameters']['sigma_star']['max']==1000,'fixed source pressure')
 for c in cases.values():
  i=c['input'];require(vector(i['initial'],7)and vector(i['parameters'],5),'reference layout')
  for x,spec in zip(i['parameters'],model['parameters'].values()):require(spec['min']<=x<=spec['max'],'parameter bounds')

def make_request(model,case,initial,strain,tolerance,budget=20000):
 return dict(model=model['id'],parameters=case['parameters'].copy(),initial=initial.copy(),strain=strain.copy(),settings=[2e-10,tolerance,45,20,budget,11])
def request_equal(a,b):
 if type(a)is not dict or set(a)!=set(b)or type(a.get('model'))is not str:return False
 if not all(vector(a.get(k),n)for k,n in [('parameters',5),('initial',7),('strain',6),('settings',6)]):return False
 if not all(type(a['settings'][i])is int for i in range(2,6)):return False
 return a==b

def expected_calls(case,n):return [(j,p)for j,d in enumerate(case['increments'],1)for p in split_increment(d,n)]
def target(case,cumulative):return reference.rounded_initial_compression(case['soil'],case['p0'],case['initial'][6],cumulative)
def errors(state,want):return dict(stress=max(abs(a-b)for a,b in zip(state[:6],want[:6])),e=abs(state[6]-want[6]))
def check_interior(z):
 require(vector(z,7),'finite seven-state vector')
 require(min(z[:3])>0 and z[6]>=0,'positive interior pressure/e support')
 # Scalar fixture is isotropic; no general SPD theorem or projection asserted.
 p=math.fsum(z[:3])/3;require(max(z[:3])-min(z[:3])<=64*math.ulp(p),'lost isotropy')
 require(z[3:6]==[0.]*3,'nonzero shear in isotropic path')

def check_response(a,r,model,success=True,partial=False):
 require(type(a)is dict and a.get('ok')is success,'response success flag')
 require(type(a.get('message'))is str and(success or bool(a['message'])),'response message type/content')
 for key,n in [('parameters',5),('initial',7),('strain',6)]:
  require(vector(r.get(key),n)and vector(a.get(key),n),'finite echo vector '+key);require(a[key]==r[key],'echo mismatch '+key)
 require(a.get('model')==r['model'] and a.get('catalogue_hash')==digest([model]),'runtime model/catalogue')
 require(vector(r.get('settings'),6),'finite settings request')
 require(type(a.get('integration_settings'))is dict and a['integration_settings']==settings(r),'settings echo')
 for key in('max_iterations','max_depth','max_substeps','max_backtracks'):require(type(a['integration_settings'].get(key))is int,'integer settings echo')
 require(vector(a.get('state'),7),'finite state result')
 d=a.get('diagnostics');require(type(d)is dict,'diagnostics object')
 for key in('substeps','rejected','iterations'):require(type(d.get(key))is int and d[key]>=0,'diagnostic counter')
 fractions=d.get('increment_fractions');require(type(fractions)is list and len(fractions)==d['substeps'] and all(finite(v)and 0<v<=1 for v in fractions),'increment fractions')
 coverage=math.fsum(fractions)
 if success:require(fractions and abs(coverage-1)<=1e-12,'successful full coverage');check_interior(a['state'])
 else:require(0<=coverage<1,'failed partial coverage');require(a['state']==r['initial'],'failed call did not roll back')
 if partial:require(d['substeps']>0 and 0<coverage<1,'budget failure did not occur after progress')
 if 'error'in d:require(finite(d['error'])and d['error']>=0,'invalid optional diagnostic error')
 return coverage

def assess_records(records,model,cases):
 require(type(records)is list,'records array');expected={(name,t,n)for name in cases for t,n in MATRIX};seen={};summary=[]
 for group in records:
  require(type(group)is dict and type(group.get('case'))is str and finite(group.get('tolerance'))and type(group.get('partitions'))is int,'trajectory label types')
  key=group['case'],group['tolerance'],group['partitions'];require(key in expected and key not in seen,'unexpected/duplicate trajectory');seen[key]=group
  case=cases[key[0]]['input'];tol,n=key[1:];initial=case['initial'].copy();calls=group.get('calls');protocol=expected_calls(case,n);require(type(calls)is list and len(calls)==len(protocol),'incomplete trajectory calls')
  total_components=[];endpoint=[];all_error=dict(stress=0.,e=0.);volume_max=0.
  for i,(record,(segment,strain))in enumerate(zip(calls,protocol),1):
   require(type(record)is dict and type(record.get('request'))is dict,'call record/request')
   r=record['request'];want=make_request(model,case,initial,strain,tol)
   require(request_equal(r,want),'caller chain/protocol request mismatch')
   a=record.get('response');check_response(a,r,model);z=a['state'];total_components.extend(strain[:3]);v=math.fsum(total_components);exact=target(case,v);err=errors(z,exact)
   for channel in all_error:all_error[channel]=max(all_error[channel],err[channel])
   scale=dict(stress=case['p0'],e=1.)
   for channel in err:require(err[channel]<=scale[channel]*ENDPOINT_BOUNDS[tol]+REFERENCE_FLOOR[channel],'caller point exceeds independent error budget: '+channel)
   volume=abs(z[6]-exact[6]);volume_max=max(volume_max,volume)
   require(volume<=ENDPOINT_BOUNDS[tol]*.01+REFERENCE_FLOOR['e'],'exact volume closure discrepancy')
   if i%n==0:endpoint.append(dict(segment=segment,v=v,errors=err,state=z.copy(),target=exact))
   initial=z.copy()
  summary.append(dict(case=key[0],tolerance=tol,partitions=n,call_count=len(calls),endpoints=endpoint,maximum_caller_error=all_error,maximum_endpoint_error={k:max(x['errors'][k]for x in endpoint)for k in all_error},volume_max=volume_max))
 require(set(seen)==expected,'incomplete45trajectory matrix')
 require(sum(len(g['calls'])for g in records)==459,'459actual chained calls required')
 for name,c in cases.items():
  rows=[next(s for s in summary if(s['case'],s['tolerance'],s['partitions'])==(name,t,1))for t in(1e-4,1e-6,1e-8)]
  for channel,floor in REFERENCE_FLOOR.items():
   vals=[s['maximum_endpoint_error'][channel]for s in rows]
   require(vals[1]<=.65*vals[0]+2*floor and vals[2]<=.65*vals[1]+2*floor and vals[2]<=.35*vals[0]+2*floor,'global refinement unresolved: '+channel)
 partitions=[]
 for name in cases:
  differences=[]
  for tol in(1e-4,1e-8):
   a=seen[name,tol,1]['calls'];b=seen[name,tol,7]['calls'];ee=[errors(a[j]['response']['state'],b[(j+1)*7-1]['response']['state'])for j in range(3)]
   differences.append({k:max(x[k]for x in ee)for k in REFERENCE_FLOOR})
  require(all(differences[1][k]<=.35*differences[0][k]+2*f for k,f in REFERENCE_FLOOR.items()),'caller partition shrink unresolved')
  partitions.append(dict(case=name,loose=differences[0],tight=differences[1]))
 return dict(trajectories=summary,caller_partition_differences=partitions,trajectory_count=45,call_count=459)

def control_request(model,cases):
 case=next(iter(cases.values()))['input'];return make_request(model,case,case['initial'],case['increments'][0],1e-8)
def probe_requests(model,cases):
 base=control_request(model,cases);out=[]
 for kind in('budget','domain','zero'):
  r=copy.deepcopy(base)
  if kind=='budget':r['settings'][4]=3
  if kind=='domain':r['initial'][6]=-.1
  if kind=='zero':r['strain']=[0.]*6
  out.append(dict(kind=kind,request=r))
 return out

def assess_probes(probes,control,records,model,cases):
 require(type(control)is dict and request_equal(control.get('request'),control_request(model,cases)),'recovery control request')
 check_response(control.get('response'),control['request'],model)
 fixed=next(g for g in records if(g['case'],g['tolerance'],g['partitions'])==(next(iter(cases)),1e-8,1))['calls'][0]
 require(digest(control)==digest(fixed),'control differs from actual matrix call')
 wants=probe_requests(model,cases);require(type(probes)is list and len(probes)==3,'three probes required')
 for p,w in zip(probes,wants):
  require(type(p)is dict and p.get('kind')==w['kind']and request_equal(p.get('request'),w['request']),'probe protocol mismatch')
  zero=w['kind']=='zero';check_response(p.get('response'),w['request'],model,success=zero,partial=w['kind']=='budget')
  require(p['response']['state']==w['request']['initial'],'zero/failure did not preserve parent')
  if w['kind']=='domain':require(p['response']['diagnostics']['substeps']==0 and p['response']['diagnostics']['increment_fractions']==[],'initial domain rejection made progress')
  recovery=p.get('recovery');require(type(recovery)is dict and request_equal(recovery.get('request'),control['request']),'recovery request mismatch');check_response(recovery.get('response'),recovery['request'],model)
  require(digest(recovery)==digest(control),'same control did not recover identically')

def metadata(model,ref,backend):
 return copy.deepcopy(dict(version=VERSION,backend=backend,scope='Zero-spin isotropic research finite paths only; no nonisotropic/AD/experimental/public admission.',source_sha256=SOURCE_SHA256,source_pins=PINNED_DEPENDENCIES,model_definition=model,model_sha256=digest(model),catalogue_hash=digest([model]),reference_sha256=digest(ref),policy=POLICY,claims=dict(public_admission=False,AD_validated=False,nonisotropic_integration_validated=False)))
def verify(report,ref=None):
 require(type(report)is dict and report.get('backend')in('native','wasm'),'report/backend');ref,cases=checked_reference(ref);model=load(MODEL_PATH);validate_model(model,cases)
 descriptor=report.get('runtime_descriptor');require(type(descriptor)is dict and digest(descriptor.get('models'))==digest([model])and descriptor.get('sha256')==digest([model]),'runtime descriptor receipt')
 expected=metadata(model,ref,report['backend'])
 for k,v in expected.items():require(k in report and digest(report[k])==digest(v),'report identity/policy mismatch: '+k)
 result=assess_records(report.get('records'),model,cases);assess_probes(report.get('failure_probes'),report.get('recovery_control'),report['records'],model,cases)
 if report['backend']=='wasm':
  require(report.get('persistent_recovery')is True,'same-instance recovery assertion missing')
  for key in('native_report_sha256','wasm_loader_sha256','wasm_binary_sha256'):require(type(report.get(key))is str and len(report[key])==64 and all(c in '0123456789abcdef'for c in report[key]),'missing artifact receipt: '+key)
 else:require(type(report.get('native_sha256'))is str and len(report['native_sha256'])==64 and all(c in '0123456789abcdef'for c in report['native_sha256']),'native binary receipt')
 return result

def append_transport(path,record):
 if path is not None:
  with Path(path).open('a')as stream:stream.write(json.dumps(record,allow_nan=False)+'\n');stream.flush()
def native_transport(args,request,transport=None):
 # Persist opaque transport before JSON parsing, status checks, or scientific checks.
 try:process=subprocess.run(args,capture_output=True,text=True,timeout=60)
 except subprocess.TimeoutExpired as error:
  def text(value):return value.decode('utf-8',errors='replace')if isinstance(value,bytes)else value
  append_transport(transport,dict(backend='native',args=args,request=request,stdout=text(error.stdout),stderr=text(error.stderr),returncode=None,exception='TimeoutExpired'))
  raise
 append_transport(transport,dict(backend='native',args=args,request=request,stdout=process.stdout,stderr=process.stderr,returncode=process.returncode))
 return process
def native_call(binary,r,transport=None):
 args=[str(binary),'--mode','integrate','--model',r['model'],'--parameters',csv(r['parameters']),'--initial',csv(r['initial']),'--strain',csv(r['strain']),'--integration-settings',csv(r['settings'])]
 process=native_transport(args,r,transport);out=json.loads(process.stdout)
 require(process.returncode==(0 if out.get('ok')is True else 1),'native exit status');return out

def run(binary,output):
 ref,cases=checked_reference();model=load(MODEL_PATH);validate_model(model,cases)
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True);transport=output.with_suffix('.transport.jsonl');transport.write_text('')
 process=native_transport([str(binary),'--describe'],dict(mode='describe'),transport);desc=json.loads(process.stdout);require(process.returncode==0,'describe exit status')
 require(digest(desc.get('models'))==digest([model])and desc.get('sha256')==digest([model]),'isolated runtime descriptor')
 report=metadata(model,ref,'native')|dict(native_sha256=sha(binary),runtime_descriptor=desc,records=[],failure_probes=[])
 output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
 def save():output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 for name,c in cases.items():
  case=c['input']
  for tol,n in MATRIX:
   group=dict(case=name,tolerance=tol,partitions=n,calls=[]);report['records'].append(group);initial=case['initial'].copy()
   for _,strain in expected_calls(case,n):
    r=make_request(model,case,initial,strain,tol);a=native_call(binary,r,transport);group['calls'].append(dict(request=r,response=a));save();check_response(a,r,model);initial=a['state'].copy()
 report['recovery_control']=copy.deepcopy(next(g for g in report['records']if(g['case'],g['tolerance'],g['partitions'])==(next(iter(cases)),1e-8,1))['calls'][0])
 for wanted in probe_requests(model,cases):
  probe=wanted|dict(response=native_call(binary,wanted['request'],transport));report['failure_probes'].append(probe);save();r=report['recovery_control']['request'];probe['recovery']=dict(request=copy.deepcopy(r),response=native_call(binary,r,transport));save()
 report['assessment']=verify(report,ref);save();return report

def parity(wasm,native,native_path):
 verify(wasm);verify(native);require(wasm['backend']=='wasm'and native['backend']=='native','parity backends');require(wasm.get('native_report_sha256')==sha(native_path),'native raw file binding')
 maximum=0.
 for ga,gb in zip(wasm['records'],native['records']):
  require((ga['case'],ga['tolerance'],ga['partitions'])==(gb['case'],gb['tolerance'],gb['partitions']),'parity group order')
  scale=gb['calls'][0]['request']['initial'][0]
  for a,b in zip(ga['calls'],gb['calls']):
   for field in('model','parameters','strain','settings'):require(a['request'][field]==b['request'][field],'parity request controls')
   err=errors(a['response']['state'],b['response']['state']);maximum=max(maximum,err['stress']/scale,err['e'])
 require(maximum<=PARITY_BOUND,'native/Wasm state parity budget');return maximum

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--solver',type=Path);p.add_argument('--report',type=Path);p.add_argument('--native-report',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(bool(a.solver)!=bool(a.report),'one solver/report required')
 report=run(a.solver,a.output)if a.solver else read(a.report);result=verify(report)
 if a.native_report:result['maximum_native_wasm_scaled_difference']=parity(report,read(a.native_report),a.native_report)
 report['assessment']=result;a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Verified45trajectories/459chainedcalls and3transaction/recovery probes')
if __name__=='__main__':main()
