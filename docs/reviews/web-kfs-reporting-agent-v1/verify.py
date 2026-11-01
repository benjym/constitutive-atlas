"""Verify feature hashes and exact historical receipt resolution; no material calls."""
from pathlib import Path
import hashlib,json
from atlas.evidence import checked_receipt
root=Path(__file__).resolve().parents[3];packet=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((packet/'manifest.json').read_text())
for name,h in manifest['files'].items():assert sha(root/name)==h,name
edges=0
for folder in (packet,packet/'propagation-archive'):
 plan=json.loads((folder/'archive-plan.json').read_text())
 for ref in plan['references']:
  assert sha(checked_receipt(root,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256'];edges+=1
 for name,h in plan['original_bytes'].items():assert sha(root/'catalogue/source-snapshots'/h/name)==h,name
print(f"PASS: {len(manifest['files'])} feature files and {edges} historical receipt edges")
