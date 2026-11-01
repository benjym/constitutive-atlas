"""Save the exact permitted complete local website and file identities after build."""
from pathlib import Path
import hashlib,io,json,tarfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[4]
site=ROOT/'.local/lade-main-atlas-v2/site'
assert site.is_dir()
files=[]
for f in sorted(site.rglob('*')):
 assert not f.is_symlink(),f
 if f.is_file():
  assert f.suffix.lower()!='.pdf',f
  data=f.read_bytes();files.append({'path':f.relative_to(site).as_posix(),'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
manifest={'identity':'lade-main-atlas-actual-package-v2','scope':'Exact standard-builder local website; no live deployment claim','files':files}
with (HERE/'PACKAGE_MANIFEST.json').open('x') as out:json.dump(manifest,out,indent=2);out.write('\n')
archive=HERE/'website.tar.gz'
with archive.open('xb') as raw:
 with tarfile.open(fileobj=raw,mode='w:gz',format=tarfile.USTAR_FORMAT) as tar:
  for row in files:
   data=(site/row['path']).read_bytes();assert hashlib.sha256(data).hexdigest()==row['sha256']
   item=tarfile.TarInfo(row['path']);item.size=len(data);item.mode=0o644;item.mtime=0;tar.addfile(item,io.BytesIO(data))
receipt={'files':len(files),'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'manifest_sha256':hashlib.sha256((HERE/'PACKAGE_MANIFEST.json').read_bytes()).hexdigest(),'bytes':archive.stat().st_size}
with (HERE/'PACKAGE_RECEIPT.json').open('x') as out:json.dump(receipt,out,indent=2);out.write('\n')
print(json.dumps(receipt))
