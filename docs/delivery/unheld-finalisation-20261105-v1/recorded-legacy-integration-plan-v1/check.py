from pathlib import Path
import ast,json,hashlib,importlib.util,sys,tempfile,subprocess
from unittest.mock import patch
O=Path(__file__).resolve().parent;N=O.parent;R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sys.path.insert(0,str(R));checks=[]
def ok(x,n):assert x,n;checks.append(n)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
for q in O.rglob('*.py'):ast.parse(q.read_text());checks.append('Python syntax '+q.name)
g=json.loads((O/'GATES.json').read_text())
for name,row in g['base'].items():ok(sha(O/'originals'/name)==row['sha256'],'retained exact preimage '+name)
snippet=(N/'recorded-native-fixtures-fix-v1/legacy-target.cmake').read_bytes();ok(sha(N/'recorded-native-fixtures-fix-v1/legacy-target.cmake')==g['accepted_snippet']['sha256'],'accepted target exactpin')
ok((O/'proposed/CMakeLists.txt').read_bytes()==(O/'originals/CMakeLists.txt').read_bytes()+b'\n'+snippet,'CMake only exact append')
old=(O/'originals/.github/workflows/qualification.yml').read_text();new=(O/'proposed/.github/workflows/qualification.yml').read_text();start=new.index('    - name: Build separately bound historical recorded catalogue');end=new.index('    - name: Verify recorded-path JSON replay',start);buildstep=new[start:end]
a=new.replace(buildstep,'').replace('        ATLAS_RECORDED_LEGACY_SOLVER: "${{ github.workspace }}/build/atlas_recorded_legacy_solver"\n','').replace('        ATLAS_RECORDED_LEGACY_SHA256: "${{ steps.recorded_legacy_build.outputs.solver_sha256 }}"\n','');start=a.index('    - name: Retain historical recorded build receipts');end=a.index('    timeout-minutes: 180\n  wasm:',start);retain=a[start:end];a=a[:start]+a[end:];ok(a==old,'whole workflow inverse exact old74command/matrices/othersteps')
ok('if: always()'in retain and 'actions/upload-artifact@v4'in retain,'always retain genuine build failures')
ok('id: recorded_legacy_build'in buildstep and '--github-output "$GITHUB_OUTPUT"'in buildstep,'genuine output producer')
h=load('_fixture_source',N/'recorded-native-fixtures-fix-v1/proposed/tests/recorded_native_fixtures.py');models=[json.loads(q.read_text())for q in h.legacy_paths()];legacyrows=h.LEGACY_INPUTS
m=load('_proposed_build',O/'proposed/tools/build_recorded_legacy_ci.py')
for scenario in ['pass','failed-status','raised-child','source-drift','wrong-catalogue','tool-drift']:
 with tempfile.TemporaryDirectory(prefix='recorded-build-mock-',dir=O)as td:
  t=Path(td).resolve();root=t/'repo';root.mkdir();m.ROOT=root;m.__file__=str(root/'tools/build_recorded_legacy_ci.py');h.ROOT=root
  names=['CMakeLists.txt','.github/workflows/qualification.yml','cpp/main.cpp','tests/recorded_native_fixtures.py','tools/build_recorded_legacy_ci.py','tools/generate_recorded_legacy_models.py','atlas/compiler.py','cpp/include/solver.hpp','schemas/model.schema.json','cmake/AtlasScalarFunctions.cmake','cpp/scalar-functions/a.c']
  for name in names:q=root/name;q.parent.mkdir(parents=True,exist_ok=True);q.write_text('inert source')
  for row in legacyrows:q=root/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((R/row['path']).read_bytes())
  driver=t/'inert-cxx';driver.write_text('INERT NO PROCESS');cmake=t/'inert-cmake';cmake.write_text('INERT NO PROCESS');build=t/'build';(build/'CMakeFiles/fake').mkdir(parents=True)
  (build/'CMakeCache.txt').write_text('CMAKE_HOME_DIRECTORY:INTERNAL='+str(root)+'\n');(build/'CMakeFiles/fake/CMakeCXXCompiler.cmake').write_text('set(CMAKE_CXX_COMPILER "'+str(driver)+'")\n')
  output=t/'out';github=t/'github-output';calls=[]
  def fake(argv,**kw):
   calls.append(argv);kw['stdout'].write('genuine manufactured stdout\n');kw['stderr'].write('manufactured diagnostic\n')
   if scenario=='raised-child':raise OSError('manufactured process failure')
   gen=build/'recorded-legacy-generated';gen.mkdir();(gen/'models.hpp').write_text('manufactured header');(gen/'models.json').write_text(json.dumps({'sha256':h.LEGACY_HASH if scenario!='wrong-catalogue'else'bad','models':models}));(build/'atlas_recorded_legacy_solver').write_text('MANUFACTURED NOT EXECUTABLE')
   if scenario=='source-drift':(root/'cpp/main.cpp').write_text('mutated')
   if scenario=='tool-drift':cmake.write_text('mutated')
   return subprocess.CompletedProcess(argv,17 if scenario=='failed-status'else 0)
  with patch.object(m.shutil,'which',return_value=str(cmake)),patch.object(m.subprocess,'run',side_effect=fake),patch.dict(sys.modules,{'tests.recorded_native_fixtures':h}):
   try:r=m.run(build,output,github)
   except (ValueError,RuntimeError,OSError):ok(scenario!='pass','reject '+scenario)
   else:ok(scenario=='pass','only positive accepts')
  receipt=json.loads((output/'receipt.json').read_text());ok(len(calls)==1 and calls[0][-4:]==['--target','atlas_recorded_legacy_solver','--parallel','1'],'one serial exacttarget '+scenario);ok(len(receipt['logs'])==2,'both rawlogs retained '+scenario)
  if scenario=='pass':ok(receipt['status']=='passed'and receipt['returncode']==0 and receipt['post_bindings_unchanged']and github.read_text()=='solver_sha256='+receipt['artifact']['sha256']+'\n','genuine success output only');ok(receipt['prior_configure_process']is None,'no invented priorconfigure process');ok(receipt['configured_after']['resolved_cxx']==receipt['tools']['cxx'],'configured compiler bound')
  else:ok(receipt['status']=='failed'and not github.exists(),'failedreceipt no output '+scenario)
  if scenario=='failed-status':ok(receipt['returncode']==17,'original nonzero status preserved')
  if scenario=='raised-child':ok('returncode'not in receipt and receipt['process_status']=='raised','unknown exit not invented')
  if scenario in ['source-drift','tool-drift']:ok(receipt['returncode']==0 and 'post_binding_error'in receipt,'successfulchild+failedpostguard preserved')
(O/'check.stdout.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'manufactured_only':True,'actual_cmake_native_material_calls':0,'temporary_resources_removed':True},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
