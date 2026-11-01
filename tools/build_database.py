"""Package the public SQLite atlas against the website's exact model catalogue."""
import argparse
from contextlib import closing
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.model import all_models
from atlas.research import approved_definitions, export_database

DATABASE = 'atlas.sqlite'
MANIFEST = 'atlas-database.json'
PUBLIC_TABLES = frozenset(('models', 'sources', 'publications', 'publication_relations',
                          'publication_models', 'publication_screening', 'screening_evidence',
                          'model_approvals', 'agent_reviews'))


def _sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _models(values):
    if not isinstance(values, list) or any(not isinstance(m, dict) or not isinstance(m.get('id'), str) for m in values):
        raise ValueError('Invalid packaged model catalogue')
    indexed = {m['id']: m for m in values}
    if len(indexed) != len(values):
        raise ValueError('Duplicate packaged model identity')
    return indexed


def _source_inputs(ordinary, approvals):
    names = {
        'catalogue/manifest.json', 'catalogue/approved-models.json',
        'catalogue/publications.json', 'catalogue/screening.jsonl',
        'atlas/research.py', 'atlas/agent_review.py', 'tools/build_database.py',
        'catalogue/agent-reviews/source-archive-map.json',
    }
    names.update('models/' + mid + '.json' for mid in ordinary)
    for approval in approvals:
        names.add(approval['definition']['path'])
        if approval.get('review', {}).get('kind') == 'agent-model-review':
            names.add(approval['review']['path'])
    result = {}
    for name in sorted(names):
        relative = Path(name)
        source = (ROOT / relative).resolve()
        if relative.is_absolute() or '..' in relative.parts or not source.is_relative_to(ROOT):
            raise ValueError('Unsafe database source input')
        result[name] = _sha(source)
    return result


def bundle(destination):
    destination = Path(destination)
    ordinary = _models(all_models())
    # Compare and hash the same bytes; later reads cannot redefine the baseline.
    package_bytes = {name: (destination / name).read_bytes()
                     for name in ('models.json', 'catalogue.json')}
    source_catalogue = (ROOT / 'catalogue/manifest.json').read_bytes()
    package_inputs = {name: hashlib.sha256(data).hexdigest()
                      for name, data in package_bytes.items()}
    metadata = json.loads(package_bytes['models.json'])
    packaged = _models(metadata.get('models'))
    if _canonical(packaged) != _canonical(ordinary):
        raise ValueError('Database and packaged model definitions differ')
    catalogue = json.loads(package_bytes['catalogue.json'])
    if _canonical(catalogue) != _canonical(json.loads(source_catalogue)):
        raise ValueError('Database and packaged discovery catalogue differ')
    approved, approvals = approved_definitions()
    inputs = _source_inputs(ordinary, approvals)
    if inputs['catalogue/manifest.json'] != hashlib.sha256(source_catalogue).hexdigest():
        raise ValueError('Database source catalogue changed during capture')
    expected = {**ordinary, **approved}
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.database-', dir=destination) as temporary:
        staging = Path(temporary)
        database = staging / DATABASE
        export_database(database)
        with closing(sqlite3.connect(database)) as connection:
            tables = {name for (name,) in connection.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")}
            if tables != PUBLIC_TABLES:
                raise ValueError('Database contains an unsupported public table set')
            if connection.execute('PRAGMA integrity_check').fetchall() != [('ok',)]:
                raise ValueError('Database integrity check failed')
            if connection.execute('PRAGMA foreign_key_check').fetchall():
                raise ValueError('Database contains broken foreign keys')
            definitions = {mid: json.loads(raw) for mid, raw in connection.execute(
                'SELECT id,definition_json FROM models WHERE definition_json IS NOT NULL')}
            executable = {mid for (mid,) in connection.execute('SELECT id FROM models WHERE executable=1')}
            if _canonical(definitions) != _canonical(expected) or executable != set(ordinary):
                raise ValueError('Database changed model definitions or ordinary engine membership')
            exported = {identity: json.loads(raw) for identity, raw in connection.execute(
                'SELECT id,record_json FROM model_approvals')}
            if _canonical(exported) != _canonical({a['id']: a for a in approvals}):
                raise ValueError('Database changed exact approval records')
            reviews = {identity: json.loads(raw) for identity, raw in connection.execute(
                'SELECT id,record_json FROM agent_reviews')}
            expected_reviews = {}
            for approval in approvals:
                review = approval.get('review', {})
                if review.get('kind') == 'agent-model-review':
                    record = json.loads((ROOT / review['path']).read_text())
                    expected_reviews[record['id']] = record
            if _canonical(reviews) != _canonical(expected_reviews):
                raise ValueError('Database changed exact agent review records')
            sources = Counter(connection.execute('SELECT model_id,url,locator,role FROM sources'))
            required = Counter((mid, source['url'], source['locator'], source['role'])
                               for mid, model in expected.items() for source in model.get('sources', []))
            if any(sources[row] < count for row, count in required.items()):
                raise ValueError('Database omitted model source provenance')
            counts = {table: connection.execute('SELECT count(*) FROM ' + table).fetchone()[0]
                      for table in ('models', 'sources', 'publications', 'model_approvals', 'agent_reviews')}
        if _canonical(_models(all_models())) != _canonical(ordinary):
            raise ValueError('Ordinary model membership changed during export')
        if inputs != _source_inputs(ordinary, approvals) or any(
                _sha(destination / name) != digest for name, digest in package_inputs.items()):
            raise ValueError('Database package inputs changed during export')
        manifest = {
            'schema_version': '0.1', 'kind': 'constitutive-atlas-database-package',
            'database': {'path': DATABASE, 'sha256': _sha(database), 'bytes': database.stat().st_size,
                         'media_type': 'application/vnd.sqlite3'},
            'counts': counts, 'definition_count': len(definitions),
            'ordinary_engine_model_ids': sorted(ordinary),
            'package_inputs': package_inputs, 'source_inputs': inputs,
            'scope': 'Public model, source, publication and approval records. Ordinary engine membership, '
                     'review scope and experimental validation remain separate fields.',
            'measurements_included': False, 'source_documents_included': False,
            'compiled_engines_included': False,
        }
        (staging / MANIFEST).write_text(json.dumps(manifest, indent=2, allow_nan=False) + '\n')
        # Restore the previous database if the second ordinary replacement fails.
        # This is exception recovery, not a crash-atomic two-file transaction.
        previous = staging / 'previous.sqlite'
        target = destination / DATABASE
        existed = target.exists()
        if existed:
            shutil.copyfile(target, previous)
        database.replace(target)
        try:
            (staging / MANIFEST).replace(destination / MANIFEST)
        except OSError:
            if existed:
                previous.replace(target)
            else:
                target.unlink()
            raise
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True,
                        help='Website directory already containing matching models.json and catalogue.json')
    args = parser.parse_args()
    manifest = bundle(args.output)
    print(f"Packaged {manifest['definition_count']} definitions in {args.output / DATABASE}")


if __name__ == '__main__':
    main()
