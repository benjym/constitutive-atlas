"""Independent exact-source lifecycle review; only inert/pure checks execute."""
from pathlib import Path
import ast,hashlib,importlib.util,json,runpy,sys,tempfile
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
PLAN=HERE.parents[1]/'rate-restoration-qualification-plan-v3'
V2=PLAN.parent/'rate-restoration-qualification-plan-v2'
EXPECTED='4b3a8592279b7a99a18bd0a168bf95a78ee7f95f9dbc0efe1ffcc6417fac5812'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks=[]
def ok(v,n):
 assert v,n
 checks.append(n)
ok(sha(PLAN/'manifest.json')==EXPECTED,'exact frozen v3 manifest')
manifest=json.loads((PLAN/'manifest.json').read_text())
for row in manifest['files']:
 p=PLAN/row['path'];ok(not p.is_symlink()and sha(p)==row['sha256']and p.stat().st_size==row['size_bytes'],'frozen member '+row['path'])
write=Path.write_text;temporary=tempfile.TemporaryDirectory
destinations={'check.stdout.json':'author-check-replay.json','adversarial-checks.json':'author-adversarial-replay.json'}
def redirected_write(p,data,*args,**kwargs):
 if p.parent==PLAN and p.name in destinations:p=HERE/destinations[p.name]
 return write(p,data,*args,**kwargs)
def owned_temp(*args,**kwargs):kwargs['dir']=HERE;return temporary(*args,**kwargs)
with patch.object(Path,'write_text',redirected_write),patch.object(tempfile,'TemporaryDirectory',owned_temp):
 for script in ('check.py','check_adversarial.py'):runpy.run_path(str(PLAN/script),run_name='independent_'+script)
for source,target in destinations.items():
 ok(json.loads((PLAN/source).read_text())==json.loads((HERE/target).read_text()),'exact author replay '+source)
for row in manifest['files']:ok(sha(PLAN/row['path'])==row['sha256'],'original v3 bytes retained '+row['path'])
for name in ('build.py','requests.json','external-pins.json'):
 ok((PLAN/name).read_bytes()==(V2/name).read_bytes(),'entire original scientific/build authority unchanged '+name)
ok((PLAN/'extras.mjs').read_text().replace('v3','v2')==(V2/'extras.mjs').read_text(),'supplement runner only version identity changes')
def functions(path):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(path.read_text()).body if isinstance(n,(ast.FunctionDef,ast.ClassDef))}
a=functions(V2/'collector.py');b=functions(PLAN/'collector.py')
for name in ('verify_plan','verify_cache','assert_source','assert_generated','validate_execution_freeze','GuardedTransport'):
 ok(a[name]==b[name],'unchanged collector implementation '+name)
a=functions(V2/'commands.py');b=functions(PLAN/'commands.py')
for name in ('source_freeze_argv','phase_argv','closed_environment','observe_phase'):
 ok(a[name]==b[name],'unchanged later-phase/closed-environment implementation '+name)
spec=importlib.util.spec_from_file_location('independent_v3_collector',PLAN/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for name in ('source_files','source_freeze','freeze','collect','assess_pair','interface_cases'):
 ok(Path(getattr(m.M,name).__code__.co_filename)==m.OLD/'collector.py','original v5 mathematical delegate '+name)
for bad in ('',' ','\t',' padded','padded ',None,False,[],{},1):
 for field in ('author_run','reviewer_run'):
  r={'author_run':'author','reviewer_run':'reviewer'};r[field]=bad
  try:m.independent_identities(r)
  except (AssertionError,TypeError):checks.append('independent malformed '+field+' '+repr(bad))
  else:raise AssertionError('invalid identity accepted')
m.independent_identities({'author_run':'author','reviewer_run':'reviewer'});checks.append('canonical distinct identities accepted')
try:m.independent_identities({'author_run':'same','reviewer_run':'same'})
except AssertionError:checks.append('self review rejected')
else:raise AssertionError('self review accepted')
cmd=(PLAN/'commands.py').read_text();col=(PLAN/'collector.py').read_text()
ok('return m.guarded_source_freeze(manifest_sha,launch_pin,Path(node),tools,operation,report)'in cmd,'required outer route uses real first-phase guard')
ok("timeout=1800"in cmd and "env=closed_environment()"in cmd,'same original observer limits/environment')
ok("ACTUAL.parent/(ACTUAL.name+'-outer-source-freeze')"in cmd and "ACTUAL.parent/(ACTUAL.name+'-source-freeze-outer-binding.json')"in cmd,'outer outputs remain actual-directory siblings')
ok("traceback.format_exception(type(primary),primary,primary.__traceback__)"in col,'primary traceback retained')
ok("for item in [*snapshot['source_inventory'],*snapshot['inputs']]:attempt"in col,'every captured pin checked despite earlier errors')
ok("with report.open('x')"in col and "sys.stderr.write(json.dumps(record,allow_nan=False)"in col,'exclusive report plus observer raw-stderr fallback')
ok(not any(p.is_dir()for p in HERE.iterdir()),'owned temporary fixtures all removed')
(HERE/'checks.json').write_text(json.dumps({'status':'PASS','independent_checks':len(checks),'labels':checks,'exact_author_replays':[188,85],'preservation_author_saved':15,'actual_source_freeze_build_material_observer_calls':0,'pure_node_syntax_and_comparator_only':True,'fixtures_removed':True},indent=2)+'\n')
print(json.dumps({'status':'PASS','independent_checks':len(checks),'exact_author_replays':[188,85]}))
