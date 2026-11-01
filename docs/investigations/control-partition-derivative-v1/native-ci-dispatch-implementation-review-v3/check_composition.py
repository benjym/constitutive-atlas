"""Read-only final composition and selected-suite transitive source audit."""
import sys
sys.dont_write_bytecode=True
import ast,hashlib,json,re,subprocess
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';P=C/'native-ci-fixture-composition-v3';P2=C/'native-ci-fixture-composition-v2';A=C/'native-ci-dispatch-implementation-v3';T=Path('/private/tmp/atlas-md1997-native-ci-fixture-v3/source');S=Path('/private/tmp/atlas-md1997-ci-dispatch-v3/source');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('composition manifest exact',h(P/'manifest.json')=='1390ac8a36132a5b0c47013350111b6cdaac1d20351f80f3453c898e4c186eab')
for n,v in read(P/'manifest.json')['files'].items():ck('packet '+n,h(P/n)==v)
f=read(P/'source-freeze.json')['files'];old=read(P2/'source-freeze.json')['files'];ci=read(A/'source-freeze.json')['source_files'];ck('complete594 inventory',len(f)==594 and set(f)=={p.relative_to(T).as_posix()for p in T.rglob('*')if p.is_file()})
for n,v in f.items():ck('source '+n,h(T/n)==v)
ck('only2overlayfrom594parent',set(f)==set(old) and {n for n in f if f[n]!=old[n]}=={'tools/check_native_fixture_dispatch.py','tests/test_native_fixture_dispatch.py'})
ck('all592CIv3 exact except accepted fixture',set(f)-set(ci)=={'tools/collect_scalar_functions.py','tools/check_scalar_functions.py'} and {n for n in ci if f[n]!=ci[n]}=={'tests/test_solver.cpp'})
ck('accepted fixtureexact',f['tests/test_solver.cpp']=='1b4555f246d6b572b8f653e5ca771c37177ee48883e2466fda96dc7665d85623' and (T/'tests/test_solver.cpp').read_bytes()==Path('/private/tmp/atlas-md1997-native-fixture-v3/source/tests/test_solver.cpp').read_bytes())
for n in ['tools/collect_scalar_functions.py','tools/check_scalar_functions.py']:
 b=subprocess.check_output(['git','show','37d70660e3561c342bb114716c233a3d06651bcb:'+n]);ck('exact Git37d nested scalar '+n,(T/n).read_bytes()==b)
 imports=[x.name.split('.')[0]for node in ast.walk(ast.parse(b)) if isinstance(node,ast.Import)for x in node.names]+[node.module.split('.')[0]for node in ast.walk(ast.parse(b))if isinstance(node,ast.ImportFrom)and node.module];ck('nested imports standardlibrary '+n,all(x in sys.stdlib_module_names for x in imports))
req=read(T/'tests/fixtures/scalar-functions/requests.json')['cases'];ref=read(T/'tests/fixtures/scalar-functions/references.json')['rows'];ck('scalar391request/referencealignment',len(req)==len(ref)==391 and [x['id']for x in req]==[x['id']for x in ref])
p=read(P/'execution-plan.json');steps=p['steps'];ck('13stages',len(steps)==13);builds=[s for s in steps if s['argv'][0]=='cmake' and '--build'in s['argv']];ck('9serialtargets',len(builds)==9 and all(s['argv'][-2:]==['--parallel','1']and s['argv'].count('--target')==1 for s in builds));ck('allstagesunoptimized',all(s['env']['PYTHONOPTIMIZE']=='0' and s['env']['PYTHONDONTWRITEBYTECODE']=='1' for s in steps))
a=read(P2/'execution-plan.json');b=json.loads(json.dumps(p));b['identity']=a['identity'];b['source_freeze_sha256']=a['source_freeze_sha256'];s=json.dumps(b).replace('atlas-md1997-native-ci-fixture-v3','atlas-md1997-native-ci-fixture-v2');b=json.loads(s)
for step in b['steps']:step['env'].pop('PYTHONOPTIMIZE')
b['pending_preconditions']=a['pending_preconditions']
ck('13stages reverse exact beforeversioned metadata',b==a)
# Same bounded source-closure algorithm as prior review, now against full594.
cm=(T/'CMakeLists.txt').read_text();todo=[]
for s in builds:
 target=s['argv'][s['argv'].index('--target')+1];m=re.search(r'add_(?:executable|library)\('+target+r'\s+(?:(?:SHARED|EXCLUDE_FROM_ALL)\s+)*([^\s)]+)',cm);ck('target declared '+target,m is not None);ck('source present '+m.group(1),(T/m.group(1)).is_file());todo.append(T/m.group(1))
seen=set();unresolved=[];generated=set()
while todo:
 p=todo.pop()
 if p in seen:continue
 seen.add(p)
 for rel in re.findall(r'^\s*#include\s+"([^"]+)"',p.read_text(),re.M):
  found=next((q for q in [p.parent/rel,T/'cpp/include'/rel,T/'tests'/rel]if q.is_file()),None)
  if found:todo.append(found)
  elif rel in ['models.hpp','history_programs.hpp']:generated.add(rel)
  else:unresolved.append([str(p.relative_to(T)),rel])
ck('selectedCppheaderclosure',not unresolved)
modules=set();todo=[T/'atlas/compiler.py',T/'atlas/history_compiler.py']
while todo:
 p=todo.pop()
 if p in modules:continue
 modules.add(p)
 for n in ast.walk(ast.parse(p.read_text())):
  names=[x.name for x in n.names]if isinstance(n,ast.Import)else[n.module]if isinstance(n,ast.ImportFrom)and n.module else[]
  for name in names:
   if name.startswith('atlas'):
    q=T/Path(*name.split('.'));q=q.with_suffix('.py')if q.with_suffix('.py').is_file()else q/'__init__.py';ck('compiler import '+name,q.is_file());todo.append(q)
for n in ['time','expm','expm-history','log1p','log1p-history']:ck('generationinput '+n,bool(list((T/'tests/fixtures'/n).glob('*.json'))))
print(json.dumps({'identity':'independent-native-ci-composition-v3-review','checks':len(checks),'check_names':checks,'source_files':594,'cpp_local_closure_files':len(seen),'compiler_modules':len(modules),'generated_future_headers':sorted(generated),'missing_static_selected_suite_inputs':[],'R1_resolved':True,'fixture_v3_exact':True,'plan_stages':13,'build_targets':9,'compiled_calls':0,'builds':0,'decision_scope':'Prospective exact Linux selected-suite/strict/recorded study only; actual toolchain prepost and serial slot still mandatory.'},indent=2))
