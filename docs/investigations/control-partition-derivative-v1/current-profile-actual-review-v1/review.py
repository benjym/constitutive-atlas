"""Independent saved-evidence review; no subprocess/artifact calls permitted."""
import sys
sys.dont_write_bytecode=True
import ast,contextlib,copy,datetime,hashlib,importlib.util,io,json,math,os,subprocess,tarfile
from pathlib import Path
if not __debug__:raise RuntimeError('Unoptimized review required')
D=Path(__file__).resolve().parent;R=D.parent
P=R/'current-profile-execution-v3'
S=Path('/private/tmp/atlas-control-partition-support-v4/source')
B=Path('/private/tmp/atlas-control-partition-profile-execution-v3')
def denied(*a,**k):raise RuntimeError('Reviewer forbids process execution')
subprocess.run=denied;subprocess.Popen=denied;os.system=denied
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pairs(items):
 d={}
 for k,v in items:
  if k in d:raise ValueError('duplicate JSON key')
  d[k]=v
 return d
def read(p):return json.loads(Path(p).read_text(),object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in()).throw(ValueError(x)))
def save(name,data):
 p=D/name
 text=json.dumps(data,indent=2,allow_nan=False)+'\n'
 if p.exists():
  if p.read_text()!=text:raise RuntimeError('Existing review output differs: '+str(p))
  return
 with p.open('x')as f:f.write(text)
checks=[]
def check(name,condition):
 checks.append({'check':name,'passed':bool(condition)})
 if not condition:raise AssertionError(name)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def manifest(path,expected=None):
 if expected:check(str(path)+' exact identity',sha(path)==expected)
 data=read(path)
 for n,h in data['files'].items():check('manifest member '+str(path.parent/n),sha(path.parent/n)==h)
 return data

def common():
 manifest(P/'manifest.json')
 plan=read(P/'plan.json');f=read(plan['source_freeze']);tools=read(P/'toolchain.json')
 check('source count',len(f['files'])==2722)
 for n,h in f['files'].items():check('source '+n,sha(S/n)==h)
 actual={str(p.relative_to(S))for p in S.rglob('*')if p.is_file()}
 check('exact source inventory',actual==set(f['files']))
 check('tool count',len(tools['files'])==6821)
 for n,row in tools['files'].items():check('tool '+n,sha(n)==row['sha256']and str(Path(n).resolve())==row['realpath'])
 return plan,f,tools

