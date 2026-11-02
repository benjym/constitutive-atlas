"""Prospective coordinator freeze: reads Git/source/assets only, writes NEW freeze here.
Never provisions, executes modules/materials/builds/browser, or mutates Git.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,os,stat
HERE=Path(__file__).resolve().parent;REPO=Path('/Users/bmar5496/code/constitutive-atlas')
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
     data=q.read_bytes();item.update(kind='file',bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),git_blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),git_mode='100755' if st.st_mode&stat.S_IXUSR else '100644')
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
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--revision',required=True);a=ap.parse_args();plan=json.loads((HERE/'plan.json').read_text());root=Path(plan['cwd']);assert root.is_dir();assert parents(a.revision)==plan['parents'];assert not (HERE/'source-freeze.json').exists();tracked=tree(a.revision);copied=copied_members(root,tracked)
 changed=set()
 for parent in plan['parents']:changed.update(n.decode() for n in git('diff-tree','-r','--no-commit-id','--name-only','-z',parent,a.revision).split(b'\0') if n)
 prefixes=('tools/','atlas/','web/','models/','schemas/','cpp/','catalogue/','data/','docs/models/','docs/benchmarks/','docs/capabilities/','docs/development/')
 selected={n for n in tracked if n.startswith(prefixes) and not n.startswith('catalogue/source-snapshots/') and '/dist/' not in n and '/preview/' not in n}|{n for n in changed if n in tracked}
 selected.update(n for n in ['CMakeLists.txt','pyproject.toml','requirements.txt','requirements-dev.txt'] if n in tracked)
 # Follow explicit source/receipt SHA pairs, including canonical snapshots, without scanning all historical evidence.
 def references(value):
  if isinstance(value,dict):
   if any(isinstance(value.get(k),str) and len(value[k])==64 for k in ['sha256','hash']):
    for field in ['path','original_path','archived_path']:
     if isinstance(value.get(field),str):yield value[field]
   for k,v in value.items():
    if isinstance(k,str) and '/' in k and isinstance(v,str) and len(v)==64:yield k
    yield from references(v)
  elif isinstance(value,list):
   for item in value:yield from references(item)
 parsed=set()
 while True:
  queue=sorted(n for n in selected-parsed if n.endswith('.json'))
  if not queue:break
  for n in queue:
   parsed.add(n)
   try:obj=json.loads((root/n).read_text())
   except (UnicodeError,json.JSONDecodeError):continue
   selected.update(n for n in references(obj) if n in tracked)
 # No historical-tree byte scan. Every selected actual file must equal its target Git blob.
 total=sum((root/n).stat().st_size for n in selected);assert total<=750*1024*1024,('Closure unexpectedly large; retain diagnostic and explicitly review closure rather than silently omit',total)
 source={}
 for n in sorted(selected):
  q=root/n;assert q.is_file() and not q.is_symlink();data=q.read_bytes();blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest();assert blob==tracked[n]['git_blob'],('Actual source differs from commit',n)
  source[n]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),**tracked[n]}
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
 report={'status':'frozen-source-only; no package execution','revision':a.revision,'parents':plan['parents'],'cwd':str(root),'plan_sha256':sha(HERE/'plan.json'),'wrapper_sha256':sha(HERE/'run_package.py'),'freeze_script_sha256':sha(__file__),'process_helper_sha256':sha(HERE/'owned_process.py'),'copied_members':copied,'asset_member_sets':asset_sets,'branch_delta_paths':sorted(changed),'source':source,'deleted_paths':deleted,'qualified_assets_and_ignored_witness':assets,'source_bytes':total,'selection':'union of both parent deltas; runtime/source/model/schema/catalogue/data roots; public dossiers/benchmark/capability/development inputs; recursive explicit JSON receipt hash references. No all-history byte scan.'}
 with (HERE/'source-freeze.json').open('x') as f:json.dump(report,f,indent=2);f.write('\n')
 print(json.dumps({'status':report['status'],'source_files':len(source),'source_bytes':total,'assets':len(assets),'revision':a.revision},indent=2))
if __name__=='__main__':main()
