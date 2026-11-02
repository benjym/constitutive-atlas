"""Source fixtures + fake Popen/group snapshots only. No real child or signals."""
from pathlib import Path
import hashlib,json,os,sys,stat,io,signal
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
from freeze_inputs import sha,copied_members,asset_members
import owned_process as lifecycle
from unittest.mock import patch
ROOT=HERE/'source-fake-fixture-v2';assert not ROOT.exists();ROOT.mkdir();checks=[]
def check(name,ok):assert ok,name;checks.append(name)
def rejects(name,fn):
 try:fn()
 except (AssertionError,OSError):checks.append(name);return
 raise AssertionError('Expected rejection: '+name)
tracked={}
for name,data in [('models/a.json',b'{"fixture":"model"}\n'),('schemas/a.json',b'{"fixture":"schema"}\n')]:
 q=ROOT/name;q.parent.mkdir(exist_ok=True);q.write_bytes(data);tracked[name]={'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),'mode':'100644'}
check('B1 sha string equals Path',sha(str(ROOT/'models/a.json'))==sha(ROOT/'models/a.json'));check('B1 sha __file__ string succeeds',len(sha(__file__))==64)
baseline=copied_members(ROOT,tracked);check('B2 exact target-tree baseline',len(baseline)==4)
q=ROOT/'models/added.json';q.write_text('{}');rejects('B2 added untracked model rejected at freeze',lambda:copied_members(ROOT,tracked));check('B2 added model detected by pre/post guard',copied_members(ROOT)!=baseline)
started=[]
with patch('owned_process.subprocess.Popen',side_effect=lambda *a,**k:started.append(True)):
 def guard():assert copied_members(ROOT)==baseline
 rejects('B2 extra member rejected before launch',lambda:lifecycle.run_owned(['INERT-NOT-RUN'],ROOT,{},io.BytesIO(),io.BytesIO(),guard,lambda *a:None))
check('B2 no Popen on rejected preflight',not started);q.unlink()
q=ROOT/'schemas/a.json';saved=q.read_bytes();q.unlink();rejects('B2 removed schema rejected',lambda:copied_members(ROOT,tracked));q.write_bytes(saved)
q.write_bytes(b'changed');rejects('B2 changed schema rejected',lambda:copied_members(ROOT,tracked));q.write_bytes(saved)
mode=stat.S_IMODE(q.stat().st_mode);os.chmod(q,mode|stat.S_IXUSR);rejects('B2 Git executable-mode mismatch rejected',lambda:copied_members(ROOT,tracked));os.chmod(q,mode)
q=ROOT/'models/empty';q.mkdir();rejects('B2 empty extra directory rejected',lambda:copied_members(ROOT,tracked));q.rmdir()
q=ROOT/'schemas/link';q.symlink_to(ROOT/'models/a.json');rejects('B2 symlink rejected',lambda:copied_members(ROOT,tracked));q.unlink()
check('B2 baseline recovery exact',copied_members(ROOT,tracked)==baseline)
assets=ROOT/'assets';assets.mkdir();(assets/'engine.wasm').write_bytes(b'inert nonmodule');frozen=asset_members(assets);(assets/'added.json').write_text('{}');check('B2 recursive asset member addition detected',asset_members(assets)!=frozen)
class Fault(Exception):pass
class FakeChild:
 pid=424242
 returncode=None
 def wait(self,timeout=None):self.returncode=-15;events.append('reap');return self.returncode
results=[]
for scenario in ['already-terminal','surviving-descendant','ownership-mismatch']:
 events=[];child=FakeChild();state={'killed':False}
 def snapshot(pgid):
  assert pgid==child.pid
  if scenario=='already-terminal' or state['killed']:return [{'pid':child.pid,'state':'Z'},{'pid':child.pid+1,'state':'Z'}]
  return [{'pid':child.pid,'state':'Z'},{'pid':child.pid+1,'state':'S'}]
 def killpg(pgid,sig):assert pgid==child.pid;events.append(sig.name);state['killed']=sig==signal.SIGKILL
 def fault(c,ownership):raise Fault('manufactured exception after fake Popen')
 with patch.object(lifecycle.subprocess,'Popen',return_value=child) as popen,patch.object(lifecycle.os,'getpgid',return_value=child.pid),patch.object(lifecycle.os,'getsid',return_value=child.pid if scenario!='ownership-mismatch' else child.pid+9),patch.object(lifecycle.os,'killpg',side_effect=killpg),patch.object(lifecycle.time,'monotonic',side_effect=iter(range(50))),patch.object(lifecycle.time,'sleep'):
  try:lifecycle.run_owned(['FAKE-NOT-EXECUTED'],ROOT,{},io.BytesIO(),io.BytesIO(),lambda:None,fault,snapshot=snapshot)
  except (Fault,AssertionError) as e:cleanup=e.owned_process_cleanup
  else:raise AssertionError('Expected injected fault')
  check('B3 '+scenario+' starts dedicated session',popen.call_args.kwargs['start_new_session'] is True)
 if scenario=='already-terminal':check('B3 terminal whole group reaped without unnecessary signals',events==['reap'])
 elif scenario=='surviving-descendant':check('B3 surviving descendant triggers verified TERM KILL then reap',events==['SIGTERM','SIGKILL','reap'])
 else:check('B3 foreign session never signalled and blocks resumption',events==['reap'] and cleanup['status']=='cleanup-incomplete-block-resumption')
 results.append({'scenario':scenario,'events':events,'receipt':cleanup})
v3=HERE.parent/'package-v3';m=json.loads((v3/'manifest.json').read_text());check('v3 immutable reviewed manifest',sha(v3/'manifest.json')=='239bb2307146255172061a74e434ec4ec286a6a557126640fb32c9d580796ef1');check('v3 all pinned files intact',all(sha(v3/n)==h for n,h in m['files'].items()))
report={'status':'passed-source-fixtures-fake-child-only','count':len(checks),'checks':checks,'fake_lifecycle_results':results,'real_child_signal_ps_freeze_provision_package_material_browser_gitwrite_calls':0}
(HERE/'source-fake-results-v2.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
