"""Replay exact public packet and locally retained private primary source pins."""
import hashlib,json
from pathlib import Path
D=Path(__file__).resolve().parent
manifest=json.loads((D/'manifest.json').read_text())
for pin in manifest['files']:
    p=D/pin['path'];assert p.stat().st_size==pin['bytes'],pin['path']
    assert hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'],pin['path']
receipt=json.loads((D/'source-receipt.json').read_text())
private_available=0
for pin in receipt['sources']:
    p=Path(pin['private_path'])
    if p.exists():
        assert p.stat().st_size==pin['bytes'],str(p)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==pin['sha256'],str(p)
        private_available+=1
model_hash=hashlib.sha256((D/'candidate.json').read_bytes()).hexdigest()
for name in ['crosswalk.json','candidate-check-results.json']:
    assert json.loads((D/name).read_text())['model_sha256']==model_hash,name
result={'identity':'kelvin-voigt-comsol63-source-packet-check-v1','all_public_pins_passed':True,'public_file_count':len(manifest['files']),'private_source_pins_verified':private_available,'private_source_total':len(receipt['sources']),'all_private_pins_locally_verified':private_available==len(receipt['sources']),'model_sha256':model_hash,'limitations':['Private original sources are not redistributed; offline clones may report unavailable private pins','Manifest does not replace independent scientific review or native/Wasm qualification']}
out=json.dumps(result,indent=2)+'\n';dest=D/'packet-check-results.json'
if dest.exists():assert dest.read_text()==out,'retained results differ; preserve prior results before changing environment'
else:dest.write_text(out)
print(out,end='')
