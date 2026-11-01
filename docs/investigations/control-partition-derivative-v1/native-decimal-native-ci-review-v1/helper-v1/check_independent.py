"""Independent prospective transport probes. All material/process callbacks mocked."""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('unoptimized review required')
import argparse,base64,hashlib,importlib.util,json,subprocess
from pathlib import Path
from unittest.mock import patch

def audit(event,args):
 if event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:raise RuntimeError('review forbids process execution')
sys.addaudithook(audit)

def main():
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--author-manifest',type=Path,required=True);p.add_argument('--author-sha256',required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
 h=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
 if h(a.author_manifest)!=a.author_sha256:raise RuntimeError('author pin mismatch')
 sys.path.insert(0,str(a.source));s=importlib.util.spec_from_file_location('author_mock_fixtures',a.source/'tests/test_native_fixture_dispatch.py');m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
 results=[]
 def exercise(name,mutation=None,operation='decimal',suite=None,success=False):
  t=m.DispatchTests();t.setUp()
  try:
   source,build=t.fixture();runner=t.direct_run(source,build)if operation=='decimal'else t.ctest_run(source,build,'16',suite)
   original=runner
   def run(argv,**kw):
    row=original(argv,**kw)
    if mutation:mutation(t,source,build,argv,row)
    return row
   error=None;report=None
   with patch.object(m.dispatch.shutil,'which',return_value=str(build/'mock-ctest')):
    try:report=t.execute(source,build,run,'independent.json',operation,suite)
    except Exception as e:error=type(e).__name__+': '+str(e)
   saved=json.loads((t.base/'independent.json').read_text())
   if success:
    if error or saved['status']!='passed' or len(saved['decimal_assessments'])!=1:raise RuntimeError(name+' positive rejected '+str(error))
    assessment=saved['decimal_assessments'][0]
    if assessment['comparisons']!=588 or assessment['purpose']!='synthetic-test-only':raise RuntimeError('positive identity')
   elif not error or saved['status']!='failed':raise RuntimeError(name+' corruption accepted')
   results.append(dict(name=name,passed=True,expected='synthetic acceptance'if success else 'rejection',observed_status=saved['status'],error=error,process_count=len(saved['processes'])))
  finally:t.doCleanups()
 for op,suite in [('decimal',None),('ctest','linux-main'),('ctest','macos-main')]:exercise(op+'-'+str(suite),operation=op,suite=suite,success=True)
 def on_export(fn):return lambda t,s,b,argv,row:fn(t,s,b,row)if Path(argv[0]).name=='atlas_numerical_tests'else None
 for value in [False,True,0.0,-9,1]:exercise('export-return-'+repr(value),on_export(lambda t,s,b,r,v=value:setattr(r,'returncode',v)))
 exercise('export-late-stderr',on_export(lambda t,s,b,r:setattr(r,'stderr',b'late failure')))
 exercise('export-oversize',on_export(lambda t,s,b,r:setattr(r,'stdout',b'{'+b' '*m.decimal.MAX_OUTPUT+b'}\n')))
 exercise('export-duplicate-json',on_export(lambda t,s,b,r:setattr(r,'stdout',r.stdout[:-2]+b',"models":16}\n')))
 exercise('export-nonutf8',on_export(lambda t,s,b,r:setattr(r,'stdout',b'\xff')))
 for target in ['models/linear-elastic.json','tools/collect_md1997_decimal.py','tests/test_solver.cpp']:
  def mutate(t,s,b,argv,row,target=target):
   if Path(argv[2]).name=='assess_saved.py'if len(argv)>2 else False:(s/target).write_bytes((s/target).read_bytes()+b' ')
  exercise('post-assessor-source-'+target,mutate)
 for target in ['atlas_numerical_tests','generated/models.hpp','mock-ctest']:
  def mutate(t,s,b,argv,row,target=target):
   if Path(argv[2]).name=='assess_saved.py'if len(argv)>2 else False:(b/target).write_bytes((b/target).read_bytes()+b' ')
  exercise('post-assessor-artifact-'+target,mutate)
 for value in [False,True,0.0,1]:
  def mutate(t,s,b,argv,row,value=value):
   if Path(argv[2]).name=='assess_saved.py'if len(argv)>2 else False:row.returncode=value
  exercise('assessor-return-'+repr(value),mutate)
 def remove_report(t,s,b,argv,row):
  if Path(argv[2]).name=='assess_saved.py'if len(argv)>2 else False:Path(argv[-1]).unlink()
 exercise('assessor-report-removed',remove_report)
 for op,suite in [('ctest','linux-main'),('ctest','macos-main')]:
  def fake(t,s,b,argv,row):
   if '--test-dir'in argv:
    log=b/'Testing/Temporary/LastTest.log';text=log.read_text();text=text.replace('"rank13": true','"rank13": false');log.write_text(text)
  exercise(op+'-'+suite+'-bad-actual-child',fake,op,suite)
 out=dict(identity='independent-decimal-transport-mocks-v1',purpose='synthetic-source-only-not-material-observations',author_manifest_sha256=a.author_sha256,source=str(a.source),checks=results,passed=all(x['passed']for x in results))
 a.output.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'passed':out['passed'],'checks':len(results)}))
if __name__=='__main__':main()
