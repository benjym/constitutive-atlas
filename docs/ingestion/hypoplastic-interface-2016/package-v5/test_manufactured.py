"""Pure temporary-file fixtures only; no actual source freeze, child launch or package."""
import sys,hashlib,json,tempfile,io,stat,os
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import freeze_inputs as f
checks=[]
def check(label,condition):assert condition,label;checks.append(label)
def fail(label,fn):
 try:fn()
 except (AssertionError,FileNotFoundError):checks.append(label);return
 raise AssertionError(label)
def row(n,data,mode='100644'):return {'path':n,'bytes':len(data),'mode':mode,'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
def identity(rows):return {'entries':rows,'files':len(rows),'logical_bytes':sum(r['bytes'] for r in rows)}
with tempfile.TemporaryDirectory(prefix='interface2016-v5-source-fake-') as td:
 root=Path(td);p=root/'a';data=b'1234567890'*210000;p.write_bytes(data);os.chmod(p,0o644)
 calls=[];original=os.fdopen
 class ReadWatch:
  def __init__(self,h):self.h=h
  def __enter__(self):return self
  def __exit__(self,*a):self.h.close()
  def fileno(self):return self.h.fileno()
  def read(self,n):calls.append(n);return self.h.read(n)
 def watch(fd,*args,**kw):return ReadWatch(original(fd,*args,**kw))
 with patch.object(os,'fdopen',watch):v=f.stream_regular(str(p))
 check('str path accepted',v['bytes']==len(data));check('all streamed reads exactly1MiB',len(calls)>=3 and set(calls)=={1048576});check('sha256 exact',v['sha256']==hashlib.sha256(data).hexdigest());check('Gitblob exact',v['git_blob']==row('a',data)['git_blob'])
 rows=[row('a',data)];out=f.source_members(root,identity(rows));check('complete fixture member',set(out)=={'a'})
 fail('wrong expectedsize rejected',lambda:f.source_members(root,identity([{**rows[0],'bytes':len(data)+1}])));fail('wrong Gitblob rejected',lambda:f.source_members(root,identity([{**rows[0],'git_blob':'0'*40}])));fail('wrong mode rejected',lambda:f.source_members(root,identity([{**rows[0],'mode':'100755'}])))
 fail('count mismatch rejected',lambda:f.source_members(root,{**identity(rows),'files':2}));fail('total mismatch rejected',lambda:f.source_members(root,{**identity(rows),'logical_bytes':0}))
 p.write_bytes(b'changed');fail('changed source rejected',lambda:f.source_members(root,identity(rows)));p.unlink();fail('removed source rejected',lambda:f.source_members(root,identity(rows)))
 p.symlink_to('not-present');fail('unexpected symlink rejected without target open',lambda:f.source_members(root,identity(rows)));p.unlink()
 link=root/f.KNOWN_LINK;link.parent.mkdir(parents=True);link.symlink_to('../else/deep');linkrow=row(f.KNOWN_LINK,b'../else/deep','120000');check('known negative symlink payload verified without following',f.source_members(root,identity([linkrow]))[f.KNOWN_LINK]['bytes']==12)
 link.unlink();link.symlink_to('elsewhere');fail('changed link payload rejected',lambda:f.source_members(root,identity([linkrow])))
 (root/'outside').mkdir();(root/'outside/x').write_bytes(b'x');(root/'via').symlink_to(root/'outside');fail('ancestor symlink rejected',lambda:f.source_members(root,identity([row('via/x',b'x')])))
 # Exact copied-root membership guards inherited from v4.
 (root/'models').mkdir(parents=True,exist_ok=True)
 c=root/'models/one.json';c.write_bytes(b'{}');os.chmod(c,0o644);tracked={'models/one.json':{k:row('models/one.json',b'{}')[k] for k in ['mode','git_blob']}}
 base=f.copied_members(root,tracked);check('copied root fixture matches Git',base['models/one.json']['bytes']==2)
 (root/'models/added.json').write_bytes(b'{}');fail('added copied member rejected',lambda:f.copied_members(root,tracked));(root/'models/added.json').unlink();(root/'models/empty').mkdir();fail('added empty directory rejected',lambda:f.copied_members(root,tracked))
check('lifecycle helper byte-identical v4',(HERE/'owned_process.py').read_bytes()==(HERE.parent/'package-v4/owned_process.py').read_bytes())
plan=json.loads((HERE/'plan.json').read_text());old=json.loads((HERE.parent/'package-v4/plan.json').read_text());check('normal argv differs only site-v5',plan['argv'][:-1]==old['argv'][:-1] and plan['argv'][-1]==old['argv'][-1].replace('site-v4','site-v5'));check('same cwd and ordered parents',plan['cwd']==old['cwd'] and plan['parents']==old['parents']);check('no JSON discovery in freezer','def references(' not in (HERE/'freeze_inputs.py').read_text())
for name in ('freeze_inputs.py','run_package.py','owned_process.py'):compile((HERE/name).read_text(),str(HERE/name),'exec')
check('scripts syntax valid',True)
result={'status':'passed pure manufactured file and source checks; no actual freeze/package/child','checks':checks,'count':len(checks)}
with (HERE/'manufactured-results-v2.json').open('x') as out:json.dump(result,out,indent=2);out.write('\n')
print(json.dumps(result,indent=2))
