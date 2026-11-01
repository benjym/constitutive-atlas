"""Recheck the exact pre-edit inventory, independent of unrelated new receipts."""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from atlas.evidence import checked_receipt


def main():
    before = json.loads((HERE/'frozen/bindings-before-v2.json').read_text())
    passed, retained, failures = [], [], []
    for row in before['primary_references'] + before['secondary_source_map_references']:
        if row['resolution'] == 'unresolved':
            retained.append(row)
            continue
        try:
            if row['resolution'] in ('archived-sidecar-entry', 'live-sidecar-entry'):
                # These original_path objects are historical map entries, not
                # primary receipt documents accepted by checked_receipt.
                snapshot = ROOT/'catalogue/source-snapshots'/row['sha256']/row['original_path']
                target = snapshot if snapshot.is_file() else ROOT/row['original_path']
                assert hashlib.sha256(target.read_bytes()).hexdigest() == row['sha256']
            else:
                checked_receipt(ROOT, row['document'], row['original_path'], row['sha256'])
            passed.append({k:row[k] for k in ('document','original_path','sha256')})
        except Exception as error:
            failures.append({'binding':row, 'error':str(error)})
    result = {'scope':'all previously resolvable bindings in exact pre-edit inventory',
              'passed':len(passed), 'retained_preexisting_unresolved':len(retained),
              'failures':failures}
    (HERE/'preservation-check.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
    assert not failures


if __name__ == '__main__':
    main()
