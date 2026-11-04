"""Own manufactured plan fixtures and AST only; no generation/build/module/material calls."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,sys,tempfile,types
sys.dont_write_bytecode=True
P=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261105-v1/controlled-path-refresh-plan-v1')
OWN=Path(__file__).resolve().parent
checks=[]
def check(name,ok):
 assert ok,name
 checks.append(name)
def reject(name,fn):
 try:fn()
 except (ValueError,FileNotFoundError):check(name,True);return
 raise AssertionError(name)
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
pre=json.loads((P/'preimages.json').read_text());R=Path(pre['source'])
# Saved helper source only. No call to closure/run/collect/generation or bundlers against real source.
old=load('old_qualifier',R/'tools/qualify_controlled_path_refresh.py');Q=load('new_qualifier',P/'proposed/tools/qualify_controlled_path_refresh.py')
for r in pre['files']:check('exact preimage '+r['path'],hashlib.sha256((R/r['path']).read_bytes()).hexdigest()==r['preimage_sha256'])
for library in ['libatlas_path_capability.dylib','libatlas_path_capability.so']:
 check('default commands byte-equivalent '+library,Q.commands(library)==old.commands(library))
for key in ['MODEL_PATHS','MODELS','GENERATED','GATES']:check('unchanged '+key,getattr(Q,key)==getattr(old,key))
def funcs(path):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef)}
a=funcs(R/'tools/qualify_controlled_path_refresh.py');b=funcs(P/'proposed/tools/qualify_controlled_path_refresh.py')
for name in ['sha','relative','write_new','closure','check_backend_identity','finalize']:check('unchanged function '+name,a[name]==b[name])
with tempfile.TemporaryDirectory(prefix='controlled-selection-',dir=OWN) as tmp:
 root=Path(tmp).resolve();Q.ROOT=root
 # Isolated fixture substitutes the expensive broad closure only; production code is untouched.
 Q.closure=lambda:{'fixture':'fixture-hash'}
 original=Q.prepare();check('default plan identity unchanged',original['identity']=='controlled-path-refresh-plan-v5')
 check('default load exact',Q.load_plan()==original)
 selected=Q.prepare(Q.CURRENT_PLAN);digest=Q.sha(Q.relative(Q.CURRENT_PLAN))
 check('new selected plan identity',selected['identity']=='controlled-path-refresh-plan-20261105-v1')
 check('new selected load exact',Q.load_plan(Q.CURRENT_PLAN,digest)==selected)
 oldcommands=old.commands(selected['native_library']);newcommands=selected['commands']
 normalized=json.loads(json.dumps(newcommands).replace(str(Q.CURRENT_PACKET),str(Q.PACKET)).replace('.local/controlled-path-refresh-20261105-v1','.local/controlled-path-refresh-v2'))
 check('only output/build paths differ in full numerical commands',normalized==oldcommands)
 for name,fn in [
 ('missinghash',lambda:Q.load_plan(Q.CURRENT_PLAN)),('wronghash',lambda:Q.load_plan(Q.CURRENT_PLAN,'0'*64)),
 ('malformedhash',lambda:Q.load_plan(Q.CURRENT_PLAN,'x'*64)),('absolute',lambda:Q.load_plan(root/'plan.json',digest)),
 ('traversal',lambda:Q.load_plan('../plan.json',digest)),('unknown',lambda:Q.load_plan('docs/other-plan.json',digest))]:reject('selected rejects '+name,fn)
 Q.closure=lambda:{'fixture':'changed'};reject('selected rejects stale closure',lambda:Q.load_plan(Q.CURRENT_PLAN,digest));Q.closure=lambda:{'fixture':'fixture-hash'}
 f=Q.relative(Q.CURRENT_PLAN);saved=f.read_bytes();f.unlink();f.symlink_to(root/'outside');reject('selected rejects symlink',lambda:Q.load_plan(Q.CURRENT_PLAN,digest));f.unlink();f.write_bytes(saved)
 # Receipt selects strict plan before any artifact read. Bad pin cannot fall back to old default.
 build=root/'engine';build.mkdir();receipt={'binding':{'plan':{'path':str(Q.CURRENT_PLAN),'sha256':'0'*64}}};(build/'refresh-qualification.json').write_text(json.dumps(receipt));reject('receipt wrong selected hash rejects',lambda:Q.validate_refresh(build,Q.MODELS['norsand']))
 receipt['binding']['plan']['path']='../wrong.json';(build/'refresh-qualification.json').write_text(json.dumps(receipt));reject('receipt unsafe selected path rejects',lambda:Q.validate_refresh(build,Q.MODELS['norsand']))
 # Guard import sees isolated qualifier module; no real package guards are called.
 originalmodule=sys.modules.get('tools.qualify_controlled_path_refresh');sys.modules['tools.qualify_controlled_path_refresh']=Q
 try:
  D=load('new_dependency_guard',P/'proposed/tools/check_current_dependency_assets.py')
  check('dependency default engines unchanged',D.selected_engines()==D.ENGINES)
  engines=D.selected_engines(Q.CURRENT_PLAN,digest)
  check('Maxwell retained exactly',engines['maxwell']==D.ENGINES['maxwell'])
  for key in ['norsand','interface2016']:check('new selected engine '+key,engines[key]==str(Q.CURRENT_PACKET/'execution-v2'/key/'engine'))
  reject('dependency hash without plan rejects',lambda:D.selected_engines(None,digest))
  reject('dependency stale plan rejects',lambda:D.selected_engines(Q.CURRENT_PLAN,'0'*64))
 finally:
  if originalmodule is None:sys.modules.pop('tools.qualify_controlled_path_refresh',None)
  else:sys.modules['tools.qualify_controlled_path_refresh']=originalmodule
print(json.dumps({'identity':'controlled-path-explicit-plan-source-checks-v1','status':'PASS','count':len(checks),'checks':checks,'actual_tool_build_generation_module_material_browser_git_remote_calls':0,'fixtures':'all own temporary fixtures removed'},indent=2))
