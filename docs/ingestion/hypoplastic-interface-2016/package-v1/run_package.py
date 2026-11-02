"""Coordinator-owned serial standard package execution with closed logs and frozen inputs."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
HERE=Path(__file__).resolve().parent
plan=json.loads((HERE/'plan.json').read_text());root=Path(plan['cwd']);revision=sys.argv[1]
assert len(revision)==40 and all(c in '0123456789abcdef' for c in revision)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
inventory=json.loads((HERE.parent/'integration-v1/commit-preparation-v1/inventory-v2.json').read_text())
pins={e['path']:e['sha256'] for e in inventory['entries']}
repo=Path('/Users/bmar5496/code/constitutive-atlas')
def git(*args):return subprocess.check_output(['git',*args],cwd=repo)
assert git('rev-parse',revision+'^{commit}').decode().strip()==revision
assert git('rev-parse',revision+'^').decode().strip()==inventory['parent']
for entry in inventory['entries']:
 assert git('rev-parse',revision+':'+entry['path']).decode().strip()==entry['git_blob_sha1'],('Commit blob differs',entry['path'])
def verify():
 for p,h in pins.items():assert sha(root/p)==h,('Source changed',p)
verify();env=os.environ.copy();env.update(GITHUB_SHA=revision,PYTHONDONTWRITEBYTECODE='1')
record=dict(argv=plan['argv'],cwd=str(root),source_revision=revision,start=time.time(),source_pins=pins,status='running')
(HERE/'run.json').write_text(json.dumps(record,indent=2)+'\n')
with (HERE/'stdout.log').open('wb') as out,(HERE/'stderr.log').open('wb') as err:
 child=subprocess.Popen(plan['argv'],cwd=root,env=env,stdout=out,stderr=err);record['pid']=child.pid;(HERE/'run.json').write_text(json.dumps(record,indent=2)+'\n');code=child.wait()
record.update(exit_code=code,end=time.time(),status='passed' if code==0 else 'failed-retained',logs={n:sha(HERE/n) for n in ['stdout.log','stderr.log']})
try:verify();record['source_post_unchanged']=True
finally:(HERE/'run.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps({k:v for k,v in record.items() if k not in ['source_pins']},indent=2));sys.exit(code)
