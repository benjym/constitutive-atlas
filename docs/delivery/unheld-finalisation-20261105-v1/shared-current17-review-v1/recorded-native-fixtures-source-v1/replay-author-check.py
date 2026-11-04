from pathlib import Path
import ast,copy,hashlib,importlib.util,json,os,sys,tempfile,unittest
from unittest.mock import patch
O=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/recorded-native-fixtures-fix-v1');OUT=Path(__file__).resolve().parent;R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sys.path.insert(0,str(R));checks=[];sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def ck(n,v):
 assert v,n
 checks.append(n)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m
helper=load('tests.recorded_native_fixtures',O/'proposed/tests/recorded_native_fixtures.py')
models=[json.loads(p.read_text())for p in helper.legacy_paths()]
ck('exactfive v01 catalogue1cac',len(models)==5 and all(m['schema_version']=='0.1'for m in models))
from atlas.model import all_models
current={m['id']:m for m in all_models()}
for id,values in helper.EXPLICIT_INITIALS.items():
 def initial(m):return [x for f in m['state']for x in (f['initial']if f.get('shape')=='sym'else[f['initial']])]
 ck('frozen current explicit state '+id,values==initial(current[id]))
 ck('same original legacy state '+id,values==initial(next(m for m in models if m['id']==id)))
for name in ['test_recorded_api.py','test_recorded_restarts.py']:
 old=ast.parse((R/'tests'/name).read_text());new=ast.parse((O/'proposed/tests'/name).read_text())
 # Every original assertion call remains identical, ordered, including negative contexts.
 assertions=lambda tree:[ast.dump(n,include_attributes=False)for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr.startswith('assert')]
 # ast.walk order changes with one enclosing context; compare within each function.
 oldf={n.name:n for n in ast.walk(old)if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))};newf={n.name:n for n in ast.walk(new)if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))}
 for n,f in oldf.items():ck(name+' assertions '+n,assertions(f)==assertions(newf[n]))
 ck(name+' Python syntax',bool(new))
# Full byte reversal of exactly the declared fixture/context adaptations.
a=(O/'proposed/tests/test_recorded_api.py').read_text().replace('from tests.recorded_native_fixtures import explicit_recorded_fixture\n','').replace("return explicit_recorded_fixture(dict(version='experimental-recorded-run-0.1', model='linear-elastic', path=path))","return dict(version='experimental-recorded-run-0.1', model='linear-elastic', path=path)").replace("'--model','linear-elastic','--initial',','.join(map(str,specimen()['initial'])),'--initial-strain'","'--model','linear-elastic','--initial-strain'")
ck('entire API source exact reverse',a==(R/'tests/test_recorded_api.py').read_text())
b=(O/'proposed/tests/test_recorded_restarts.py').read_text().replace('from tests.recorded_native_fixtures import explicit_recorded_fixture,historical_recorded_context\n','').replace('        s=explicit_recorded_fixture(s)\n','').replace("'--model','linear-elastic','--initial',','.join(map(str,specimen()['initial'])),'--initial-strain'","'--model','linear-elastic','--initial-strain'").replace("'--model','linear-elastic','--initial',','.join(map(str,specimen()['initial'])),'--strain'","'--model','linear-elastic','--strain'")
start=b.index('        with historical_recorded_context(self,globals()):\n');end=b.index('\n    def test_three_coarse_paths',start);body=b[start:end].splitlines(True)[1:];b=b[:start]+''.join(x[4:]if x.strip()else x for x in body)+b[end:]
ck('entire restart source exact reverse',b==(R/'tests/test_recorded_restarts.py').read_text())
api=load('tests.test_recorded_api',O/'proposed/tests/test_recorded_api.py');restart=load('tests.test_recorded_restarts',O/'proposed/tests/test_recorded_restarts.py')
ck('explicit specimen no mutation',api.specimen()['initial']==helper.EXPLICIT_INITIALS['linear-elastic'])
a={'model':'drucker-prager','initial':[1]};b=copy.deepcopy(a);ck('explicit supplied initial untouched',helper.explicit_recorded_fixture(a)==a and a==b)
a={'model':'drucker-prager','path':{'x':[1]}};b=copy.deepcopy(a);adapt=helper.explicit_recorded_fixture(a);adapt['path']['x'].append(2);ck('adapter no input alias/mutation',a==b)
try:helper.explicit_recorded_fixture({'model':'unfrozen'})
except KeyError:ck('unknown missing-state fixture rejected',True)
else:raise AssertionError('unknown accepted')
# Source generation only. No configure/compiler process/material executable.
gen=load('_proposed_recorded_legacy_generator',O/'proposed/tools/generate_recorded_legacy_models.py')
with tempfile.TemporaryDirectory(prefix='atlas-recorded-legacy-source-check-')as tmp:
 result=gen.generate_legacy(Path(tmp)/'generated');ck('current pure generator exacthistorical metadata',result['sha256']==helper.LEGACY_HASH and result['models']==models)
 ck('generated legacy engine keeps original implicit-state contract','inline bool explicit_initialization_required(int model) { switch(model) {default: return false;} }'in (Path(tmp)/'generated/models.hpp').read_text())
 (OUT/'generated-source-check.json').write_text(json.dumps({'catalogue_hash':result['sha256'],'model_count':len(models),'header_sha256':sha(Path(tmp)/'generated/models.hpp'),'json_sha256':sha(Path(tmp)/'generated/models.json'),'compiled_execution':False},indent=2)+'\n')
