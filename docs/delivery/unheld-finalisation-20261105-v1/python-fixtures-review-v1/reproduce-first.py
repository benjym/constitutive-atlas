from pathlib import Path
import json,hashlib,ast,sys,types,importlib.util,unittest,io,copy
P=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/python-explicit-fixtures-fix-v1');OWN=Path(__file__).resolve().parent;W=Path('/private/tmp/atlas-baseline-delivery-20261105/source');sys.path.insert(0,str(W));checks=[]
def ck(n,b=True):assert b,n;checks.append(n)
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
patch=json.loads((P/'patch-proof.json').read_text())
for path,substitutions in patch.items():
 old=(P/'original'/path).read_text();new=(P/'proposed'/path).read_text();restored=new
 for change in reversed(substitutions):ck(path+' unique patch',restored.count(change['new'])==1);restored=restored.replace(change['new'],change['old'])
 ck(path+' reversebyteexact',restored==old)
 oldassert=[ast.dump(x)for x in ast.walk(ast.parse(old))if isinstance(x,ast.Assert)or isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and (x.func.attr.startswith('assert')or x.func.attr=='subTest')]
 newassert=[ast.dump(x)for x in ast.walk(ast.parse(new))if isinstance(x,ast.Assert)or isinstance(x,ast.Call)and isinstance(x.func,ast.Attribute)and (x.func.attr.startswith('assert')or x.func.attr=='subTest')]
 ck(path+' every original assertion/context unchanged',oldassert==newassert)
for rel in ['tests/historical_generation.py','tests/fixtures/historical-test-contexts.json']:
 ck('Current helper authority '+rel,(W/rel).read_bytes()==(P/'evidence/source'/rel).read_bytes())
from tests.historical_generation import public_models,public_paths
legacy={m['id']:m for m in public_models()};paths={p.name:p for p in public_paths()}
for row in json.loads((P/'state-proof.json').read_text()):
 mid=row['id'];m=legacy[mid];ck(mid+' exactfrozen0.1',m['schema_version']=='0.1'and hashlib.sha256(paths[mid+'.json'].read_bytes()).hexdigest()==row['legacy']['sha256']);ck(mid+' exactfullstate',row['initial']==[v for f in m['state']for v in(f['initial']if f['shape']=='sym'else[f['initial']])]);ck(mid+' currenthashpin',hashlib.sha256((W/f'models/{mid}.json').read_bytes()).hexdigest()==row['current_sha256'])
# Execute only original run/csv function AST and literal fixture map with a manufactured subprocess boundary.
source=(P/'proposed/tests/test_atlas.py').read_text();tree=ast.parse(source);nodes=[x for x in tree.body if isinstance(x,ast.FunctionDef)and x.name in ['csv','run']or isinstance(x,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='BASELINE_INITIAL_EXAMPLES'for t in x.targets)];calls=[]
def fake_run(argv,**kwargs):calls.append((argv,kwargs));return types.SimpleNamespace(returncode=0,stdout='{"ok":true}',stderr='')
namespace={'SOLVER':Path('/owned-inert/no-execution'),'subprocess':types.SimpleNamespace(run=fake_run),'json':json};exec(compile(ast.Module(body=nodes,type_ignores=[]),'manufactured-helper','exec'),namespace)
for mid,state in namespace['BASELINE_INITIAL_EXAMPLES'].items():
 for args in [{'protocol':1,'target':.001,'steps':20},{'mode':'integrate','strain':'0,0,0,0,0,0'},{'parameters':'1','steps':0,'target':'nan','confinement':123},{'initial':'1','mode':'integrate'},{'initial':'','mode':'integrate'}]:
  original=copy.deepcopy(args);namespace['run'](mid,**args);wire,settings=calls[-1];oldwire=['/owned-inert/no-execution','--model',mid]+[s for k,v in args.items()for s in('--'+k.replace('_','-'),str(v))];expected=oldwire+([]if'initial'in args else['--initial',namespace['csv'](state)]);ck(mid+' exactargumentwire '+str(args),wire==expected);ck('Caller kwargs unchanged',args==original)
namespace['run']('unowned-model',mode='evaluate',current='1');ck('Unknown model receives no default guess','--initial'not in calls[-1][0])
namespace['run']('linear-elastic',mode='evaluate',current='2',initial='3',strain='4');ck('Evaluate current/previous explicit bindings preserved',calls[-1][0][-6:]==['--current','2','--initial','3','--strain','4'])
# Real unchanged pure legacy transport/validation assertions; callbacks are identity/toy-preparation only.
history=module('proposed_history',P/'proposed/tests/test_history_legacy.py');capacity=module('proposed_capacity',P/'proposed/tests/test_capacity.py');suite=unittest.defaultTestLoader.loadTestsFromTestCase(history.LegacyHistoryTests);suite.addTest(capacity.CapacityTests('test_legacy_26_component_multiplier_layout'));stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite);(OWN/'pure-legacy.stdout.txt').write_text(stream.getvalue());ck('All original purelegacy tests pass',result.wasSuccessful());ck('Legacy explicitv03 rejection retained', 'test_explicit_v03_draft_is_rejected_by_legacy_transport' in stream.getvalue())
report={'status':'PASS_SOURCE_MANUFACTURED_AND_PURE_LEGACY_ONLY','count':len(checks),'checks':checks,'manufactured_helper_calls':len(calls),'pure_legacy_tests_run':result.testsRun,'actual_compiled_module_material_browser_network_calls':0,'temporary_resources_remaining':0};print(json.dumps(report,indent=2))
