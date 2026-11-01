from pathlib import Path
import hashlib,json,subprocess,sys
p=Path(__file__).resolve().parent;root=p.parents[2];sys.path.insert(0,str(root))
from atlas.evidence import checked_receipt
portable=json.loads((p/'portable-freeze.json').read_text())
assert hashlib.sha256((p/'prospective-freeze.json').read_bytes()).hexdigest()==portable['original_prospective_freeze_sha256']
for name,h in portable['files'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
assert set(portable['omitted_incidental_bytecode'])=={'__pycache__/assess.cpython-314.pyc'}
manifest=json.loads((p/'manifest.json').read_text())
for name,h in manifest['files'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
for name,h in json.loads((p/'source-pins.json').read_text())['sources'].items():
    resolved=checked_receipt(root,(p/'source-pins.json').relative_to(root).as_posix(),name,h)
    assert hashlib.sha256(resolved.read_bytes()).hexdigest()==h,name
subprocess.run([sys.executable,'-B',str(p/'assess.py'),'--both'],check=True)
print('retained manifest and 111 original build-source bindings verified; no builds or artifact execution')
