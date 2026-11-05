"""Retain this failed study and its full physical site identity without copying it."""
from pathlib import Path
import hashlib,json,stat,time

HERE=Path(__file__).resolve().parent
N=HERE.parent
SITE=Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v3')
OBS=N/'standard-web-delivery-actual-v3'
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
    return h.hexdigest()
def write(name,data):
    p=HERE/name
    assert not p.exists(),p
    p.write_text(json.dumps(data,indent=2)+'\n')
def pin(p):return dict(path=str(p),sha256=sha(p),bytes=p.stat().st_size)
phases=['fast-source-contracts','retained-source-guards','standard-web-package',
        'package-engine-smoke','all994-built-dataset-transport',
        'original-package-contracts','supported17-public-inputs']
results=[]
for i,phase in enumerate(phases):
    r=json.loads((OBS/('outer-'+phase)/'receipt.json').read_text())
    b=json.loads((OBS/(phase+'-source-binding.json')).read_text())
    assert r['mandatory_reap']is True and r['reaped_returncode']==r['returncode']
    assert r['returncode']==(1 if i==6 else 0)
    assert b['source_pre_passed']is True and b['source_post_passed']is True
    results.append(dict(phase=phase,returncode=r['returncode'],mandatory_reap=True))
assert not (OBS/'outer-original-scoped-parity').exists()
rows=[]
for p in sorted(SITE.rglob('*')):
    assert not p.is_symlink(),p
    if p.is_file():
        rows.append(dict(path=str(p.relative_to(SITE)),sha256=sha(p),
                         size_bytes=p.stat().st_size,mode=stat.S_IMODE(p.stat().st_mode)))
write('physical-site-inventory.json',dict(identity='retained-complete-site-v3',site=str(SITE),
    files=rows,total_bytes=sum(r['size_bytes']for r in rows),acceptance=False))
files=[p for p in OBS.rglob('*')if p.is_file()]
files += [p for p in (N/'standard-web-launch-v4').rglob('*')if p.is_file()and'__pycache__'not in p.parts]
files += [HERE/'freeze.py',HERE/'physical-site-inventory.json']
write('manifest.json',dict(identity='standard-web-failed-supported-source-pin-v3',
    frozen_epoch=time.time(),source_revision='023a67e4d83b96491fffda8d89c8479f2c8f38a3',
    scope='Six phases passed; supported-input phase failed on stale controlled-time source pin; scoped parity not run. No package/browser/live acceptance.',
    phase_results=results,site_retention=str(SITE),files=[pin(p)for p in sorted(set(files))]))
print(json.dumps(dict(manifest_sha256=sha(HERE/'manifest.json'),site_files=len(rows),
    site_bytes=sum(r['size_bytes']for r in rows),evidence_files=len(files))))
