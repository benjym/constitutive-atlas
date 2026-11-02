"""Independent exact-source and manufactured-byte checks only; no real source freeze."""
from pathlib import Path
import ast,hashlib,importlib.util,json,os,sys,tempfile
from unittest.mock import patch
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;P=HERE.parent/'package-v5';V4=HERE.parent/'package-v4'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def row(n,data,mode='100644'):return {'path':n,'bytes':len(data),'mode':mode,'git_blob':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()}
def identity(rows):return {'entries':rows,'files':len(rows),'logical_bytes':sum(r['bytes'] for r in rows)}
def main():
 assert sha(P/'MANIFEST.json')=='8e5db686a6ddb87d0a32d158a125c7f71d6c11be31f71d5b9df3c154e62a7d85'
 manifest=json.loads((P/'MANIFEST.json').read_text());assert all(sha(P/n)==h for n,h in manifest['files'].items())
 spec=importlib.util.spec_from_file_location('independent_v5_freezer',P/'freeze_inputs.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
 checks=[]
 def check(n,v):assert v,n;checks.append(n)
 def reject(n,fn):
  try:fn()
  except (AssertionError,OSError):checks.append(n);return
  raise AssertionError('Unexpected acceptance: '+n)
 for n in ['freeze_inputs.py','run_package.py','owned_process.py']:ast.parse((P/n).read_text())
 check('lifecycle byte-identical accepted v4',sha(P/'owned_process.py')==sha(V4/'owned_process.py')=='699bdfcd2e5ddc7168b319b6bc8620fcc2834be6edd54912d639e8b787d3407c')
 def fn_ast(path,name):return ast.dump(next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name))
 check('asset membership guard unchanged',fn_ast(P/'freeze_inputs.py','asset_members')==fn_ast(V4/'freeze_inputs.py','asset_members'))
 old=json.loads((V4/'plan.json').read_text());new=json.loads((P/'plan.json').read_text());argv=list(old['argv']);argv[-1]=argv[-1].replace('site-v4','site-v5')
 check('exact full argv only site5 output differs',argv==new['argv']);check('cwd and ordered parents unchanged',old['cwd']==new['cwd'] and old['parents']==new['parents'])
 check('exact accepted metadata identity',sha(F.RESOURCE_IDENTITY)==F.RESOURCE_IDENTITY_SHA256==manifest['external_resource_identity']['sha256'])
 with tempfile.TemporaryDirectory(dir=HERE,prefix='synthetic-') as tmp:
  root=Path(tmp);q=root/'data';data=b'abcdefgh'*300000;q.write_bytes(data);q.chmod(0o644);r=row('data',data)
  sizes=[];fdopen=os.fdopen
  class Watch:
   def __init__(self,h,mutate=False):self.h=h;self.mutate=mutate
   def __enter__(self):return self
   def __exit__(self,*a):self.h.close()
   def fileno(self):return self.h.fileno()
   def read(self,n):
    sizes.append(n);b=self.h.read(n)
    if self.mutate and b:self.mutate=False;q.write_bytes(b'z'*len(data))
    return b
  with patch.object(F.os,'fdopen',side_effect=lambda fd,*a,**k:Watch(fdopen(fd,*a,**k))):out=F.stream_regular(q)
  check('one MiB stream calls',len(sizes)>=4 and set(sizes)=={1048576});check('simultaneous SHA256 and Gitblob correct',out=={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'git_blob':r['git_blob']})
  check('complete synthetic source result',set(F.source_members(root,identity([r])))=={'data'})
  for field,value in [('bytes',len(data)+1),('mode','100755'),('git_blob','0'*40)]:reject('reject wrong '+field,lambda k=field,v=value:F.source_members(root,identity([{**r,k:v}])))
  reject('reject wrong count',lambda:F.source_members(root,{**identity([r]),'files':2}))
  reject('reject duplicate logical path',lambda:F.source_members(root,identity([r,r])))
  with patch.object(F.os,'fdopen',side_effect=lambda fd,*a,**k:Watch(fdopen(fd,*a,**k),True)):reject('reject same-size mutation during open read',lambda:F.stream_regular(q))
  q.write_bytes(data);q.chmod(0o644)
  link=root/F.KNOWN_LINK;link.parent.mkdir(parents=True);link.symlink_to('../else/deep');lr=row(F.KNOWN_LINK,b'../else/deep','120000')
  check('known dangling link verified readlink only',F.source_members(root,identity([lr]))[F.KNOWN_LINK]['bytes']==12)
  link.unlink();link.symlink_to('changed');reject('reject changed knownlink',lambda:F.source_members(root,identity([lr])))
  (root/'via').symlink_to(root);reject('reject ancestor symlink',lambda:F.source_members(root,identity([row('via/data',data)])))
  (root/'unexpected').symlink_to('data');reject('reject unexpected leaf symlink',lambda:F.stream_regular(root/'unexpected'))
  # Both logical names must be retained even when case-insensitive disk aliases them.
  a=root/'ALIAS';a.write_bytes(b'alias');a.chmod(0o644);b=root/'alias'
  if not b.exists():b.write_bytes(b'alias');b.chmod(0o644)
  aliases=F.source_members(root,identity([row('ALIAS',b'alias'),row('alias',b'alias')]))
  check('two logical aliases count separately',len(aliases)==2 and sum(v['bytes'] for v in aliases.values())==10)
 check('no recursive JSON selector', 'def references(' not in (P/'freeze_inputs.py').read_text())
 report={'status':'passed-independent-source-and-manufactured-byte-checks','manifest_sha256':sha(P/'MANIFEST.json'),'members':len(manifest['files']),'checks':checks,'count':len(checks),'actual_source_bytes_hashed':False,'actual_freeze_child_package_compiled_module_browser_remote_calls':0}
 (HERE/'check-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
