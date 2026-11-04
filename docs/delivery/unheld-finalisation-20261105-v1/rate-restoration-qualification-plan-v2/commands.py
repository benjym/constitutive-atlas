"""Pure argv and original-observer adapter; never auto-executes phases."""
from pathlib import Path
import hashlib,importlib.util,json
HERE=Path(__file__).resolve().parent
ACTUAL=HERE.parent/'rate-restoration-qualification-actual-v2';WORK=Path('/private/tmp/atlas-baseline-delivery-20261105/rate-control-build-v1');SOURCE=Path('/private/tmp/atlas-baseline-delivery-20261105/source')
OBSERVER=HERE.parents[1]/'unheld-finalisation-20261102-v1/baseline-five-host-context-dispatch-v3/proposed/tools/baseline_observe_child_v3.py'
OBSERVER_SHA='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e'
def source_freeze_argv(python,node,tools,manifest_sha,launch_binding):
 assert set(tools)=={'cmake','native_cxx','emcmake','emcc'}
 assert all(Path(p).is_absolute()for p in[python,node,*tools.values()])
 return[python,'-B',str(HERE/'collector.py'),'source-freeze','--plan-manifest-sha256',manifest_sha,'--launch-binding',str(launch_binding),'--node',node,*[v for k in sorted(tools)for v in('--tool',k+'='+tools[k])]]
def phase_argv(pre,manifest_sha):
 python=pre['python']['path'];node=pre['node']['path'];base=[python,'-B',str(HERE/'collector.py')]
 result={phase:[*base,phase,'--plan-manifest-sha256',manifest_sha]for phase in('freeze','native','wasm','pair')}
 result['build']=[python,'-B',str(HERE/'build.py'),'--source-freeze',str(ACTUAL/'source-freeze.json'),'--work',str(WORK),'--slot-handoff','unheld-baseline-five-native-then-wasm-v1','--output',str(ACTUAL/'build'),'--plan-manifest-sha256',manifest_sha]
 for phase in('native','wasm','pair'):result['extra-'+phase]=[node,str(HERE/'extras.mjs'),phase,str(ACTUAL),manifest_sha]
 result['numerical-build']=[pre['build_tools']['cmake']['path'],'--build',str(WORK/'native'),'--target','atlas_numerical_tests','--parallel','1']
 result['md-numerical']=[python,'-B',str(SOURCE/'tools/check_md1997_numerical_ci.py'),'--build',str(WORK/'native'),'--output',str(ACTUAL/'md-numerical')]
 return result
def closed_environment():
 return {'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(WORK/'env-home'),'XDG_CONFIG_HOME':str(WORK/'env-xdg'),'TMPDIR':str(WORK/'env-tmp'),'LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','PYTHONHASHSEED':'0','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_COUNT':'0','GIT_ATTR_NOSYSTEM':'1','GIT_NO_REPLACE_OBJECTS':'1','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}
def observe_phase(pre,phase,manifest_sha):
 assert hashlib.sha256(OBSERVER.read_bytes()).hexdigest()==OBSERVER_SHA
 spec=importlib.util.spec_from_file_location('_original_observer',OBSERVER);o=importlib.util.module_from_spec(spec);spec.loader.exec_module(o)
 spec=importlib.util.spec_from_file_location('_fresh_C_collector',HERE/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
 def bound():
  m.verify_plan(manifest_sha);m.assert_source(SOURCE)
  for pin in [*pre['inputs'],*pre['build_tools'].values(),pre['node'],pre['python']]:m.verify(pin)
  assert [m.pin(p)for p in m.source_files(SOURCE)]==pre['source_inventory']
  if (ACTUAL/'execution-freeze.json').exists():m.validate_execution_freeze(json.loads((ACTUAL/'execution-freeze.json').read_text()))
 bound();primary=None
 try:
  result=o.observe(phase_argv(pre,manifest_sha)[phase],str(SOURCE),ACTUAL/('outer-'+phase),env=closed_environment(),timeout=1800)
  assert result.returncode==0,'first failure retained; stop later phases'
  return result
 except BaseException as error:primary=error;raise
 finally:
  try:bound()
  except BaseException as error:
   (ACTUAL/('post-binding-error-'+phase+'.json')).write_text(json.dumps({'error':repr(error),'primary':repr(primary)if primary else None})+'\n')
   if primary is None:raise
