"""Bounded four-path fixed-plane clay2014 common-engine study; no constitutive solver here.
Independent original-initial caller references, all7 states, actual generated chaining.
Estimated RK4 uncertainty is separate and not a certified error bound or admission.
"""
import argparse,copy,hashlib,json,math,subprocess,select,tempfile,os,time
from decimal import Decimal,localcontext
from pathlib import Path
from atlas.model import ROOT,load
from tools import clay2014_path_reference as reference
VERSION='clay2014-fixed-plane-integration-v1'
MODEL_PATH=ROOT/'models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json'
REFERENCE_PATH=ROOT/'catalogue/investigations/clay2014-path-reference-v1/reference.json'
SOURCE_SHA256='2eb8598297e3ac9cf245161f56674d6cef622b35fc612adc89dc129568b55202'
MATRIX=tuple((t,n)for n in(1,7)for t in(1e-4,1e-6,1e-8))
ENDPOINT_BOUNDS={1e-4:2e-3,1e-6:1e-4,1e-8:8e-6}
VOID_BOUNDS={1e-4:5e-6,1e-6:3e-7,1e-8:2e-8}
REFERENCE_FLOOR=dict(stress=5e-12,e=5e-13)
def floors(case):return dict(stress=REFERENCE_FLOOR["stress"]*case["stress_scale"],e=REFERENCE_FLOOR["e"])
PARITY_BOUND=5e-11
POLICY=dict(reference.POLICY,parity_scaled_bound=PARITY_BOUND,settings=[2e-10,'rate_tolerance',45,20,20000,11],transaction='oblique-reversal two-call actualprefix then thirdcontrol; budget3/domain0.9I/zero',compiled_accuracy='every callerpoint group stress/void <= declared budget without added allowances')
PINNED_DEPENDENCIES={'tools/clay2014_path_reference.py': '04cb9be360cde48a5cb64768e10129b90c10ac33d3d1c3b1a34dc75b683d315a', 'tools/reference_clay2014_cartesian.py': '0bc6e129d836fbe9f17b176eb1bcfe6728c4a9293db37c3449d67a39d044465c', 'catalogue/investigations/clay2014-path-reference-v1/reference.json': '7f7b2f8fb0eb04294fcd9959470a4dd7d342a38ea403dc1b18bc6d338cd5f301', 'catalogue/investigations/clay2014-path-reference-v1/manifest.json': 'ac976a30996d9af571e68e5bfaefcc74c5355d447a39d42615455de17b67a117', 'catalogue/investigations/clay2014-path-design-v1/DESIGN.md': 'cc4b999883e62a7c2daa540aae91fc00f337025b4654ce007693edf36cbdf716', 'models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json': '9077e7d5d7cdb42a7cc5c2ab49c29c1643543c54310caad26c17b5f256236de5', 'atlas/compiler.py': '4c7ffb54a59ec2f0ad8afc90e755243ea100d4172790de7ae4466f1e749c9292', 'atlas/dsl.py': 'd98844ee61060aca4ca39198bf261552f29ebc480abcf196cc2e836016e8cb6d', 'atlas/model.py': 'b7ee41dfe6f6d12a87f963256ab5a09f1eb6e66a5a5fb181b14e18fd69614276', 'atlas/scalar_math.py': 'ed29e8ee35045a4de313accf1fc2bae7ae6f8f09af1ab297fe4c21a5582bef89', 'atlas/structure.py': '30b1ef624c642b217e19e0a58e6988c2a2f802f0bfc5f892c6d7a38def1bcd47', 'atlas/symmetric_expm.py': 'c7ab6549501736bd84da7eca03500f8abd763610b07f2b7de98e6100a0a2c205', 'schemas/model.schema.json': '85acda14fe4a8dcd12fced802202b7c3a11a60e811e5da2d7db8224d35621ec7', 'cpp/main.cpp': '88f35705114993bac3eabb3ae33ddadedf27fe4d01b666b7ec5d036dc06cb4e7', 'cpp/include/atlas/expm.hpp': '267a9044b686082ba4faf9777ec271ea91ec9eed3495219abd3d5559a680c85f', 'cpp/include/atlas/history_runtime.hpp': 'aecb42fd96c0b5a318ce58680a0d35db7eb8ef8f9f807d695ff2572ae28517af', 'cpp/include/atlas/linearize.hpp': '40f8ed4bc722636c3ce0573af150dcbe6afe59618e0dad1542aa9a2b9e7b4319', 'cpp/include/atlas/recorded.hpp': '9c0f9fae85a033d1af1c8f6ffc718ea1f04e5f6ac6e94dacda233870d1ffaba6', 'cpp/include/atlas/schedule.hpp': '5c90e6cede9f24f124286cf10e2254a47a991e5d62f9bc7b3899ed62e6deb7e9', 'cpp/include/atlas/settings.hpp': '3eb1171ae1ef17440b19e8becfc8e9bf92335519a88da8f1e9be407d3488662b', 'cpp/include/atlas/solver.hpp': '7842240f542949a1ba547f4a2fea44e4ef1fadf50b35a18fd86f8fe4327164d5', 'cpp/include/atlas/tensor.hpp': '62a7456ed71910033b165df6479b52cd416425614d5aa354f13501228c794a08', 'cpp/include/atlas/time.hpp': '7b9942fbb1eae296201ad12db210c0c767fb3cc53c1f37de37de3e517f13f4d1', 'tests/research_integrate_driver.cpp': 'fe606af7e101c6807b8e2696b0622544bbf016ec47761a0e43e56e178e2b204a', 'CMakeLists.txt': '6e9061faf9ac1aa386f71dcb3283d675c732ea2a2abd71ff5e504825a47e452c'}
def require(ok,message):
 if not ok:raise ValueError(message)
