"""Independent mocked dispatcher probes; never invoke a material or real CTest."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import json,hashlib,unittest,io,copy,subprocess,base64,argparse,re
from unittest.mock import patch
D=Path(__file__).resolve().parent;C=D.parent;A=C/'native-ci-dispatch-implementation-v1';S=Path('/private/tmp/atlas-md1997-ci-dispatch-v1/source')
args=argparse.ArgumentParser();args.add_argument('--output',type=Path,required=True);DEST=args.parse_args().output;DEST.mkdir(parents=True,exist_ok=False)
sys.path.insert(0,str(S))
from tools import check_native_fixture_dispatch as d
from tools import check_md1997_native_fixture_contract as md
from tests import test_native_fixture_dispatch as tests
from tests import test_ci_profiles,test_native_fixture_contracts
out={'identity':'independent-native-ci-dispatch-implementation-mock-review-v1','compiled_calls':0,'real_CTest_calls':0,'checks':[],'witnesses':[]}
def note(name,passed,**more):out['checks'].append(dict(id=name,passed=passed,**more));assert passed,name
stream=io.StringIO();suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(m)for m in [tests,test_ci_profiles,test_native_fixture_contracts]);result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
(DEST/'author-mock-test-replay.txt').write_text(stream.getvalue());note('author18-mock-unit-tests-reproduced',result.wasSuccessful()and result.testsRun==18,testsRun=result.testsRun)
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
  output=DEST/('witness-omitted-registration-'+name+'.json')
  with patch.object(d.shutil,'which',return_value=str(build/'mock-ctest')):
   r=d.execute('ctest',build/'generated/models.json',source,build,output,name,abbreviated,{})
  note('witness-omitted-registration-accepted-'+name,r['status']=='passed')
 out['witnesses'].append({'id':'B1','observed':'all three suite routes accept a two-registration CTest catalogue, omitting eight mandatory native registrations present in unchanged CMake source','native_CMake_sha256':hashlib.sha256((source/'CMakeLists.txt').read_bytes()).hexdigest(),'omitted':['atlas_tensor_square','atlas_python','atlas_time','atlas_capacity','atlas_recorded_fixture','atlas_expm_context','atlas_log1p_context','atlas_scalar_functions'],'all_processes':'explicit synthetic callbacks; no CTest executed'})
 # B2: the selected CTest executable is hashed before invocation but is absent
 # from the post-observation context comparison.
 names=re.findall(r'add_test\(NAME ([^ ]+) COMMAND',(source/'CMakeLists.txt').read_text())
 note('exact unchanged source declares ten mandatory native tests',len(names)==10)
 (build/'CTestTestfile.cmake').write_text(''.join('add_test("'+n+'" "stand-in")\n'for n in names))
 def complete_log(argv,env,**kwargs):
  selected=[n for n in names if (re.search(argv[-1],n)is not None)==(argv[-2]=='-R')]
  log='Start testing\n'+''.join(f'{i}/10 Testing: {n}\n{i}/10 Test: {n}\nCommand: \"stand-in\"\nDirectory: synthetic\nOutput:\n----------------------------------------------------------\n'+(md.POSITIVE_STDOUT if n=='atlas_numerical'else '')+'<end of output>\nTest time = 0.00 sec\n----------------------------------------------------------\nTest Passed.\n'for i,n in enumerate(selected,1))+'End testing\n'
  q=build/'Testing/Temporary/LastTest.log';q.parent.mkdir(parents=True,exist_ok=True);q.write_text(log)
  return subprocess.CompletedProcess(argv,0,b'synthetic complete CTest',b'')
 before=hashlib.sha256((build/'mock-ctest').read_bytes()).hexdigest()
 def mutate_ctest(argv,env,**kwargs):
  r=complete_log(argv,env,**kwargs);(build/'mock-ctest').write_bytes(b'CHANGED SYNTHETIC CTEST EXECUTABLE\n');return r
 with patch.object(d.shutil,'which',return_value=str(build/'mock-ctest')):
  r=d.execute('ctest',build/'generated/models.json',source,build,DEST/'witness-ctest-artifact-drift.json','macos-main',mutate_ctest,{})
 after=hashlib.sha256((build/'mock-ctest').read_bytes()).hexdigest()
 note('witness-CTest-artifact-drift-accepted',r['status']=='passed'and before!=after and r['ctest_executable_sha256']==before)
 out['witnesses'].append({'id':'B2','observed':'receipt passes after selected CTest executable bytes change during callback; only prehash retained','before':before,'after':after})
 # B3: a substring with a nonempty prefix is accepted as an exact profile line.
 def prefix_label(argv,env,**kwargs):
  result=complete_log(argv,env,**kwargs)
  log=build/'Testing/Temporary/LastTest.log';log.write_text(log.read_text().replace(md.POSITIVE_STDOUT,'WRONG-PREFIX '+md.POSITIVE_STDOUT))
  return result
 with patch.object(d.shutil,'which',return_value=str(build/'mock-ctest')):
  r=d.execute('ctest',build/'generated/models.json',source,build,DEST/'witness-nonexact-positive-label.json','macos-main',prefix_label,{})
 note('witness-nonexact-positive-label-accepted',r['status']=='passed')
 out['witnesses'].append({'id':'B3','observed':'all10 registrations present, but the only positive label line is prefixed WRONG-PREFIX and still qualifies by substring'})
 # C1: timeout+nonUTF8 fails overall and retains raw, but loses row terminal state.
 def timeout_utf(argv,**kwargs):raise subprocess.TimeoutExpired(argv,120,output=b'\xff',stderr=b'partial-timeout')
 try:d.execute('check',build/'generated/models.json',source,build,DEST/'concern-timeout-nonutf8.json',None,timeout_utf,{})
 except UnicodeDecodeError:pass
 else:raise AssertionError('nonUTF8 timeout accepted')
 r=json.loads((DEST/'concern-timeout-nonutf8.json').read_text());row=r['processes'][0]
 note('concern-nonUTF8-timeout-original-failure-lost',r['status']=='failed'and row['status']=='started'and 'error_type'not in row and base64.b64decode(row['stdout_base64'])==b'\xff')
 out['concerns']=[{'id':'C1','observed':'timeout with nonUTF8 partial stdout fails overall with UnicodeDecodeError and retains bytes, but row remains started and loses TimeoutExpired type/details','not_false_acceptance':True}]
finally:t.doCleanups()
(DEST/'transport-probes.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({'author_tests':result.testsRun,'witnesses':[w['id']for w in out['witnesses']],'compiled_calls':0}))
