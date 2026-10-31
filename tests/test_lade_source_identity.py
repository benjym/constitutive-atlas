"""Primary metadata and catalogue propagation for the Lade–Duncan DOI repair."""
from contextlib import closing
import hashlib
import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from atlas.model import ROOT
from atlas.research import export_database

HERE = ROOT/'docs/ingestion/lade-duncan-1975/identity-v1'

class LadeSourceIdentityTests(unittest.TestCase):
    def test_primary_metadata_distinguishes_two_publications(self):
        good = json.loads((HERE/'crossref-204.json').read_bytes())['message']
        bad = json.loads((HERE/'crossref-208.json').read_bytes())['message']
        self.assertEqual(good['DOI'].lower(), '10.1061/ajgeb6.0000204')
        self.assertEqual(good['title'], ['Elastoplastic Stress-Strain Theory for Cohesionless Soil'])
        self.assertEqual([a['family'] for a in good['author']], ['Lade', 'Duncan'])
        self.assertEqual(good['page'], '1037-1053')
        self.assertEqual(good['published']['date-parts'], [[1975, 10]])
        self.assertEqual(bad['DOI'].lower(), '10.1061/ajgeb6.0000208')
        self.assertEqual(bad['title'], ['Uplift Capacity of Buried Model Piles in Sand'])
        self.assertEqual([a['family'] for a in bad['author']], ['Das', 'Seeley'])

    def test_receipt_and_pre_correction_catalogue_are_exact(self):
        receipt = json.loads((HERE/'receipt.json').read_bytes())
        for record in [receipt['correct'], receipt['rejected_previous_binding'], receipt['previous_catalogue']]:
            self.assertEqual(hashlib.sha256((ROOT/record['path']).read_bytes()).hexdigest(), record['sha256'])
        previous = json.loads((ROOT/receipt['previous_catalogue']['path']).read_bytes())
        entry = next(m for m in previous['models'] if m['id']=='lade-duncan-1975')
        self.assertTrue(entry['discovery_url'].endswith('0000208'))
        self.assertFalse(receipt['source_complete'])
        self.assertFalse(receipt['publisher_pdf_request']['is_pdf'])
        self.assertEqual(receipt['publisher_pdf_request']['status'], 403)
        manifest = json.loads((HERE/'manifest.json').read_bytes())
        for f,h in manifest['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/f).read_bytes()).hexdigest(), h)

    def test_corrected_source_reaches_export_without_admitting_candidate(self):
        manifest = json.loads((ROOT/'catalogue/manifest.json').read_bytes())
        entry = next(m for m in manifest['models'] if m['id']=='lade-duncan-1975')
        self.assertEqual(entry['discovery_url'], 'https://doi.org/10.1061/AJGEB6.0000204')
        self.assertEqual(entry['status'], 'candidate'); self.assertFalse(entry['executable'])
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/'atlas.sqlite'; export_database(path)
            with closing(sqlite3.connect(path)) as db:
                urls = {row[0] for row in db.execute('SELECT url FROM sources WHERE model_id=?', (entry['id'],))}
                self.assertIn(entry['discovery_url'], urls)
                self.assertNotIn('https://doi.org/10.1061/AJGEB6.0000208', urls)
                row=db.execute('SELECT executable,definition_json FROM models WHERE id=?',(entry['id'],)).fetchone()
                self.assertEqual(row,(0,None))

if __name__=='__main__': unittest.main()
