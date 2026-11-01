"""Read-only whole packet and original-input byte verification."""
import sys
sys.dont_write_bytecode = True
import ast,json
from pathlib import Path
from frozen_logic import D,sha,frozen
frozen()
manifest=json.loads((D/'manifest.json').read_text())
assert not any(p.is_symlink()or '__pycache__'in p.parts or p.suffix.lower()in{'.pdf','.dll','.zip','.png','.so','.dylib','.pyc','.pyo','.o','.a'}for p in D.rglob('*')),'forbidden generated/binary/cache artifact'
assert sorted(manifest)==sorted(str(p.relative_to(D))for p in D.rglob('*')if p.is_file()and p!=D/'manifest.json'),'exact packet inventory'
for name,digest in manifest.items():assert sha(D/name)==digest,'packet drift: '+name
for path in D.glob('*.py'):ast.parse(path.read_text(),filename=str(path))
print(json.dumps({'identity':'md1997-raw-link-freeze-v7','passed':True,'files':len(manifest),'manifest_sha256':sha(D/'manifest.json'),'compiled_calls':0}))