def finite(x):
 try:return type(x)in(int,float)and math.isfinite(x)
 except OverflowError:return False
def vector(x,n):return type(x)is list and len(x)==n and all(finite(v)for v in x)
def same(a,b):
 if type(a)is bool or type(b)is bool:return type(a)is type(b)and a==b
 if finite(a)and finite(b):return a==b
 if type(a)is not type(b):return False
 if type(a)is dict:return set(a)==set(b)and all(same(a[k],b[k])for k in a)
 if type(a)is list:return len(a)==len(b)and all(same(x,y)for x,y in zip(a,b))
 return a==b
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
 ref=read(REFERENCE_PATH)if ref is None else ref
 reference.checked_reference(ref)
 cases={};points={}
 for row in ref['cases']:
  inp=row['input'];name=inp['id'];n=row['caller_partitions'];scale=row['stress_scale_Pa']
  if n==1:cases[name]=dict(id=name,initial=inp['initial'],parameters=[inp['parameters'][k]for k in reference.source.PARAMETER_ORDER],increments=inp['increments'],stress_scale=scale)
  actual=[]
  for index,(knot,target)in enumerate(zip(row['caller_points'],row['grids'][-1]['trajectory']),1):
   actual.append(dict(knot,index=index,original_segment=knot['segment'],original_endpoint=knot['caller']==n,state=target['state']))
  points[name,n]=dict(points=actual,row=row)
 require(len(cases)==4 and len(points)==8,'four complete reference paths')
 return ref,cases,points

def point_state(p):return p['state']
def errors(state,want):return dict(stress=math.hypot(*(a-b for a,b in zip(state[:6],want[:6]))),e=abs(state[6]-want[6]))
def uncertainties(row):
 return [dict(stress=max(a['stress_Pa'],b['stress_Pa']),e=max(a['void_ratio'],b['void_ratio']))for a,b in zip(row['row']['coarse_middle'],row['row']['middle_fine'])]
def validate_model(model,cases):
 require(model['id']=='hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane-research'and model['integration']=='rate','selected source variant')
 require([(s['name'],s['shape'],s['unit'])for s in model['state']]==[('sigma','sym','Pa'),('e','scalar','1')],'seven physical state layout')
 require(list(model['parameters'])==reference.source.PARAMETER_ORDER,'parameter order')
 for c in cases.values():
  require(vector(c['parameters'],17),'parameter vector')
  for x,spec in zip(c['parameters'],model['parameters'].values()):require(spec['min']<=x<=spec['max'],'parameter bounds')
