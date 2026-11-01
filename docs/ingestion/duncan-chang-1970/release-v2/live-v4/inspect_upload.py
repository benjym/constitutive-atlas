"""Safely unpack the exact tested Pages artifact and seal its complete file manifest."""
from pathlib import Path,PurePosixPath
import tarfile,sys,json,hashlib
archive=Path(sys.argv[1]);site=Path(sys.argv[2]);assert not site.exists();site.mkdir(parents=True)
with tarfile.open(archive) as t:
    members=t.getmembers()
    for m in members:
        q=PurePosixPath(m.name)
        assert not q.is_absolute() and '..' not in q.parts
        assert m.isfile() or m.isdir(),m.name
    t.extractall(site,filter='data')
rows=[]
for f in sorted(site.rglob('*')):
    if f.is_file():
        b=f.read_bytes();rows.append({'path':str(f.relative_to(site)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()})
out={'source_commit':'0b1b15ac5f4c8038bce3b26a098d31116c28b537','run_id':41340720867,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'count':len(rows),'bytes':sum(x['bytes'] for x in rows),'files':rows}
Path(__file__).with_name('upload-manifest.json').write_text(json.dumps(out,indent=2)+'\n');print(out['count'],out['bytes'],out['archive_sha256'])
