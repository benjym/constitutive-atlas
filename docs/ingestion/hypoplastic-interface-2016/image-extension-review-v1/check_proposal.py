"""Independent read-only verification of exact JPEG relocation proposal; no install."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
PACKET=ROOT/'docs/ingestion/hypoplastic-interface-2016'
FIX=PACKET/'image-extension-fix-v1'
def sha(data):return hashlib.sha256(data).hexdigest()
def pin(path):
 data=path.read_bytes();return {'path':path.relative_to(ROOT).as_posix(),'sha256':sha(data),'bytes':len(data)}
def main():
 inv=json.loads((FIX/'inventory.json').read_text());pre=json.loads((FIX/'preflight.json').read_text())
 rows=inv['files'];assert len(rows)==15 and len({r['path']for r in rows})==15
 prohibited={'.pdf','.dll','.zip','.png','.so','.dylib','.pyc','.pyo','.o','.a'}
 actual={p.relative_to(ROOT).as_posix()for p in PACKET.rglob('*')if p.suffix.lower()in prohibited}
 assert actual=={r['path']for r in rows},actual
 mappings={}
 for row,prepared in zip(rows,pre['entries']):
  old=ROOT/row['path'];assert old.is_file() and not old.is_symlink()
  assert old.relative_to(PACKET).parts[0]in ('browser-v1','browser-v2') and '..'not in old.parts
  data=old.read_bytes();assert len(data)==row['bytes'] and sha(data)==row['sha256']
  assert data[:3]==b'\xff\xd8\xff' and data[-2:]==b'\xff\xd9'
  original=subprocess.run(['git','show',inv['revision']+':'+row['path']],cwd=ROOT,check=True,capture_output=True).stdout
  assert original==data
  target=old.with_suffix('.jpg');archive=ROOT/'catalogue/source-snapshots'/row['sha256']/row['path']
  assert prepared==dict(original_path=row['path'],current_path=target.relative_to(ROOT).as_posix(),archived_path=archive.relative_to(ROOT).as_posix(),sha256=row['sha256'],bytes=len(data))
  for other in (target,archive):
   if other.exists():assert other.read_bytes()==data
  mappings[row['path']]=prepared
 receipts=[]
 for relative,key in [('browser-v1/manifest.json','entries'),('browser-v2/ARTIFACT-MANIFEST.json','files')]:
  doc=PACKET/relative;immutable=doc.read_bytes()
  assert subprocess.run(['git','show',inv['revision']+':'+doc.relative_to(ROOT).as_posix()],cwd=ROOT,check=True,capture_output=True).stdout==immutable
  moved=0
  for receipt in json.loads(immutable)[key]:
   orig=doc.parent/receipt['path'];assert not Path(receipt['path']).is_absolute() and '..'not in Path(receipt['path']).parts
   path=orig.relative_to(ROOT).as_posix();data=orig.read_bytes()
   assert sha(data)==receipt['sha256'] and len(data)==receipt['bytes']
   if path in mappings:
    mapped=mappings[path];assert receipt['sha256']==mapped['sha256'] and receipt['bytes']==mapped['bytes'];moved+=1
  receipts.append(dict(manifest=pin(doc),verified=len(json.loads(immutable)[key]),relocated=moved))
 assert sum(r['relocated']for r in receipts)==15
 tests=ROOT/'tests/test_ingestion_packets.py'
 assert tests.read_bytes()==subprocess.run(['git','show',inv['revision']+':tests/test_ingestion_packets.py'],cwd=ROOT,check=True,capture_output=True).stdout
 return dict(status='pass',reviewer='/root/interface_image_repair_review',source_revision=inv['revision'],images=15,jpeg_magic_and_eof_verified=15,source_git_images_exact=15,all_current_forbidden_packet_paths_accounted_for=True,receipt_closure=receipts,unchanged_safeguard=pin(tests),inputs=[pin(FIX/n)for n in ('repair.py','inventory.json','preflight.json')],limitation='Read-only prospective proof. Real archive/alias creation, deletion, unchanged targeted unittest and complete release CI remain coordinator actions.')
if __name__=='__main__':print(json.dumps(main(),indent=2))