# Resolver plumbing only: inert file, mocked describe/transport; never invoke executable.
with tempfile.TemporaryDirectory(prefix='atlas-recorded-resolver-fixture-')as tmp:
 binary=Path(tmp)/'inert-fixture';binary.write_text('NOT AN EXECUTABLE\n');namespace={'all_models':lambda:['current']};test=type('Fixture',(),{'records':[],'run_spec':lambda self,s:None})()
 with patch.dict(os.environ,{},clear=True):
  try:
   with helper.historical_recorded_context(test,namespace):pass
  except RuntimeError:ck('resolver fails closed absent binding',True)
  else:raise AssertionError('missing solver accepted')
 env={'ATLAS_RECORDED_LEGACY_SOLVER':str(binary),'ATLAS_RECORDED_LEGACY_SHA256':sha(binary)}
 original={'model':'linear-elastic','version':'experimental-recorded-run-0.1'};before=copy.deepcopy(original)
 with patch.dict(os.environ,env),patch.object(helper.subprocess,'check_output',return_value=json.dumps({'sha256':helper.LEGACY_HASH,'models':models})),patch.object(helper,'execute_recorded',side_effect=lambda spec,solver: {'specification':copy.deepcopy(spec)})as transport:
  with helper.historical_recorded_context(test,namespace):
   ck('historical catalogue context exact',namespace['all_models']()==models);test.run_spec(original)
  ck('historical request missing-state bytes preserved',transport.call_args.args[0]==before and original==before and 'initial'not in transport.call_args.args[0]);ck('current namespace restored',namespace['all_models']()==['current'])
 for field in ('sha256','models'):
  bad={'sha256':helper.LEGACY_HASH,'models':models};bad[field]='wrong'
  with patch.dict(os.environ,env),patch.object(helper.subprocess,'check_output',return_value=json.dumps(bad)):
   try:
    with helper.historical_recorded_context(test,namespace):pass
   except RuntimeError:ck('resolver rejects bad '+field,True)
   else:raise AssertionError('wrong catalogue accepted')
# Replay every original historical request through resolver plumbing using saved
# responses as an explicitly manufactured transport fixture, never an actual pass.
import gzip
with tempfile.TemporaryDirectory(prefix='atlas-recorded-all-legacy-fixture-')as tmp:
 binary=Path(tmp)/'inert';binary.write_text('INERT FIXTURE ONLY')
 rows=json.load(gzip.open(R/'catalogue/investigations/recorded-restarts-v1/responses.json.gz','rt'))
 def key(s):return json.dumps(s,sort_keys=True,separators=(',',':'))
 lookup={key(row['request']):row['response']for row in rows};requests=[]
 def saved(spec,solver):
  requests.append(copy.deepcopy(spec));return copy.deepcopy(lookup[key(spec)])
 env={'ATLAS_RECORDED_LEGACY_SOLVER':str(binary),'ATLAS_RECORDED_LEGACY_SHA256':sha(binary)}
 test=restart.RestartNativeTests('test_disabled_legacy_responses_exact')
 with patch.dict(os.environ,env),patch.object(helper.subprocess,'check_output',return_value=json.dumps({'sha256':helper.LEGACY_HASH,'models':models})),patch.object(helper,'execute_recorded',side_effect=saved):
  test.test_disabled_legacy_responses_exact()
 ck('all22 legacy context calls retain original requests',len(requests)==22 and all(key(x)in lookup for x in requests))
 ck('no missing initial injected across historical calls',any('initial'not in x for x in requests))
 badenv=dict(env,ATLAS_RECORDED_LEGACY_SHA256='0'*64)
 with patch.dict(os.environ,badenv),patch.object(helper.subprocess,'check_output')as no_transport:
  try:
   with helper.historical_recorded_context(test,{}):pass
  except RuntimeError:ck('changed executable fails before transport',not no_transport.called)
  else:raise AssertionError('changed binary accepted')
# Existing pure tests only; native classes intentionally excluded, no added skips.
suite=unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromTestCase(c)for c in [api.RecordedRunContractTests,api.RetainedRecordedAPITests,restart.RestartContractTests,restart.RetainedRestartTests]);r=unittest.TextTestRunner(verbosity=0).run(suite);ck('original pure contracts retained',r.wasSuccessful()and not r.skipped)
(OUT/'check.stdout.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'pure_unittests':r.testsRun,'manufactured_only':True,'compiled_or_material_calls':0},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks),'pure_tests':r.testsRun}))