def make_request(model,case,initial,strain,tolerance,budget=20000):return dict(model=model['id'],parameters=case['parameters'].copy(),initial=initial.copy(),strain=strain.copy(),settings=[2e-10,tolerance,45,20,budget,11])
def request_equal(a,b):
 if type(a)is not dict or set(a)!=set(b)or type(a.get('model'))is not str:return False
 if not all(vector(a.get(k),n)for k,n in [('parameters',17),('initial',7),('strain',6),('settings',6)]):return False
 if not all(type(a['settings'][i])is int for i in range(2,6)):return False
 return a==b
def check_interior(z):
 require(vector(z,7),'finite seven-state vector');require(z[6]>=0,'void ratio outside research support')
 n=math.hypot(*z[:6]);require(n>0,'zero stress outside support');x,y,w,a,b,c=[v/n for v in z[:6]]
 det=x*y*w-(x*b*b+y*c*c+w*a*a)/2+a*b*c/math.sqrt(2)
 require(min(x,y,w)>0 and x*y-a*a/2>64*math.ulp(1.) and det>64*math.ulp(1.),'outside conservative numerical stress interior')
def check_response(a,r,model,success=True,partial=False):
 require(type(a)is dict and set(a)=={'ok','message','state','diagnostics','integration_settings','catalogue_hash','model','parameters','initial','strain'} and a.get('ok')is success,'response shape/success flag')
 require(type(a.get('message'))is str and(a['message']==''if success else bool(a['message'])),'response message type/content')
 for key,n in [('parameters',17),('initial',7),('strain',6)]:
  require(vector(r.get(key),n)and vector(a.get(key),n),'finite echo vector '+key);require(a[key]==r[key],'echo mismatch '+key)
 require(a.get('model')==r['model'] and a.get('catalogue_hash')==digest([model]),'runtime model/catalogue')
 require(vector(r.get('settings'),6),'finite settings request')
 require(type(a.get('integration_settings'))is dict and a['integration_settings']==settings(r),'settings echo')
 require(a['integration_settings'].get('version')=='incremental-settings-0.1'and a['integration_settings'].get('norm')=='scaled_component_max','settings contract')
 for key in('residual_tolerance','rate_tolerance'):require(finite(a['integration_settings'].get(key)),'numeric settings echo')
 for index in range(2,6):require(type(r['settings'][index])is int,'integer settings request')
 for key in('max_iterations','max_depth','max_substeps','max_backtracks'):require(type(a['integration_settings'].get(key))is int,'integer settings echo')
 require(vector(a.get('state'),7),'finite state result')
 d=a.get('diagnostics');require(type(d)is dict and set(d)=={'iterations','substeps','rejected','increment_fractions'},'diagnostics object')
 for key in('substeps','rejected','iterations'):require(type(d.get(key))is int and d[key]>=0,'diagnostic counter')
 fractions=d.get('increment_fractions');require(type(fractions)is list and len(fractions)==d['substeps'] and all(finite(v)and 0<v<=1 for v in fractions),'increment fractions')
 # The selected rate solver appends two equal dyadic half-step fractions per
 # accepted recursive leaf; each leaf is bounded by max_depth/max_substeps.
 require(d['substeps']<=r['settings'][4] and d['substeps']%2==0,'rate substep budget/pair count')
 for left,right in zip(fractions[::2],fractions[1::2]):
  require(left==right,'rate substep fractions must be paired equal')
  mantissa,exponent=math.frexp(float(left));depth=1-exponent
  require(mantissa==.5 and 1<=depth<=r['settings'][3]+1,'rate substep fraction dyadic/depth contract')
 coverage=math.fsum(fractions)
 if success:
  require(fractions and abs(coverage-1)<=1e-12,'successful full coverage');check_interior(a['state'])
  reference.source.evaluate(dict(state=a['state'],increment=[0.]*6,parameters=dict(zip(reference.source.PARAMETER_ORDER,r['parameters']))))
 else:require(0<=coverage<1,'failed partial coverage');require(a['state']==r['initial'],'failed call did not roll back')
 if partial:require(d['substeps']>0 and 0<coverage<1,'budget failure did not occur after progress')
 if 'error'in d:require(finite(d['error'])and d['error']>=0,'invalid optional diagnostic error')
 return coverage


