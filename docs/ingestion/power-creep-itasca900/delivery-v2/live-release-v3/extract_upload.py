"""Extract only the exact power package and its public navigation from CI upload."""
from pathlib import Path
import argparse,hashlib,json,tarfile
p=argparse.ArgumentParser();p.add_argument('tar',type=Path);p.add_argument('output',type=Path);p.add_argument('--receipt',type=Path,required=True);a=p.parse_args()
with tarfile.open(a.tar) as archive:
 members={m.name.removeprefix('./'):m for m in archive.getmembers() if m.isfile()}
 assert 'power-creep-package.json' in members,'Actual tested upload omitted the approved power package'
 raw=archive.extractfile(members['power-creep-package.json']).read();manifest=json.loads(raw)
 names=[*manifest['files'],'power-creep-package.json','index.html','catalogue.json','app.js','timed-route.mjs','style.css']
 rows=[]
 for name in names:
  relative=Path(name);assert not relative.is_absolute() and '..' not in relative.parts
  b=archive.extractfile(members[name]).read();h=hashlib.sha256(b).hexdigest()
  if name in manifest['files']:assert h==manifest['files'][name],name
  dest=a.output/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(b);rows.append(dict(path=name,sha256=h,bytes=len(b)))
a.receipt.write_text(json.dumps(dict(revision=manifest['revision'],upload_archive_sha256=hashlib.sha256(a.tar.read_bytes()).hexdigest(),extracted=rows),indent=2)+'\n')
print('Verified actual uploaded manifest and extracted',len(rows),'assets for',manifest['revision'])
