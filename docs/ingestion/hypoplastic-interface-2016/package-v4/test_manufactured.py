"""Manufactured source fixtures and inert Python child only. No actual package/engine."""
from pathlib import Path
import hashlib,json,os,sys,stat
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
from freeze_inputs import sha,copied_members,asset_members
from owned_process import run_owned
from unittest.mock import patch
ROOT=HERE/'manufactured-fixture';assert not ROOT.exists();ROOT.mkdir()
checks=[]
def check(name,condition):assert condition,name;checks.append(name)
def rejects(name,fn):
 try:fn()
 except (AssertionError,OSError):checks.append(name);return
 raise AssertionError('Expected rejection: '+name)
tracked={}
for name,data in [('models/a.json',b'{"fixture":"model"}\n'),('schemas/a.json',b'{"fixture":"schema"}\n')]:
 q=ROOT/name;q.parent.mkdir(exist_ok=True);q.write_bytes(data);tracked[name]={'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),'mode':'100644'}
check('B1 sha string filename equals Path',sha(str(ROOT/'models/a.json'))==sha(ROOT/'models/a.json'))
check('B1 sha __file__ string succeeds',len(sha(__file__))==64)
baseline=copied_members(ROOT,tracked);check('B2 baseline exact target-tree membership',len(baseline)==4)
q=ROOT/'models/added.json';q.write_text('{}');rejects('B2 added untracked definition rejected at freeze',lambda:copied_members(ROOT,tracked));check('B2 added definition differs at wrapper guard',copied_members(ROOT)!=baseline)
launched=[]
with (HERE/'fixture-stdout.log').open('xb') as out,(HERE/'fixture-stderr.log').open('xb') as err:
 def guard():assert copied_members(ROOT)==baseline
 with patch('owned_process.subprocess.Popen',side_effect=lambda *a,**k:launched.append(True)):
  rejects('B2 changed membership rejected before Popen',lambda:run_owned([sys.executable,'-c','pass'],ROOT,os.environ.copy(),out,err,guard,lambda *a:None))
check('B2 rejected preflight launches no process',not launched);q.unlink()
q=ROOT/'schemas/a.json';saved=q.read_bytes();q.unlink();rejects('B2 removed schema rejected',lambda:copied_members(ROOT,tracked));q.write_bytes(saved)
q.write_bytes(b'changed');rejects('B2 altered schema content rejected',lambda:copied_members(ROOT,tracked));q.write_bytes(saved)
mode=q.stat().st_mode;os.chmod(q,stat.S_IMODE(mode)|stat.S_IXUSR);rejects('B2 executable mode differs from Git tree rejected',lambda:copied_members(ROOT,tracked));os.chmod(q,stat.S_IMODE(mode))
q=ROOT/'models/empty';q.mkdir();rejects('B2 extra empty directory rejected',lambda:copied_members(ROOT,tracked));q.rmdir()
q=ROOT/'schemas/link';q.symlink_to(ROOT/'models/a.json');rejects('B2 symlink member rejected',lambda:copied_members(ROOT,tracked));q.unlink()
check('B2 recovered fixture exact baseline',copied_members(ROOT,tracked)==baseline)
assets=ROOT/'assets';assets.mkdir();(assets/'engine.wasm').write_bytes(b'inert not a module');frozen_assets=asset_members(assets);(assets/'new.json').write_text('{}');check('B2 qualified asset added membership detected',asset_members(assets)!=frozen_assets);(assets/'new.json').unlink()
child_record={}
class InjectedError(Exception):pass
try:
 with (HERE/'child-stdout.log').open('xb') as out,(HERE/'child-stderr.log').open('xb') as err:
  def started(child,ownership):
   child_record.update(child=child,ownership=ownership);raise InjectedError('manufactured wrapper exception after Popen')
  run_owned([sys.executable,'-c','import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)'],ROOT,os.environ.copy(),out,err,lambda:None,started)
except InjectedError as error:
 cleanup=error.owned_process_cleanup;check('B3 exception terminates own group and reaps leader',cleanup['status']=='owned-group-terminated-and-leader-reaped' and child_record['child'].returncode is not None)
 check('B3 own new session/group captured',len(set(child_record['ownership'].values()))==1)
 try:os.kill(child_record['child'].pid,0)
 except ProcessLookupError:checks.append('B3 reaped PID no longer exists')
 else:raise AssertionError('Own child still exists')
check('B3 synthetic log handles closed',out.closed and err.closed)
# Reproduce exact unchanged v3 reviewed manifest rather than changing the failure.
v3=HERE.parent/'package-v3';manifest=json.loads((v3/'manifest.json').read_text());check('v3 reviewed manifest preserved',sha(v3/'manifest.json')=='239bb2307146255172061a74e434ec4ec286a6a557126640fb32c9d580796ef1');check('v3 all manifest files preserved',all(sha(v3/n)==h for n,h in manifest['files'].items()))
report={'status':'passed-manufactured-source-and-inert-child-checks','checks':checks,'count':len(checks),'inert_child_cleanup':cleanup,'actual_freeze_provision_package_compiler_material_browser_gitwrite_calls':0}
(HERE/'manufactured-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
