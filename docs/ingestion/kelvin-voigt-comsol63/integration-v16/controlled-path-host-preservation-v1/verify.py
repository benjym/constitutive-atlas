"""Replay installed archival bindings without requiring superseded live input bytes."""
from pathlib import Path
import hashlib,json,sys
B=Path(__file__).resolve().parent; R=B.parents[4]; sys.path.insert(0,str(R))
from atlas.evidence import checked_receipt,verify_manifest_files
sha=lambda data:hashlib.sha256(data).hexdigest()
n=json.loads((B/'receipt.json').read_text())
for doc,h in n['original_documents'].items():assert sha((R/doc).read_bytes())==h,doc
for row in n['preserved_bindings']:checked_receipt(R,row['document'],row['original_path'],row['sha256'])
verify_manifest_files(R,str((B/'receipt.json').relative_to(R)))
for row in n['current_source_snapshots']:assert sha((R/row['archived_path']).read_bytes())==row['sha256']
from atlas.agent_review import validate_review
count=0
for f in (R/'catalogue/agent-reviews').glob('*.json'):
 if f.name=='source-archive-map.json':continue
 record=json.loads(f.read_text())
 if record.get('kind')=='agent-model-review':validate_review(f,root=R,for_approval=record.get('status')=='accepted');count+=1
print('PASS',count,'agent reviews')
print(json.dumps({'passed':True,'preserved_bindings':len(n['preserved_bindings']),'original_documents':len(n['original_documents']),'source_inputs':len(n['current_source_snapshots']),'receipt_files':len(n['files'])},indent=2))
