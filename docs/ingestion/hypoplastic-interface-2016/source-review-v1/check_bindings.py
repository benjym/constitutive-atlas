"""Verify exact author freeze, retained originals and reviewer source bindings."""
from pathlib import Path
import hashlib,json
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];SOURCE=OUT.parent/'source-v2'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
expected='9637c8859d36def48aac3cb43785141395f69572e00e54a4689e33020e70123a'
assert sha(SOURCE/'manifest.json')==expected
manifest=json.loads((SOURCE/'manifest.json').read_text());assert len(manifest['files'])==8
bindings={str((SOURCE/'manifest.json').relative_to(ROOT)):expected}
for entry in manifest['files']:
 p=Path(entry['path']);assert p.parent==SOURCE
 assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes'];bindings[str(p.relative_to(ROOT))]=sha(p)
resources=json.loads((SOURCE/'resource-receipt.json').read_text())
for entry in resources['private_files']+[resources['original1996_read_in_place']]:
 p=Path(entry['path']);assert sha(p)==entry['sha256'] and p.stat().st_size==entry['bytes'];bindings[str(p.relative_to(ROOT))]=sha(p)
for p in ['AGENTS.md','docs/MODEL_DELIVERY_CHECKLIST.md','docs/PUBLIC_MODEL_PROFILES.md','docs/FORMULATION_CONTRACT.md','docs/AGENT_REVIEW_POLICY.md','schemas/model-v0.3.schema.json','docs/ingestion/hypoplastic-interface-2016/README.md','docs/ingestion/hypoplastic-interface-2016/checks.py','docs/ingestion/hypoplastic-interface-2016/integration-contract.json']:
 bindings[p]=sha(ROOT/p)
result=dict(passed=True,reviewer='/root/hill_scientific_review',source_manifest_sha256=expected,authored_frozen_files=8,private_resources_verified=len(resources['private_files'])+1,bindings=bindings)
(OUT/'source-bindings.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
