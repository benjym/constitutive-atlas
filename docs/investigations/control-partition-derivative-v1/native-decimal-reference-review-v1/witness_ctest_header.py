"""Synthetic pre-freeze LastTest command-header challenge; no CTest call."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import tempfile,hashlib,json,importlib.util
D=Path(__file__).resolve().parent;A=D.parent/'native-decimal-reference-v1';sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('witness_assessor',A/'assess_saved.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory(dir='/private/tmp',prefix='decimal-ctest-header-')as td:
 T=Path(td);exe=T/'never-executed';exe.write_text('synthetic');out=T/'combined';out.write_bytes(b'{"synthetic":true}\n');log=T/'LastTest.log';log.write_bytes(('1/1 Testing: atlas_numerical\n1/1 Test: atlas_numerical\nCommand: "/WRONG-EXECUTABLE"\nExtra Command: "'+str(exe)+'"\nDirectory: '+str(T)+'\nOutput:\n----------------------------------------------------------\n').encode()+out.read_bytes()+b'<end of output>\nTest Passed.\n');empty=T/'empty';empty.write_bytes(b'');bind=lambda p:dict(path=str(p),sha256=sha(p));b={'executable_path':str(exe),'executable_sha256':sha(exe),'purpose':'synthetic-test-only','working_directory':str(T)};p={'identity':'md1997-decimal-ctest-child-v1','purpose':'synthetic-test-only','child_name':'atlas_numerical','child_command':[str(exe)],'child_directory':str(T),'child_status':'Test Passed.','last_test_log':bind(log),'combined_output':bind(out),'parent':{'argv':['ctest','--test-dir',str(T)],'cwd':str(T),'returncode':0,'stdout':bind(empty),'stderr':bind(empty)},'selectors':{'ATLAS_NATIVE_FIXTURES':'explicit-gis20-occ-restart-duncan-v5','ATLAS_NUMERICAL_FIXTURES':'md1997-decimal-fd-reference-v1','PYTHONOPTIMIZE':'0'},'executable_sha256':sha(exe)}
 try:r=m.transport(p,b);accepted=True;detail=r[1]
 except Exception as e:accepted=False;detail=str(e)
 print(json.dumps({'identity':'independent-prefreeze-ctest-wrong-header-witness','assessor_sha256':sha(A/'assess_saved.py'),'wrong_actual_command_with_expected_command_substring_accepted':accepted,'detail':detail,'all_inputs_synthetic':True,'compiled_calls':0},indent=2))