def exact_void(initial,point):
 with localcontext()as ctx:
  ctx.prec=100
  from fractions import Fraction
  v=sum((reference.unexact(x)for x in point['cumulative_loading_exact'][:3]),Fraction())
  V=Decimal(v.numerator)/Decimal(v.denominator)
  return float((1+Decimal.from_float(float(initial[6])))*(-V).exp()-1)
def assess_records(records,model,cases,points):
 require(type(records)is list,'records array');expected={(name,t,n)for name in cases for t,n in MATRIX};seen={};summary=[]
 for group in records:
  require(type(group)is dict and type(group.get('case'))is str and finite(group.get('tolerance'))and type(group.get('partitions'))is int,'trajectory label types')
  key=group['case'],group['tolerance'],group['partitions'];require(key in expected and key not in seen,'unexpected/duplicate trajectory');seen[key]=group
  name,tol,n=key;case=cases[name];row=points[name,n];targets=row['points'];uncertainty=uncertainties(row);initial=case['initial'].copy();calls=group.get('calls')
  require(type(calls)is list and len(calls)==3*n,'incomplete trajectory calls')
  endpoint=[];all_error=dict(stress=0.,e=0.);max_unc=dict(stress=0.,e=0.);volume_max=0.
  for record,point,unc in zip(calls,targets,uncertainty):
   require(type(record)is dict and type(record.get('request'))is dict,'call record/request');r=record['request'];want=make_request(model,case,initial,point['increment'],tol)
   require(request_equal(r,want),'caller chain/protocol request mismatch')
   a=record.get('response');check_response(a,r,model);z=a['state'];exact=point_state(point);err=errors(z,exact)
   for channel in all_error:all_error[channel]=max(all_error[channel],err[channel]);max_unc[channel]=max(max_unc[channel],unc[channel])
   for channel in err:
    bound=case['stress_scale']*ENDPOINT_BOUNDS[tol]if channel=='stress'else VOID_BOUNDS[tol]
    require(err[channel]<=bound,'caller point exceeds independent error budget: '+channel)
   volume=abs(z[6]-exact_void(case['initial'],point));volume_max=max(volume_max,volume)
   require(volume<=VOID_BOUNDS[tol],'exact volume closure discrepancy')
   if point['original_endpoint']:endpoint.append(dict(segment=point['original_segment'],errors=err,state=z.copy(),target=exact.copy(),reference_uncertainty=unc))
   initial=z.copy()
  summary.append(dict(case=name,tolerance=tol,partitions=n,call_count=len(calls),endpoints=endpoint,maximum_caller_error=all_error,maximum_endpoint_error={k:max(x['errors'][k]for x in endpoint)for k in all_error},maximum_reference_uncertainty=max_unc,volume_max=volume_max))
 require(set(seen)==expected,'incomplete24trajectory matrix');require(sum(len(g['calls'])for g in records)==288,'288actual chained calls required')
 for name in cases:
  for n in(1,7):
   rows=[next(s for s in summary if(s['case'],s['tolerance'],s['partitions'])==(name,t,n))for t in(1e-4,1e-6,1e-8)]
   for index in range(3):
    for channel,floor in floors(cases[name]).items():
     vals=[s['endpoints'][index]['errors'][channel]for s in rows];unc=max(s['endpoints'][index]['reference_uncertainty'][channel]for s in rows)
     require(vals[1]<=.65*vals[0]+2*(floor+unc)and vals[2]<=.65*vals[1]+2*(floor+unc)and vals[2]<=.35*vals[0]+2*(floor+unc),'global refinement unresolved at physical endpoint: '+channel)
 partitions=[]
 for name in cases:
  differences=[]
  for tol in(1e-4,1e-8):
   a=seen[name,tol,1]['calls'];b=seen[name,tol,7]['calls'];ee=[errors(a[j]['response']['state'],b[(j+1)*7-1]['response']['state'])for j in range(3)]
   differences.append({k:max(x[k]for x in ee)for k in REFERENCE_FLOOR})
  # Both generated paths share exact physical increments; no RK4 uncertainty is
  # added to this production-vs-production partition contraction comparison.
  require(all(differences[1][k]<=.35*differences[0][k]+2*f for k,f in floors(cases[name]).items()),'caller partition shrink unresolved')
  partitions.append(dict(case=name,loose=differences[0],tight=differences[1]))
 covariance=[]
 for tol,n in MATRIX:
  aa=seen['oblique-reversal',tol,n]['calls'];bb=seen['rotated-oblique-reversal',tol,n]['calls'];maximum=dict(stress=0.,e=0.)
  scale=cases['oblique-reversal']['stress_scale'];other=cases['rotated-oblique-reversal']['stress_scale']
  for a,b in zip(aa,bb):
   sigma=reference.source.from_mandel(a['response']['state'][:6]);want=reference.source.to_mandel(reference.source.rotate(sigma,reference.Q))+[a['response']['state'][6]]
   err=errors(want,b['response']['state'])
   require(err['stress']<=ENDPOINT_BOUNDS[tol]*(scale+other)+2*REFERENCE_FLOOR['stress']*max(scale,other),'compiled covariance stress budget')
   require(err['e']<=2*VOID_BOUNDS[tol]+2*REFERENCE_FLOOR['e'],'compiled covariance void budget')
   for k in maximum:maximum[k]=max(maximum[k],err[k])
  covariance.append(dict(tolerance=tol,partitions=n,maximum=maximum))
 return dict(trajectories=summary,caller_partition_differences=partitions,covariance=covariance,trajectory_count=24,call_count=288)

