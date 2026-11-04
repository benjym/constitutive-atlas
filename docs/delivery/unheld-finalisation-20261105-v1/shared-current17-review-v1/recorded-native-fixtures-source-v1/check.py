from pathlib import Path
import hashlib,json,importlib.util,sys,tempfile,copy,os
from unittest.mock import patch
O=Path(__file__).resolve().parent;A=O.parents[1]/'recorded-native-fixtures-fix-v1';R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sys.path.insert(0,str(R));checks=[]
def sha(q):return hashlib.sha256(q.read_bytes()).hexdigest()
def ok(v,n):assert v,n;checks.append(n)
def reject(fn,n):
 try:fn()
 except (RuntimeError,ValueError,FileNotFoundError):checks.append(n);return
 raise AssertionError('accepted '+n)
ok(sha(A/'manifest.json')=='85fa7c432c4f6b994fe1cdbad797aff79b449dbe31ce650bf3889a0496458e96','exact dispatched manifest')
for name,row in json.loads((A/'manifest.json').read_text())['files'].items():
 q=A/name;ok(q.is_file()and not q.is_symlink()and sha(q)==row['sha256']and q.stat().st_size==row['bytes'],'frozen '+name)
spec=importlib.util.spec_from_file_location('review_recorded_helper',A/'proposed/tests/recorded_native_fixtures.py');h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
for row in h.LEGACY_INPUTS:
 q=R/row['path'];receipt=R/row['receipt']['path'];ok(sha(q)==row['sha256']and sha(receipt)==row['receipt']['sha256']and json.loads(receipt.read_text())[row['receipt_key']]==row['sha256'],'genuine archival authority '+q.name)
 original=R
with tempfile.TemporaryDirectory(dir=O,prefix='archives-')as td:
 t=Path(td).resolve()
 for row in h.LEGACY_INPUTS:
  q=t/row['path'];q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((R/row['path']).read_bytes())
 h.ROOT=t;paths=h.legacy_paths();ok(len(paths)==5,'exact tiny archive closure accepted')
 for row in h.LEGACY_INPUTS:
  q=t/row['path'];b=q.read_bytes();q.write_bytes(b+b' ');reject(h.legacy_paths,'corrupt archive '+q.name);q.unlink();reject(h.legacy_paths,'missing archive '+q.name);q.write_bytes(b)
 outside=t/'outside-model';outside.write_bytes(paths[0].read_bytes());q=paths[0];b=q.read_bytes();q.unlink();q.symlink_to(O/'absent-outside');reject(h.legacy_paths,'escaped archive alias rejects');q.unlink();q.write_bytes(b)
 h.ROOT=R
 for initial in [None,[],[1],['bad']]:
  s={'model':'linear-elastic','initial':initial};ok(h.explicit_recorded_fixture(s)==s,'malformed explicit initial preserved '+repr(initial))
 s={'model':'drucker-prager'};adapt=h.explicit_recorded_fixture(s);adapt['initial'][0]=1;ok('initial'not in s and h.EXPLICIT_INITIALS['drucker-prager'][0]==100000,'fixture copy isolates caller and source constant')
 binary=t/'inert';binary.write_text('INERT NEVER EXECUTE');models=[json.loads(q.read_text())for q in h.legacy_paths()]
 env={'ATLAS_RECORDED_LEGACY_SOLVER':str(binary),'ATLAS_RECORDED_LEGACY_SHA256':sha(binary)}
 namespace={'all_models':lambda:['current']};test=type('T',(),{'records':[],'run_spec':lambda self,s:None})()
 def mutate_describe(*args,**kwargs):binary.write_text('CHANGED');return json.dumps({'sha256':h.LEGACY_HASH,'models':models})
 with patch.dict(os.environ,env),patch.object(h.subprocess,'check_output',side_effect=mutate_describe),patch.object(h,'execute_recorded')as transport:
  def invoke():
   with h.historical_recorded_context(test,namespace):pass
  reject(invoke,'describe mutating executable rejects before request');ok(not transport.called,'describe drift prevents recorded call')
 binary.write_text('INERT NEVER EXECUTE')
 def mutate_request(s,solver):binary.write_text('CHANGED');return {'ok':True}
 with patch.dict(os.environ,env),patch.object(h.subprocess,'check_output',return_value=json.dumps({'sha256':h.LEGACY_HASH,'models':models})),patch.object(h,'execute_recorded',side_effect=mutate_request):
  def invoke():
   with h.historical_recorded_context(test,namespace):test.run_spec({'model':'linear-elastic'})
  reject(invoke,'request mutating executable rejects');ok(namespace['all_models']()==['current'],'namespace restored on request failure')
 binary.write_text('INERT NEVER EXECUTE')
 with patch.dict(os.environ,env),patch.object(h.subprocess,'check_output',return_value=json.dumps({'sha256':h.LEGACY_HASH,'models':models})):
  def invoke():
   with h.historical_recorded_context(test,namespace):raise ValueError('primary test failure')
  reject(invoke,'body exception preserved');ok(namespace['all_models']()==['current'],'namespace restored on body failure')
report=json.loads((O/'check.stdout.json').read_text());ok(report['checks']==60 and report['pure_unittests']==12,'author60 plus12originalpuretests replayed')
cmake=(A/'legacy-target.cmake').read_text();handoff=(A/'ci-handoff.md').read_text()
for s in ['if(NOT EMSCRIPTEN)','EXCLUDE_FROM_ALL','atlas_recorded_legacy_solver','atlas_scalar_functions','recorded-legacy-generated']:
 ok(s in cmake,'native isolated target '+s)
ok('--parallel 1'in handoff and 'ATLAS_RECORDED_SOLVER'in handoff and 'ATLAS_RECORDED_LEGACY_SHA256'in handoff,'both engine identities and serial build required')
(O/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'actual_compiled_material_browser_network':False,'temporary_resources_removed':True},indent=2)+'\n');print(json.dumps({'passed':True,'count':len(checks)}))
