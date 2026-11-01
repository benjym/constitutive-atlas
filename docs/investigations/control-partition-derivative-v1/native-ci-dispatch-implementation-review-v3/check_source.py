"""Independent exact-byte and source-semantic preservation audit; no builds."""
import sys
sys.dont_write_bytecode=True
import ast,hashlib,json,subprocess
from pathlib import Path
C=Path.cwd()/'docs/investigations/control-partition-derivative-v1';D=C/'native-ci-dispatch-implementation-v3';O=C/'native-ci-dispatch-implementation-v2';S=Path('/private/tmp/atlas-md1997-ci-dispatch-v3/source');T=Path('/private/tmp/atlas-md1997-ci-dispatch-v2/source');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text());checks=[]
def ck(n,v):assert v,n;checks.append(n)
ck('author manifest exact',sha(D/'manifest.json')=='b9cc828fdb23aa0a393916c9c159586ac86cd6c6ea657812d5c65bd6024434f2')
m=read(D/'manifest.json');m=m.get('files',m)
for n,h in m.items():ck('author packet '+n,sha(D/n)==h)
f=read(D/'source-freeze.json')['source_files'];old=read(O/'source-freeze.json')['source_files'];ck('same592 names',len(f)==len(old)==592 and set(f)==set(old));ck('only dispatcher/mock changed',{n for n in f if f[n]!=old[n]}=={'tools/check_native_fixture_dispatch.py','tests/test_native_fixture_dispatch.py'})
for root,inv in [(S,f),(T,old)]:
 ck('complete filesystem '+str(root),set(inv)=={p.relative_to(root).as_posix()for p in root.rglob('*')if p.is_file()})
 for n,h in inv.items():ck(str(root)+'/'+n,sha(root/n)==h)
for p in (D/'files').rglob('*'):
 if p.is_file():ck('public copy '+str(p.relative_to(D/'files')),p.read_bytes()==(S/p.relative_to(D/'files')).read_bytes())
# Exact AST for every old function/class except the explicitly changed parts.
a=ast.parse((T/'tools/check_native_fixture_dispatch.py').read_text());b=ast.parse((S/'tools/check_native_fixture_dispatch.py').read_text());nodes=lambda tree:{n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))};x,y=nodes(a),nodes(b)
ck('only one added function',set(y)-set(x)=={'canonical_ctest_text'} and not set(x)-set(y))
for name in x:
 if name in ['validate_registrations','Receipt']:continue
 ck('original function unchanged '+name,ast.dump(x[name],include_attributes=False)==ast.dump(y[name],include_attributes=False))
oldreceipt=ast.unparse(x['Receipt']);newreceipt=ast.unparse(y['Receipt']).replace('native-fixture-closed-dispatch-v3','native-fixture-closed-dispatch-v2');ck('Receipt onlyidentitychanged',oldreceipt==newreceipt)
v2=x['validate_registrations'];v3=y['validate_registrations']
# The only changed check replaces loose property blacklist with full-file equality.
v2.body=[n for n in v2.body if not (isinstance(n,ast.Expr)and 'unexpected generated CTest outcome override' in ast.unparse(n))]
v3.body=[n for n in v3.body if not (isinstance(n,ast.Expr)and 'generated CTest properties/full-file grammar differ from pinned source' in ast.unparse(n))]
ck('validation otherinstructions byte semantic exact',ast.dump(v2,include_attributes=False)==ast.dump(v3,include_attributes=False))
proof=read(D/'legitimate-format-proof.json');p=Path(proof['original_path']);ck('actual saved legitimate bytes',sha(p)==proof['original_sha256'] and (D/'legitimate-CTestTestfile.cmake').read_bytes()==p.read_bytes());ck('actual CMake cache4.4.3',proof['CMake_cache_version']=={'MAJOR':'4','MINOR':'4','PATCH':'3'})
for n in ['tools/check_native_fixture_contracts.py','catalogue/laboratory-package-policy.json','tools/test_scalar_functions.py']:
 ck('published unchanged '+n,(S/n).read_bytes()==subprocess.check_output(['git','show','37d70660e3561c342bb114716c233a3d06651bcb:'+n]))
ck('sourceCMake exact61f7',sha(S/'CMakeLists.txt')=='61f7fb538fcb1f2d03259ed4eda531fc9f41bc6119ffed56f3ea49dd8c762a0d')
for p in (D/'files').rglob('*.py'):ast.parse(p.read_text())
print(json.dumps({'identity':'independent-ci-v3-source-review','checks':len(checks),'check_names':checks,'source_files':592,'preserved_v2_files':590,'compiled_calls':0,'builds':0,'decision_scope':'dispatcher correction source/mock; composition separate'},indent=2))
