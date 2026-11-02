"""Project exact new commit additions into an owned APFS clone by atomic replacement."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,tempfile,time
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
SOURCE=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v3')
OLD='dcc645785faa3c83d791fdad92e7f3a20cab9721'
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
def sha(data):return hashlib.sha256(data).hexdigest()
def main():
 revision=sys.argv[1]
 assert len(revision)==40 and git('rev-parse',revision+'^{commit}').decode().strip()==revision
 assembly=HERE.parent/'publication-assembly-v1'
 receipt=json.loads((assembly/'actual-commit.json').read_text())
 plan=json.loads((assembly/'plan.json').read_text())
 assert receipt['commit']==revision and receipt['status']=='local-only publication composition committed'
 assert receipt['plan_sha256']==sha((assembly/'plan.json').read_bytes())
 assert git('show','-s','--format=%P',revision).decode().strip().split()==[plan['published'],plan['own']]
 clone=json.loads((HERE/'clone.json').read_text())
 assert clone['status']=='copied' and clone['destination']==str(SOURCE)
 raw=git('diff-tree','-r','--no-commit-id','--name-status','-z',OLD,revision).decode().strip('\0').split('\0')
 changes=[]
 for i in range(0,len(raw),2):
  status,name=raw[i:i+2]
  assert status in ('A','M') and not Path(name).is_absolute() and '..' not in Path(name).parts,(status,name)
  mode=git('ls-tree',revision,'--',name).decode().split()[0]
  assert mode in ('100644','100755')
  data=git('show',revision+':'+name)
  changes.append((name,mode,data))
 assert SOURCE.is_dir() and not (HERE/'installation.json').exists()
 # Validate every preimage before the first mutation. New evidence may already
 # exist in the old physical projection; only exact successor bytes are allowed.
 for name,mode,data in changes:
  target=SOURCE/name
  old=subprocess.run(['git','cat-file','-e',OLD+':'+name],cwd=ROOT,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
  assert not target.is_symlink(),name
  if old.returncode==0:
   assert target.is_file() and sha(target.read_bytes())==sha(git('show',OLD+':'+name)),('Clone preimage differs',name)
  elif target.exists():
   assert target.is_file() and sha(target.read_bytes())==sha(data),('Unexpected preexisting addition',name)
 # Case aliases must have identical bytes on this case-insensitive source volume.
 aliases={}
 for name,mode,data in changes:
  key=name.casefold()
  if key in aliases:assert aliases[key]==(mode,sha(data)),name
  aliases[key]=(mode,sha(data))
 record=dict(revision=revision,clone_base=OLD,start=time.time(),method='new tempfile + atomic replace; no in-place write to inherited hardlinks',files=[])
 for name,mode,data in changes:
  target=SOURCE/name;target.parent.mkdir(parents=True,exist_ok=True)
  old_sha=sha(target.read_bytes()) if target.exists() else None
  fd,tmp=tempfile.mkstemp(prefix='.interface2016-atomic-',dir=target.parent)
  try:
   with os.fdopen(fd,'wb') as f:f.write(data)
   os.chmod(tmp,0o755 if mode=='100755' else 0o644)
   os.replace(tmp,target)
  finally:
   if os.path.exists(tmp):os.unlink(tmp)
  assert sha(target.read_bytes())==sha(data)
  record['files'].append(dict(path=name,sha256=sha(data),bytes=len(data),mode=mode,preimage_sha256=old_sha))
 record.update(status='installed matching composed delta',end=time.time(),files_count=len(changes))
 (HERE/'installation.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(dict(status=record['status'],files=len(changes),revision=revision)))
if __name__=='__main__':main()
