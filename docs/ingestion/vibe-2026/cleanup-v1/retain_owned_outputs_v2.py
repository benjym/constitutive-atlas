"""Archive only the coordinator-owned isolated outputs after consumers stop."""
from pathlib import Path
import tarfile,hashlib,json,shutil,time,subprocess
ROOT=Path('/private/tmp/atlas-vibe2026-controlled-time-v1')
DEST=Path('/Users/bmar5496/code/constitutive-atlas/.local/release-artifacts/vibe2026-v1')
NAMES=['.local/vibe-native-generic-v1','.local/vibe-native-model-v1','.local/vibe-wasm-generic-v1','.local/vibe-wasm-model-v1','.local/vibe-site-v1','.local/vibe-site-v2','.local/controlled-path-refresh-v1','.local/controlled-path-refresh-v2','.local/maxwell-refresh-v1','.local/lade-outer-predictor-v1','output/playwright','.playwright-cli']
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 assert (ROOT/'docs/ingestion/vibe-2026/browser-qualification-v4/process-cleanup.json').is_file(),'Consumers must be closed and recorded first'
 DEST.mkdir(parents=True,exist_ok=True)
 archive=DEST/'local-build-browser-retention-v1.tar.gz';index=DEST/'local-build-browser-retention-v1-files.json'
 assert not archive.exists() and not index.exists(),'Unique retention identity required'
 present=[n for n in NAMES if (ROOT/n).exists()]
 for n in present:
  assert not subprocess.check_output(['git','ls-files','--',n],cwd=ROOT).strip(),'Tracked path must never be removed: '+n
 files={str(p.relative_to(ROOT)):{'sha256':sha(p),'bytes':p.stat().st_size} for n in present for p in sorted((ROOT/n).rglob('*')) if p.is_file() and not p.is_symlink()}
 symlinks={str(p.relative_to(ROOT)):str(p.readlink()) for n in present for p in (ROOT/n).rglob('*') if p.is_symlink()}
 index.write_text(json.dumps({'files':files,'symlinks':symlinks},indent=2)+'\n')
 free_before=shutil.disk_usage(ROOT).free
 with tarfile.open(archive,'w:gz') as t:
  for n in present:t.add(ROOT/n,arcname=n)
 with tarfile.open(archive,'r:gz') as t:
  recovered={};links={}
  for member in t:
   if member.isfile():
    h=hashlib.sha256();f=t.extractfile(member)
    for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    recovered[member.name]={'sha256':h.hexdigest(),'bytes':member.size}
   elif member.issym():links[member.name]=member.linkname
  assert recovered==files and links==symlinks,'Lossless recovery check failed; preserve all originals'
 # Recheck every source immediately before deletion. No shared roots, private source originals or tracked evidence is removed.
 for name,pin in files.items():assert sha(ROOT/name)==pin['sha256'],name
 for n in present:shutil.rmtree(ROOT/n)
 receipt={'status':'verified-and-removed','owner':'/root MODEL-vibe-2026','removed_paths':present,'archive':str(archive),'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'index':str(index),'index_sha256':sha(index),'verified_files':len(files),'verified_bytes':sum(v['bytes'] for v in files.values()),'symlinks_verified':symlinks,'lossless_member_recovery':True,'free_before':free_before,'free_after':shutil.disk_usage(ROOT).free,'retained':'Tracked durable engine/source/numerical/browser evidence, private originals and shared peer archives unchanged','worktree':'Retained temporarily for scoped local release commit and pending remote authorization; no preview/build process remains'}
 (ROOT/'docs/ingestion/vibe-2026/cleanup-v1/local-output-retention-v1.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps(receipt,indent=2))
if __name__=='__main__':main()
