"""Source/tiny-fixture checks only. No source freeze, compiler, engine or module."""
from pathlib import Path
import ast,hashlib,json,importlib.util,tempfile,shutil,subprocess
O=Path(__file__).resolve().parent;N=O.parent;OLD=O.parents[1]/'unheld-finalisation-20261102-v1/baseline-qualification-plan-v5';S=N/'current17-runtime-source-v1/source';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):
 if not v:raise AssertionError(n)
 checks.append(n)
def fails(fn,n):
 try:fn()
 except(AssertionError,ValueError,FileNotFoundError):checks.append(n);return
 raise AssertionError('accepted '+n)
for p in O.glob('*.py'):ast.parse(p.read_text());checks.append('Python syntax '+p.name)
for row in json.loads((O/'external-pins.json').read_text()):ok(sha(Path(row['path']))==row['sha256'],'external originalauthority '+row['path'])
spec=importlib.util.spec_from_file_location('prospective_rate_plan',O/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
ok(m.M.HERE==OLD,'original collector HERE/policy/wasmcli location retained')
original=ast.parse((OLD/'collector.py').read_text())
for name in('source_files','source_freeze','freeze','collect','assess_pair','interface_cases'):
 node=next(n for n in original.body if isinstance(n,ast.FunctionDef)and n.name==name)
 actual=getattr(m.M,name)
 ok(actual.__code__.co_filename==str(OLD/'collector.py'),'original implementation unchanged '+name)
ok(m.source_files is m.M.source_files,'same source_files used prefreeze/build/validation')
build=(O/'build.py').read_text();base=(N/'current16-qualification-plan-v1/build.py').read_text()
reversed_build=build.replace('PLAN=HERE',"PLAN=Path('/Users/bmar5496/code/constitutive-atlas/docs/delivery/unheld-finalisation-20261102-v1/baseline-qualification-plan-v5')").replace("a.add_argument('--slot-handoff',required=True);a.add_argument('--output',type=Path,required=True);a.add_argument('--plan-manifest-sha256',required=True);args=a.parse_args();m.verify_plan(args.plan_manifest_sha256)","a.add_argument('--slot-handoff',required=True);args=a.parse_args()").replace('out=args.output.resolve()',"out=HERE/'actual-build-v1'").replace("  m.verify_plan(args.plan_manifest_sha256);m.verify(receipt['execution_script']);m.assert_source(repo)\n",'').replace("bound();m.verify_cache(work/'em-cache');assert",'bound();assert')
ok(ast.dump(ast.parse(reversed_build),include_attributes=False)==ast.dump(ast.parse(base),include_attributes=False),'accepted build main/metadata resolver AST preserved after exact declared changes')
policy=json.loads((OLD/'policy.json').read_text());expected=json.loads((N/'current17-browser-plan-v1/catalogue17.json').read_text())
# Tiny manufactured source tree, exactly the declared inputs; no generator invocation.
with tempfile.TemporaryDirectory(prefix='rate-plan-check-',dir=O)as td:
 root=Path(td);m.SOURCE=root
 names=set(policy['unchanged_gate_sha256'])|{str(p.relative_to(S))for p in(S/'models').glob('*.json')}
 for n in names:
  q=root/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes((S/n).read_bytes())
 for n,origin in [('cpp/include/atlas/solver.hpp',N/'current17-igs97-regression-diagnosis-v1/original-rate-profile-v1/proposed/cpp/include/atlas/solver.hpp'),('tests/test_ensemble.mjs',Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/manzari-dafalias-1997/delivery-v1/ensemble-ci-fix-v1/test_ensemble.mjs')),('tests/test_solver.cpp',N/'rate-control-regression-test-plan-v1/proposed/tests/test_solver.cpp')]:
  q=root/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_bytes(origin.read_bytes())
 m.assert_source(root);checks.append('exact proposed source17/B/MD/regression test fixture accepted')
 for n in('cpp/include/atlas/solver.hpp','tests/test_ensemble.mjs','tests/test_solver.cpp','models/linear-elastic.json','tools/verify_igs.py'):
  p=root/n;b=p.read_bytes();p.write_bytes(b+b' ');fails(lambda:m.assert_source(root),'changed sourcepin rejected '+n);p.write_bytes(b)
 (root/'models/linear-elastic.json').unlink();fails(lambda:m.assert_source(root),'missing original model rejected')
rows=json.loads((O/'requests.json').read_text());ok([r['id']for r in rows]==['igs97-edited-initial','md1997-drained','md1997-undrained'],'exact3 request membership/order')
for row in rows:
 spec=row['specification'];document=json.loads(Path(row['document']['path']).read_text());ok(spec==document['specification'],'exact complete public specification '+row['id']);ok(len(spec['loading']['controls_bits'])==101 and spec['steps']==100,'original101 binary64controls '+row['id'])
 if row['id'].startswith('igs'):
  ref=json.loads(Path(row['native_reference']['path']).read_text());old=json.loads(Path(row['wasm_reference']['path']).read_text());ok(ref['ok']and len(ref['points'])==101,'prior702native reference actually successful101');ok(ref['parameters']==spec['parameters']and ref['initial']==spec['initial']and ref['integration_settings']==spec['integration_settings']and ref['loading']['controls_bits']==spec['loading']['controls_bits'],'IGS priornative exactrequest');ok(old['specification']==spec,'IGS old702browser exactspec')
 else:ok(document['result']['ok']and len(document['result']['points'])==101,'originalMD livewasmreference successful101 '+row['id'])
extras=(O/'extras.mjs').read_text()
for text in("assert.deepEqual(withoutElapsed(result),withoutElapsed(entry.replay))","parity(result,normalized702(physical),policy)","assert.deepEqual(withoutElapsed(result),withoutElapsed(read(row.wasm_reference.path).result))","parity(a.result,b.result,policy)","const out=join(actual,'extra-'+backend)","if(!primary)throw e"):
 ok(text in extras,'supplement exact gate/retention '+text)
run=subprocess.run(['node','--check',str(O/'extras.mjs')],capture_output=True,text=True);ok(run.returncode==0,'JS syntax only '+run.stderr)
# Original immutable parity helper rejects drift; no material/runtime module imported.
script="import{parity,withoutElapsed}from './docs/delivery/unheld-finalisation-20261105-v1/nine-example-refresh-plan-v1/collector-core.mjs';import assert from'node:assert/strict';const p={parity_relative_tolerance:1e-10,physical_point_fields:['p']};parity({points:[{p:1}],catalogue_hash:'new'},{points:[{p:1}],catalogue_hash:'new'},p);assert.throws(()=>parity({points:[{p:1.001}],catalogue_hash:'new'},{points:[{p:1}],catalogue_hash:'new'},p));assert.throws(()=>parity({points:[{p:1}],catalogue_hash:'changed'},{points:[{p:1}],catalogue_hash:'new'},p));assert.deepEqual(withoutElapsed({p:1,elapsed_ms:2}),withoutElapsed({p:1,elapsed_ms:3}));console.log('pure parity positive/physical drift/exact metadata/replay checks PASS');"
run=subprocess.run(['node','--input-type=module','-e',script],cwd=O.parents[3],capture_output=True,text=True);ok(run.returncode==0,'unchanged parity manufactured positives/negatives '+run.stderr)
(O/'check.stdout.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'actual_source_freeze_build_material':False,'source_fixture_removed':True},indent=2)+'\n');print(json.dumps({'status':'PASS','checks':len(checks)}))
