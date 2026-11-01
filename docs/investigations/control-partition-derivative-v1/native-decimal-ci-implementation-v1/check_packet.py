"""Verify immutable packet/source bytes without invoking any process."""
import sys
sys.dont_write_bytecode=True
import hashlib,json
from pathlib import Path
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((P/'manifest.json').read_text());actual={str(p.relative_to(P))for p in P.rglob('*')if p.is_file()and p!=P/'manifest.json'}
assert actual==set(m['files'])
assert not any(p.is_symlink()or p.name=='__pycache__'or p.suffix=='.pyc'for p in P.rglob('*'))
for n,h in m['files'].items():assert sha(P/n)==h,n
for row in json.loads((P/'inputs.json').read_text()).values():assert sha(Path(row['path']))==row['sha256']
f=json.loads((P/'source-freeze.json').read_text());S=Path(f['directory'])
assert {str(p.relative_to(S))for p in S.rglob('*')if p.is_file()}==set(f['files'])
for n,h in f['files'].items():assert sha(S/n)==h,n
print(json.dumps(dict(passed=True,packet_files=len(actual),source_files=len(f['files']),compiled_calls=0)))
