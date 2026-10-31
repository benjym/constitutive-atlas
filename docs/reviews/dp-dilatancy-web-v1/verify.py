"""Verify retained hashes and reassess saved responses; never execute a backend."""
from pathlib import Path
import hashlib,json,subprocess,tempfile
D=Path(__file__).resolve().parent;R=D.parents[2]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((D/'manifest.json').read_text())
for p,h in manifest['files'].items():assert sha(D/p)==h,p
with tempfile.TemporaryDirectory() as out:
 subprocess.run(['node',str(D/'check.mjs'),str(R),'unused',out,str(D/'results/raw.json')],check=True)
 assert (Path(out)/'report.json').read_bytes()==(D/'results/report.json').read_bytes()
print('Retained hashes and exact 83-case report replay pass; no backend executed.')
