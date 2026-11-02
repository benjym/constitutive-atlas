"""Prospective coordinator freeze: reads Git/source/assets only, writes NEW freeze here.
Never provisions, executes modules/materials/builds/browser, or mutates Git.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,os,stat
RESOURCE_IDENTITY_SHA256='f7627a0638674d476b73f97045e68c8be4078d2bbef261ef2809450dbed026d5'
HERE=Path(__file__).resolve().parent;REPO=Path('/Users/bmar5496/code/constitutive-atlas')
RESOURCE_IDENTITY=HERE/'../source-closure-v5/full-tree-resource-identity.json'
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
COPY_ROOTS=('models','schemas','catalogue/evidence','catalogue/reviews','catalogue/investigations')
def copied_members(root,tracked=None):
 root=Path(root);entries={}
 for name in COPY_ROOTS:
  base=root/name
  if not base.exists():
   assert not base.is_symlink(), ('Symlink root',name)
   if tracked is not None:assert not any(n.startswith(name+'/') for n in tracked), ('Missing copied root',name)
   continue
  assert base.is_dir() and not base.is_symlink(), ('Invalid copied root',name)
  for parent,dirs,files in os.walk(base,followlinks=False):
   for q in [Path(parent)]+[Path(parent)/n for n in files]+[Path(parent)/n for n in dirs if (Path(parent)/n).is_symlink()]:
    rel=q.relative_to(root).as_posix();st=q.lstat();assert not stat.S_ISLNK(st.st_mode), ('Symlink in recursively consumed root',rel)
    item={'mode':stat.S_IMODE(st.st_mode)}
    if stat.S_ISDIR(st.st_mode):item['kind']='directory'
    else:
     assert stat.S_ISREG(st.st_mode), ('Nonregular copied member',rel)
     item.update(kind='file',**stream_regular(q),git_mode='100755' if st.st_mode&stat.S_IXUSR else '100644')
    entries[rel]=item
 if tracked is not None:
  expected={n:v for n,v in tracked.items() if any(n.startswith(k+'/') for k in COPY_ROOTS)}
  actual={n:v for n,v in entries.items() if v['kind']=='file'}
  assert set(actual)==set(expected), ('Physical copied membership differs from target Git tree', sorted(set(actual)^set(expected)))
  for n,v in actual.items():assert v['git_blob']==expected[n]['git_blob'] and v['git_mode']==expected[n]['mode'], ('Physical copied bytes/mode differ from target Git tree',n)
  expected_dirs=set()
  for n in expected:
   expected_dirs.update(p.as_posix() for p in Path(n).parents if p.as_posix()!='.' and any(p.as_posix()==k or p.as_posix().startswith(k+'/') for k in COPY_ROOTS))
  actual_dirs={n for n,v in entries.items() if v['kind']=='directory'}
  assert actual_dirs==expected_dirs, ('Untracked/missing empty directory in copied root',sorted(actual_dirs^expected_dirs))
 return entries
def asset_members(directory):
 directory=Path(directory);assert directory.is_dir() and not directory.is_symlink();result={}
 for parent,dirs,files in os.walk(directory,followlinks=False):
  dirs[:]=[n for n in dirs if n not in ['CMakeFiles','node_modules','.cache','_deps']]
  for name in dirs:assert not (Path(parent)/name).is_symlink(), ('Asset directory symlink',name)
  for name in files:
   q=Path(parent)/name
   if q.suffix in ['.js','.mjs','.wasm','.json']:
    assert not q.is_symlink() and q.is_file(), ('Invalid asset member',q)
    result[q.relative_to(directory).as_posix()]={'sha256':sha(q),'mode':stat.S_IMODE(q.stat().st_mode),'bytes':q.stat().st_size}
 return result
def git(*args):return subprocess.check_output(['git',*args],cwd=REPO)
def parents(revision):
 row=git('rev-list','--parents','-n','1',revision).decode().split();assert row[0]==revision;return row[1:]
def tree(revision):
 result={}
 for item in git('ls-tree','-r','-z',revision).split(b'\0'):
  if not item:continue
  meta,name=item.split(b'\t');mode,kind,oid=meta.decode().split();assert kind=='blob';result[name.decode()]={'git_blob':oid,'mode':mode}
 return result

def fingerprint(st):return (st.st_dev,st.st_ino,st.st_mode,st.st_size,st.st_mtime_ns,st.st_ctime_ns)
def stream_regular(path):
 path=Path(path);before=path.lstat();assert stat.S_ISREG(before.st_mode), ('Nonregular source',path)
 h=hashlib.sha256();g=hashlib.sha1(b'blob '+str(before.st_size).encode()+b'\0');size=0
 with os.fdopen(os.open(path,os.O_RDONLY|os.O_NOFOLLOW),'rb') as f:
  assert fingerprint(os.fstat(f.fileno()))==fingerprint(before), ('File identity changed before open',path)
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk);g.update(chunk);size+=len(chunk)
  assert fingerprint(os.fstat(f.fileno()))==fingerprint(before), ('Open source changed during read',path)
 assert fingerprint(path.lstat())==fingerprint(before) and size==before.st_size, ('Source changed during read',path)
 return {'bytes':size,'sha256':h.hexdigest(),'git_blob':g.hexdigest()}
def resource_identity(revision,tracked):
 assert sha(RESOURCE_IDENTITY)==RESOURCE_IDENTITY_SHA256, 'Closed resource identity changed'
 identity=json.loads(RESOURCE_IDENTITY.read_text());assert revision==identity['revision'];assert parents(revision)==identity['parents'];assert git('rev-parse',revision+'^{tree}').decode().strip()==identity['tree']
 expected={r['path']:{k:r[k] for k in ('mode','git_blob')} for r in identity['entries']}
 assert len(identity['entries'])==len(expected)==identity['files']==40318
 assert sum(r['bytes'] for r in identity['entries'])==identity['logical_bytes']==3605081558
 assert tracked==expected, 'Full tracked membership/mode/blob changed'
 return identity
KNOWN_LINK='docs/ingestion/bingham-comsol63/ci-dependency-alias-review-v1/parent-traversal-fixture/links/dir'
def source_members(root,identity):
 root=Path(root);assert root.is_dir() and not root.is_symlink();result={}
 for row in identity['entries']:
  n=row['path'];assert not Path(n).is_absolute() and '..' not in Path(n).parts
  q=root/n
  for parent in q.parents:
   if parent==root:break
   assert parent.is_dir() and not parent.is_symlink(), ('Source ancestor is symlink/non-directory',n,parent)
  before=q.lstat()
  if row['mode']=='120000':
   assert n==KNOWN_LINK and stat.S_ISLNK(before.st_mode), ('Unexpected symlink',n)
   payload=os.fsencode(os.readlink(q));assert payload==b'../else/deep';assert fingerprint(q.lstat())==fingerprint(before)
   item={'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'git_blob':hashlib.sha1(b'blob '+str(len(payload)).encode()+b'\0'+payload).hexdigest()};mode='120000'
  else:
   assert row['mode'] in ('100644','100755') and stat.S_ISREG(before.st_mode), ('Source mode/kind mismatch',n)
   item=stream_regular(q);mode='100755' if before.st_mode&stat.S_IXUSR else '100644'
  assert fingerprint(q.lstat())==fingerprint(before), ('Source changed across member verification',n)
  assert item['bytes']==row['bytes'] and item['git_blob']==row['git_blob'] and mode==row['mode'], ('Actual source differs from closed Git identity',n)
  result[n]={**item,'mode':mode,'permissions':stat.S_IMODE(before.st_mode)}
 assert len(result)==identity['files'] and sum(r['bytes'] for r in result.values())==identity['logical_bytes']
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--revision',required=True);a=ap.parse_args();plan=json.loads((HERE/'plan.json').read_text());root=Path(plan['cwd']);assert root.is_dir();assert parents(a.revision)==plan['parents'];assert not (HERE/'source-freeze.json').exists();tracked=tree(a.revision);identity=resource_identity(a.revision,tracked);copied=copied_members(root,tracked)
 changed=set()
 for parent in plan['parents']:changed.update(n.decode() for n in git('diff-tree','-r','--no-commit-id','--name-only','-z',parent,a.revision).split(b'\0') if n)
 source=source_members(root,identity);total=sum(v['bytes'] for v in source.values())
 deleted=sorted(n for n in changed if n not in tracked)
 for n in deleted:assert not (root/n).exists(),('Deleted commit path present',n)
 assets={};asset_sets={}
 for i,arg in enumerate(plan['argv']):
  if not arg.endswith('-wasm-dir'):continue
  directory=Path(plan['argv'][i+1]);assert directory.is_dir(),('Provision/retain exact assets first',directory)
  members=asset_members(directory);asset_sets[str(directory)]=members
  for n,item in members.items():assets[str(directory/n)]={'sha256':item['sha256'],'bytes':item['bytes']}
 # Normal dataset builder's implicit asset paths (including ignored retained copies).
 grants={g['archive_sha256'] for g in json.loads((root/'data/experiment_releases.json').read_text())['grants']}
 for item in json.loads((root/'data/sources.json').read_text())['sources']:
  if item['sha256'] in grants:
   q=root/'data/raw'/item['filename'];assert sha(q)==item['sha256'];assets[str(q)]={'sha256':item['sha256'],'bytes':q.stat().st_size}
 curated=root/'data/curated/index.json'
 if curated.exists():
  for item in json.loads(curated.read_text())['records']:
   q=curated.parent/item['path'];n=q.relative_to(root).as_posix()
   if n in source:assert source[n]['sha256']==item['sha256']
   else:assert sha(q)==item['sha256'];assets[str(q)]={'sha256':item['sha256'],'bytes':q.stat().st_size}
 witness=root/'.local/lade-outer-predictor-v1/native-fixed-requests/dense-0.005-400.json';assert sha(witness)=='ee7e4ad4b34c14843c6f7d0b2d66a936d8c8409fa1e2dc2c493949a9411589f9';assets[str(witness)]={'sha256':sha(witness),'bytes':witness.stat().st_size}
 report={'status':'frozen-source-only; no package execution','revision':a.revision,'parents':plan['parents'],'cwd':str(root),'plan_sha256':sha(HERE/'plan.json'),'wrapper_sha256':sha(HERE/'run_package.py'),'freeze_script_sha256':sha(__file__),'process_helper_sha256':sha(HERE/'owned_process.py'),'copied_members':copied,'asset_member_sets':asset_sets,'branch_delta_paths':sorted(changed),'source':source,'deleted_paths':deleted,'qualified_assets_and_ignored_witness':assets,'source_bytes':total,'resource_identity_sha256':sha(RESOURCE_IDENTITY),'tree':identity['tree'],'selection':'ALL exact target Git tracked paths; closed count/bytes/modes/Git blobs; no recursive JSON selection or source deduplication.'}
 with (HERE/'source-freeze.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'status':report['status'],'source_files':len(source),'source_bytes':total,'assets':len(assets),'revision':a.revision},indent=2))
if __name__=='__main__':main()
