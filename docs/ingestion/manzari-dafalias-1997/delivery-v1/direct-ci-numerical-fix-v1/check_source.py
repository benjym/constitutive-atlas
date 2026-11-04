"""Unit mocks only: no compiler/native/CTest/assessor subprocess is executed."""
from pathlib import Path
import copy,hashlib,importlib.util,json,math,shutil,tempfile
P=Path(__file__).absolute().parent;SOURCE=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source');count=0;negative=0

def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
m=load('_direct_ci_unit',SOURCE/'tools/check_md1997_numerical_ci.py');strict=load('_strict_ci_unit',SOURCE/'tools/check_native_fixture_contracts.py');H=lambda b:hashlib.sha256(b).hexdigest()
def check(v,message):
 global count
 count+=1
 if not v:raise AssertionError(message)
def refused(fn,message):
 global negative
 try:fn()
 except (ValueError,AssertionError):negative+=1;return
 raise AssertionError('admitted '+message)
with tempfile.TemporaryDirectory(prefix='unit-',dir=P)as temp:
 root=Path(temp);m.ROOT=root
 for directory in['models','atlas','cpp/include','schemas','tests','cmake','tools/md1997_decimal_reference_current17_v1']:(root/directory).mkdir(parents=True,exist_ok=True)
 for name in['CMakeLists.txt','cmake/AtlasScalarFunctions.cmake','tests/test_solver.cpp','tools/check_md1997_numerical_ci.py']:(root/name).write_text('NONACCEPTING UNIT FIXTURE\n')
 for name in m.REFERENCE_FILES:shutil.copyfile(SOURCE/'tools/md1997_decimal_reference_current17_v1'/name,root/'tools/md1997_decimal_reference_current17_v1'/name)
 for name in m.SIXTEEN:(root/'models'/(name+'.json')).write_text(json.dumps({'id':name}))
 shutil.copyfile(SOURCE/'models'/(m.MD+'.json'),root/'models'/(m.MD+'.json'));models=[json.loads(p.read_text())for p in sorted((root/'models').glob('*.json'))]
 check(m.model_set(models)is True,'exact17');check(m.model_set([x for x in models if x['id']!=m.MD])is False,'historical16')
 for bad in[models[:-1],models+[{'id':'extra'}],models+[models[0]]]:refused(lambda b=bad:m.model_set(b),'wrongmembership')
 mdpath=root/'models'/(m.MD+'.json');original=mdpath.read_bytes();mdpath.write_bytes(original+b' ');refused(lambda:m.model_set(models),'MDhash');mdpath.write_bytes(original)
 refused(lambda:m.require_unchanged({'source':'a'},{'source':'b'}),'changed source');refused(lambda:m.require_unchanged({'exe':'a'},{'exe':'b'}),'changed binary')
 build=root/'build';(build/'generated').mkdir(parents=True);(build/'generated/models.hpp').write_text('NONACCEPTING generated fixture');(build/'atlas_numerical_tests').write_text('NONEXECUTABLE unit bytes')
 def catalog(rows):
  (build/'generated/models.json').write_text(json.dumps({'schema_version':'0.1','sha256':H(m.canonical(rows)),'models':rows}))
 catalog(models);calls=[];mode='pass'
 def fake(argv,cwd,env,stdout,stderr,timeout):
  calls.append((argv,cwd,dict(env)));stdout.write_bytes(b'NONACCEPTING UNIT RAW');stderr.write_bytes(b'')
  if argv==[str(build/'atlas_numerical_tests')]:
   if mode=='child-fail':return 1
   if mode=='source-change':(root/'tests/test_solver.cpp').write_text('changed')
   if mode=='executable-change':(build/'atlas_numerical_tests').write_text('changed')
   if mode=='generated-change':(build/'generated/models.hpp').write_text('changed')
   return 0
  check(argv[1]=='-B'and argv[2]==str(root/'tools/md1997_decimal_reference_current17_v1/assess_saved.py'),'unchanged assessor CLI used')
  if mode=='assessor-fail':return 1
  if mode=='assessment-missing':return 0
  output=Path(argv[argv.index('--output')+1]);process=Path(argv[argv.index('--process')+1]);binding_hash=argv[argv.index('--build-binding-sha256')+1]
  output.write_text(json.dumps({'identity':'md1997-decimal-saved-assessment-current17-v1','passed':mode!='assessment-false','purpose':'actual','comparisons':587 if mode=='wrongcount'else 588,'failures':[],'build_binding_sha256':'f'*64 if mode=='wrongbinding'else binding_hash,'process_sha256':H(process.read_bytes()),'raw_output_sha256':H((output.parent/'native.stdout').read_bytes())}));return 0
 m.run_process=fake
 report=m.run(build,root/'positive');check(report['passed']and report['comparisons']==588,'mocked full route');check(len(calls)==2 and calls[0][2]['ATLAS_NUMERICAL_FIXTURES']==m.DECIMAL,'exact Decimal selector');binding=json.loads((root/'positive/build-binding.json').read_text());check(binding['fixture_sha256']==H((root/'tests/test_solver.cpp').read_bytes())and binding['executable_sha256']==H((build/'atlas_numerical_tests').read_bytes()),'honest local fixture/executable hashes');check(binding['source_freeze_sha256']==H(m.canonical(json.loads((root/'positive/source-before.json').read_text())))and binding['generated_catalogue_sha256']==H((build/'generated/models.json').read_bytes()),'source map and actual catalogue hashes')
 for value in ['child-fail','assessor-fail','assessment-missing','assessment-false','wrongcount','wrongbinding','source-change','executable-change','generated-change']:
  mode=value;refused(lambda v=value:m.run(build,root/v),value);check(json.loads((root/value/'result.json').read_text())['passed']is False,'failure result retained');(root/'tests/test_solver.cpp').write_text('NONACCEPTING UNIT FIXTURE\n');(build/'atlas_numerical_tests').write_text('NONEXECUTABLE unit bytes');(build/'generated/models.hpp').write_text('NONACCEPTING generated fixture')
 mode='pass';mdpath.unlink();catalog([x for x in models if x['id']!=m.MD]);calls.clear();check(m.run(build,root/'legacy16')['passed']and len(calls)==1 and 'ATLAS_NUMERICAL_FIXTURES'not in calls[0][2],'legacy16 numerical no assessor')
 # Strict OCC analytical failure: unchanged formula and failure pattern.
 shutil.copyfile(SOURCE/'models'/(strict.OCC+'.json'),root/'models'/(strict.OCC+'.json'));model=json.loads((root/'models'/(strict.OCC+'.json')).read_text());params={k:v['default']for k,v in model['parameters'].items()};axial=1e-4;volume=model['state'][1]['initial']/(1+axial);pressure=params['pref']*math.exp((params['Gamma']+params['lambda_c']-params['kappa']-volume)/params['lambda_c']);residual=abs(pressure-100000)/100000;message=f'failed knot 1 residual {residual:.17g} trials 1 de0 0.0001 de1 0\ndrained replay failed: {strict.OCC} singular mixed-control system; last committed knot retained\n'
 old={**strict.PRIOR_THIRTEEN,strict.DUNCAN:strict.DUNCAN_HASH,strict.RAMBERG:strict.RAMBERG_HASH,strict.SCLAY:strict.SCLAY_HASH};current={**old,strict.MD:strict.MD_HASH};check('current-seventeen'in strict.check_recorded_failure(message,current,root=root),'strict17 OCC positive');check('current-sixteen'in strict.check_recorded_failure(message,old,root=root),'strict16 unchanged')
 for bad in [{**current,strict.MD:'0'*64},{k:v for k,v in current.items()if k!=strict.SCLAY},{**current,'unknown':'0'*64}]:refused(lambda b=bad:strict.check_recorded_failure(message,b,root=root),'strict catalogue')
 refused(lambda:strict.check_recorded_failure(message.replace('trials 1','trials 2'),current,root=root),'strict failure signature')
result={'identity':'direct-ci-numerical-source-unit-v1','assertions':count,'refusals':negative,'actual_compiled_calls':0,'actual_assessor_calls':0,'mocked_outputs_nonaccepting':True,'fixtures_cleaned':True};(P/'checks.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n');print(json.dumps(result))
