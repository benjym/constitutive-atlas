"""Synthetic saved transports only, never a native process or real build receipt."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import importlib.util,json,hashlib,tempfile,copy
D=Path(__file__).resolve().parent;A=D.parent/'native-decimal-reference-v1';sys.path.insert(0,str(A));spec=importlib.util.spec_from_file_location('reviewed_assessor',A/'assess_saved.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,b):
 if not b:raise RuntimeError(n)
 checks.append(n)
def reject(n,fn):
 try:r=fn()
 except(Exception):checks.append(n);return
 ck(n,r['passed']is False)
with tempfile.TemporaryDirectory(dir='/private/tmp',prefix='decimal-assessor-review-')as td:
 T=Path(td);exe=T/'never-executed';exe.write_text('SYNTHETIC NONEXECUTABLE RECEIPT ONLY');q=read(A/'requests.json');r=read(A/'reference.json');binding={'identity':'md1997-decimal-native-build-binding-v1','purpose':'synthetic-test-only','source_freeze_sha256':'a'*64,'fixture_sha256':'b'*64,'generated_catalogue_sha256':'c'*64,'executable_sha256':sha(exe),'executable_path':str(exe),'working_directory':str(T),'model_sha256':q['model_sha256']};bp=T/'binding.json';bp.write_text(json.dumps(binding));bh=sha(bp)
 base={k:q[k]for k in ['layout','state_hex','previous_hex','loading_hex','parameters_hex','scales_hex']};bindings={k:r[k]for k in ['evaluator_sha256','policy_sha256','base_source_freeze_sha256','model_sha256']};bindings.update(request_sha256=sha(A/'requests.json'),reference_sha256=sha(A/'reference.json'),build_binding_sha256=bh)
 env=dict(identity='md1997-decimal-ad-export-v1',selector='md1997-decimal-fd-reference-v1',status='exported-unassessed',models=16,bindings=bindings,base=base,endpoints=[{**x,'domain':True,'branch':True}for x in q['endpoints']],ad_hex=[[float(r['data']['120']['secants'][2*col][row]).hex()for col in range(14)]for row in range(14)],cpp_checks={'rank13':True,'rotation':True,'other_models':True})
 stdout=T/'stdout';stderr=T/'stderr';stderr.write_bytes(b'');pp=T/'process.json'
 def run(obj=None,mutprocess=None,raw=None):
  stdout.write_bytes(json.dumps(env if obj is None else obj).encode()if raw is None else raw);p={'identity':'md1997-decimal-direct-process-v1','purpose':'synthetic-test-only','argv':[str(exe)],'cwd':str(T),'returncode':0,'stdout':{'path':str(stdout),'sha256':sha(stdout)},'stderr':{'path':str(stderr),'sha256':sha(stderr)},'selectors':{'ATLAS_NATIVE_FIXTURES':'explicit-gis20-occ-restart-duncan-v5','ATLAS_NUMERICAL_FIXTURES':'md1997-decimal-fd-reference-v1','PYTHONOPTIMIZE':'0'},'executable_sha256':sha(exe)}
  if mutprocess:mutprocess(p)
  pp.write_text(json.dumps(p));return m.assess(A/'requests.json',A/'reference.json',pp,bp,bh)
 positive=run();ck('full synthetic588 accepted',positive['passed']is True and positive['comparisons']==588 and positive['purpose']=='synthetic-test-only')
 for name,change in [
 ('missing endpoint',lambda x:x['endpoints'].pop()),('extra endpoint',lambda x:x['endpoints'].append(x['endpoints'][0])),('duplicate endpoint',lambda x:x['endpoints'].__setitem__(1,x['endpoints'][0])),('false branch',lambda x:x['endpoints'][0].__setitem__('branch',False)),('integer domain',lambda x:x['endpoints'][0].__setitem__('domain',1)),('changed endpoint',lambda x:x['endpoints'][0]['state_hex'].__setitem__(0,float(12).hex())),('changed previous',lambda x:x['base']['previous_hex'].__setitem__(0,float(12).hex())),('partial AD',lambda x:x['ad_hex'].pop()),('infinite AD',lambda x:x['ad_hex'][0].__setitem__(0,'inf')),('wrong AD',lambda x:x['ad_hex'][0].__setitem__(0,float(1e30).hex())),('false cpp flag',lambda x:x['cpp_checks'].__setitem__('other_models',False)),('integer cpp flag',lambda x:x['cpp_checks'].__setitem__('rank13',1)),('wrong reference binding',lambda x:x['bindings'].__setitem__('reference_sha256','0'*64)),('unknown field',lambda x:x.__setitem__('unexpected',True)),('wrong model count',lambda x:x.__setitem__('models',15))]:
  x=copy.deepcopy(env);change(x);reject(name,lambda x=x:run(x))
 for name,change in [('bad returncode',lambda p:p.__setitem__('returncode',1)),('bool returncode',lambda p:p.__setitem__('returncode',False)),('wrong argv',lambda p:p.__setitem__('argv',['/wrong'])),('wrong selector',lambda p:p['selectors'].__setitem__('ATLAS_NUMERICAL_FIXTURES','wrong')),('wrong raw digest',lambda p:p['stdout'].__setitem__('sha256','0'*64)),('unknown process field',lambda p:p.__setitem__('extra',1))]:reject(name,lambda change=change:run(mutprocess=change))
 reject('duplicate JSON key',lambda:run(raw=json.dumps(env).replace('"models": 16','"models": 16,"models": 16').encode()));reject('nonUTF8 raw',lambda:run(raw=b'\xff'));reject('trailing raw garbage',lambda:run(raw=json.dumps(env).encode()+b'garbage'))
print(json.dumps({'identity':'independent-synthetic-decimal-assessor-probes','checks':len(checks),'check_names':checks,'positive_comparisons':588,'all_inputs_explicitly_synthetic':True,'builds':0,'compiled_calls':0},indent=2))
