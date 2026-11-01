"""Independent mocks: no real CTest, compiled calls or builds."""
import sys
sys.dont_write_bytecode=True
import json,hashlib,subprocess,unittest,io,base64
from pathlib import Path
from unittest.mock import patch
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);O=p.parse_args().output;O.mkdir(exist_ok=False,parents=True)
S=Path('/private/tmp/atlas-md1997-ci-dispatch-v2/source');sys.path.insert(0,str(S))
from tools import check_native_fixture_dispatch as d
from tools import check_md1997_native_fixture_contract as md
from tests import test_native_fixture_dispatch as tests,test_ci_profiles,test_native_fixture_contracts
stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromModule(x) for x in [tests,test_ci_profiles,test_native_fixture_contracts]));(O/'author-mocks.txt').write_text(stream.getvalue());assert result.wasSuccessful() and result.testsRun==23
checks=[]
def check(n,v):assert v,n;checks.append({'id':n,'passed':True})
t=tests.DispatchTests();t.setUp()
try:
 s,b=t.fixture('16');registry=b/'CTestTestfile.cmake';original=registry.read_bytes()
 registry.write_text('add_test("atlas_numerical" "stand-in")\nadd_test("atlas_recorded" "stand-in")\n')
 for suite in d.SUITES:
  calls=[]
  def never(*a,**k):calls.append(a);raise AssertionError('must not call')
  try:d.execute('ctest',b/'generated/models.json',s,b,O/('B1-'+suite+'.json'),suite,never,{})
  except ValueError:pass
  else:raise AssertionError('B1 still accepted')
  check('B1 rejects prior omitted inventory '+suite,not calls)
 registry.write_bytes(original)
 runner=t.ctest_run(s,b,'16','linux-main')
 def drift(*a,**k):
  r=runner(*a,**k);(b/'mock-ctest').write_text('changed mock');return r
 with patch.object(d.shutil,'which',return_value=str(b/'mock-ctest')):
  try:d.execute('ctest',b/'generated/models.json',s,b,O/'B2.json','linux-main',drift,{})
  except ValueError:pass
  else:raise AssertionError('B2 still accepted')
 check('B2 rejects prior executable byte drift',json.loads((O/'B2.json').read_text())['status']=='failed')
 for mode in ['prefix','suffix','unterminated','duplicate','metadata']:
  def badlabel(*a,**k):
   r=runner(*a,**k);f=b/'Testing/Temporary/LastTest.log';text=f.read_text()
   if mode=='prefix':text=text.replace(md.POSITIVE_STDOUT,'WRONG-PREFIX '+md.POSITIVE_STDOUT)
   elif mode=='suffix':text=text.replace(md.POSITIVE_STDOUT,md.POSITIVE_STDOUT.rstrip()+' WRONG-SUFFIX\n')
   elif mode=='unterminated':text=text.replace(md.POSITIVE_STDOUT,md.POSITIVE_STDOUT.rstrip('\n'))
   elif mode=='duplicate':text=text.replace(md.POSITIVE_STDOUT,md.POSITIVE_STDOUT*2)
   else:text=text.replace(md.POSITIVE_STDOUT,'').replace('Output:\n',md.POSITIVE_STDOUT+'Output:\n',1)
   f.write_text(text);return r
  with patch.object(d.shutil,'which',return_value=str(b/'mock-ctest')):
   try:d.execute('ctest',b/'generated/models.json',s,b,O/('B3-'+mode+'.json'),'linux-main',badlabel,{})
   except ValueError:pass
   else:raise AssertionError('B3 accepted '+mode)
  check('B3 rejects '+mode,True)
 def timeout(argv,**kwargs):raise subprocess.TimeoutExpired(argv,120,output=b'\xff',stderr=b'partial-timeout')
 try:d.execute('check',b/'generated/models.json',s,b,O/'C1.json',None,timeout,{})
 except subprocess.TimeoutExpired:pass
 else:raise AssertionError('timeout accepted or changed error')
 r=json.loads((O/'C1.json').read_text());row=r['processes'][0]
 check('C1 retains terminal timeout and nonUTF8 bytes',r['error_type']==row['error_type']=='TimeoutExpired' and row['status']=='failed' and row['decode_error']['type']=='UnicodeDecodeError' and base64.b64decode(row['stdout_base64'])==b'\xff')
 # New source-derived semantic-context witness: generated properties are not
 # validated even though they can change execution outside the fixed argv.
 registry.write_bytes(original+b'\nset_tests_properties("atlas_time" PROPERTIES ENVIRONMENT "LD_PRELOAD=/unreviewed/inject.so")\n')
 with patch.object(d.shutil,'which',return_value=str(b/'mock-ctest')):
  r=d.execute('ctest',b/'generated/models.json',s,b,O/'R2-unreviewed-properties.json','linux-main',runner,{})
 check('R2 unreviewed generated execution environment accepted',r['status']=='passed')
 # Actual immutable composition source, with only synthetic generated/build artifacts.
 registry.write_bytes(original.replace(str(s).encode(),b'/private/tmp/atlas-md1997-native-ci-fixture-v1/source'))
 cache=b/'CMakeCache.txt';cache.write_text(cache.read_text().replace(str(s),'/private/tmp/atlas-md1997-native-ci-fixture-v1/source'))
 meta,_=d.context(b/'generated/models.json',Path('/private/tmp/atlas-md1997-native-ci-fixture-v1/source'),b)
 check('actual composition context classifies exact16 with synthetic build only',meta['route']=='16' and len(meta['registrations'])==10)
finally:t.doCleanups()
(O/'summary.json').write_text(json.dumps({'author_mock_methods':23,'independent_checks':checks,'original_findings_closed':['B1','B2','B3','C1'],'new_blocking_findings':['R2'],'compiled_calls':0,'real_CTest_calls':0},indent=2)+'\n')
print(json.dumps({'author_tests':23,'independent_checks':len(checks),'R2':'unreviewed CTest ENVIRONMENT accepted','compiled_calls':0}))
