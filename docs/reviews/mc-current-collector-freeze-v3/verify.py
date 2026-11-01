"""Verify a source-only checkpoint, never authorize compiled execution."""
from pathlib import Path
import hashlib,json,sys,tarfile,tempfile
p=Path(__file__).resolve().parent
sys.path.insert(0,str(p))
from assess_binding import verify as binding
from assess_paths import assess as paths,load
from assess_replays import assess as replays
from assess_parity import assess as parity
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for n,h in load(p/'manifest.json')['files'].items():assert sha(p/n)==h,n
binding()
for label in ['audit-original','audit-role-closure']:
 a=p/label;m=load(a/'manifest.json')['files']
 with tarfile.open(a/'packet.tar.gz','r:gz')as archive:
  assert set(archive.getnames())==set(m)|{'manifest.json'}
  for n,h in m.items():assert hashlib.sha256(archive.extractfile(n).read()).hexdigest()==h,n
  assert archive.extractfile('manifest.json').read()==(a/'manifest.json').read_bytes()
for n,h in load(p/'compatibility-policy.json')['baseline'].items():assert sha(p.parents[2]/n)==h,n
with tempfile.TemporaryDirectory()as tmp:
 d=Path(tmp)
 with tarfile.open(p/'observer-synthetic.tar.gz','r:gz')as archive:
  assert set(archive.getnames())=={'journal.json','calls.json','replays.json','rejections.json'}
  for n in archive.getnames():(d/n).write_bytes(archive.extractfile(n).read())
 req=load(p/'requests.json');rows=load(d/'journal.json')
 assert paths(rows,req,load(p/'reference/reference-p360.json'),load(p/'catalogue.json'))['passed']
 assert replays(d,'synthetic')['passed']
 assert parity(rows,rows,req)['passed']
status=load(p/'preparation-status.json');assert status['compiled_calls']==0 and status['open_gates']
print('Verified source-only MC collector checkpoint:14 manufactured paths/834points,93 raw bindings. Execution freeze remains incomplete; no build authorized by this checkpoint.')
