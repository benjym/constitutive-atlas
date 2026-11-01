"""Synthetic saved transport only. Mock artifact is plain text, never executed."""
if not __debug__:raise RuntimeError('Unoptimized Python required')
from pathlib import Path
import json,copy,hashlib
import assess_saved as A
D=Path(__file__).resolve().parent;M=D/'synthetic-transport';M.mkdir(exist_ok=True);read=A.read;write=lambda p,x:p.write_text(json.dumps(x,indent=2)+'\n');sha=A.sha
q=read(D/'requests.json');r=read(D/'reference.json');artifact=M/'not-an-executable.txt';artifact.write_text('Synthetic transport fixture, NOT a compiled artifact.\n')
b=dict(identity='md1997-decimal-native-build-binding-v1',purpose='synthetic-test-only',source_freeze_sha256=sha(D/'source-freeze.json'),fixture_sha256=q['fixture_sha256'],generated_catalogue_sha256='1'*64,executable_sha256=sha(artifact),executable_path=str(artifact),working_directory=str(M),model_sha256=q['model_sha256']);write(M/'binding.json',b)
bind={k:r[k]for k in ['evaluator_sha256','policy_sha256','base_source_freeze_sha256','model_sha256']};bind.update(request_sha256=sha(D/'requests.json'),reference_sha256=sha(D/'reference.json'),build_binding_sha256=sha(M/'binding.json'))
base={k:q[k]for k in ['layout','state_hex','previous_hex','loading_hex','parameters_hex','scales_hex']}
env=dict(identity='md1997-decimal-ad-export-v1',selector='md1997-decimal-fd-reference-v1',status='exported-unassessed',models=16,bindings=bind,base=base,endpoints=[{**e,'domain':True,'branch':True}for e in q['endpoints']],ad_hex=[[float(r['data']['120']['secants'][2*col][row]).hex()for col in range(14)]for row in range(14)],cpp_checks={'rank13':True,'rotation':True,'other_models':True})
selectors={'ATLAS_NATIVE_FIXTURES':'explicit-gis20-occ-restart-duncan-v5','ATLAS_NUMERICAL_FIXTURES':'md1997-decimal-fd-reference-v1','PYTHONOPTIMIZE':'0'}
records=[]
def rawfile(name,data):
 p=M/name;p.write_bytes(data);return dict(path=str(p),sha256=sha(p))
def process(e,kind='direct',raw=None):
 wire=(json.dumps(e,indent=2)+'\n').encode()if raw is None else raw
 if kind=='direct':return dict(identity='md1997-decimal-direct-process-v1',purpose='synthetic-test-only',argv=[str(artifact)],cwd=str(M),returncode=0,stdout=rawfile('stdout',wire),stderr=rawfile('stderr',b''),selectors=selectors.copy(),executable_sha256=sha(artifact))
 log=('Start testing: synthetic\n1/10 Testing: atlas_numerical\n1/10 Test: atlas_numerical\nCommand: "'+str(artifact)+'"\nDirectory: '+str(M)+'\n"atlas_numerical" start time: synthetic\nOutput:\n----------------------------------------------------------\n').encode()+wire+b'<end of output>\nTest time = 0 sec\n----------------------------------------------------------\nTest Passed.\nEnd testing: synthetic\n'
 return dict(identity='md1997-decimal-ctest-child-v1',purpose='synthetic-test-only',child_name='atlas_numerical',child_command=[str(artifact)],child_directory=str(M),child_status='Test Passed.',last_test_log=rawfile('LastTest.log',log),combined_output=rawfile('combined-output',wire),parent=dict(argv=['ctest','--test-dir',str(M),'--output-on-failure'],cwd=str(M),returncode=0,stdout=rawfile('parent-stdout',b'synthetic parent CTest stdout\n'),stderr=rawfile('parent-stderr',b'')),selectors=selectors.copy(),executable_sha256=sha(artifact))
def run(label,e=None,kind='direct',modify=None,raw=None,expected=True,binding_hash=None):
 p=process(copy.deepcopy(env if e is None else e),kind,raw)
 if modify:modify(p)
 write(M/'process.json',p)
 try:
  out=A.assess(D/'requests.json',D/'reference.json',M/'process.json',M/'binding.json',binding_hash or sha(M/'binding.json'));passed=out['passed'];err=out.get('failures',[])
  if passed:assert out['comparisons']==588 and out['purpose']=='synthetic-test-only'
 except(Exception)as ex:passed=False;err=str(ex)
 if passed!=expected:raise AssertionError((label,passed,err))
 records.append(dict(label=label,expected_pass=expected,observed_pass=passed,error=err))
