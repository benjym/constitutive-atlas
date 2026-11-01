import runpy,json,tempfile,copy,sys,io,contextlib,hashlib,importlib.util,importlib.abc,importlib.machinery
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
D=Path(__file__).resolve().parent;P=D.parents[1];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert sha(P/'ordinary-regression-v3/manifest.json')=='8f3c2e4663ecd73f7c1350445ad796d36eb77a60cd2a4ee5f7fd9c89021960bf'
for file,h in json.loads((P/'ordinary-regression-v3/manifest.json').read_text()).items():assert sha(P/'ordinary-regression-v3'/file)==h
policy=json.loads((P/'ordinary-regression-policy-v2.json').read_text());cases={c['model']:c for c in policy['cases']};results=[]
originalspec=importlib.util.spec_from_file_location
class Loader(importlib.abc.Loader):
 def __init__(self,backend):self.backend=backend
 def create_module(self,spec):return None
 def exec_module(self,module):module.Backend=self.backend
def test(version,name,mutation,expected):
 class FakeBackend:
  def __init__(self,args,out):pass
  def close(self):pass
  def call(self,request,log):
   c=cases[request['model']]
   assert request=={'mode':'run','model':c['model'],'parameters':c['parameters'],'initial':c['initial'],'settings':c['integration_settings'],'protocol':c['protocol'],'target':c['target'],'steps':c['steps'],'cycles':c['cycles']}
   if c['expected_ok']:response={'ok':True,'points':[{'control':c['target']*i/c['steps'],'state':c['initial'].copy(),'strain':[0.]*6} for i in range(c['steps']+1)]}
   else:response={'ok':False,'message':c['declared_failure']['message'],'points':[{'control':0.,'state':c['initial'].copy(),'strain':[0.]*6}]}
   mutation(c,response);log.write(json.dumps({'SYNTHETIC_ONLY':True,'request':request,'response':response})+'\n');return response
 def spec(name,path,*a,**kw):
  return importlib.machinery.ModuleSpec(name,Loader(FakeBackend)) if name=='generic_request_transport' else originalspec(name,path,*a,**kw)
 ns=runpy.run_path(str(P/version/'run.py'))
 with tempfile.TemporaryDirectory(dir=D) as td:
  td=Path(td);artifact=td/'SYNTHETIC-not-an-executable';artifact.write_text('not an executable, mocked transport only')
  argv=['run.py','--solver',str(artifact),'--output',str(td/'out')]
  with patch.object(sys,'argv',argv),patch.object(importlib.util,'spec_from_file_location',spec),contextlib.redirect_stdout(io.StringIO()):
   try:ns['main']();code=0
   except SystemExit as ex:code=ex.code
  r=json.loads((td/'out/report.json').read_text());passed=r['passed']
  results.append({'version':version,'test':name,'expected':expected,'runner_accepted':passed,'expectation_met':passed==expected,'exit_code':code,'failed_models':[c['model'] for c in r['cases'] if not c['passed']]})
first=policy['cases'][0]['model']
def onlyfirst(m):return lambda c,r:m(r) if c['model']==first else None
def onlyfail(m):return lambda c,r:m(r) if not c['expected_ok'] else None
for ver in ['ordinary-regression-v2','ordinary-regression-v3']:
 test(ver,'synthetic ideal baseline',lambda c,r:None,True)
 test(ver,'malformed retained GISpoint',onlyfail(lambda r:r.__setitem__('points',[{}])),False)
for name,mutation in [('missing success point',onlyfirst(lambda r:r['points'].pop())),('wrong success state length',onlyfirst(lambda r:r['points'][0].__setitem__('state',[]))),('wrong success control',onlyfirst(lambda r:r['points'][1].__setitem__('control',-1))),('transport error',onlyfirst(lambda r:r.__setitem__('harness_error','synthetic'))),('missing GISpoint',onlyfail(lambda r:r.__setitem__('points',[]))),('wrong GISmessage',onlyfail(lambda r:r.__setitem__('message','different'))),('corrupted GISparent',onlyfail(lambda r:r['points'][0]['state'].__setitem__(0,99))),('corrupted GISstrain',onlyfail(lambda r:r['points'][0]['strain'].__setitem__(0,.1)))]:test('ordinary-regression-v3',name,mutation,False)
# Isolated Python transport call with subprocess mocked, never executes a file.
mod=runpy.run_path(str(P/'execution-v1/run_native.py'));backend=mod['Backend'](SimpleNamespace(wasm_engine=None,solver='SYNTHETIC-UNEXECUTED'),D)
req={'mode':'integrate','model':'synthetic','parameters':[1.],'initial':[1.],'settings':[1.],'strain':[0.]*6};log=io.StringIO();error=None
with patch('subprocess.run',return_value=SimpleNamespace(stdout='{"ok":false,"state":[NaN]}',stderr='',returncode=1)):
 try:backend.call(req,log)
 except Exception as ex:error=repr(ex)
raw={'test':'nonfinite JSON backend response','no_actual_subprocess':True,'error':error,'raw_response_retained':bool(log.getvalue()),'log':log.getvalue()}
assert error is not None and not raw['raw_response_retained']
(D/'mock-checks.json').write_text(json.dumps({'scope':'mocked transport only, no backend calls','tests':results,'raw_transport_preservation_failure':raw},indent=2)+'\n')
print(json.dumps({'tests':len(results),'v3_expectations_met':all(r['expectation_met'] for r in results if r['version']=='ordinary-regression-v3'),'retained_v2_false_accept':any(not r['expectation_met'] for r in results if r['version']=='ordinary-regression-v2'),'raw_retention_failure_confirmed':not raw['raw_response_retained']},indent=2))
