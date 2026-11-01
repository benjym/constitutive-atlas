"""Recheck delivery identity and retained history without rebuilding artifacts."""
from pathlib import Path
import hashlib, json, tempfile, sqlite3
from atlas.evidence import checked_receipt
from atlas.model import load
from atlas.agent_review import validate_review
from atlas.research import export_database

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
model = 'power-creep-itasca900-both-active-ode'
definition = ROOT/'models/research/power-creep'/f'{model}.json'
assert sha(definition) == '67f3fabd6aecfda19b977bf3baeae2dce45f9081fa81a4436a750a41825a4bef'
load(definition)
freeze = json.loads((OUT/'interface-freeze-v2.json').read_text())
for name, digest in freeze['files'].items():
    assert sha(ROOT/name) == digest, name
edges = 0
for receipt in [OUT/'archive-result.json', OUT/'summary-update/archive-result.json']:
    record = json.loads(receipt.read_text())
    for name, digest in record['snapshots'].items():
        assert sha(ROOT/'catalogue/source-snapshots'/digest/name) == digest, name
    for edge in record['receipt_edges']:
        context = 'catalogue/agent-reviews/power-creep-agent-v2.json' if edge['document'] == 'catalogue/approved-models.json' else edge['document']
        assert sha(checked_receipt(ROOT, context, edge['path'], edge['sha256'])) == edge['sha256']
        edges += 1
validate_review(ROOT/'catalogue/agent-reviews/power-creep-agent-v2.json', for_approval=True)
with tempfile.TemporaryDirectory() as tmp:
    path = Path(tmp)/'atlas.sqlite'
    export_database(path)
    with sqlite3.connect(path) as db:
        status, executable, raw = db.execute('SELECT status,executable,definition_json FROM models WHERE id=?',(model,)).fetchone()
        assert json.loads(raw) == json.loads(definition.read_text())
        assert status == 'draft' and executable == 0
        assert db.execute('SELECT count(*) FROM model_approvals WHERE model_id=?',(model,)).fetchone()[0] >= 2
        assert db.execute('SELECT count(*) FROM agent_reviews WHERE model_id=?',(model,)).fetchone()[0] == 1
print(json.dumps(dict(ok=True, frozen_files=len(freeze['files']), historical_edges=edges,
                     exact_definition=True, accepted_agent_review=True, sqlite_identity=True), indent=2))
