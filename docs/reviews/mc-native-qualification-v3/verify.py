"""Saved-only native replay; no compiler or engine call."""
from pathlib import Path
import hashlib,json,tarfile,tempfile,sys
p=Path(__file__).resolve().parent;r=p.parents[2];c=p.parent/'mc-current-collector-freeze-v3';driver=p.parent/'mc-execution-driver-v3';sys.path.insert(0,str(c));sys.path.insert(0,str(driver))
from assess_paths import assess as paths,load
from assess_replays import assess as replays
from assess_compatibility import assess as compatibility
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for n,h in load(p/'manifest.json')['files'].items():assert sha(p/n)==h,n
receipt=load(p/'receipt.json');assert receipt['completed']is True and receipt['role']=='native'and receipt['freeze_sha256']==sha(driver/'freeze.json')
assert [x['label']for x in receipt['commands']]==['generate','configure','build','observe','paths','replays','compatibility-collect','compatibility-assess']
assert all(type(x['status'])is int and x['status']==0 and x['signal']is None for x in receipt['commands'])
assert receipt['commands'][2]['argv'][-4:]==['--target','atlas_solver','--parallel','1']
with tempfile.TemporaryDirectory()as tmp:
 d=Path(tmp);pins=load(p/'archive-files.json')
 with tarfile.open(p/'observations.tar.gz','r:gz')as tar:
  assert set(tar.getnames())==set(pins)
  for n,h in pins.items():
   data=tar.extractfile(n).read();assert hashlib.sha256(data).hexdigest()==h
   f=d/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 assert(d/'receipt.json').read_bytes()==(p/'receipt.json').read_bytes()
 for n,h in receipt['observations'].items():assert sha(d/'observations'/n)==h,n
 out=d/'observations';assert paths(load(out/'journal.json'),load(c/'requests.json'),load(c/'reference/reference-p360.json'),load(c/'catalogue.json'))['passed']
 assert replays(out,'native')['passed']
 assert compatibility(out/'compatibility.json','native')['passed']
print('Verified saved native MC qualification:14paths/834points,93raw bindings,12recovery pairs and12full-response compatibility requests. Wasm/admission remain open.')
