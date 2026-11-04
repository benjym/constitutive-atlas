from pathlib import Path
import ast,hashlib,json,tempfile,types,sys,contextlib,io,subprocess
from unittest.mock import patch
O=Path(__file__).resolve().parent;N=O.parents[1];A=N/'recorded74-actual-plan-v1';P=N/'rate-restoration-qualification-plan-v3';checks=[]
def h(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ok(x,n):assert x,n;checks.append(n)
ok(h(A/'manifest.json')=='b5c695f05c55a96c1e97e3606c32eb8a62b8b1d04b841aeb1cb392709f33e9cf','exact parent proposal')
for r in json.loads((A/'manifest.json').read_text())['files']:ok(h(A/r['path'])==r['sha256']and(A/r['path']).stat().st_size==r['bytes'],'frozen '+r['path'])
ok(h(P/'manifest.json')=='4b3a8592279b7a99a18bd0a168bf95a78ee7f95f9dbc0efe1ffcc6417fac5812','exact acceptedC3 delegated manifest')
for r in json.loads((P/'manifest.json').read_text())['files']:ok(h(P/r['path'])==r['sha256'],'unmodified delegate '+r['path'])
s=(A/'launch.py').read_text();tree=ast.parse(s)
attrs=[n.targets[0].attr for n in tree.body if isinstance(n,ast.Assign)and len(n.targets)==1 and isinstance(n.targets[0],ast.Attribute)and isinstance(n.targets[0].value,ast.Name)and n.targets[0].value.id=='c']
ok(attrs==['phase_argv','closed_environment'],'only runtime argv/env accessors assigned')
ok("result=c.observe_phase(pre,phase,MANIFEST)"in s,'delegates unmodified guardedobserver path')
ok("'\u005cnOK\u005cn'"in s and "'skipped='not in result.stderr"in s,'strict original74 OK zero skips checks')
head,body=s.split("pre=json.loads",1);body='pre=json.loads'+body
for scenario,phase in [('legacy-positive','legacy-build'),('recorded-positive','recorded74'),('prior-nonzero','legacy-build'),('prior-unreaped','legacy-build'),('active-compiled','legacy-build'),('legacy-failed','recorded74'),('artifact-drift','recorded74'),('wrong-74count','recorded74'),('skipped-tests','recorded74')]:
 with tempfile.TemporaryDirectory(dir=O,prefix='inert-')as d:
  t=Path(d);root=t/'repo';fakeN=root/'docs/delivery/N';fakeN.mkdir(parents=True);(root/'.local/retained-evidence').mkdir(parents=True);actual=t/'actual';actual.mkdir();work=t/'work';(work/'native').mkdir(parents=True);source=t/'source';source.mkdir()
  prior=actual/('outer-extra-pair'if phase=='legacy-build'else'outer-legacy-build');prior.mkdir();(prior/'receipt.json').write_text(json.dumps({'returncode':1 if scenario=='prior-nonzero'else 0,'mandatory_reap':False if scenario=='prior-unreaped'else True}))
  (actual/'source-freeze.json').write_text(json.dumps({'python':{'path':'/absolute/inert-python'}}));legacy=actual/'recorded-legacy-build';legacy.mkdir();binary=work/'native/atlas_recorded_legacy_solver';binary.write_text('INERT NEVER EXECUTE');sha=h(binary)
  (legacy/'receipt.json').write_text(json.dumps({'status':'failed'if scenario=='legacy-failed'else'passed','post_bindings_unchanged':True,'historical_catalogue':'1cac1ed6b2a284b561ed6fed00dd751e384748ea5e5f9d14467e410dc18a218c','artifact':{'path':str(binary),'sha256':'0'*64 if scenario=='artifact-drift'else sha}}))
  env={'__file__':str(A/'launch.py'),'__name__':'inert_review'};exec(compile(head,str(A/'launch.py'),'exec'),env);c=env['c'];c.ACTUAL=actual;c.WORK=work;c.SOURCE=source;original_env={'CLOSED':'unchanged'};c.closed_environment=lambda:dict(original_env);c.phase_argv=lambda pre,manifest:{'old-phase':['inert-old']};calls=[]
  def observe(pre,phase,manifest):
   calls.append({'phase':phase,'manifest':manifest,'argv':c.phase_argv(pre,manifest),'env':c.closed_environment()})
   stderr='Ran 73 tests in 1s\n\nOK\n'if scenario=='wrong-74count'else'Ran 74 tests in 1s\n\nOK (skipped=1)\n'if scenario=='skipped-tests'else'Ran 74 tests in 1s\n\nOK\n'
   return types.SimpleNamespace(returncode=0,stderr=stderr,receipt={'mandatory_reap':True,'elapsed_seconds':1})
  c.observe_phase=observe;env['N']=fakeN
  with patch.object(sys,'argv',[str(A/'launch.py'),phase]),patch.object(subprocess,'check_output',return_value='123 1 /inert/atlas_solver\n'if scenario=='active-compiled'else'123 1 /inert/other-process\n'),patch.object(env['shutil'],'disk_usage',return_value=types.SimpleNamespace(free=123456)),contextlib.redirect_stdout(io.StringIO()):
   try:exec(compile(body,str(A/'launch.py'),'exec'),env)
   except SystemExit as e:ok(e.code==0 and scenario.endswith('positive'),'only positive exits0 '+scenario)
   except AssertionError:ok(not scenario.endswith('positive'),'reject '+scenario)
   else:raise AssertionError('missing terminal')
  if scenario.endswith('positive'):
   call=calls[0];ok(call['manifest']=='4b3a8592279b7a99a18bd0a168bf95a78ee7f95f9dbc0efe1ffcc6417fac5812'and call['argv']['old-phase']==['inert-old'],'delegate retains manifest and old phases '+scenario)
   if phase=='recorded74':ok(len(call['argv']['recorded74'])==13 and call['argv']['recorded74'][1:4]==['-B','-m','unittest']and call['env']=={**original_env,'ATLAS_RECORDED_SOLVER':str(work/'native/atlas_solver'),'ATLAS_RECORDED_LEGACY_SOLVER':str(binary),'ATLAS_RECORDED_LEGACY_SHA256':sha},'exact8modules and only3env additions')
   else:ok(call['env']==original_env and call['argv']['legacy-build'][-2:]==['--output',str(legacy)],'legacy helper exact args closedenv')
  elif scenario not in ['wrong-74count','skipped-tests']:ok(not calls or scenario in ['legacy-failed','artifact-drift'],'invalid preconditions prevent observer dispatch '+scenario)
(O/'checks.json').write_text(json.dumps({'passed':True,'count':len(checks),'checks':checks,'actual_compiled_browser_material_network':False,'fixtures_removed':True},indent=2)+'\n');print(json.dumps({'passed':True,'count':len(checks)}))
