"""Independent mocked dispatcher probes; never invoke a material or real CTest."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,unittest,io,copy,subprocess,base64
from unittest.mock import patch
D=Path(__file__).resolve().parent;C=D.parent;A=C/'native-ci-dispatch-implementation-v1';S=Path('/private/tmp/atlas-md1997-ci-dispatch-v1/source')
sys.path.insert(0,str(S))
from tools import check_native_fixture_dispatch as d
from tools import check_md1997_native_fixture_contract as md
from tests import test_native_fixture_dispatch as tests
from tests import test_ci_profiles,test_native_fixture_contracts
out={'identity':'independent-native-ci-dispatch-implementation-mock-review-v1','compiled_calls':0,'real_CTest_calls':0,'checks':[],'witnesses':[]}
def note(name,passed,**more):out['checks'].append(dict(id=name,passed=passed,**more));assert passed,name
stream=io.StringIO();suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m)for m in [tests,test_ci_profiles,test_native_fixture_contracts]);result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
(D/'author-mock-test-replay.txt').write_text(stream.getvalue());note('author18-mock-unit-tests-reproduced',result.wasSuccessful()and result.testsRun==18,testsRun=result.testsRun)
# Reuse only the author's synthetic filesystem constructor; expected decisions,
# modified records and witnesses below are independent. All artifacts are
# non-executable text; each process callback is supplied explicitly.
t=tests.DispatchTests();t.setUp()
try:
 source,build=t.fixture('16')
 # Bind actual reviewed CMake bytes, although the artifact remains synthetic.
 (source/'CMakeLists.txt').write_bytes((S/'CMakeLists.txt').read_bytes())
 # B1: removing mandatory registrations is accepted because expected coverage
 # is derived solely from the potentially incomplete generated registration.
 (build/'CTestTestfile.cmake').write_text('add_test("atlas_numerical" "stand-in")\nadd_test("atlas_recorded" "stand-in")\n')
 def abbreviated(argv,env,**kwargs):
  names=['atlas_recorded']if argv[-1]=='^atlas_recorded$'and argv[-2]=='-R'else ['atlas_numerical']
  log='Start testing\n'+''.join(f'{i}/2 Testing: {name}\nOutput:\n'+(md.POSITIVE_STDOUT if name=='atlas_numerical'else '')+'Test Passed.\n'for i,name in enumerate(names,1))+'End testing\n'
  p=build/'Testing/Temporary/LastTest.log';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(log)
  return subprocess.CompletedProcess(argv,0,b'synthetic abbreviated CTest',b'')
 for name in ['macos-main','linux-main','recorded']:
  output=D/('witness-omitted-registration-'+name+'.json')
  with patch.object(d.shutil,'which',return_value=str(build/'mock-ctest')):
   r=d.execute('ctest',build/'generated/models.json',source,build,output,name,abbreviated,{})
  note('witness-omitted-registration-accepted-'+name,r['status']=='passed')
 out['witnesses'].append({'id':'B1','observed':'all three suite routes accept a two-registration CTest catalogue, omitting eight mandatory native registrations present in unchanged CMake source','native_CMake_sha256':hashlib.sha256((source/'CMakeLists.txt').read_bytes()).hexdigest(),'omitted':['atlas_tensor_square','atlas_python','atlas_time','atlas_capacity','atlas_recorded_fixture','atlas_expm_context','atlas_log1p_context','atlas_scalar_functions'],'all_processes':'explicit synthetic callbacks; no CTest executed'})
 # B2: the selected CTest executable is hashed before invocation but is absent
 # from the post-observation context comparison.
 (build/'CTestTestfile.cmake').write_text('add_test("atlas_numerical" "stand-in")\nadd_test("atlas_recorded" "stand-in")\n')
 before=hashlib.sha256((build/'mock-ctest').read_bytes()).hexdigest()
 def mutate_ctest(argv,env,**kwargs):
  r=abbreviated(argv,env,**kwargs);(build/'mock-ctest').write_bytes(b'CHANGED SYNTHETIC CTEST EXECUTABLE\n');return r
 with patch.object(d.shutil,'which',return_value=str(build/'mock-ctest')):
  r=d.execute('ctest',build/'generated/models.json',source,build,D/'witness-ctest-artifact-drift.json','macos-main',mutate_ctest,{})
 after=hashlib.sha256((build/'mock-ctest').read_bytes()).hexdigest()
 note('witness-CTest-artifact-drift-accepted',r['status']=='passed'and before!=after and r['ctest_executable_sha256']==before)
 out['witnesses'].append({'id':'B2','observed':'receipt passes after selected CTest executable bytes change during callback; only prehash retained','before':before,'after':after})
finally:t.doCleanups()
(D/'transport-probes.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'author_tests':result.testsRun,'witnesses':[w['id']for w in out['witnesses']],'compiled_calls':0}))
