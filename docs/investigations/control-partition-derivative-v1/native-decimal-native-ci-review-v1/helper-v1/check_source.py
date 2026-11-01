"""Independent immutable helper inventory, boundary, and saved synthetic replay."""
import sys
sys.dont_write_bytecode=True
if not __debug__:raise RuntimeError('unoptimized review required')
import ast,hashlib,importlib.util,json
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1];A=R/'native-decimal-ci-implementation-v1';S=Path('/private/tmp/atlas-md1997-decimal-ci-v1/source')
def guard(event,args):
 if event in ['subprocess.Popen','os.system','os.exec','os.posix_spawn']:raise RuntimeError('source-only review forbids process execution')
sys.addaudithook(guard)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_bytes())
rows=[]
def check(ok,name):
 if not ok:raise RuntimeError(name)
 rows.append(name)
check(sha(A/'manifest.json')=='edfd86bad08ebdc87cb1dfc8947d491236fc7b6731140dd2abb4352d4f85ffdf','exact author pin')
m=read(A/'manifest.json');check({str(p.relative_to(A))for p in A.rglob('*')if p.is_file()and p.name!='manifest.json'}==set(m['files']),'complete92packet inventory')
for n,h in m['files'].items():check(sha(A/n)==h,'packet '+n)
for p in [A,S]:check(not any(x.is_symlink()or x.name=='__pycache__'or x.suffix=='.pyc'for x in p.rglob('*')),'no caches/symlinks '+str(p))
for n,row in read(A/'inputs.json').items():check(sha(Path(row['path']))==row['sha256'],'input '+n)
f=read(A/'source-freeze.json');check(sha(A/'source-freeze.json')==m['source_freeze_sha256'],'source freeze pin');actual={str(p.relative_to(S)):sha(p)for p in S.rglob('*')if p.is_file()};check(actual==f['files']and len(actual)==601,'full601 source')
B=R/'native-ci-fixture-composition-v3';bf=read(B/'source-freeze.json');check(sha(B/'source-freeze.json')=='24d76c20e7e43caf8de20d81373b3c28315d066c69ea3f7fbd63cfaf7a3e7c7a','accepted baseline594 pin')
base=bf['files'];changed=sorted(k for k in base if actual.get(k)!=base[k]);added=sorted(set(actual)-set(base));check(changed==['tests/test_native_fixture_dispatch.py','tools/check_native_fixture_dispatch.py'],'only2authorized changed files');check(len(added)==7 and set(base)<=set(actual),'only7 additions')
check(read(A/'preparation.json')['base_files']==base,'base receipt exact594 mapping')
for n,h in base.items():check(sha(Path(bf['directory'])/n)==h,'preserved baseline '+n)
for n in added+changed:check((A/'files'/n).read_bytes()==(S/n).read_bytes(),'mirrored '+n)
O=R/'native-decimal-reference-v1'
for n in added:
 if '/md1997_decimal_reference/'in n:check((S/n).read_bytes()==(O/Path(n).name).read_bytes(),'exact accepted oracle '+n)
old=ast.parse((Path(bf['directory'])/'tools/check_native_fixture_dispatch.py').read_text());new=ast.parse((S/'tools/check_native_fixture_dispatch.py').read_text())
def defs(tree):return {n.name:ast.dump(n,include_attributes=False)for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
x,y=defs(old),defs(new);check(sorted(k for k in x if x[k]!=y.get(k))==['Receipt','check_contracts','context','ctest','execute','main'],'preserved12 strict grammar/catalogue/OCC definitions')
for tree in [old,new]:
 constants={n.targets[0].id:ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and isinstance(n.targets[0],ast.Name)and n.targets[0].id in ['IDENTITIES','HELPERS','POLICIES','REGISTRATIONS','SUITES','NATIVE_CMAKE_SHA256']}
 if tree is old:c=constants
 else:check(constants==c,'all frozen routes/catalogues/CMake/registrations/suites exact')
sys.path.insert(0,str(S));spec=importlib.util.spec_from_file_location('independent_bound_collector',S/'tools/collect_md1997_decimal.py');collector=importlib.util.module_from_spec(spec);spec.loader.exec_module(collector)
for case in ['direct','linux-main','macos-main']:
 receipt=read(A/'synthetic-evidence-v2'/(case+'.json'));typed=A/'synthetic-evidence-v2'/(case+'-decimal')/'typed-process.json';process=read(typed);ext=read(Path(receipt['decimal_execution_freeze']['path']));binding=Path(ext['build_binding']['path']);report=collector.oracle().assess(collector.SUPPORT/'requests.json',collector.SUPPORT/'reference.json',typed,binding,ext['build_binding']['sha256']);saved=read(typed.parent/'assessment.json');check(report==saved and report['purpose']=='synthetic-test-only'and report['comparisons']==588 and report['passed']is True,'full saved588replay '+case)
 for field in ['raw_output_sha256','purpose','comparisons']:check(receipt['decimal_assessments'][0][field]==saved[field],'saved report edge '+case+' '+field)
strict=read(A/'synthetic-evidence-v2/strict-eleven.json');check(len(strict['processes'])==11 and strict['status']=='passed','saved11negative rows')
rej=read(A/'synthetic-evidence-v2/rejected-export.json');check(rej['status']=='failed'and not rej.get('decimal_assessments'),'saved scientific mock failure retained')
log=(P/'author-mock-replay.log').read_text();check('Ran 37 tests'in log and log.rstrip().endswith('OK'),'independent37mock rerun')
check(sha(A/'manifest.json')=='edfd86bad08ebdc87cb1dfc8947d491236fc7b6731140dd2abb4352d4f85ffdf','author post pin')
(P/'source-checks.json').write_text(json.dumps(dict(identity='independent-decimal-ci-source-review-v1',passed=True,checks=len(rows),results=rows,compiled_calls=0,spawned_processes=0),indent=2)+'\n');print(json.dumps(dict(passed=True,checks=len(rows))))
