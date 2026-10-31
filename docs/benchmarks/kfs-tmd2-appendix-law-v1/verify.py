"""Replay source algebra and input identity only; never invoke a backend."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
D=Path(__file__).resolve().parent;R=D.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for name,h in json.loads((D/'manifest.json').read_text())['files'].items():assert sha(D/name)==h,name
for row in json.loads((D/'source-review/manifest.json').read_text())['files']:assert sha(D/'source-review'/row['path'])==row['sha256']
for row in json.loads((D/'source-review/sources.json').read_text())['reviewed_inputs']:assert sha(R/row['path'])==row['sha256'],row['path']
output=subprocess.check_output([sys.executable,'-B',str(D/'source-review/check.py')])
assert output==(D/'source-review/checks.json').read_bytes()
with tempfile.TemporaryDirectory() as out:
 p=Path(out)/'bindings.json'
 subprocess.run([sys.executable,'-B',str(D/'check_bindings.py'),'--root',str(R),'--output',str(p)],check=True)
 assert p.read_bytes()==(D/'bindings.json').read_bytes()
print('Retained hashes, 24 structural fixtures, 10 tensor transformations and exact input-audit replay pass. No material evaluator/backend executed.')
