"""Create only the reviewed evidence repair on its own ref and alternate index."""
import hashlib,json,os,subprocess,tempfile,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def git(*args,data=None,env=None):return subprocess.check_output(['git',*args],input=data,cwd=ROOT,env=env)
def main():
 planbytes=(HERE/'commit-plan.json').read_bytes();plan=json.loads(planbytes)
 assert git('rev-parse','HEAD').decode().strip()==plan['root_head']
 assert sha((ROOT/'.git/index').read_bytes())==plan['root_index_sha256']
 content=[]
 for row in plan['entries']:
  p=row['path'];assert not Path(p).is_absolute() and '..' not in Path(p).parts and '\n' not in p and '\t' not in p
  b=(ROOT/p).read_bytes();assert sha(b)==row['sha256'] and len(b)==row['bytes'];content.append((p,b))
 content.append(((HERE/'commit-plan.json').relative_to(ROOT).as_posix(),planbytes))
 assert len({p for p,b in content})==len(content)
 assert set(plan['deletions'])=={r['path'] for r in json.loads((HERE/'inventory.json').read_text())['files']}
 if '--execute' not in sys.argv:
  print(json.dumps(dict(status='preflight passed',additions=len(content),deletions=len(plan['deletions']))));return
 assert subprocess.run(['git','show-ref','--verify','--quiet',plan['ref']],cwd=ROOT).returncode==1
 fd,index=tempfile.mkstemp(prefix='atlas-interface2016-image-index-',dir='/private/tmp');os.close(fd);os.unlink(index)
 env=os.environ.copy();env['GIT_INDEX_FILE']=index
 try:
  git('read-tree',plan['parent'],env=env);payload=bytearray()
  for p,b in content:
   oid=git('hash-object','-w','--stdin',data=b,env=env).decode().strip();payload.extend(f'100644 {oid}\t{p}\0'.encode())
  for p in plan['deletions']:payload.extend(f'0 {"0"*40}\t{p}\0'.encode())
  git('update-index','-z','--index-info',data=bytes(payload),env=env)
  actual=set(git('diff','--cached','--no-renames','--name-only','-z',plan['parent'],env=env).decode().strip('\0').split('\0'))
  assert actual==set(plan['deletions'])|{p for p,b in content}
  tree=git('write-tree',env=env).decode().strip()
  commit=git('commit-tree',tree,'-p',plan['parent'],data=b'Correct JPEG browser evidence names and preserve immutable originals\n',env=env).decode().strip()
  assert git('rev-parse','HEAD').decode().strip()==plan['root_head'] and sha((ROOT/'.git/index').read_bytes())==plan['root_index_sha256']
  git('update-ref',plan['ref'],commit,'0'*40)
  result=dict(commit=commit,tree=tree,parent=plan['parent'],ref=plan['ref'],plan_sha256=sha(planbytes),root_head_unchanged=True,root_index_unchanged=True,pushed=False)
  (HERE/'actual-commit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
 finally:
  if Path(index).exists():Path(index).unlink()
if __name__=='__main__':main()
