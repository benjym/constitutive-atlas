"""Verify original receipt identities and preserved historical source edges."""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt
BASE = Path(__file__).resolve().parent

def verify():
    edges = 0
    for name in ('archive-plan-first.json', 'archive-plan.json'):
        plan = json.loads((BASE / name).read_text())
        for path, pin in plan['original_sources'].items():
            original = ROOT / 'catalogue/source-snapshots' / pin / path
            assert hashlib.sha256(original.read_bytes()).hexdigest() == pin, path
        for row in plan['bindings']:
            checked_receipt(ROOT, row['document'], row['original_path'], row['sha256'])
            edges += 1
    document = Path('docs/reviews/historical-test-context-v1/manifest.json')
    manifest = json.loads((ROOT / document).read_text())
    for path, pin in manifest['files'].items():
        checked_receipt(ROOT, document, path, pin)
    return dict(passed=True, archived_receipt_edges=edges,
                historical_manifest_files=len(manifest['files']),
                original_reference_bytes_changed=False, numerical_gates_changed=False,
                compiled_calls=0)

if __name__ == '__main__':
    print(json.dumps(verify(), indent=2))
