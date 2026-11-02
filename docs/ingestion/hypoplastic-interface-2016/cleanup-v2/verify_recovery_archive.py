"""Future read-only archive verifier. Does not extract, execute, delete or rebuild."""
from pathlib import Path,PurePosixPath
import argparse,json,tarfile,hashlib,stat
p=argparse.ArgumentParser();p.add_argument('archive',type=Path);a=p.parse_args()
manifest=json.loads(Path(__file__).with_name('recovery-inventory.json').read_text());expected={r['path']:r for r in manifest['entries']};seen=set()
with tarfile.open(a.archive,'r|*') as archive:
 for member in archive:
  name=member.name.removeprefix('./').rstrip('/');parts=PurePosixPath(name).parts
  assert name and not name.startswith('/') and '..' not in parts, ('Unsafe member',name)
  if name in ['site-v1','source-guard-checks-v1']:
   assert member.isdir();continue
  assert name in expected and name not in seen, ('Unexpected/duplicate member',name)
  row=expected[name];assert member.mode==row['mode'], ('Mode mismatch',name)
  if row['kind']=='directory':assert member.isdir()
  else:
   assert row['kind']=='file' and member.isfile() and member.size==row['size'], ('Type/size mismatch',name)
   h=hashlib.sha256();f=archive.extractfile(member)
   for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
   assert h.hexdigest()==row['sha256'], ('Content mismatch',name)
  seen.add(name)
assert seen==set(expected), ('Missing members',set(expected)-seen)
print(json.dumps({'status':'complete exact-content/mode archive verification','entries':len(seen),'archive':str(a.archive),'recovery_inventory_sha256':hashlib.sha256(Path(__file__).with_name('recovery-inventory.json').read_bytes()).hexdigest(),'extraction_or_execution':False}))
