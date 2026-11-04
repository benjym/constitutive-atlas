"""Independent saved-source and inert-process review; no real child permitted."""
from pathlib import Path
import ast, hashlib, importlib.util, json, runpy, sys, tempfile, types
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
AUTHOR=HERE.parents[1]/'recorded-legacy-integration-plan-v1'
EXPECTED='6215f058576a4ff63640e0b00e89ae68fdcea278f1ccbf1055bfb7ea256c1c59'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ok(v,n):
 assert v,n
 checks.append(n)
ok(sha(AUTHOR/'manifest.json')==EXPECTED,'exact frozen author manifest')
manifest=json.loads((AUTHOR/'manifest.json').read_text())
for row in manifest['files']:
 p=AUTHOR/row['path'];ok(p.is_file()and not p.is_symlink()and sha(p)==row['sha256']and p.stat().st_size==row['size_bytes'],'author member '+row['path'])
saved=json.loads((AUTHOR/'check.stdout.json').read_text())
# Execute unchanged author checks, redirect only their output/temporary fixture roots.
write=Path.write_text;temporary=tempfile.TemporaryDirectory
def redirected_write(p,data,*args,**kwargs):
 if p==AUTHOR/'check.stdout.json':p=HERE/'author-replay.json'
 return write(p,data,*args,**kwargs)
def owned_temp(*args,**kwargs):
 kwargs['dir']=HERE
 return temporary(*args,**kwargs)
with patch.object(Path,'write_text',redirected_write),patch.object(tempfile,'TemporaryDirectory',owned_temp):
 runpy.run_path(str(AUTHOR/'check.py'),run_name='independent_exact_author_replay')
ok(json.loads((HERE/'author-replay.json').read_text())==saved,'all39 author checks exact report equality')
ok(sha(AUTHOR/'manifest.json')==EXPECTED,'author manifest unchanged after replay')
for row in manifest['files']:ok(sha(AUTHOR/row['path'])==row['sha256'],'author bytes unchanged '+row['path'])
delta=json.loads((AUTHOR/'source-delta.json').read_text())['files']
ok({r['path']for r in delta}=={'CMakeLists.txt','.github/workflows/qualification.yml','tools/build_recorded_legacy_ci.py'},'exact three canonical paths')
for row in delta:
 p=AUTHOR/row['proposal'];ok(sha(p)==row['sha256']and p.stat().st_size==row['bytes'],'delta payload '+row['path'])
old=(AUTHOR/'originals/.github/workflows/qualification.yml').read_text();new=(AUTHOR/'proposed/.github/workflows/qualification.yml').read_text()
ok(new.count('id: recorded_legacy_build')==1,'unique step producer')
ok(new.count('ATLAS_RECORDED_LEGACY_SHA256:')==1,'one exact SHA environment binding')
ok(new.count('ATLAS_RECORDED_SOLVER:')==old.count('ATLAS_RECORDED_SOLVER:'),'current recorded runtime still declared')
ok(new.index('Build separately bound historical recorded catalogue')<new.index('Verify recorded-path JSON replay')<new.index('Retain historical recorded build receipts'),'build/test/always retention ordering')
cmake=(AUTHOR/'proposed/CMakeLists.txt').read_text()
ok(cmake.count('add_executable(atlas_recorded_legacy_solver EXCLUDE_FROM_ALL cpp/main.cpp)')==1,'one opt-in generic native target')
ok('if(NOT EMSCRIPTEN)'in cmake.split('# Proposed native-only addition;')[1],'target excluded from Wasm')
spec=importlib.util.spec_from_file_location('independent_legacy_build',AUTHOR/'proposed/tools/build_recorded_legacy_ci.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with temporary(prefix='independent-inert-',dir=HERE)as td:
 t=Path(td).resolve();root=t/'repo';root.mkdir();m.ROOT=root
 driver=t/'inert-driver';driver.write_text('not executable');build=t/'build';(build/'CMakeFiles/v').mkdir(parents=True)
 cache=build/'CMakeCache.txt';compiler=build/'CMakeFiles/v/CMakeCXXCompiler.cmake'
 cache.write_text('CMAKE_HOME_DIRECTORY:INTERNAL='+str(root)+'\n');compiler.write_text('set(CMAKE_CXX_COMPILER "'+str(driver)+'")\n')
 ok(m.metadata(build)['resolved_cxx']==m.pin(driver),'actual metadata parser pins configured driver')
 cache.write_text('CMAKE_HOME_DIRECTORY:INTERNAL=/wrong\n')
 try:m.metadata(build)
 except ValueError:checks.append('wrong configured source rejects')
 else:raise AssertionError('wrong source accepted')
 cache.write_text('CMAKE_HOME_DIRECTORY:INTERNAL='+str(root)+'\n');compiler.write_text('no compiler')
 try:m.metadata(build)
 except ValueError:checks.append('missing configured compiler rejects')
 else:raise AssertionError('missing compiler accepted')
 # Primary launch error and source postguard error must both survive.
 source=t/'source';source.write_text('before');cm=t/'inert-cmake';cm.write_text('inert')
 primary=OSError('independent inert launch failure')
 def inventory():return {'fixture':m.pin(source)}
 def fake(*args,**kw):
  kw['stdout'].write('raw before exception\n');kw['stderr'].write('diagnostic before exception\n');source.write_text('after');raise primary
 metadata={'resolved_cxx':m.pin(driver),'files':[],'purpose':'manufactured'}
 with patch.object(m,'inventory',inventory),patch.object(m,'metadata',return_value=metadata),patch.object(m.shutil,'which',return_value=str(cm)),patch.object(m.subprocess,'run',side_effect=fake):
  try:m.run(build,t/'receipt',t/'github-output')
  except OSError as e:ok(e is primary,'original launch exception survives simultaneous postguard failure')
  else:raise AssertionError('launch failure accepted')
 r=json.loads((t/'receipt/receipt.json').read_text())
 ok(r['status']=='failed'and r['process_status']=='raised'and 'returncode'not in r,'unknown returncode remains unknown')
 ok('independent inert launch failure'in r['error']and 'source mutated'in r['post_binding_error'],'both failures durably retained')
 ok(len(r['logs'])==2 and all(Path(x['path']).read_text()for x in r['logs']),'both closed raw logs retained')
 ok(not(t/'github-output').exists(),'no success SHA after failure')
ok(not list(HERE.glob('independent-inert-*'))and not list(HERE.glob('recorded-build-mock-*')),'all owned fixtures removed')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'original_author_checks':39,'actual_processes':0,'fixtures_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','independent_checks':len(checks),'original_author_checks':39}))
