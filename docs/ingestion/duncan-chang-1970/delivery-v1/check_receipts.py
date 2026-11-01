"""Verify this source-gate receipt; this is not constitutive verification."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def main():
    checked = []
    missing_private = []
    for row in json.loads((HERE / 'input-pins.json').read_text())['files']:
        path = ROOT / row['path']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == row['sha256'], row['path']
        checked.append(row['path'])
    receipt = json.loads((HERE / 'source-receipts.json').read_text())
    for key in ('target_original', 'target_erratum'):
        assert receipt[key]['received'] is False
        assert receipt[key]['sha256'] is None
    for row in receipt['private_received']:
        path = ROOT / row['private_path']
        if not path.exists():
            missing_private.append(row['private_path'])
            continue
        data = path.read_bytes()
        assert len(data) == row['bytes']
        assert hashlib.sha256(data).hexdigest() == row['sha256'], str(path)
        assert data.startswith(b'%PDF-')
        assert row['source_equations_available'] is False
        checked.append(row['private_path'])
    assert receipt['source_complete'] is False
    assert receipt['capability_gap_proven'] is False
    print(json.dumps({'result': 'pass', 'checks': len(checked),
                      'missing_private': missing_private,
                      'source_complete': False, 'constitutive_verification': False}, indent=2))


if __name__ == '__main__':
    main()
