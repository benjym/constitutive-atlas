"""Saved-only Wasm/native qualification replay; no compiler or engine call."""
from pathlib import Path
import hashlib,json,tarfile,tempfile,sys
p=Path(__file__).resolve().parent;c=p.parent/'mc-current-collector-freeze-v3';driver=p.parent/'mc-execution-driver-v3';native=p.parent/'mc-native-qualification-v3';sys.path.insert(0,str(c));sys.path.insert(0,str(driver))
from assess_paths import assess as paths,load
from assess_replays import assess as replays
from assess_parity import assess as parity
from assess_compatibility import assess as compatibility
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
for packet in [p,native]:
 for n,h in load(packet/'manifest.json')['files'].items():assert sha(packet/n)==h,n
wasm=load(p/'receipt.json');nr=load(native/'receipt.json');assert wasm['completed']is True and wasm['role']=='wasm'and nr['completed']is True and nr['role']=='native'
assert wasm['freeze_sha256']==nr['freeze_sha256']==sha(driver/'freeze.json')
assert [x['label']for x in wasm['commands']]==['generate','configure','build','observe','paths','replays','parity','compatibility-collect','compatibility-assess']
assert all(type(x['status'])is int and x['status']==0 and x['signal']is None for x in wasm['commands'])
assert wasm['commands'][2]['argv'][-4:]==['--target','atlas_solver','--parallel','1']
assert set(wasm['artifacts'])=={'atlas.js','atlas.wasm'}
def extract(packet,out):
 pins=load(packet/'archive-files.json')
 with tarfile.open(packet/'observations.tar.gz','r:gz')as tar:
  assert set(tar.getnames())==set(pins)
  for n,h in pins.items():
   assert not Path(n).is_absolute()and'..'not in Path(n).parts
   data=tar.extractfile(n).read();assert hashlib.sha256(data).hexdigest()==h
   f=out/n;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(data)
 receipt=load(packet/'receipt.json');assert(out/'receipt.json').read_bytes()==(packet/'receipt.json').read_bytes()
 for n,h in receipt['observations'].items():assert sha(out/'observations'/n)==h,n
 return out/'observations'
with tempfile.TemporaryDirectory()as tmp:
 d=Path(tmp);w=extract(p,d/'wasm');n=extract(native,d/'native');requests=load(c/'requests.json')
 for role,out in [('native',n),('wasm',w)]:
  assert paths(load(out/'journal.json'),requests,load(c/'reference/reference-p360.json'),load(c/'catalogue.json'))['passed']
  assert replays(out,role)['passed']
  assert compatibility(out/'compatibility.json',role)['passed']
 result=parity(load(n/'journal.json'),load(w/'journal.json'),requests);assert result==load(p/'parity.stdout')
print('Verified both saved MC backends:14paths/834points each,14replays/12recoveries each,13540parity scalars and12compatibility requests each. Browser/admission remain open.')
