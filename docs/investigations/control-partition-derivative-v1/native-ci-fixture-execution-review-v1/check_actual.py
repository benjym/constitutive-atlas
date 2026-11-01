"""Audit retained source/build/process archive only; never execute artifacts."""
import sys
sys.dont_write_bytecode=True
import base64,datetime,hashlib,importlib.util,json,re,tarfile
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'native-ci-fixture-execution-v1';S=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source');read=lambda p:json.loads(p.read_text());sha=lambda b:hashlib.sha256(b).hexdigest();checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('actualpacket manifest exact',sha((D/'manifest.json').read_bytes())=='42ab7b60dd6ca4c976eb202f82bde8951743fc729bc2f8c71e294509bb88f471')
for n,v in read(D/'manifest.json')['files'].items():ck('public '+n,sha((D/n).read_bytes())==v)
a=read(D/'archive-receipt.json');archive=D/a['archive'];ck('archive size/hash',archive.stat().st_size==a['bytes'] and sha(archive.read_bytes())==a['sha256'])
blobs={}
with tarfile.open(archive,'r:gz') as tar:
 members=tar.getmembers();ck('exact999regularuniquemembers',len(members)==len(a['members'])==999 and len({m.name for m in members})==999 and all(m.isfile() and not Path(m.name).is_absolute() and '..'not in Path(m.name).parts for m in members));ck('full member inventory',{m.name for m in members}==set(a['members']))
 for m in members:
  b=tar.extractfile(m).read();ck('archive member '+m.name,sha(b)==a['members'][m.name]);blobs[m.name]=b
J=lambda name:json.loads(blobs[name]);f=read(C/'native-ci-fixture-composition-v3/source-freeze.json')['files'];ck('full594source retained',len(f)==594 and {k.removeprefix('source/')for k in blobs if k.startswith('source/')}==set(f))
for n,v in f.items():ck('frozen source '+n,sha(blobs['source/'+n])==v and sha((S/n).read_bytes())==v)
freeze=read(D/'freeze.json')
for n,v in freeze['inputs'].items():ck('preinput still exact '+n,sha(Path(n).read_bytes())==v)
plan=read(C/'native-ci-fixture-composition-v3/execution-plan.json');outcomes=read(D/'outcomes.json')['outcomes'];end=None;processrows=[]
for i,stage in enumerate(plan['steps']):
 name=stage['id'];prefix='evidence/processes/'+name+'/';raw=blobs[prefix+'process.json'];r=json.loads(raw);ck('stage identity '+name,r['stage']==stage and r['index']==i and r['freeze_sha256']==sha((D/'freeze.json').read_bytes()))
 ck('stage raw hashes '+name,sha(blobs[prefix+'stdout'])==r['stdout_sha256'] and sha(blobs[prefix+'stderr'])==r['stderr_sha256'])
 ck('stage pre/post checks '+name,r['pre']==r['post']=={'source_files':594,'tool_files':6821})
 start=datetime.datetime.fromisoformat(r['start']);last=datetime.datetime.fromisoformat(r['end']);ck('serial timestamps '+name,start<=last and (end is None or start>=end));end=last
 expected_rc=1 if name=='ctest-linux-main'else 0;ck('actual expected outcome '+name,r['returncode']==expected_rc and r['status']==('failed'if expected_rc else 'passed'))
 ck('outcome bytebinding '+name,outcomes[name]=={'status':r['status'],'returncode':r['returncode'],'process_sha256':sha(raw)})
 processrows.append({'stage':name,'status':r['status'],'returncode':r['returncode'],'start':r['start'],'end':r['end']})
ck('exact13process inventory',{n.split('/')[2]for n in blobs if n.startswith('evidence/processes/')}=={x['id']for x in plan['steps']})
# Read-only original helper predicates, no subprocess/compiled calls.
spec=importlib.util.spec_from_file_location('md_saved_contract',S/'tools/check_md1997_native_fixture_contract.py');md=importlib.util.module_from_spec(spec);spec.loader.exec_module(md)
strict=J('evidence/check-strict-eight.json');ck('strict8reportpassed',strict['status']=='passed'and len(strict['processes'])==8 and strict['context']['route']=='16')
for i,row in enumerate(strict['processes']):
 for key in ['stdout','stderr']:b=base64.b64decode(row[key+'_base64'],validate=True);ck('strict raw '+str(i)+key,sha(b)==row[key+'_sha256']and b.decode()==row[key])
 ck('strict actual failure outcome '+str(i),row['status']=='completed'and type(row['returncode'])is int and row['returncode']==1)
 if i>=4:md.verify(row,md.contracts()[i-4]);checks.append('strict originalMDpredicate '+str(i))
