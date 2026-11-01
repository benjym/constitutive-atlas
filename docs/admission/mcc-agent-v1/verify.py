"""Verify exact review, model, artifacts and registered approval without building."""
from pathlib import Path
import hashlib,json
from atlas.agent_review import approval_entry,validate_review
root=Path(__file__).resolve().parents[3]
packet=root/'docs/reviews/mcc-agent-v1'
manifest=json.loads((packet/'manifest.json').read_text())
for name,expected in manifest['files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
path=root/'catalogue/agent-reviews/mcc-agent-v1.json'
assert path.read_bytes()==(packet/'agent-review.json').read_bytes()
validate_review(path,root,for_approval=True)
entry=approval_entry(path,root)
assert entry==json.loads((Path(__file__).parent/'approval-entry.json').read_text())
registered=[x for x in json.loads((root/'catalogue/approved-models.json').read_text())['models'] if x['id']==entry['id']]
assert registered==[entry]
print(f"MCC: {len(manifest['files'])} bindings, independent acceptance and exact registered approval verified")
