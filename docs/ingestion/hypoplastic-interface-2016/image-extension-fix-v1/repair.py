"""Preserve screenshot bytes, correct JPEG names, and verify original receipts.

No model execution or policy changes. Run without --install for preflight.
"""
import hashlib,json,sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 inventory=json.loads((HERE/'inventory.json').read_text())
 entries=[]
 for row in inventory['files']:
  old=ROOT/row['path']; new=old.with_suffix('.jpg')
  archive=ROOT/'catalogue/source-snapshots'/row['sha256']/row['path']
  assert old.suffix=='.png' and '/browser-v' in row['path']
  source=old if old.exists() else archive
  data=source.read_bytes()
  assert data.startswith(b'\xff\xd8\xff') and len(data)==row['bytes'] and sha(data)==row['sha256']
  for target in (new,archive):
   if target.exists():assert target.read_bytes()==data
  entries.append(dict(original_path=row['path'],current_path=new.relative_to(ROOT).as_posix(),archived_path=archive.relative_to(ROOT).as_posix(),sha256=row['sha256'],bytes=len(data)))
 if '--install' in sys.argv:
  # All checks above finish before mutation; archives and aliases before removal.
  for row in entries:
   old=ROOT/row['original_path'];data=(old if old.exists() else ROOT/row['archived_path']).read_bytes()
   for key in ('archived_path','current_path'):
    target=ROOT/row[key];target.parent.mkdir(parents=True,exist_ok=True)
    if not target.exists():target.write_bytes(data)
    assert target.read_bytes()==data
  for row in entries:
   old=ROOT/row['original_path']
   if old.exists():
    assert sha(old.read_bytes())==row['sha256'];old.unlink()
  (HERE/'RELOCATION.json').write_text(json.dumps(dict(version='browser-jpeg-relocation-1',original_revision=inventory['revision'],entries=entries),indent=2)+'\n')
 # Resolve original manifests by their unchanged original relative pins.
 mapping={r['original_path']:r for r in entries}; receipts=[]
 for relative,key in [('browser-v1/manifest.json','entries'),('browser-v2/ARTIFACT-MANIFEST.json','files')]:
  doc=HERE.parent/relative;count=0
  for pin in json.loads(doc.read_text())[key]:
   original=(doc.parent/pin['path']).relative_to(ROOT).as_posix()
   selected=ROOT/(mapping[original]['archived_path'] if original in mapping and '--install' in sys.argv else original)
   data=selected.read_bytes();assert sha(data)==pin['sha256'] and len(data)==pin['bytes'],original
   count+=1
  receipts.append(dict(path=doc.relative_to(ROOT).as_posix(),sha256=sha(doc.read_bytes()),members_verified=count))
 result=dict(status='installed and verified' if '--install' in sys.argv else 'preflight passed',images=len(entries),original_manifests=receipts,entries=entries)
 if '--install' in sys.argv:(HERE/'verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
