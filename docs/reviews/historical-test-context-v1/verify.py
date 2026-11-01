"""Verify source identities and all retained original receipt edges; no builds."""
import hashlib
import json
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt
from tests.historical_generation import contexts, verified

def verify():
    packet = Path(__file__).resolve().parent
    manifest = json.loads((packet / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == expected, name
    plan = json.loads((packet / 'archive-plan.json').read_text())
    for row in plan['references']:
        checked_receipt(ROOT, row['document'], row['original_path'], row['sha256'])
    data = contexts()
    for row in data['models'] + list(data['compilers'].values()) + list(data['catalogues'].values()) + data['expected_artifacts']:
        verified(row)
    return {'pass': True, 'original_receipt_edges': len(plan['references']), 'historical_models': len(data['models']), 'current_models': len(data['current_models'])}

if __name__ == '__main__':print(json.dumps(verify(), sort_keys=True))