def packet(name,expected,plan,f,tools):
 public=R/f'current-profile-actual-{name}-v3';profile='power-creep'if name=='power'else name
 work=B/profile;ev=work/'evidence';spec=next(x for x in plan['profiles']if x['profile']==profile)
 manifest(public/'manifest.json',expected)
 receipt=read(public/'archive-receipt.json');archive=public/receipt['archive']
 check(name+' archive size/hash',archive.stat().st_size==receipt['bytes']and sha(archive)==receipt['sha256'])
 with tarfile.open(archive,'r:gz')as tar:
  members=tar.getmembers();check(name+' unique archive inventory',len(members)==len(receipt['members'])and {m.name for m in members}==set(receipt['members']))
  for m in members:
   check(name+' regular safe archive '+m.name,m.isfile()and not Path(m.name).is_absolute()and '..'not in Path(m.name).parts)
   check(name+' archive bytes '+m.name,hashlib.sha256(tar.extractfile(m).read()).hexdigest()==receipt['members'][m.name])
   check(name+' working/archive '+m.name,sha(work/m.name)==receipt['members'][m.name])
 for stage in spec['steps']:
  st=stage['stage'];folder=ev/'processes'/st;proc=read(folder/'process.json')
  check(name+' process argv/cwd '+st,proc['argv']==stage['argv']and proc['cwd']==stage['cwd'])
  check(name+' process complete '+st,proc['status']=='observed'and type(proc['returncode'])is int and proc['returncode']==0 and datetime.datetime.fromisoformat(proc['end'])>=datetime.datetime.fromisoformat(proc['start']))
  for channel in ['stdout','stderr']:check(name+' raw '+st+channel,sha(folder/channel)==proc[channel+'_sha256'])
  for phase in ['pre','post']:
   rpath=ev/'stage-receipts'/f'{st}.{phase}.json';r=read(rpath);rp=read(ev/'processes'/f'{st}.{phase}'/'process.json')
   check(name+' receipt process '+st+phase,rp['status']=='observed'and type(rp['returncode'])is int and rp['returncode']==0)
   for channel in ['stdout','stderr']:check(name+' receipt process raw '+st+phase+channel,sha(ev/'processes'/f'{st}.{phase}'/channel)==rp[channel+'_sha256'])
   check(name+' receipt exact '+st+phase,r['identity']=='current-profile-stage-receipt-v3'and r['passed']is True and r['phase']==phase and r['profile']==profile and r['stage']==st and r['command']==stage and r['packet_manifest_sha256']==sha(P/'manifest.json')and r['plan_sha256']==sha(P/'plan.json')and r['source_freeze_sha256']==sha(plan['source_freeze'])and r['toolchain_sha256']==sha(P/'toolchain.json')and r['source_files']==2722 and r['tool_files']==6821)
   if phase=='post':
    check(name+' post linkage '+st,r['exit_status']==0 and type(r['exit_status'])is int and r['pre_receipt_sha256']==sha(ev/'stage-receipts'/f'{st}.pre.json'))
    for channel in ['stdout','stderr']:check(name+' post raw linkage '+st+channel,r[channel]=={'path':str(folder/channel),'sha256':sha(folder/channel)})
  if st.endswith('-build'):check(name+' serial explicit build '+st,stage['argv'][-2:]==['--parallel','1']and stage['argv'].count('--target')==1)
 for kind in ['native','wasm']:
  build=work/f'{kind}-build';binding=read(ev/f'{kind}-configure.inputs.json')
  check(name+' '+kind+' actual configure cache',binding['passed']is True and binding['cache_sha256']==sha(build/'CMakeCache.txt'))
  cache=(build/'CMakeCache.txt').read_text();check(name+' '+kind+' Release','CMAKE_BUILD_TYPE:STRING=Release'in cache)
  for n,h in binding.get('compiler_binding_files',{}).items():check(name+' compiler metadata '+n,sha(build/n)==h)
  for key,row in binding['actual_tool_pins'].items():
   check(name+' actual configured tool '+key,sha(row['path'])==row['sha256']and str(Path(row['path']).resolve())==row['realpath'])
   expected_tool=tools['files'].get(row['path'])
   check(name+' tool frozen provenance '+key,(expected_tool is not None and expected_tool['realpath']==row['realpath']and expected_tool['sha256']==row['sha256'])or(row['path']in ['/usr/bin/c++','/usr/bin/cc']and row['path']==row['realpath']and row['sha256']==tools['files']['/usr/bin/clang']['sha256']))
  for n,row in binding['sdk_settings'].items():check(name+' SDK '+n,sha(n)==row['sha256'])
  generated=build/('power-creep-generated'if name=='power'else'generated');g=read(generated/'models.json')
  modelpath=S/('models/research/power-creep/power-creep-itasca900-both-active-ode.json'if name=='power'else'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json')
  check(name+' '+kind+' generated model exact',g['models']==[read(modelpath)])
  check(name+' '+kind+' generated canonical identity',g['sha256']==hashlib.sha256(json.dumps(g['models'],sort_keys=True,separators=(',',':')).encode()).hexdigest())
  check(name+' '+kind+' generated header identity',g['sha256']in(generated/'models.hpp').read_text())
 for freeze in public.glob('freeze*.json'):
  for n,h in read(freeze).get('inputs',{}).items():check(name+' execution freeze '+n,sha(n)==h)
 return spec,work

def power(work):
 sys.path.insert(0,str(S/'tools'));study=load('independent_saved_power',S/'tools/power_creep_study.py');study.PACKET=study.PACKET/'refinement-v2'
 requests=read(study.PACKET/'study.json')['requests'];check('Power frozen27',len(requests)==27)
 for kind in ['native','wasm']:
  for r in requests:
   row=read(work/'evidence'/kind/(r['id']+'.process.json'));check('Power request status '+kind+r['id'],type(row['returncode'])is int and row['returncode']==(0 if r['ok']else 1))
   if kind=='native':check('Power native exact command/hash '+r['id'],row['command']==[str(work/'native-build/atlas_power_creep_solver'),*r['command']]and row['binary_sha256']==sha(work/'native-build/atlas_power_creep_solver'))
   else:check('Power Wasm exact request/artifacts '+r['id'],row['function']==r['function']and row['args']==r['args']and row['module_sha256']==sha(work/'wasm-build/power-creep.js')and row['wasm_sha256']==sha(work/'wasm-build/power-creep.wasm'))
   check('Power empty percall stderr '+kind+r['id'],(work/'evidence'/kind/(r['id']+'.stderr')).read_bytes()==b'')
  out=io.StringIO()
  with contextlib.redirect_stdout(out):study.assess(work/'evidence'/kind,work/'evidence/native'if kind=='wasm'else None)
  report=json.loads(out.getvalue());check('Power saved assessor reproduction '+kind,report==read(R/'current-profile-actual-power-v3'/f'{kind}-assess.json'))
  save(f'power-{kind}-recomputed.json',report)
 # Recompute independent Cartesian source rate values, not production AD.
 for r in requests[:8]:
  expected=study.reference_rate(list(map(float,r['args'][2].split(','))),list(map(float,r['args'][3].split(','))),list(map(float,r['args'][1].split(','))))[0]
  check('Power source rate expected '+r['id'],expected==r['checks'][0]['value'])
 return {'requests_per_backend':27,'native_wasm_parity':'unchanged physical fields only; diagnostics excluded','artifacts':{str(p.relative_to(work)):sha(p)for p in [work/'native-build/atlas_power_creep_solver',work/'wasm-build/power-creep.js',work/'wasm-build/power-creep.wasm']}}

