"""Static screening validation and SQLite export; no material execution."""
import copy
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import patch

from atlas.dsl import ValidationError
from atlas.research import export_database, load_screening, validate_screening


class ScreeningExportTests(unittest.TestCase):
    def test_export_preserves_decisions_occurrences_and_doi_identity(self):
        records = load_screening()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'atlas.sqlite'
            for _ in range(2):
                export_database(path)
                with closing(sqlite3.connect(path)) as db:
                    self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
                    exported = {i: json.loads(r) for i, r in db.execute(
                        'SELECT publication_id,record_json FROM publication_screening')}
                    self.assertEqual(exported, {r['publication_id']: r for r in records})
                    evidence = db.execute('SELECT publication_id,path,sha256,locator,url FROM screening_evidence').fetchall()
                    self.assertCountEqual(evidence, [(r['publication_id'], e['path'], e['sha256'], e['locator'], e['url'])
                        for r in records for e in r['evidence']])
                    counts = dict(db.execute('SELECT decision,COUNT(*) FROM publication_screening GROUP BY decision'))
                    self.assertEqual(counts, {'exclude': 34, 'include-for-full-text': 1, 'unresolved': 2})
                    self.assertEqual(len(evidence), 53)
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM publications').fetchone()[0], 43)
                    # Shared DOI: richer lineage remains canonical, original decision survives unchanged.
                    pid = 'doi:10.1002/nag.1610181203'
                    node = json.loads(db.execute('SELECT record_json FROM publications WHERE id=?', (pid,)).fetchone()[0])
                    self.assertEqual(node['version_role'], 'version-of-record')
                    self.assertEqual(exported[pid]['decision'], 'include-for-full-text')

    def test_invalid_evidence_and_claims_are_rejected(self):
        records = load_screening()
        mutations = [
            lambda r: r.append(copy.deepcopy(r[0])),
            lambda r: r[0].update(publication_id='doi:10.9999/wrong'),
            lambda r: r[0].update(model_ids=['missing-model']),
            lambda r: r[0].update(full_text_reviewed=True),
            lambda r: r[0].update(screening_basis='full-text'),
            lambda r: r[0].update(independent_review='accepted'),
            lambda r: r[0].update(reviewed_at='2026-02-30'),
            lambda r: r[0]['evidence'][0].update(path='../outside.json'),
            lambda r: r[0]['evidence'][0].update(sha256='0' * 64),
            lambda r: r[0]['evidence'][0].update(locator='/response/message/items/9999'),
            lambda r: r[0]['evidence'][0].update(locator='/response/message/items/-1'),
            lambda r: r[0]['evidence'][0].update(url='https://example.org/wrong-search'),
            lambda r: r[0].update(title='different publication'),
            lambda r: r[0]['evidence'].append(copy.deepcopy(r[0]['evidence'][0])),
        ]
        for i, mutate in enumerate(mutations):
            with self.subTest(mutation=i):
                bad = copy.deepcopy(records)
                mutate(bad)
                with self.assertRaises(ValidationError):
                    validate_screening(bad)

    def test_failed_prevalidation_leaves_existing_database_unchanged(self):
        records = load_screening()
        records[0]['evidence'][0]['sha256'] = '0' * 64
        with tempfile.TemporaryDirectory() as directory:
            path = export_database(Path(directory) / 'atlas.sqlite')
            before = path.read_bytes()
            with patch('atlas.research.load_screening', side_effect=lambda: validate_screening(records)):
                with self.assertRaises(ValidationError):
                    export_database(path)
            self.assertEqual(path.read_bytes(), before)
