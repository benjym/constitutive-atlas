"""Read-only HTTP/package equality check; does not operate the browser."""
import hashlib,json,urllib.request
from pathlib import Path
s=Path('/private/tmp/atlas-interface2016-delivery-v1/site-v6')
out=Path(__file__).with_name('served-assets.json')
assert not out.exists()
paths=['index.html','app.js','model-profile-data.mjs','interface2016-laboratory.mjs','perzyna-laboratory.mjs','atlas.sqlite']
for d in ['material-point-interface2016/engine-path','engine-perzyna']:
    paths.extend(q.relative_to(s).as_posix() for q in (s/d).rglob('*') if q.is_file())
rows=[]
for n in sorted(set(paths)):
    with urllib.request.urlopen('http://127.0.0.1:51723/constitutive-atlas/'+n,timeout=30) as f:
        body=f.read();status=f.status
    expected=hashlib.file_digest((s/n).open('rb'),'sha256').hexdigest()
    actual=hashlib.sha256(body).hexdigest()
    assert status==200 and actual==expected,n
    rows.append(dict(path=n,status=status,bytes=len(body),sha256=actual,package_match=True))
out.write_text(json.dumps(dict(source_revision='4e60096f3ab4535c53fd48ee92acb094b5682f4d',assets=rows,count=len(rows)),indent=2)+'\n')
print(dict(assets_passed=len(rows)))
