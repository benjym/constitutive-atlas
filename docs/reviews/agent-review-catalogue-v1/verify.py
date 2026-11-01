"""Check exact feature receipts and preserved historical source bindings only."""
from pathlib import Path
import hashlib
import json
from atlas.evidence import checked_receipt

ROOT = Path(__file__).resolve().parents[3]
PACKET = Path(__file__).resolve().parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def verify():
    manifest_path = (PACKET / 'manifest.json').relative_to(ROOT).as_posix()
    manifest = json.loads((PACKET / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        assert sha(checked_receipt(ROOT, manifest_path, name, expected)) == expected
    plan_path = (PACKET / 'archive-plan.json').relative_to(ROOT).as_posix()
    plan = json.loads((PACKET / 'archive-plan.json').read_text())
    for name, expected in plan['original_bytes'].items():
        assert sha(checked_receipt(ROOT, plan_path, name, expected)) == expected
    for reference in plan['references']:
        assert sha(checked_receipt(ROOT, reference['document'], reference['original_path'], reference['sha256'])) == reference['sha256']
    print(f"PASS: {len(manifest['files'])} feature/evidence files, {len(plan['original_bytes'])} retained source/map states and {len(plan['references'])} receipt edges.")

if __name__ == '__main__':
    verify()