def burgers(work):
 os.environ['ATLAS_QUALIFICATION_SOURCE']=str(S)
 sys.path.insert(0,str(S/'docs/ingestion/burgers-itasca900/integration-v1'));sys.path.insert(0,str(S))
 study=load('independent_saved_burgers',P/'adapters/study.py')
 ref=load('independent_burgers_reference',S/'docs/ingestion/burgers-itasca900/integration-v1/reference.py')
 req=read(study.R/'requests.json');refs=read(study.R/'references.json')
 for c in req['schedules']:check('Burgers original closed form '+c['id'],ref.reference(c['spec'],160)==refs[c['id']])
 outputs={}
 for kind in ['native','wasm']:
  rows=read(work/'evidence'/kind/'calls.json');check('Burgers44 '+kind,len(rows)==44)
  class Replay:
   def __init__(self):self.calls=[]
   def call(self,label,function,args,command):
    row=rows[len(self.calls)];check('Burgers request replay '+kind+label,(label,function,args)==(row['label'],row['function'],row['args']));self.calls.append(row);return row['response']
  replay=Replay();study.execute(replay);check('Burgers full replay '+kind,len(replay.calls)==len(rows))
  report=study.assess(rows);outputs[kind]=report
  tree=ast.parse((P/'adapters/test_burgers_native.py').read_text());fn=next(x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name=='refinement');scope={'PACKET':study.R,'json':json};exec(compile(ast.Module(body=[fn],type_ignores=[]),'frozen-saved-refinement','exec'),scope)
  complete={**report,'separate_refinement':scope['refinement'](rows)}
  corrupted=copy.deepcopy(rows);target=next(c['response']['points'][-1]['state']for c in corrupted if c['label']=='relaxation');target[9]+=10*complete['separate_refinement']['Kelvin']['coarse']
  try:scope['refinement'](corrupted)
  except AssertionError:complete['Kelvin_corruption_rejected']=True
  check('Burgers source/full refinement report exact '+kind,complete==read(work/'evidence'/kind/'report.json'))
  save('burgers-'+kind+'-recomputed.json',complete)
 original=ast.parse((P/'burgers-original-verify.py').read_text());fn=next(x for x in original.body if isinstance(x,ast.FunctionDef)and x.name=='parity');env={'math':math};exec(compile(ast.Module(body=[fn],type_ignores=[]),'original-saved-parity','exec'),env)
 outputs['parity']=env['parity'](read(work/'evidence/native/calls.json'),read(work/'evidence/wasm/calls.json'));outputs['complete_request_replay']=True
 check('Burgers paired report exact',outputs==read(work/'evidence/paired-assessment.json'));save('burgers-recomputed.json',outputs)
 return {'calls_per_backend':44,'source_points_per_backend':outputs['native']['analytical_schedule_points'],'parity_scalars':outputs['parity']['physical_scalars'],'maximum_source_budget_fraction':outputs['native']['maximum_state_budget_fraction'],'transport_scope':'parsed responses/request records retained; original percall stdout spelling not retained','artifacts':{str(p.relative_to(work)):sha(p)for p in [work/'native-build/atlas_burgers_solver',work/'wasm-build/burgers.mjs',work/'wasm-build/burgers.wasm']}}

def main():
 plan,f,tools=common()
 for name,expected,fn in [('power','b79c079bc54db5a89eeba945a51841d9c203032bb90f451d3f8f9ff8dd172ad3',power),('burgers','34bc02ca04b6ba226e9a466732e691f93a3aee860c04dea4a9f8575e0435b350',burgers)]:
  start=len(checks);spec,work=packet(name,expected,plan,f,tools);facts=fn(work)
  save(name+'-decision.json',{'identity':'independent-current-profile-actual-review-v1','profile':name,'author_manifest_sha256':expected,'decision':'ACCEPT_BOUNDED_SAVED_NATIVE_WASM_STUDY','blocking_findings':[],'facts':facts,'checks_after_common':len(checks)-start,'excluded':['full MD scientific/admission','current package catalogue approval','all seven profiles','app/browser/live delivery','unbounded parameter/loading qualification'],'reviewer_compiled_calls':0})
 save('checks.json',{'identity':'current-profile-actual-independent-checks-v1','passed':True,'checks':len(checks),'results':checks,'process_execution_disabled':True})
 print(json.dumps({'checks':len(checks),'passed':True,'compiled_calls':0}))
if __name__=='__main__':
 try:main()
 except Exception as exc:
  save('retained-failure-'+str(len(list(D.glob('retained-failure-*.json'))))+'.json',{'type':type(exc).__name__,'error':str(exc),'checks':checks});raise
