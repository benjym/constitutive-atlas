"""Independent immutable-byte/composition and bounded selected-suite input audit."""
import sys
sys.dont_write_bytecode=True
import ast,hashlib,json,re,subprocess
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'native-ci-dispatch-implementation-review-v2';A=C/'native-ci-dispatch-implementation-v2';P=C/'native-ci-fixture-composition-v1';S=Path('/private/tmp/atlas-md1997-ci-dispatch-v2/source');T=Path('/private/tmp/atlas-md1997-native-ci-fixture-v1/source');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):assert v,n;checks.append(n)
for x,digest in [(A,'24c1de6f57ec7694d326bf590aa959e2951cfcc0a82114058655eb97c9bcd865'),(P,'b18cfd1f256babe54161e56bb4c230b369b5f2fbbbbf933f32e15e8c8dbbd049')]:
 ck(x.name+' manifest',h(x/'manifest.json')==digest)
 for n,v in read(x/'manifest.json').get('files',read(x/'manifest.json')).items():ck(x.name+'/'+n,h(x/n)==v)
f=read(A/'source-freeze.json')['source_files'];g=read(P/'source-freeze.json');g=g.get('files',g.get('source_files'));ck('both592',len(f)==len(g)==592)
for root,inventory in [(S,f),(T,g)]:
 ck(str(root)+' exact inventory',set(inventory)=={p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()})
 for n,v in inventory.items():ck(str(root)+'/'+n,h(root/n)==v)
pre=read(A/'preparation.json');old=Path(pre['prior_source_directory']);ck('all prior591 immutable',len(pre['prior591'])==591 and all(h(old/n)==v for n,v in pre['prior591'].items()));ck('exact3 correction paths',{n for n,v in pre['prior591'].items() if f[n]!=v}==set(pre['authorized_changes']));ck('exact one addition',set(f)-set(pre['prior591'])=={'tools/test_scalar_functions.py'})
ck('scalar exact published Git37d',(S/'tools/test_scalar_functions.py').read_bytes()==subprocess.check_output(['git','show','37d70660e3561c342bb114716c233a3d06651bcb:tools/test_scalar_functions.py']))
ck('composition only accepted fixture',set(f)==set(g) and [n for n in f if f[n]!=g[n]]==['tests/test_solver.cpp'] and g['tests/test_solver.cpp']=='1b4555f246d6b572b8f653e5ca771c37177ee48883e2466fda96dc7665d85623')
ck('fixture bytes equal accepted fixturev3',(T/'tests/test_solver.cpp').read_bytes()==Path('/private/tmp/atlas-md1997-native-fixture-v3/source/tests/test_solver.cpp').read_bytes())
plan=read(P/'execution-plan.json');steps=plan['steps'];builds=[x for x in steps if x['argv'][0]=='cmake' and '--build' in x['argv']];targets=[x['argv'][x['argv'].index('--target')+1]for x in builds];ck('13 stages /9 serial explicit targets',len(steps)==13 and len(builds)==9 and all(x['argv'][-2:]==['--parallel','1'] and x['argv'].count('--target')==1 for x in builds))
cm=(T/'CMakeLists.txt').read_text();sources=[]
for target in targets:
 match=re.search(r'add_(?:executable|library)\('+target+r'\s+(?:(?:SHARED|EXCLUDE_FROM_ALL)\s+)*([^\s)]+)',cm);ck('declared buildtarget '+target,match is not None);src=match.group(1);ck('target source exists '+src,(T/src).is_file());sources.append(T/src)
# Resolve quoted local headers; generated model/history headers are intentional
# future compiler outputs bound to exact CMake source and fixture catalogues.
seen=set();generated=set();unresolved=[];todo=sources[:]
while todo:
 p=todo.pop()
 if p in seen:continue
 seen.add(p)
 for rel in re.findall(r'^\s*#include\s+"([^"]+)"',p.read_text(),re.M):
  found=next((q for q in [p.parent/rel,T/'cpp/include'/rel,T/'tests'/rel] if q.is_file()),None)
  if found:todo.append(found)
  elif rel in ['models.hpp','history_programs.hpp']:generated.add(rel)
  else:unresolved.append([str(p.relative_to(T)),rel])
ck('all selected C++ local headers present or declared generated',not unresolved)
# Compiler/history compiler imports are inspected recursively, never executed.
todo=[T/'atlas/compiler.py',T/'atlas/history_compiler.py'];modules=set()
while todo:
 p=todo.pop()
 if p in modules:continue
 modules.add(p)
 for n in ast.walk(ast.parse(p.read_text())):
  names=[x.name for x in n.names] if isinstance(n,ast.Import) else [n.module] if isinstance(n,ast.ImportFrom) and n.module else []
  for name in names:
   if name.startswith('atlas'):
    q=T/Path(*name.split('.'));q=q.with_suffix('.py') if q.with_suffix('.py').is_file() else q/'__init__.py';ck('compiler import '+name,q.is_file());todo.append(q)
for path in ['tests/fixtures/time','tests/fixtures/expm','tests/fixtures/expm-history','tests/fixtures/log1p','tests/fixtures/log1p-history']:
 ck('generation input JSON '+path,bool(list((T/path).glob('*.json'))))
missing=['tools/collect_scalar_functions.py','tools/check_scalar_functions.py'];ck('R1 exact missing scalar scripts',all(not (T/n).exists() for n in missing));ck('scalar requests/references present',all((T/'tests/fixtures/scalar-functions'/n).is_file() for n in ['requests.json','references.json']))
blobs={}
for n in missing:
 b=subprocess.check_output(['git','show','37d70660e3561c342bb114716c233a3d06651bcb:'+n]);ast.parse(b);blobs[n]=hashlib.sha256(b).hexdigest()
 # Only standard-library imports in these future exact inputs.
 imports=[x.name.split('.')[0]for node in ast.walk(ast.parse(b)) if isinstance(node,ast.Import) for x in node.names]+[node.module.split('.')[0]for node in ast.walk(ast.parse(b)) if isinstance(node,ast.ImportFrom) and node.module]
 ck('scalar nested imports standard library '+n,all(x in sys.stdlib_module_names for x in imports))
print(json.dumps({'checks':len(checks),'check_names':checks,'source_only':True,'compiled_calls':0,'source_inventory':592,'composition_only_changed':'tests/test_solver.cpp','selected_targets':targets,'cpp_local_closure_files':len(seen),'compiler_modules':len(modules),'intentionally_generated_headers':sorted(generated),'composition_blocker_R1':blobs,'no_further_static_selected_suite_missing_inputs_found':True,'scope_limit':'C++ selected source/quoted headers, generation fixture trees and local atlas imports, scalar nested script/literal inputs. Toolchain, actual generated output and dynamic environment remain future prerequisites; excluded Python discovery is not claimed.'},indent=2))
