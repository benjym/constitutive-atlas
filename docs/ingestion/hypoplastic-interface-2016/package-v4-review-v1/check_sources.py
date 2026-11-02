"""Independent source/temporary-file/inert fake-process regression review."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,signal,stat,sys,tempfile
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parent/'package-v4'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def module(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def main():
 assert sha(P/'manifest.json')=='59808fdc34ecfdbe257e7fac7ba0f701bf080770cafd0dbc6c081fba735e793e'
 manifest=json.loads((P/'manifest.json').read_text());assert all(sha(P/n)==h for n,h in manifest['files'].items())
 F=module('v4_freeze_review',P/'freeze_inputs.py');L=module('v4_lifecycle_review',P/'owned_process.py');checks=[]
 def check(n,v):assert v,n;checks.append(n)
 def rejects(n,f):
  try:f()
  except (AssertionError,OSError):checks.append(n);return
  raise AssertionError('Unexpected acceptance: '+n)
 for n in ['freeze_inputs.py','owned_process.py','run_package.py']:ast.parse((P/n).read_text())
 check('B1 string/Path equality',F.sha(str(P/'run_package.py'))==F.sha(P/'run_package.py'))
 v3=json.loads((HERE.parent/'package-v3/plan.json').read_text());v4=json.loads((P/'plan.json').read_text());old=list(v3['argv']);old[old.index('--output')+1]=old[old.index('--output')+1].replace('site-v3','site-v4')
 check('exact full argv unchanged except new output',v4['argv']==old);check('same cwd and ordered parents',v3['cwd']==v4['cwd'] and v3['parents']==v4['parents'])
 with tempfile.TemporaryDirectory(dir=HERE) as tmp:
  root=Path(tmp);q=root/'models/a.json';q.parent.mkdir();q.write_text('{}');q.chmod(0o644)
  tracked={'models/a.json':{'git_blob':hashlib.sha1(b'blob 2\0{}').hexdigest(),'mode':'100644'}};baseline=F.copied_members(root,tracked)
  for n in ['models/extra.json','schemas/extra.json','catalogue/evidence/extra.json']:
   extra=root/n;extra.parent.mkdir(parents=True,exist_ok=True);extra.write_text('{}')
   rejects('B2 freeze rejects '+n,lambda:F.copied_members(root,tracked));check('B2 pre/post detects '+n,F.copied_members(root)!=baseline);extra.unlink()
   while extra.parent!=root and extra.parent!=q.parent:
    parent=extra.parent
    try:parent.rmdir()
    except OSError:break
    extra=parent
  q.chmod(0o755);rejects('B2 rejects changed Git executable mode',lambda:F.copied_members(root,tracked));q.chmod(0o644)
  check('B2 restoration exact',F.copied_members(root,tracked)==baseline)
  (root/'models/empty').mkdir();rejects('B2 rejects empty-directory addition',lambda:F.copied_members(root,tracked));(root/'models/empty').rmdir()
  (root/'models/link').symlink_to('a.json');rejects('B2 rejects symlink',lambda:F.copied_members(root,tracked));(root/'models/link').unlink()
  assets=root/'assets';assets.mkdir();(assets/'x.json').write_text('{}');a=F.asset_members(assets);(assets/'y.json').write_text('{}');check('asset added membership detected',F.asset_members(assets)!=a)
 scenarios=[]
 class Fault(Exception):pass
 for scenario in ['terminal','descendant','visibility-denied','foreign-session','kill-denied']:
  events=[];state={'killed':False}
  class Child:
   pid=4444
   def wait(self,timeout=None):events.append('reap');return -15
  child=Child()
  def snapshot(pgid):
   if scenario=='visibility-denied':raise PermissionError('synthetic visibility refusal')
   return [{'pid':4444,'state':'Z'}] if scenario=='terminal' or state['killed'] else [{'pid':4444,'state':'Z'},{'pid':4445,'state':'S'}]
  def killpg(pgid,sig):
   assert pgid==4444;events.append(sig.name)
   if scenario=='kill-denied' and sig==signal.SIGKILL:raise PermissionError('synthetic signal refusal')
   if sig==signal.SIGKILL:state['killed']=True
  def started(*a):raise Fault('synthetic wrapper interruption')
  with patch.object(L.subprocess,'Popen',return_value=child) as popen,patch.object(L.os,'getpgid',return_value=4444),patch.object(L.os,'getsid',return_value=9999 if scenario=='foreign-session' else 4444),patch.object(L.os,'killpg',side_effect=killpg),patch.object(L.time,'monotonic',side_effect=iter(range(100))),patch.object(L.time,'sleep'):
   try:L.run_owned(['INERT'],HERE,{},None,None,lambda:None,started,snapshot=snapshot)
   except (Fault,AssertionError) as e:receipt=e.owned_process_cleanup
   else:raise AssertionError('No injected exception')
   check(scenario+' owns new session',popen.call_args.kwargs['start_new_session'] is True)
  if scenario=='terminal':check('terminal group reaped without signal',events==['reap'])
  elif scenario=='descendant':check('live descendant TERM KILL then reap',events==['SIGTERM','SIGKILL','reap'])
  else:
   check(scenario+' blocks resumption',receipt['status']=='cleanup-incomplete-block-resumption')
   if scenario in ['visibility-denied','foreign-session']:check(scenario+' sends no signal',events==['reap'])
  scenarios.append({'scenario':scenario,'events':events,'cleanup':receipt})
 oldmanifest=json.loads((HERE.parent/'package-v3/manifest.json').read_text());check('v3 unchanged',sha(HERE.parent/'package-v3/manifest.json')=='239bb2307146255172061a74e434ec4ec286a6a557126640fb32c9d580796ef1' and all(sha(HERE.parent/'package-v3'/n)==h for n,h in oldmanifest['files'].items()))
 report={'status':'passed-independent-prospective-source-fake-regression','manifest_sha256':sha(P/'manifest.json'),'members_checked':len(manifest['files']),'checks':checks,'count':len(checks),'lifecycle_fake_results':scenarios,'actual_child_ps_signal_freeze_package_engine_browser_remote_calls':0}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
