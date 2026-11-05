"""Lossless file retention against an existing durable Pages archive; no deletion."""
from pathlib import Path,PurePosixPath
import hashlib,json,stat,tarfile,zipfile
H=Path(__file__).resolve().parent;N=H.parent
ROOT=Path('/Users/bmar5496/code/constitutive-atlas')
SITE=Path('/private/tmp/atlas-baseline-delivery-20261105/site-C-standard-v2')
BASE=ROOT/'.local/retained-evidence/baseline-five-pages702-20261105.zip'
BASE_SHA='ed215bc438e97151120be79c0e0b2fcb57d42f24f0939559ba2c87d2c3765f41'
DELTA=ROOT/'.local/retained-evidence/baseline-five-C-failed-site-v2-delta-20261105.tar.gz'
def digest(f):
 h=hashlib.sha256();n=0
 for b in iter(lambda:f.read(1024*1024),b''):h.update(b);n+=len(b)
 return h.hexdigest(),n
def pin(p):
 with p.open('rb')as f:s,n=digest(f)
 return dict(path=str(p),sha256=s,bytes=n)
assert not DELTA.exists()and not(H/'retention.json').exists()
assert pin(BASE)['sha256']==BASE_SHA
old=json.loads((N/'standard-web-failure-v2/partial-site-inventory.json').read_text())
print(json.dumps({'inventory_keys':list(old)}))
expected={r['path']:r for r in old['files']}
target={};dirs=[]
for p in sorted(SITE.rglob('*')):
 assert not p.is_symlink(),p
 if p.is_dir():dirs.append(dict(path=str(p.relative_to(SITE)),mode=stat.S_IMODE(p.stat().st_mode)))
 elif p.is_file():
  r=pin(p);r['path']=str(p.relative_to(SITE));r['mode']=stat.S_IMODE(p.stat().st_mode);target[r['path']]=r
assert set(target)==set(expected)
for name,r in target.items():
 oldr=expected[name]
 assert r['sha256']==oldr['sha256']and r['bytes']==oldr.get('bytes',oldr.get('size_bytes'))
 if 'mode'in oldr:assert r['mode']==(int(oldr['mode'],8)if isinstance(oldr['mode'],str)else oldr['mode'])
base={}
with zipfile.ZipFile(BASE)as z:
 zi=[i for i in z.infolist()if not i.is_dir()];assert len(zi)==1 and zi[0].filename=='artifact.tar'
 with z.open(zi[0])as f,tarfile.open(fileobj=f,mode='r|*')as t:
  for member in t:
   if member.isdir():continue
   name=member.name.removeprefix('./');p=PurePosixPath(name)
   assert member.isfile()and not p.is_absolute()and'..'not in p.parts and name not in base
   stream=t.extractfile(member);s,n=digest(stream);assert n==member.size
   base[name]=dict(sha256=s,bytes=n)
changed=[name for name,r in target.items()if name not in base or any(r[k]!=base[name][k]for k in ['sha256','bytes'])]
with tarfile.open(DELTA,'x:gz')as t:
 for name in changed:t.add(SITE/name,arcname=name,recursive=False)
delta={}
with tarfile.open(DELTA,'r:gz')as t:
 for member in t:
  assert member.isfile()and member.name in changed and member.name not in delta
  s,n=digest(t.extractfile(member));delta[member.name]=dict(sha256=s,bytes=n,mode=member.mode)
assert set(delta)==set(changed)
for name,r in target.items():
 recovered=delta.get(name,base.get(name));assert recovered is not None
 assert all(r[k]==recovered[k]for k in ['sha256','bytes'])
 if name in delta:assert r['mode']==delta[name]['mode']
receipt=dict(identity='C-failed-site-v2-lossless-retention-v1',removed=False,
 site=str(SITE),base_archive=pin(BASE),delta_archive=pin(DELTA),
 rule='For each target inventory path read delta member if present, otherwise same-name base tar member; restore target mode, directory inventory and root mode. Ignore other base members.',
 files=list(target.values()),directories=dirs,root_mode=stat.S_IMODE(SITE.stat().st_mode),
 exact_verified_files=len(target),target_bytes=sum(r['bytes']for r in target.values()),
 delta_files=len(changed),source_inventory=pin(N/'standard-web-failure-v2/partial-site-inventory.json'),
 failure_manifest=pin(N/'standard-web-failure-v2/manifest.json'),
 retention='Base and delta are durable ignored private originals. Both are required; old receipts stay unchanged. No active consumer of v2 reported by all three workers.')
(H/'retention.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps({k:receipt[k]for k in ['exact_verified_files','target_bytes','delta_files','delta_archive']}))
