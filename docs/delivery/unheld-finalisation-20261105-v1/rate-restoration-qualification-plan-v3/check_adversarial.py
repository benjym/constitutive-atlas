"""Manufactured identity and first-phase failure tests; no real phase observation."""
from pathlib import Path
import copy,hashlib,importlib.util,io,json,sys,tempfile,traceback
from contextlib import redirect_stderr
from unittest.mock import patch
from types import SimpleNamespace
O=Path(__file__).resolve().parent;checks=[]
def ck(n,v):
 assert v,n
 checks.append(n)
spec=importlib.util.spec_from_file_location('_v3_adversarial_collector',O/'collector.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
with tempfile.TemporaryDirectory(prefix='v3-first-phase-manufactured-',dir=O)as tmp:
 root=Path(tmp).resolve();m.HERE=root/'plan';m.HERE.mkdir();m.OLD=root/'original';m.OLD.mkdir();m.SOURCE=root/'source';m.SOURCE.mkdir();m.ACTUAL=root/'actual'
 def put(path,text='unchanged'):
  path.write_text(text);return path
 for n in ('collector.py','wasm-cli.mjs','policy.json'):put(m.OLD/n)
 put(m.HERE/'manifest.json','{}');expected=m.sha(m.HERE/'manifest.json')
 source=[put(m.SOURCE/'code.dat'),put(m.SOURCE/'reference.dat')];expected_source=[m.pin(p)for p in source]
 reference=put(root/'external.json');put(m.HERE/'external-pins.json',json.dumps([m.pin(reference)]))
 tools={name:str(put(root/name))for name in ('cmake','native_cxx','emcmake','emcc')};node=put(root/'node');receipt=put(root/'installation.json','{}')
 reviews={role:put(root/(role+'.json'),json.dumps({'accepted':True,'author_run':'author','reviewer_run':'reviewer','proposal_manifest_sha256':expected}))for role in ('plan','compatibility','fixtures')}
 def launch():
  return {'identity':'control-restoration-C-reviewed-launch-binding-v3','plan_manifest_sha256':expected,'solver_sha256':'3278b22140ca2057a9a2e415654f5213b8183f398df79a7f5c56628756e8dc99','plan_review':m.pin(reviews['plan']),'installations':{role:{'receipt':m.pin(receipt),'review':m.pin(reviews[role]),'source_pins':[m.pin(source[0])]}for role in ('compatibility','fixtures')}}
 launchfile=root/'launch.json'
 def launchpin():put(launchfile,json.dumps(launch()));return m.pin(launchfile)
 original_reviews={k:p.read_bytes()for k,p in reviews.items()}
 for role,p in reviews.items():
  for field in ('author_run','reviewer_run'):
   for value in (None,1,False,{},[],'',' ',' author','author ', 'reviewer'if field=='author_run'else'author'):
    row=json.loads(original_reviews[role]);row[field]=value;put(p,json.dumps(row));pin=launchpin()
    try:m.verify_launch(pin)
    except (AssertionError,KeyError,TypeError):ck('reject malformed '+str((role,field,value)),True)
    else:raise AssertionError('invalid identity accepted '+str((role,field,value)))
    p.write_bytes(original_reviews[role])
 m.verify_launch(launchpin());ck('valid canonical three-role identities accepted',True)
 # Only manufactured binding functions are patched. The guarded finally/retention
 # implementation and byte hashing are the real proposed production functions.
 def verify_plan(digest):
  assert m.sha(m.HERE/'manifest.json')==digest
  for pin in json.loads((m.HERE/'external-pins.json').read_text()):m.verify(pin)
 def assert_source(repo):
  assert repo==m.SOURCE
  for pin in expected_source:m.verify(pin)
 m.verify_plan=verify_plan;m.assert_source=assert_source;m.source_files=lambda repo:sorted(repo.glob('*.dat'))
 counter=0
 def run(operation):
  global counter
  counter+=1;report=root/('guard'+str(counter)+'.json');pin=launchpin();result=m.guarded_source_freeze(expected,pin,node,tools,operation,report);return result,json.loads(report.read_text())
 result,record=run(lambda:'clean-result');ck('clean firstphase without planbinding retained',result=='clean-result'and record['passed']and not record['plan_binding_exists']and record['snapshot']['source_inventory']==expected_source)
 class PrimaryFailure(RuntimeError):pass
 error=PrimaryFailure('primary failure before plan-binding exists')
 def fail():raise error
 try:run(fail)
 except PrimaryFailure as seen:ck('clean primary exception identity preserved',seen is error and seen.first_phase_post_errors==[])
 else:raise AssertionError('primary lost')
 record=json.loads((root/('guard'+str(counter)+'.json')).read_text());ck('primary trace retained before planbinding',not record['passed']and not record['plan_binding_exists']and 'PrimaryFailure'in record['primary_traceback'])
 backups={p:p.read_bytes()for p in [*source,reference,node,Path(tools['cmake']),reviews['fixtures']]}
 def mutate():
  source[0].write_text('changed source');source[1].unlink();put(m.SOURCE/'added.dat','new namespace member');reference.write_text('changed external reference');node.write_text('changed node');Path(tools['cmake']).write_text('changed tool');reviews['fixtures'].write_text('changed review')
 def mutate_and_fail():mutate();raise error
 try:run(mutate_and_fail)
 except PrimaryFailure as seen:ck('mutation plus primary preserves original exception',seen is error)
 else:raise AssertionError('primary mutation lost')
 record=json.loads((root/('guard'+str(counter)+'.json')).read_text());labels=[x['guard']for x in record['post_guard_errors']]
 for name in ['plan/reference authorities','declared source contract','launch/review/installation authorities','full source/reference inventory',*['pin '+str(p)for p in backups]]:ck('all final guards retained '+name,name in labels)
 ck('primary and allposterrors durably together',not record['passed']and 'PrimaryFailure'in record['primary_traceback']and len(record['post_guard_errors'])>=10)
 for p,data in backups.items():p.write_bytes(data)
 (m.SOURCE/'added.dat').unlink()
 def mutate_only():source[0].write_text('success but bad poststate');return 'not accepted'
 try:run(mutate_only)
 except RuntimeError as seen:ck('postguard failure rejects successful operation','first-phase binding failure'in str(seen))
 else:raise AssertionError('postguard success accepted')
 record=json.loads((root/('guard'+str(counter)+'.json')).read_text());ck('postonly errors retained without invented primary',record['primary_error']is None and not record['passed']and record['post_guard_errors'])
 source[0].write_bytes(backups[source[0]])
 # Report I/O failure cannot mask an already raised primary. Original observer
 # would retain the stderr fallback; here it is captured explicitly as a fixture.
 report=root/'existing-report.json';report.write_text('retain-original');stderr=io.StringIO()
 with redirect_stderr(stderr):
  try:m.guarded_source_freeze(expected,launchpin(),node,tools,fail,report)
  except PrimaryFailure as seen:ck('report I/O failure preserves primary',seen is error and any(x['guard']=='durable first-phase report'for x in seen.first_phase_post_errors))
 ck('existing report never overwritten',report.read_text()=='retain-original')
 fallback=json.loads(stderr.getvalue());ck('I/O fallback retains primary plusfailure',not fallback['passed']and 'PrimaryFailure'in fallback['primary_traceback']and fallback['post_guard_errors'][-1]['guard']=='durable first-phase report')
# Outer observer route tested with inert modules only; no original observer call.
spec=importlib.util.spec_from_file_location('_v3_commands',O/'commands.py');commands=importlib.util.module_from_spec(spec);spec.loader.exec_module(commands)
calls=[];observer=SimpleNamespace(observe=lambda *a,**kw:(calls.append((a,kw))or SimpleNamespace(returncode=0)))
collector=SimpleNamespace(sys=sys,pin=lambda p:{'path':str(p)},guarded_source_freeze=lambda *a:a[4]())
def fake_spec(name,path):return SimpleNamespace(name=name,loader=SimpleNamespace(exec_module=lambda m:None))
with patch.object(commands.importlib.util,'spec_from_file_location',side_effect=fake_spec),patch.object(commands.importlib.util,'module_from_spec',side_effect=lambda spec:observer if spec.name=='_original_observer'else collector):
 commands.observe_source_freeze(str(Path(sys.executable).resolve()),'/absolute/node',{x:'/absolute/'+x for x in ('cmake','native_cxx','emcmake','emcc')},'frozen-manifest','/absolute/launch.json')
args,kwargs=calls[0];ck('outer observer firstphase exact1800closedenv',kwargs['timeout']==1800 and kwargs['env']==commands.closed_environment())
ck('outer receipt sibling not actual child',args[2].parent==commands.ACTUAL.parent and args[2]!=commands.ACTUAL and not args[2].is_relative_to(commands.ACTUAL))
ck('sourcefreeze original argv route unchanged',args[0][2:4]==[str(commands.HERE/'collector.py'),'source-freeze'])
ck('original observer identity unchanged',commands.OBSERVER_SHA=='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e')
(O/'adversarial-checks.json').write_text(json.dumps({'status':'PASS','checks':len(checks),'labels':[label.replace(str(root),'<fixture-root>')for label in checks],'actual_source_freeze_observer_tool_or_material_calls':0,'tiny_fixtures_removed':True},indent=2)+'\n');print(json.dumps({'status':'PASS','adversarial_checks':len(checks)}))
