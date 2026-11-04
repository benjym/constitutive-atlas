from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,math,sys
sys.dont_write_bytecode=True
O=Path(__file__).resolve().parent
N=O.parents[1]
R=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
BASE=Path('docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-v1/execution-v2')
E=R/BASE
D=N/'controlled-path-refresh-v1/execution-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
Q=load('controlled_review_qualifier',R/'tools/qualify_controlled_path_refresh.py')
PLAN=Q.load_plan(Q.CURRENT_PLAN,'ed7839d19ec5c5b3615f5bf54d2e6273b8ec19fbe811f12a0336938c42581361')
assert len(PLAN['commands'])==22 and len(PLAN['source_closure'])==250
observations=json.loads((N/'controlled-path-observations-v1.json').read_text())
assert set(observations['files'])=={p.relative_to(D).as_posix() for p in D.rglob('*') if p.is_file()}
for name,pin in observations['files'].items():
 assert sha(D/name)==pin['sha256'] and (D/name).stat().st_size==pin['bytes']
 assert (D/name).read_bytes()==(E/name).read_bytes()
run=json.loads((E/'run.json').read_text())
for row in PLAN['commands']:
 receipt=json.loads((E/(row['id']+'.receipt.json')).read_text())
 assert receipt['argv']==[a.replace('$ROOT',str(R)) for a in row['argv']]
 assert receipt['returncode']==0 and receipt['plan_sha256']==run['plan_sha256']
 assert receipt['repository_root']==str(R)
 assert receipt['started_unix']<=receipt['finished_unix']
 assert sha(R/receipt['log']['path'])==receipt['log']['sha256']