def committed_controls(records,cases):
 name='oblique-reversal';groups=[g for g in records if(g['case'],g['tolerance'],g['partitions'])==(name,1e-8,1)]
 require(len(groups)==1 and len(groups[0]['calls'])==3,'transaction prefix/control matrix group')
 return copy.deepcopy(groups[0]['calls'][:2]),copy.deepcopy(groups[0]['calls'][2])
def probe_requests(control):
 out=[]
 for kind in('budget','domain','zero'):
  r=copy.deepcopy(control['request'])
  if kind=='budget':r['settings'][4]=3
  if kind=='domain':r['strain']=[.9,.9,.9,0.,0.,0.]
  if kind=='zero':r['strain']=[0.]*6
  out.append(dict(kind=kind,request=r))
 return out

def assess_probes(probes,prefix,control,records,model,cases):
 want_prefix,want_control=committed_controls(records,cases)
 require(type(prefix)is list and len(prefix)==2 and same(prefix,want_prefix),'actual committed two-call prefix mismatch')
 require(type(control)is dict and same(control,want_control),'recovery control differs from actual third matrix call')
 for call in prefix:check_response(call['response'],call['request'],model)
 check_response(control['response'],control['request'],model)
 require(prefix[1]['request']['initial']==prefix[0]['response']['state']and control['request']['initial']==prefix[1]['response']['state'],'control not from committed two-call prefix')
 wants=probe_requests(control);require(type(probes)is list and len(probes)==3,'three probes required')
 for p,w in zip(probes,wants):
  require(type(p)is dict and p.get('kind')==w['kind']and request_equal(p.get('request'),w['request']),'probe protocol mismatch')
  zero=w['kind']=='zero';check_response(p.get('response'),w['request'],model,success=zero,partial=w['kind']=='budget')
  require(p['response']['state']==control['request']['initial'],'zero/failure did not preserve committed parent')
  recovery=p.get('recovery');require(type(recovery)is dict and request_equal(recovery.get('request'),control['request']),'recovery request mismatch');check_response(recovery.get('response'),recovery['request'],model)
  require(same(recovery,control),'same-parent control did not recover identically')