# Original strict four exact strings plus unchanged source analytical OCC proof.
for i in [0,2]:ck('strict default full16 '+str(i),strict['processes'][i]['stdout']=='Strict original default fixtures; models=16\n')
ck('strict numerical default failure',strict['processes'][0]['stderr']=='FD test outside domain\n')
for i in [1,3]:ck('strict unknown native '+str(i),strict['processes'][i]['stdout']==''and strict['processes'][i]['stderr']=='unknown native fixture profile\n')
spec=importlib.util.spec_from_file_location('original_saved_contract',S/'tools/check_native_fixture_contracts.py');helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper);mapping=dict(strict['context']['model_definitions']);del mapping['manzari-dafalias-1997-constant-m-be-v1'];helper.check_recorded_failure(strict['processes'][2]['stderr'],mapping,root=S);checks.append('unchanged OCC analytical failure proof passes exact15projection')
for i,row in enumerate(strict['processes']):
 native=None if i in [0,2,6] else 'unknown'if i in [1,3] else md.NATIVE if i in [4,5] else 'explicit-gis20-occ-restart-v4'
 numerical=None if i<5 else 'unknown'if i==5 else md.NUMERICAL
 selectors={k:v for k,v in zip(md.SELECTORS,[native,numerical])if v is not None}
 target='atlas_recorded_tests'if i in [2,3]else 'atlas_numerical_tests'
 ck('strict exactargv/selectors '+str(i),row['argv']==[str(Path(plan['build'])/target)]and row['requested_selectors']==selectors and row['effective_selectors']==selectors)
logs={};suite_outcomes={}
for name,expected_status,expected_rc in [('ctest-linux-main','failed',8),('ctest-recorded','passed',0)]:
 r=J('evidence/'+name+'.json');ck('helper outcome '+name,r['status']==expected_status and len(r['processes'])==1);q=r['processes'][0];ck('CTest return '+name,q['status']=='completed'and q['returncode']==expected_rc)
 for k in ['stdout','stderr']:b=base64.b64decode(q[k+'_base64'],validate=True);ck('CTest raw '+name+k,sha(b)==q[k+'_sha256']and b.decode()==q[k])
 b=base64.b64decode(r['ctest_log']['base64'],validate=True);ck('embedded loghash '+name,sha(b)==r['ctest_log']['sha256']);logs[name]=b.decode();parts=re.split(r'(?m)(?=^\d+/\d+ Testing: )',b.decode())[1:];rows=[]
 for part in parts:
  m=re.match(r'^\d+/\d+ Testing: ([^\n]+)',part);rows.append({'test':m.group(1),'passed':'Test Passed.'in part,'failed':'Test Failed.'in part})
 suite_outcomes[name]=rows
 ck('CTest tool stable '+name,r['ctest_postflight']['same_path']is True and r['ctest_postflight']['sha256']==r['ctest_executable_sha256'] and r['ctest_postflight']['resolved_path']==r['ctest_executable_resolved_path'])
 for path,v in r['context']['registered_artifacts'].items():
  p=Path(path)
  if str(p).startswith(plan['build']+'/'):ck('registered artifact retained '+name+str(p),sha(blobs['native-build/'+p.relative_to(plan['build']).as_posix()])==v)
linux=suite_outcomes['ctest-linux-main'];expected=['atlas_numerical','atlas_tensor_square','atlas_time','atlas_capacity','atlas_recorded_fixture','atlas_expm_context','atlas_log1p_context','atlas_scalar_functions'];ck('exactlinux8coverage', [x['test']for x in linux]==expected and linux[0]['failed']and not linux[0]['passed']and all(x['passed']and not x['failed']for x in linux[1:]));ck('exactMDfailure message','MD AD/FD residual Jacobian mismatch\n'in logs['ctest-linux-main']);ck('recorded separateonlyPASS',suite_outcomes['ctest-recorded']==[{'test':'atlas_recorded','passed':True,'failed':False}])
rec=J('evidence/ctest-recorded.json');ck('priorfailedlinuxlogpreserved',base64.b64decode(rec['previous_ctest_log']['base64']).decode()==logs['ctest-linux-main'])
config=read(D/'actual-configure-inputs.json');ck('actualcache retained',sha(blobs['native-build/CMakeCache.txt'])==config['cache_sha256'])
for n,v in config['compiler_metadata'].items():ck('actual compiler metadata '+n,sha(blobs['native-build/'+n])==v)
for n,v in config['compiler_tool_sdk_settings'].items():p=Path(v['path']);ck('actual toolsdk post '+n,str(p.resolve())==v['realpath']and sha(p.read_bytes())==v['sha256'])
tool=read(D/'toolchain.json')
for path,v in tool['files'].items():p=Path(path);ck('toolchain post '+path,str(p.resolve())==v['realpath']and sha(p.read_bytes())==v['sha256'])
print(json.dumps({'identity':'independent-md1997-native-ci-actual-v1-review','checks':len(checks),'check_names':checks,'archive_members':999,'source_files':594,'process_stages':processrows,'all9builds_pass':True,'strict8negative_contracts_pass':True,'linux_suite':linux,'recorded_separate':suite_outcomes['ctest-recorded'],'decision':'retained actual failure accepted; positive native numerical qualification FAIL','gate_waivers':0,'review_compiled_calls':0,'review_builds':0,'diagnostic_scope_separate':True},indent=2))
