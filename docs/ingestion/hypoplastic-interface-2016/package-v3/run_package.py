"""Coordinator-only standard full package wrapper. Never call without fresh slot handoff."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
from freeze_inputs import sha,git,parents,tree
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--revision',required=True);p.add_argument('--preflight-only',action='store_true');a=p.parse_args()
plan=json.loads((HERE/'plan.json').read_text());freeze=json.loads((HERE/'source-freeze.json').read_text());root=Path(plan['cwd']);output=Path(plan['argv'][plan['argv'].index('--output')+1]);assert len(a.revision)==40 and all(c in '0123456789abcdef' for c in a.revision)
assert freeze['revision']==a.revision and freeze['parents']==parents(a.revision)==plan['parents'];assert freeze['cwd']==str(root);assert sha(HERE/'plan.json')==freeze['plan_sha256'];assert sha(__file__)==freeze['wrapper_sha256'];assert sha(HERE/'freeze_inputs.py')==freeze['freeze_script_sha256'];freeze_digest=sha(HERE/'source-freeze.json');actual_tree=tree(a.revision)
for n,item in freeze['source'].items():assert actual_tree[n]=={k:item[k] for k in ['git_blob','mode']},('Committed source changed',n)
def verify():
 assert sha(HERE/'source-freeze.json')==freeze_digest,'Freeze changed'
 assert sha(HERE/'plan.json')==freeze['plan_sha256'],'Plan changed'
 assert sha(__file__)==freeze['wrapper_sha256'],'Wrapper changed'
 assert sha(HERE/'freeze_inputs.py')==freeze['freeze_script_sha256'],'Freeze helper changed'
 for n,item in freeze['source'].items():assert sha(root/n)==item['sha256'],('Source changed',n)
 for n,item in freeze['qualified_assets_and_ignored_witness'].items():assert sha(Path(n))==item['sha256'],('Qualified asset/witness changed',n)
 for n in freeze['deleted_paths']:assert not (root/n).exists(),('Deleted source path appeared',n)
verify()
if a.preflight_only:print('Source/commit/parents/plan/assets preflight passed; no package launched');sys.exit(0)
assert not output.exists() and not output.is_symlink(),'Use distinct output; retain prior failures'
for n in ['run.json','stdout.log','stderr.log']:assert not (HERE/n).exists(),'Retain prior observation; use distinct packet for retry'
record={'argv':plan['argv'],'cwd':str(root),'source_revision':a.revision,'parents':plan['parents'],'freeze_sha256':sha(HERE/'source-freeze.json'),'plan_sha256':sha(HERE/'plan.json'),'wrapper_sha256':sha(__file__),'status':'running','start':time.time()}
def save():(HERE/'run.json').write_text(json.dumps(record,indent=2)+'\n')
save();env=os.environ.copy();env.update(GITHUB_SHA=a.revision,PYTHONDONTWRITEBYTECODE='1');code=1
try:
 with (HERE/'stdout.log').open('xb') as out,(HERE/'stderr.log').open('xb') as err:
  child=subprocess.Popen(plan['argv'],cwd=root,env=env,stdout=out,stderr=err);record['pid']=child.pid;save();code=child.wait()
 record['exit_code']=code
 try:verify();record['source_and_assets_post_unchanged']=True
 except Exception as e:record['post_guard_error']=str(e);record['source_and_assets_post_unchanged']=False;code=1
 record['status']='passed' if code==0 else 'failed-retained'
except BaseException as e:
 record.update(status='failed-retained',wrapper_error=repr(e));raise
finally:
 record['end']=time.time();record['logs']={n:sha(HERE/n) for n in ['stdout.log','stderr.log'] if (HERE/n).exists()};save()
print(json.dumps(record,indent=2));sys.exit(code)
