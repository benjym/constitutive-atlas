"""Verify exact review, model, artifacts and registered approval without building."""
from pathlib import Path
import hashlib,json
from atlas.agent_review import approval_entry,validate_review
root=Path(__file__).resolve().parents[3]
packet=root/'docs/reviews/barodesy2017-agent-v1'
manifest=json.loads((packet/'manifest.json').read_text())
for name,expected in manifest['files'].items():
    assert hashlib.sha256((root/name).read_bytes()).hexdigest()==expected,name
path=root/'catalogue/agent-reviews/barodesy2017-agent-v1.json'
assert path.read_bytes()==(packet/'agent-review.json').read_bytes()
validate_review(path,root,for_approval=True)
entry=approval_entry(path,root)
assert entry==json.loads((Path(__file__).parent/'approval-entry.json').read_text())
registered=[x for x in json.loads((root/'catalogue/approved-models.json').read_text())['models'] if x['id']==entry['id']]
assert registered==[entry]
print(f"Barodesy2017: {len(manifest['files'])} bindings, independent acceptance and exact registered approval verified")

# Check the normal public projection preserves exact approval scope and bytes.
from atlas.review_export import collect
rows, originals, omitted = collect(root, {entry['model_id']})
row = next(x for x in rows if x['id'] == entry['id'].removesuffix('-approval'))
assert row['definition_current'] and row['registered_approval_id'] == entry['id']
assert row['scope'] == entry['scope']['use']
assert originals[path.relative_to(root).as_posix()] == path.read_bytes()
assert not any(n.startswith('.local/') for n in originals)
assert json.loads((Path(__file__).parent/'parent-results.json').read_text()) == json.loads((packet/'check-results.json').read_text())
print('Exact current definition, scoped approval, canonical public decision and deterministic parent result export verified')
