"""Compare the actual Pages upload with public project-path assets."""
import argparse, hashlib, json, urllib.request
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('upload', type=Path)
p.add_argument('--revision', required=True)
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
base = 'https://benjym.github.io/constitutive-atlas/'
sha = lambda raw: hashlib.sha256(raw).hexdigest()
manifest = json.loads((a.upload/'power-creep-package.json').read_text())
assert manifest['revision'] == a.revision
identity = json.loads((a.upload/'engine/identity.json').read_text())
assert identity['release_revision'] == a.revision
assert identity['model_sha256'] == '67f3fabd6aecfda19b977bf3baeae2dce45f9081fa81a4436a750a41825a4bef'
names = [*manifest['files'], 'power-creep-package.json', 'index.html', 'catalogue.json']
rows = []
for name in names:
    relative = Path(name)
    assert not relative.is_absolute() and '..' not in relative.parts
    local = (a.upload/name).read_bytes()
    if name in manifest['files']:
        assert sha(local) == manifest['files'][name]
    request = urllib.request.Request(base+name+'?revision='+a.revision,
                                     headers={'Cache-Control':'no-cache'})
    with urllib.request.urlopen(request, timeout=45) as response:
        live = response.read()
        assert response.status == 200
    assert live == local, 'Live upload mismatch: '+name
    rows.append(dict(path=name, sha256=sha(live), bytes=len(live), exact_upload_match=True))
record = dict(ok=True, revision=a.revision, url=base+'power-creep.html',
              identity=identity, assets=rows,
              scope='Exact tested upload byte comparison; actual live browser runs recorded separately.')
a.output.write_text(json.dumps(record, indent=2)+'\n')
print(json.dumps(dict(ok=True, revision=a.revision, exact_assets=len(rows))))
