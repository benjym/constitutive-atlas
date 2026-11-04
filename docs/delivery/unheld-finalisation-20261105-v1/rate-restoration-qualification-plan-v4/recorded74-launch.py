from pathlib import Path
import importlib.util,json,sys,hashlib,subprocess,shutil,time
N=Path(__file__).resolve().parents[1];P=N/'rate-restoration-qualification-plan-v3';MANIFEST='4b3a8592279b7a99a18bd0a168bf95a78ee7f95f9dbc0efe1ffcc6417fac5812'
spec=importlib.util.spec_from_file_location('reviewed_C_commands',P/'commands.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
pre=json.loads((c.ACTUAL/'source-freeze.json').read_text());phase=sys.argv[1];assert phase in('legacy-build','recorded74')
spec=importlib.util.spec_from_file_location('continuation_v4',Path(__file__).resolve().parent/'commands.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
V4SHA=sys.argv[2];review_pin=json.loads(Path(sys.argv[3]).read_text());v.guard(pre,V4SHA,review_pin)
c.ACTUAL=v.ACTUAL
previous=c.ACTUAL/'outer-extra-pair/receipt.json' if phase=='legacy-build'else c.ACTUAL/'outer-legacy-build/receipt.json';r=json.loads(previous.read_text());assert r['returncode']==0 and r['mandatory_reap'] is True
legacy_output=c.ACTUAL/'recorded-legacy-build';python=pre['python']['path'];modules=['tests.test_experiment_replay','tests.test_recorded_api','tests.test_recorded_path','tests.test_web_recorded','tests.test_refinement','tests.test_isotropic_reference','tests.test_resolution_diagnosis','tests.test_recorded_restarts']
base_argv=c.phase_argv;base_env=c.closed_environment
extra_argv={'legacy-build':[python,'-B',str(c.SOURCE/'tools/build_recorded_legacy_ci.py'),'--build',str(c.WORK/'native'),'--output',str(legacy_output)],'recorded74':[python,'-B','-m','unittest',*modules,'-v']}
def phase_argv(pre,manifest):return {**base_argv(pre,manifest),**extra_argv}
def environment():
 env=base_env()
 if phase=='recorded74':
  receipt=json.loads((legacy_output/'receipt.json').read_text());assert receipt['status']=='passed' and receipt['post_bindings_unchanged'] is True
  artifact=receipt['artifact'];assert hashlib.sha256(Path(artifact['path']).read_bytes()).hexdigest()==artifact['sha256'];assert receipt['historical_catalogue']=='1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c'
  env.update(ATLAS_RECORDED_SOLVER=str(c.WORK/'native/atlas_solver'),ATLAS_RECORDED_LEGACY_SOLVER=artifact['path'],ATLAS_RECORDED_LEGACY_SHA256=artifact['sha256'])
 return env
c.phase_argv=phase_argv;c.closed_environment=environment
ps=subprocess.check_output(['/bin/ps','-axo','pid=,ppid=,command='],text=True);private=N.parents[2]/'.local/retained-evidence'/('baseline-five-C-v4-'+phase+'-preflight-20261105.raw');assert not private.exists();private.write_text(ps);active=[]
for line in ps.splitlines():
 parts=line.strip().split(None,2)
 if len(parts)!=3:continue
 words=parts[2].split();base=Path(words[0]).name if words else ''
 if base.startswith('atlas_')or base in('clang','clang++','emcc','em++')or(base=='cmake'and'--build'in words)or(base in('node','nodejs')and any(s in parts[2]for s in('/wasm-cli.mjs','/extras.mjs'))):active.append({'pid':int(parts[0]),'executable':base})
assert not active,active
(c.ACTUAL/(phase+'-preflight.json')).write_text(json.dumps({'epoch':time.time(),'private_process_inventory':str(private),'active_compiled':active,'free_bytes':shutil.disk_usage('/private/tmp').free,'argv':extra_argv[phase]},indent=2)+'\n')
primary=None
try:result=c.observe_phase(pre,phase,MANIFEST)
except BaseException as error:primary=error;raise
finally:
 try:v.guard(pre,V4SHA,review_pin)
 except BaseException as error:
  target=c.ACTUAL/('post-v4-binding-error-'+phase+'.json');assert not target.exists()
  target.write_text(json.dumps({'error':repr(error),'primary':repr(primary)if primary else None})+'\n')
  if primary is None:raise
if phase=='recorded74':
 assert 'Ran 74 tests in ' in result.stderr and '\nOK\n' in result.stderr and 'skipped='not in result.stderr,'original mandatory74 suite/count/zero-skip gate failed; raw retained'
print(json.dumps({'phase':phase,'returncode':result.returncode,'mandatory_reap':result.receipt['mandatory_reap'],'elapsed_seconds':result.receipt['elapsed_seconds']}));sys.exit(result.returncode)
