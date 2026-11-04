"""Independent continuation review: saved bytes, pure JS, and inert observer only."""
from pathlib import Path
import ast,contextlib,hashlib,importlib.util,io,json,runpy,sys,tempfile,types
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parents[1]/'rate-restoration-qualification-plan-v4'
EXPECTED='50bc4648bc749bdac1c04313de861f6ea75fdec1cd954824198527c4b10f4f0e'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();checks=[]
def ok(v,n):assert v,n;checks.append(n)
ok(sha(P/'manifest.json')==EXPECTED,'exact frozen v4 manifest')
manifest=json.loads((P/'manifest.json').read_text())
for r in manifest['files']:
 q=P/r['path'];ok(not q.is_symlink()and sha(q)==r['sha256']and q.stat().st_size==r['size_bytes'],'frozen member '+r['path'])
stdout=io.StringIO()
with contextlib.redirect_stdout(stdout):runpy.run_path(str(P/'check.py'),run_name='independent_exact_v4_replay')
result=json.loads(stdout.getvalue());(HERE/'author-replay.json').write_text(json.dumps(result,indent=2)+'\n')
ok(result==json.loads((P/'check.stdout.json').read_text()),'exact133 source plus73 pure JS author replay')
for r in manifest['files']:ok(sha(P/r['path'])==r['sha256'],'original author bytes unchanged '+r['path'])
v3=P.parent/'rate-restoration-qualification-plan-v3'
for name in ('requests.json','external-pins.json'):ok((P/name).read_bytes()==(v3/name).read_bytes(),'entire original authority '+name)
s=(P/'extras.mjs').read_text()
for b in ('native','wasm'):
 ok("join(plan.output,'extra-"+b+"/report.json')"in s and "join(actual,'extra-"+b+"/report.json')"not in s,'pair consumes fresh v4 '+b)
for text in ('assert.deepEqual(withoutElapsed(result),withoutElapsed(entry.replay))','parity(result,normalized702(physical),policy)','assert.deepEqual(withoutElapsed(result),withoutElapsed(read(row.wasm_reference.path).result))','parity(a.result,b.result,policy)','assert.equal(result.ok,true)','assert.deepEqual(document.specification,row.specification)'):
 ok(text in s,'mandatory original gate '+text)
scope=(P.parent/'nine-example-refresh-plan-v1/context/web/laboratory-scope.mjs').read_text();contract=(P/'response-contract.mjs').read_text()
ok("r.loading===undefined&&r.target===s.target&&r.cycles===s.cycles"in scope,'existing legacy response contract source')
ok('assert.equal(result.loading,undefined)'in contract and 'assert.equal(result.target,specification.target)'in contract and 'assert.equal(result.cycles,specification.cycles)'in contract,'legacy helper exact shape/target/cycles')
ok('assert.deepEqual(result.loading.controls_bits,specification.loading.controls_bits)'in contract and 'assert.deepEqual(result.integration_settings,specification.integration_settings)'in contract,'controlled and settings gates preserved')
plan=json.loads((P/'plan.json').read_text());ok(plan['actual']!=plan['output']and plan['fresh_build_required']is False,'new outputs reuse genuine build identity explicitly')
prior=json.loads((P/'predecessor-pins.json').read_text());priorpaths={x['path']for x in prior}
for name in ('source-freeze.json','execution-freeze.json','build/receipt.json','native/receipt.json','wasm/receipt.json','pair.json','extra-native/report.json','outer-extra-native/receipt.json'):
 ok(str(Path(plan['actual'])/name)in priorpaths,'genuine old evidence bound '+name)
failure=json.loads((P/'failure.json').read_text());old=json.loads(Path(failure['report']['path']).read_text())
ok(old['status']=='failed'and len(old['rows'])==5 and old['rows'][-1]['result']['ok']is True,'stopped actual failure retained without waiver')
spec=importlib.util.spec_from_file_location('independent_v4_commands',P/'commands.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='inert-observer-',dir=HERE)as td:
 m.ACTUAL=Path(td).resolve();calls=[];guard_calls=[]
 def guard(*args):
  guard_calls.append(True)
  if len(guard_calls)==2:raise ValueError('manufactured final binding error')
 def observe(*args,**kwargs):calls.append((args,kwargs));return types.SimpleNamespace(returncode=17)
 fake=types.SimpleNamespace(observe=observe)
 def make_spec(*args):return types.SimpleNamespace(loader=types.SimpleNamespace(exec_module=lambda mod:None))
 with patch.object(m,'guard',guard),patch.object(m.importlib.util,'spec_from_file_location',side_effect=make_spec),patch.object(m.importlib.util,'module_from_spec',return_value=fake):
  try:m.observe({'node':{'path':'/inert/node'}},'extra-native',EXPECTED,{'path':'/inert/review','sha256':'0'*64})
  except AssertionError as e:ok('failure retained'in str(e),'primary nonzero observer failure survives final binding error')
  else:raise AssertionError('expected primary failure')
 ok(len(calls)==1 and len(guard_calls)==2,'continuation pre/final guard both invoked')
 args,kwargs=calls[0];ok(kwargs['timeout']==1800 and kwargs['env']==m.c.closed_environment(),'original1800 closed environment')
 ok(args[0][0]=='/inert/node'and args[0][2]=='native'and args[0][3]==plan['actual'],'actual engine catalogue read from genuine v3 binding')
 error=json.loads((m.ACTUAL/'post-binding-error-extra-native.json').read_text());ok('manufactured final binding error'in error['error']and 'failure retained'in error['primary'],'both primary/postguard errors durably retained')
ok(not list(HERE.glob('inert-observer-*')),'all owned tiny fixtures removed')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':checks,'exact_author_source_checks':133,'exact_author_pure_JS_checks':73,'real_engine_or_observer_calls':0,'fixtures_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','independent_checks':len(checks),'author_replay':[133,73]}))