run('direct positive');run('actual CTest merged-output positive',kind='ctest')
for k in ['identity','selector','status','models']:
 e=copy.deepcopy(env);e[k]='wrong';run('wrong '+k,e,expected=False)
for k in bind:
 e=copy.deepcopy(env);e['bindings'][k]='0'*64;run('wrong binding '+k,e,expected=False)
for label,mut in [('missing endpoint',lambda e:e['endpoints'].pop()),('extra endpoint',lambda e:e['endpoints'].append(e['endpoints'][0])),('duplicate endpoint',lambda e:e['endpoints'].__setitem__(1,e['endpoints'][0])),('wrong bits',lambda e:e['endpoints'][0]['state_hex'].__setitem__(0,'0x1p+0')),('truthy domain',lambda e:e['endpoints'][0].__setitem__('domain',1)),('false branch',lambda e:e['endpoints'][0].__setitem__('branch',False)),('AD short row',lambda e:e['ad_hex'][0].pop()),('AD wrong derivative',lambda e:e['ad_hex'][0].__setitem__(0,'0x0p+0')),('AD nan',lambda e:e['ad_hex'][0].__setitem__(0,'nan')),('missing rank13',lambda e:e['cpp_checks'].pop('rank13')),('extra envelope key',lambda e:e.__setitem__('extra',1))]:
 e=copy.deepcopy(env);mut(e);run(label,e,expected=False)
for raw in [b'not json',b'\xff',b'{"a":1,"a":2}',b'{}\n{}',b'{"a":NaN}',b'{"a":1e999}']:run('malformed wire '+repr(raw),raw=raw,expected=False)
for label,mut in [('nonzero exit',lambda p:p.__setitem__('returncode',1)),('boolean exit',lambda p:p.__setitem__('returncode',False)),('wrong argv',lambda p:p.__setitem__('argv',['other'])),('wrong cwd',lambda p:p.__setitem__('cwd','/wrong')),('wrong selector',lambda p:p['selectors'].__setitem__('ATLAS_NUMERICAL_FIXTURES','old')),('optimizer',lambda p:p['selectors'].__setitem__('PYTHONOPTIMIZE','1')),('rawhash drift',lambda p:p['stdout'].__setitem__('sha256','0'*64)),('extra process key',lambda p:p.__setitem__('extra',0)),('stderr log',lambda p:p.__setitem__('stderr',rawfile('stderr',b'bad\n')))]:run(label,modify=mut,expected=False)
run('wrong external build pin',binding_hash='0'*64,expected=False)
for label,mut in [('CTest parent nonzero',lambda p:p['parent'].__setitem__('returncode',1)),('CTest wrong child',lambda p:p.__setitem__('child_name','atlas_other')),('CTest wrong directory',lambda p:p.__setitem__('child_directory','/wrong')),('CTest missing success',lambda p:p.__setitem__('child_status','Test Failed.')),('CTest invented stderr',lambda p:p.__setitem__('stderr',{}))]:run(label,kind='ctest',modify=mut,expected=False)
def corrupt_log(p,kind):
 path=Path(p['last_test_log']['path']);data=path.read_text();expected='Command: "'+str(artifact)+'"'
 if kind=='command':data=data.replace(expected,'Command: "/wrong"\nExtra '+expected)
 elif kind=='directory':data=data.replace('Directory: '+str(M),'Directory: /wrong\nExtra Directory: '+str(M))
 elif kind=='duplicate-header':data=data.replace(expected,expected+'\n'+expected)
 elif kind=='duplicate-test':data=data+data
 elif kind=='status':data=data.replace('Test Passed.','Test Failed.')
 path.write_text(data);p['last_test_log']['sha256']=sha(path)
for kind in ['command','directory','duplicate-header','duplicate-test','status']:
 run('CTest forged '+kind,kind='ctest',modify=lambda p,k=kind:corrupt_log(p,k),expected=False)
# Leave stable positive synthetic fixtures; no actual process is represented.
run('final stable direct positive');write(M/'envelope.json',env);write(M/'ctest-process.json',process(env,'ctest'))
(D/'assessor-test-results.json').write_text(json.dumps(dict(passed=True,cases=len(records),records=records,synthetic_only=True,compiled_calls=0),indent=2)+'\n');print(len(records),'strict saved-assessor mocks passed')
