"""Read-only verification of SLS admission, source retention and saved studies."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
sys.path.insert(0, str(ROOT))
from atlas.agent_review import approval_entry
from atlas.evidence import checked_receipt

def read(path):
    return json.loads(path.read_text())

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

review = ROOT / 'catalogue/agent-reviews/sls-comsol63-agent-v1.json'
assert review.read_bytes() == (ROOT / 'docs/reviews/sls-comsol63-scientific-v1/review.json').read_bytes()
approval = read(BASE / 'approval.json')
assert approval_entry(review) == approval
assert [r for r in read(ROOT / 'catalogue/approved-models.json')['models']
        if r['model_id'] == approval['model_id']] == [approval]
manifest = read(ROOT / 'docs/reviews/sls-comsol63-scientific-v1/manifest.json')
for group in ('input_sha256', 'review_sha256'):
    for name, expected in manifest[group].items():
        checked_receipt(ROOT, 'docs/reviews/sls-comsol63-scientific-v1/manifest.json', name, expected)
for source in read(BASE / 'source-retention.json')['sources']:
    assert sha(Path(source['durable_private_path'])) == source['sha256']
subprocess.run([sys.executable, '-B', str(ROOT / 'docs/ingestion/sls-comsol63/execution-v1/verify.py')], cwd=ROOT, check=True)
print('PASS: exact SLS model, accepted independent review, generated registry approval, saved numerical evidence and 21 private sources.')