def metadata(model,ref,backend):
 return copy.deepcopy(dict(version=VERSION,backend=backend,study_sha256=sha(Path(__file__)),wasm_collector_sha256=sha(Path(__file__).with_name('test_clay2014_paths_wasm.mjs')),scope='Four fixed-plane printed-Am/proposed-alpha clay2014 research paths only; no public/experimental/tangent/IGS/axis-transport admission.',source_sha256=SOURCE_SHA256,source_pins=PINNED_DEPENDENCIES,model_definition=model,model_sha256=digest(model),catalogue_hash=digest([model]),reference_sha256=digest(ref),policy=POLICY,claims=dict(public_admission=False,AD_validated=False,full_model_validated=False)))
def verify(report,ref=None):
 require(type(report)is dict and report.get('backend')in('native','wasm'),'report/backend');ref,cases,points=checked_reference(ref);model=load(MODEL_PATH);validate_model(model,cases)
 descriptor=report.get('runtime_descriptor');require(type(descriptor)is dict and same(descriptor.get('models'),[model])and descriptor.get('sha256')==digest([model]),'runtime descriptor receipt')
 for k,v in metadata(model,ref,report['backend']).items():require(k in report and same(report[k],v),'report identity/policy mismatch: '+k)
 result=assess_records(report.get('records'),model,cases,points);assess_probes(report.get('failure_probes'),report.get('transaction_prefix'),report.get('recovery_control'),report['records'],model,cases)
 if report['backend']=='wasm':
  require(report.get('persistent_recovery')is True,'same-instance recovery assertion missing')
  keys=('native_report_sha256','native_transport_sha256','wasm_loader_sha256','wasm_binary_sha256')
 else:
  keys=('native_sha256',)
  require(report.get('persistent_recovery')is True,'persistent native recovery assertion')
  require(type(report.get('native_exit_status'))is int and report['native_exit_status']==0,'native process exit status')
  require(type(report.get('native_stderr'))is str and report.get('native_trailing_stdout')=='','native process transport termination')
  command=report.get('native_command');require(type(command)is list and len(command)==2 and all(type(x)is str for x in command)and command[1]=='--stream','native persistent command')
 for key in (*keys,'transport_sha256'):require(type(report.get(key))is str and len(report[key])==64 and all(c in '0123456789abcdef'for c in report[key]),'missing artifact receipt: '+key)
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

