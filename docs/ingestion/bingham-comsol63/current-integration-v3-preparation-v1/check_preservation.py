#!/usr/bin/env python3
"""Read-only current-e6f06114 database and ordinary-catalogue preservation gate."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
BASELINE = 'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1/baseline-public-records.json'
MODEL = 'bingham-comsol63-mises-perfect-zero-spin-ode'
SHA = '6c5ee29c5c8cfbe18eaac09808a86ed7b656c8716511409bb23ecd0d3ad89850'
EXPECTED = {'models': 49, 'model_approvals': 26, 'agent_reviews': 22, 'sources': 205}

def bag(rows):
    return Counter(json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':')) for row in rows)

def preserved(old, new, expected):
    if len(new) != expected:
        raise ValueError(f'Count mismatch: {len(new)} != {expected}')
    missing = bag(old) - bag(new)
    if missing:
        raise ValueError(f'Prior rows changed or lost: {sum(missing.values())}')
    remaining = bag(new) - bag(old)
    return [json.loads(row) for row, count in remaining.items() for _ in range(count)]

def check(database, catalogue, review_path):
    pins = json.loads((HERE/'INPUTS.json').read_text())['release_inputs']
    base_bytes = (ROOT/BASELINE).read_bytes()
    if hashlib.sha256(base_bytes).hexdigest() != pins[BASELINE]:
        raise ValueError('Immutable baseline bytes changed')
    baseline = json.loads(base_bytes)
    ordinary_bytes = catalogue.read_bytes()
    ordinary = json.loads(ordinary_bytes)
    if hashlib.sha256(ordinary_bytes).hexdigest() != baseline['ordinary_catalogue_sha256']:
        raise ValueError('Ordinary catalogue exact bytes changed')
    if len(ordinary['models']) != 15 or ordinary['models'] != baseline['ordinary_catalogue']['models']:
        raise ValueError('All fifteen ordinary definitions must be unchanged')
    if MODEL in {row['id'] for row in ordinary['models']}:
        raise ValueError('Bingham must not enter ordinary strain-path catalogue')
    if not database.is_file():
        raise ValueError('Database absent')
    delta = {}
    with sqlite3.connect(database.resolve().as_uri() + '?mode=ro', uri=True) as connection:
        connection.row_factory = sqlite3.Row
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
        if tables != set(baseline['tables']):
            raise ValueError('Database table membership changed')
        for table, old in baseline['tables'].items():
            # Table names come only from the hash-pinned baseline.
            rows = [dict(row) for row in connection.execute('SELECT * FROM "' + table + '"')]
            delta[table] = preserved(old, rows, EXPECTED.get(table, baseline['counts'][table]))
    if len(delta['models']) != 1 or delta['models'][0]['id'] != MODEL or delta['models'][0]['executable'] != 0:
        raise ValueError('Only exact nonordinary Bingham model may be added')
    model = json.loads(delta['models'][0]['definition_json'])
    candidate = ROOT/'docs/ingestion/bingham-comsol63/source-v1/candidate.json'
    if hashlib.sha256(candidate.read_bytes()).hexdigest() != SHA or model != json.loads(candidate.read_text()):
        raise ValueError('Database model differs from frozen Bingham definition')
    expected_model = {'id':MODEL, 'name':model['name'], 'family':model['family'], 'status':model['status'], 'executable':0, 'definition_json':json.dumps(model)}
    if delta['models'] != [expected_model]:
        raise ValueError('Added model metadata does not exactly match the frozen definition')
    expected_sources = [dict(model_id=MODEL, **source) for source in model['sources']]
    if bag(delta['sources']) != bag(expected_sources):
        raise ValueError('Source delta must be exactly the three source-confirmed Bingham rows')
    review_path = review_path.resolve()
    if review_path.parent != (ROOT/'catalogue/agent-reviews').resolve():
        raise ValueError('Review must be canonical')
    sys.path.insert(0, str(ROOT))
    from atlas.agent_review import approval_entry
    approval = approval_entry(review_path, root=ROOT)
    review = json.loads(review_path.read_text())
    if approval['model_id'] != MODEL or approval['definition']['sha256'] != SHA:
        raise ValueError('Review model mismatch')
    expected_approval = {'id': approval['id'], 'model_id': MODEL,
        'definition_path': approval['definition']['path'], 'definition_sha256': SHA,
        'record_json': json.dumps(approval)}
    expected_review = {'id': review['id'], 'model_id': MODEL,
        'path': review_path.relative_to(ROOT).as_posix(),
        'sha256': hashlib.sha256(review_path.read_bytes()).hexdigest(), 'record_json': json.dumps(review)}
    if delta['model_approvals'] != [expected_approval] or delta['agent_reviews'] != [expected_review]:
        raise ValueError('Database approval/review delta must equal actual generated E5 records')
    registry = json.loads((ROOT/'catalogue/approved-models.json').read_text())['models']
    if [entry for entry in registry if entry['model_id'] == MODEL] != [approval]:
        raise ValueError('Registry does not equal actual generated approval')
    return {'kind':'bingham-current-database-preservation-v1', 'pass':True,
        'prior_rows_preserved':baseline['counts'], 'counts':{**baseline['counts'], **EXPECTED},
        'ordinary_models_unchanged':15, 'database':str(database), 'catalogue_sha256':hashlib.sha256(ordinary_bytes).hexdigest()}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path, required=True)
    parser.add_argument('--catalogue', type=Path, required=True)
    parser.add_argument('--review', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.database, args.catalogue, args.review), indent=2))

if __name__ == '__main__':
    main()
