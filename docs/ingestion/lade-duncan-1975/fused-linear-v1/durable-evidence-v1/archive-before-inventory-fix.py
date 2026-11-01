"""Archive existing saved evidence; never run a material or modify inputs."""
from pathlib import Path
import hashlib, json, tarfile, gzip, io
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
LOCAL=ROOT/'.local/lade-fused-linear-v1'
def sha(b):return hashlib.sha256(b).hexdigest()
paths=set()
for p in LOCAL.iterdir():
    if p.name=='emscripten-cache':continue
    if p.name.endswith('-build'):
        paths.update(q for q in p.iterdir() if q.is_file() and (q.name.startswith('atlas_') or q.suffix in ('.mjs','.wasm')))
    elif p.is_dir():paths.update(q for q in p.rglob('*') if q.is_file())
    elif p.is_file():paths.add(p)
recovery=json.loads((OUT.parent/'legacy-prerequisite-recovery-v1/RECOVERY.json').read_text())
# Canonical recovered originals are separate exact-byte files, not replacements.
for p in (ROOT/'catalogue/source-snapshots').glob('*/.local/lade-fused-linear-v1/wasm-requests/native-legacy-results-*.json'):
    paths.add(p)
assert len(paths)>10000,len(paths)
archive=OUT/'saved-evidence.tar.gz';manifest=OUT/'MANIFEST.json'
assert not archive.exists() and not manifest.exists()
files={}
with archive.open('xb') as raw,gzip.GzipFile(fileobj=raw,mode='wb',mtime=0,filename='') as gz,tarfile.open(fileobj=gz,mode='w',format=tarfile.PAX_FORMAT) as tar:
    for p in sorted(paths):
        assert not p.is_symlink(),p
        rel=p.relative_to(ROOT).as_posix();data=p.read_bytes();files[rel]=sha(data)
        info=tarfile.TarInfo(rel);info.size=len(data);info.mode=0o755 if p.name.startswith('atlas_') else 0o644;info.mtime=0;info.uid=info.gid=0;info.uname=info.gname=''
        tar.addfile(info,io.BytesIO(data))
result={'format':'lade-saved-evidence-archive-1','scope':'Exact existing qualified F source mirrors, executables, generated files, requests and worker streams; no execution; no private copyrighted papers; excludes caches and build objects. Recovered originals have canonical archive paths.','archive':{'path':archive.relative_to(ROOT).as_posix(),'sha256':sha(archive.read_bytes()),'bytes':archive.stat().st_size},'member_count':len(files),'files':files}
manifest.write_text(json.dumps(result,indent=2)+'\n')
# Reopen and independently check every member and the complete inventory.
with tarfile.open(archive,'r:gz') as tar:
    actual={m.name:sha(tar.extractfile(m).read()) for m in tar if m.isfile()}
assert actual==files
print(json.dumps({'members':len(files),'compressed_bytes':archive.stat().st_size,'archive_sha256':result['archive']['sha256'],'manifest_sha256':sha(manifest.read_bytes()),'roundtrip':'passed'}))