def stream_line(r):return '--describe'if r==dict(mode='describe')else '\t'.join([r['model']]+[csv(r[k])for k in('parameters','initial','strain','settings')])
class NativeSession:
 """One native process for descriptor, all updates, failure and recovery."""
 def __init__(self,binary,transport):
  self.command=[str(binary),'--stream'];self.transport=transport;self.stderr=tempfile.TemporaryFile(mode='w+t');self.pending=b'';self.partial=b''
  self.process=subprocess.Popen(self.command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=self.stderr,text=True,bufsize=1)
 def read_line(self):
  deadline=time.monotonic()+60;self.partial=self.pending;self.pending=b''
  while b'\n'not in self.partial:
   remaining=deadline-time.monotonic()
   require(remaining>0 and bool(select.select([self.process.stdout],[],[],remaining)[0]),'persistent native response line timeout')
   chunk=os.read(self.process.stdout.fileno(),65536)
   require(bool(chunk),'persistent native unexpected EOF before response newline')
   self.partial+=chunk
  line,self.pending=self.partial.split(b'\n',1);self.partial=line+b'\n'
  return self.partial.decode('utf-8',errors='strict')
 def call(self,r):
  line=stream_line(r);self.partial=b''
  try:
   self.process.stdin.write(line+'\n');self.process.stdin.flush();raw=self.read_line()
  except Exception as error:
   append_transport(self.transport,dict(backend='native',mode='persistent_stream',request_line=line,request=r,stdout=self.partial.decode('utf-8',errors='replace'),stdout_hex=self.partial.hex(),exception=str(error)));raise
  append_transport(self.transport,dict(backend='native',mode='persistent_stream',request_line=line,request=r,stdout=raw))
  return json.loads(raw,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite native JSON')))
 def close(self):
  self.process.stdin.close();self.process.stdin=None
  try:out,_=self.process.communicate(timeout=60)
  except subprocess.TimeoutExpired:
   self.process.kill();out,_=self.process.communicate();self.stderr.seek(0);err=self.stderr.read();self.stderr.close()
   return self.process.returncode,err,self.pending.decode('utf-8',errors='replace')+(out or '')
  self.stderr.seek(0);err=self.stderr.read();self.stderr.close()
  return self.process.returncode,err,self.pending.decode('utf-8',errors='replace')+(out or '')

def run(binary,output):
 ref,cases,points=checked_reference();model=load(MODEL_PATH);validate_model(model,cases)
 output=Path(output);transport=output.with_suffix('.transport.jsonl');require(not output.exists()and not transport.exists(),'fresh output and transport paths required')
 output.parent.mkdir(parents=True,exist_ok=True);transport.write_text('');binary_pin=sha(binary)
 report=metadata(model,ref,'native')|dict(native_sha256=binary_pin,records=[],failure_probes=[],persistent_recovery=True,native_command=[str(binary),'--stream'])
 def save():output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
 save();session=NativeSession(binary,transport)
 try:
  desc=session.call(dict(mode='describe'));report['runtime_descriptor']=desc;save()
  require(type(desc)is dict and same(desc.get('models'),[model])and desc.get('sha256')==digest([model]),'isolated runtime descriptor')
  for name,case in cases.items():
   for tol,n in MATRIX:
    group=dict(case=name,tolerance=tol,partitions=n,calls=[]);report['records'].append(group);initial=case['initial'].copy()
    for point in points[name,n]['points']:
     r=make_request(model,case,initial,point['increment'],tol);a=session.call(r);group['calls'].append(dict(request=r,response=a));save();check_response(a,r,model);initial=a['state'].copy()
  report['transaction_prefix'],report['recovery_control']=committed_controls(report['records'],cases);save()
  for wanted in probe_requests(report['recovery_control']):
   probe=wanted|dict(response=session.call(wanted['request']));report['failure_probes'].append(probe);save()
   r=copy.deepcopy(report['recovery_control']['request']);probe['recovery']=dict(request=r,response=session.call(r));save()
 finally:
  code,err,trailing=session.close();report.update(native_exit_status=code,native_stderr=err,native_trailing_stdout=trailing,transport_sha256=sha(transport));save()
 require(sha(binary)==binary_pin,'native artifact changed during collection')
 require(code==0 and not trailing,'persistent native process exit/trailing output')
 report['assessment']=verify(report,ref);verify_transport(report,transport);save();return report

def parity(wasm,native,native_path,wasm_transport,native_transport):
 # Bind the supplied parsed object to the very bytes whose hash Wasm records.
 held=Path(native_path).read_bytes();native_pin=hashlib.sha256(held).hexdigest()
 parsed=json.loads(held,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite native report')))
 require(same(parsed,native),'supplied native report differs from pinned file bytes')
 raw_pins={str(p):sha(p)for p in(wasm_transport,native_transport)}
 verify(wasm);verify(native);verify_transport(wasm,wasm_transport);verify_transport(native,native_transport);require(wasm['backend']=='wasm'and native['backend']=='native','parity backends')
 require(wasm.get('native_report_sha256')==native_pin,'native raw file binding');require(wasm.get('native_transport_sha256')==raw_pins[str(native_transport)],'native raw companion binding')
 require(len(wasm['records'])==len(native['records'])==24,'parity matrix count');maximum=0.
 for ga,gb in zip(wasm['records'],native['records']):
  require((ga['case'],ga['tolerance'],ga['partitions'])==(gb['case'],gb['tolerance'],gb['partitions']),'parity group order')
  scale=max(1.,math.hypot(*gb['calls'][0]['request']['initial'][:6]));require(len(ga['calls'])==len(gb['calls']),'parity call count')
  for a,b in zip(ga['calls'],gb['calls']):
   for field in('model','parameters','strain','settings'):require(a['request'][field]==b['request'][field],'parity request controls')
   for location in('initial',):
    err=errors(a['request'][location],b['request'][location]);maximum=max(maximum,err['stress']/scale,err['e'])
   err=errors(a['response']['state'],b['response']['state']);maximum=max(maximum,err['stress']/scale,err['e'])
 require(maximum<=PARITY_BOUND,'native/Wasm state parity budget');require(sha(native_path)==native_pin,'native report changed during parity');require(all(sha(p)==pin for p,pin in raw_pins.items()),'raw transport changed during parity');return maximum

def verify_transport(report,path):
 held=Path(path).read_bytes();pin=hashlib.sha256(held).hexdigest();require(pin==report.get('transport_sha256'),'raw transport file binding')
 rows=[json.loads(line,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite raw JSON')))for line in held.decode().splitlines()]
 calls=[c for g in report['records']for c in g['calls']]+[c for p in report['failure_probes']for c in(p,p['recovery'])]
 require(len(rows)==1+len(calls)==295,'complete raw transport count')
 expected=[dict(request=dict(mode='describe'),response=report['runtime_descriptor'])]+calls
 for index,(raw,record)in enumerate(zip(rows,expected)):
  require(type(raw)is dict and raw.get('backend')==report['backend'],'raw backend')
  require(same(raw.get('request'),record['request']),'raw request binding')
  text=raw.get('stdout')if report['backend']=='native'else raw.get('raw');require(type(text)is str,'raw response text')
  parsed=json.loads(text,parse_constant=lambda x:(_ for _ in()).throw(ValueError('nonfinite response JSON')))
  require(same(parsed,record['response']),'raw parsed response binding')
  if report['backend']=='native':
   require(raw.get('mode')=='persistent_stream'and type(raw.get('request_line'))is str and raw['request_line']==stream_line(record['request']),'native stream/request binding')
  else:
   require(raw.get('name')==('atlas_describe'if index==0 else 'atlas_integrate_with_settings'),'raw CABI name')
   if index==0:require(raw.get('types')==[]and raw.get('args')==[],'CABI descriptor arguments')
   else:
    require(raw.get('types')==['string']*5 and type(raw.get('args'))is list and len(raw['args'])==5,'CABI argument layout')
    require(raw['args'][0]==record['request']['model'],'CABI model argument')
    for text,key in zip(raw['args'][1:],('parameters','initial','strain','settings')):
     require(type(text)is str,'CABI CSV string');parsed_args=[float(x)for x in text.split(',')];require(all(finite(x)for x in parsed_args)and parsed_args==record['request'][key],'CABI CSV/request binding')
 require(sha(path)==pin,'raw transport changed during audit');return dict(rows=len(rows),call_count=len(calls),raw_sha256=pin)

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--solver',type=Path);p.add_argument('--report',type=Path);p.add_argument('--transport',type=Path);p.add_argument('--native-report',type=Path);p.add_argument('--native-transport',type=Path);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(bool(a.solver)!=bool(a.report),'one solver/report required')
 if a.report:require(not a.output.exists()and all(a.output.resolve()!=x.resolve()for x in(a.report,a.transport,a.native_report,a.native_transport)if x is not None),'fresh assessment output distinct from all inputs required')
 report=run(a.solver,a.output)if a.solver else read(a.report)
 require(report.get('backend')!='wasm'or(a.native_report is not None and a.native_transport is not None),'Wasm full assessment requires --native-report and --native-transport for pinned binding and parity')
 require(a.solver is not None or a.transport is not None,'archived assessment requires --transport raw companion')
 result=verify(report);verify_transport(report,a.output.with_suffix('.transport.jsonl')if a.solver else a.transport)
 if a.native_report:result['maximum_native_wasm_scaled_difference']=parity(report,read(a.native_report),a.native_report,a.output.with_suffix('.transport.jsonl')if a.solver else a.transport,a.native_transport)
 report['assessment']=result;a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print('Verified24trajectories/288chainedcalls and3same-parent transaction/recovery probes')
if __name__=='__main__':main()
