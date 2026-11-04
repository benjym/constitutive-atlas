import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from atlas.model import ROOT, all_models
from atlas.research import export_database


class CatalogueTests(unittest.TestCase):
    def test_directory_coverage_has_resolvable_provenance(self):
        manifest = json.loads((ROOT / 'catalogue/manifest.json').read_text())
        entries = {e['id']: e for e in manifest['models']}
        self.assertEqual(len(entries), len(manifest['models']))
        coverage = json.loads((ROOT / 'catalogue/discovery/soilmodels-2026-10-30.json').read_text())
        # Frozen directory observation, including family and extension overviews.
        self.assertEqual(len(coverage['entries']), 13)
        self.assertEqual(len({e['url'] for e in coverage['entries']}), 13)
        for record in coverage['entries']:
            self.assertTrue(record['model_ids'])
            for ident in record['model_ids']:
                with self.subTest(directory=record['url'], model=ident):
                    self.assertIn(ident, entries)
                    self.assertIn(record['url'], [s['url'] for s in entries[ident]['catalogue_sources']])
        # Discovery must not advertise candidates as executable definitions.
        definitions = {m['id'] for m in all_models()}
        for entry in entries.values():
            self.assertEqual(entry['executable'], entry['id'] in definitions)
            if not entry['executable']:
                self.assertEqual(entry['status'], 'candidate')
                self.assertTrue(entry['capability_gap'])

    def test_database_keeps_candidate_and_executable_sources(self):
        manifest = json.loads((ROOT / 'catalogue/manifest.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'atlas.sqlite'
            # Re-export must be idempotent rather than accumulating citations.
            for _ in range(2):
                export_database(path)
                with sqlite3.connect(path) as db:
                    self.assertEqual(db.execute('SELECT COUNT(*) FROM models').fetchone()[0], len(manifest['models']))
                    for entry in manifest['models']:
                        urls = {r[0] for r in db.execute('SELECT url FROM sources WHERE model_id=?', (entry['id'],))}
                        expected = [s['url'] for s in entry.get('catalogue_sources', []) + entry.get('research_sources', [])]
                        if entry.get('discovery_url'):
                            expected.append(entry['discovery_url'])
                        self.assertTrue(set(expected) <= urls, entry['id'])
                    row = db.execute('SELECT executable,definition_json FROM models WHERE id=?', ('vibe-2026',)).fetchone()
                    self.assertEqual(row, (0, None))
                    elastic = next(m for m in all_models() if m['id'] == 'linear-elastic')
                    urls = {r[0] for r in db.execute('SELECT url FROM sources WHERE model_id=?', ('linear-elastic',))}
                    self.assertTrue({s['url'] for s in elastic['sources']} <= urls)
                    count = db.execute('SELECT COUNT(*) FROM sources').fetchone()[0]
                    if _:
                        self.assertEqual(count, prior_count)
                    prior_count = count
