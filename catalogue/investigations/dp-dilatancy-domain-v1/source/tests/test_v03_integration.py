"""Current draft integration and original document-bound source identities."""
import hashlib
import json
from pathlib import Path
import unittest
from atlas.evidence import checked_receipt
from atlas.initialization import initialize_state
from atlas.model import ROOT, defaults, load


class V03Integration(unittest.TestCase):
    def test_original_receipt_chains_keep_their_exact_source_bytes(self):
        for version in range(1, 6):
            path = ROOT / f'catalogue/source-replays/v03-integration-identity-v{version}/inventory.json'
            rows = json.loads(path.read_text())['references']
            self.assertTrue(rows)
            for row in rows:
                with self.subTest(document=row['document'], source=row['original_path']):
                    self.assertEqual(hashlib.sha256((ROOT / row['document']).read_bytes()).hexdigest(), row['document_sha256'])
                    self.assertEqual(checked_receipt(ROOT, row['document'], row['original_path'], row['sha256']),
                                     (ROOT / row['archived_path']).resolve())

    def test_draft_matches_the_tested_definition_and_initializes_explicitly(self):
        path = ROOT / 'models/barodesy-clay-2017.json'
        frozen = ROOT / 'catalogue/investigations/barodesy2017-preview-v2/models/barodesy-clay-2017.json'
        self.assertEqual(path.read_bytes(), frozen.read_bytes())
        model = load(path)
        self.assertEqual(model['schema_version'], '0.3')
        self.assertEqual(model['status'], 'draft')
        state = {'sigma': [100000, 100000, 100000, 0, 0, 0], 'e': .8}
        result = initialize_state(model, state, defaults(model))
        self.assertEqual(result['initial'], state['sigma'] + [.8])
        catalogue = json.loads((ROOT / 'catalogue/manifest.json').read_text())['models']
        entry = next(row for row in catalogue if row['id'] == model['id'])
        self.assertIs(entry['executable'], True)
        self.assertEqual(entry['status'], model['status'])
        self.assertIn('https://doi.org/10.1007/s11440-016-0458-4', [s['url'] for s in model['sources']])