summary={}
for key in ['norsand','interface2016']:
 build=E/key/'engine';pending=json.loads((build/'qualification-pending.json').read_text());b=pending['binding']
 assert pending['schema_version']=='controlled-path-refresh-1' and pending['status']=='passed-original-backend-gates-pending-independent-review'
 assert pending['implementation_run']==run['implementation_run']
 assert pending['model']==Q.MODELS[key] and pending['gates']==Q.GATES[key]
 assert b['source_closure']==PLAN['source_closure']
 assert b['plan']=={'path':str(Q.CURRENT_PLAN),'sha256':run['plan_sha256']}
 assert b['model']==Q.MODELS[key] and b['model_sha256']==sha(R/Q.MODEL_PATHS[key][0])
 for group,directory in [('artifacts',build),('build_metadata',build),('commands',R),('results',R)]:
  for name,digest in b[group].items():assert sha(directory/name)==digest,(key,group,name)
 assert set(b['artifacts'])=={'native/'+PLAN['native_library'],'atlas_path_capability.mjs','atlas_path_capability.wasm'}
 assert set(b['commands'])=={str(BASE/(row['id']+ext)) for row in PLAN['commands'] for ext in ['.receipt.json','.log']}
 expected=('native.json','wasm.json') if key=='norsand' else ('native.json','wasm.json','native-check.json','wasm-check.json','parity.json')
 assert set(b['results'])=={str(BASE/key/n) for n in expected}
 assert set(b['build_metadata'])=={'build-metadata/'+back+'/'+n for back in ['native','wasm'] for n in ['CMakeCache.txt','compile_commands.json']}
 for name,digest in b['generated'].items():assert sha(build/'generated'/name)==digest
 assert b['generated']==b['native_generated'] and set(b['generated'])==set(Q.GENERATED)
 for backend in ['native','wasm']:
  original=R/('.local/controlled-path-refresh-20261105-v1/'+key+'-'+backend)
  for name in Q.GENERATED:assert sha(original/'generated'/name)==b['generated'][name]
  for name in ['CMakeCache.txt','compile_commands.json']:assert (build/'build-metadata'/backend/name).read_bytes()==(original/name).read_bytes()
  entries=json.loads((build/'build-metadata'/backend/'compile_commands.json').read_text());assert entries
  assert all(x['directory']==str(original) for x in entries)
 Q.check_backend_identity(key,b['artifacts'],b['results'])
 a=json.loads((E/key/'native.json').read_text());w=json.loads((E/key/'wasm.json').read_text())
 summary[key]={'requests_per_backend':len(a['rows']),'successes_native':sum(x['status'] for x in a['rows']),'successes_wasm':sum(x['status'] for x in w['rows']),'pending_sha256':sha(build/'qualification-pending.json'),'artifacts':b['artifacts']}
 if key=='norsand':
  checker=load('saved_norsand_checker',R/Q.NORSAND/'check_backend_results_v3.py');stream=io.StringIO()
  with contextlib.redirect_stdout(stream):checker.main(str(R/Q.NORSAND/'backend-requests-v2.json'),str(E/key/'native.json'),str(E/key/'wasm.json'))
  (O/'norsand-checker-replay.json').write_text(stream.getvalue())
  assert len(a['rows'])==58 and sum(x['status'] for x in a['rows'])==40 and sum(x['status'] for x in w['rows'])==40
 else:
  checker=load('saved_interface_checker',R/Q.INTERFACE/'implementation-v1/check_backend_results_v2.py')
  for backend in ['native','wasm']:
   result=checker.assess(json.loads((E/key/(backend+'.json')).read_text()))
   saved=json.loads((E/key/(backend+'-check.json')).read_text())
   assert saved['passed'] and saved['checker_sha256']==sha(Path(checker.__file__))
   assert saved['results'][0]['assessment']==result and saved['results'][0]['sha256']==sha(E/key/(backend+'.json'))
   (O/('interface-'+backend+'-checker-replay.json')).write_text(json.dumps(result,indent=2)+'\n')
  freeze=R/Q.INTERFACE/'execution-v1/source-freeze-v2.json';policy=json.loads(freeze.read_text());details=[]
  for x,y in zip(a['rows'],w['rows']):
   assert x['id']==y['id'] and x['status']==y['status'] and x['coordinate']==y['coordinate'] and math.isfinite(x['coordinate'])
   assert len(x['state'])==len(y['state'])==5 and len(x['observables'])==len(y['observables'])==8
   errors=[]
   for field,scales in [('state',policy['state_scales']),('observables',policy['observable_scales'])]:
    for av,bv,scale in zip(x[field],y[field],scales):
     assert type(av) in [float,int] and type(bv) in [float,int] and math.isfinite(av) and math.isfinite(bv)
     error=abs(av-bv)/scale;assert error<=policy['parity_scaled_absolute'];errors.append(error)
   details.append({'id':x['id'],'max_scaled_error':max(errors)})
  saved=json.loads((E/key/'parity.json').read_text());assert saved['passed'] and saved['requests']==59 and saved['scaled_absolute_limit']==policy['parity_scaled_absolute']==1e-10
  assert saved['rows']==details and saved['inputs']=={'native.json':sha(E/key/'native.json'),'wasm.json':sha(E/key/'wasm.json'),'source-freeze-v2.json':sha(freeze)}
observer=json.loads((N/'controlled-path-refresh-observer-v1/receipt.json').read_text())
assert observer['returncode']==observer['reaped_returncode']==0 and observer['mandatory_reap'] and observer['status']=='passed' and observer['cleanup_errors']==[]
assert observer['started_epoch']<=observer['ended_epoch']
for key in ['stdout','stderr','executable']:
 pin=observer[key];p=Path(pin['path']);assert sha(p)==pin['sha256'] and p.stat().st_size==pin['bytes']
assert observer['argv'][-1]==run['implementation_run'] and observer['cwd']==str(R)
(O/'checks.json').write_text(json.dumps({'status':'PASS','retained_files':len(observations['files']),'source_files':250,'command_receipts_and_logs':22,'summary':summary,'outer_exit_and_mandatory_reap':True,'compiled_executions_by_reviewer':0},indent=2)+'\n')
print(json.dumps(summary))
