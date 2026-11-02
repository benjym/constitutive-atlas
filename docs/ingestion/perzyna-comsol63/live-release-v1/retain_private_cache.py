from pathlib import Path
import hashlib,json,tarfile,time,os
root=Path(__file__).resolve().parents[4]
destination=Path('/Users/bmar5496/code/constitutive-atlas/.local/perzyna-retained-v1')
archive=destination/'task-ignored-resources-v1.tar.gz'
assert not archive.exists()
selected=['.local/emscripten-cache','.local/lade-outer-predictor-v1','.local/perzyna-implicit-preflight-v1','.local/perzyna-prior-preflight-v1','.local/perzyna-site-v1','.local/perzyna-site-v2','.local/perzyna-source-database-v1','.local/private-sources','build-perzyna-native','build-perzyna-public','build-perzyna-wasm']
files={};links={}
for name in selected:
 for p in sorted((root/name).rglob('*')):
  relative=p.relative_to(root).as_posix()
  if p.is_symlink():links[relative]=os.readlink(p)
  elif p.is_file():files[relative]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
print('Pinned',len(files),'regular files;',sum(x['bytes'] for x in files.values()),'bytes',flush=True)
with tarfile.open(archive,'w:gz',compresslevel=6,dereference=False) as tar:
 for name in selected:tar.add(root/name,arcname=name,recursive=True)
verified=set();verified_links={}
with tarfile.open(archive,'r:gz') as tar:
 for member in tar:
  assert not Path(member.name).is_absolute() and '..' not in Path(member.name).parts
  if member.isfile():
   data=tar.extractfile(member).read();assert member.name in files;assert len(data)==files[member.name]['bytes'];assert hashlib.sha256(data).hexdigest()==files[member.name]['sha256'];verified.add(member.name)
  elif member.issym():verified_links[member.name]=member.linkname
assert verified==set(files) and verified_links==links
index={'kind':'private-task-resumption-archive','source_worktree':str(root),'archive':str(archive),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'archive_bytes':archive.stat().st_size,'roots':selected,'files':files,'symlinks':links,'all_file_recovery_verified':True,'no_compiled_execution':True,'scope':'Only task-owned ignored directories; borrowed Bingham assets excluded; private source originals remain private'}
(destination/'TASK-CACHE-INDEX.json').write_text(json.dumps(index,indent=2)+'\n')
receipt={k:v for k,v in index.items() if k not in ['files','symlinks']};receipt.update(regular_files=len(files),symlinks=len(links),original_regular_bytes=sum(x['bytes'] for x in files.values()),index_sha256=hashlib.sha256((destination/'TASK-CACHE-INDEX.json').read_bytes()).hexdigest())
(root/'docs/ingestion/perzyna-comsol63/live-release-v1/PRIVATE-CACHE-RETENTION.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt),flush=True)
