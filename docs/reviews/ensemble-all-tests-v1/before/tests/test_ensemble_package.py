import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from tools.build_ensemble_web import bundle, ROOT

class EnsemblePackageTests(unittest.TestCase):
    def test_pinned_lossless_radial_source_and_deterministic_assets(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination=Path(temporary)
            manifest=bundle(destination)
            raw=(destination/manifest['path']).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(),manifest['sha256'])
            self.assertEqual(len(raw),manifest['size_bytes'])
            record=json.loads(raw)
            source=json.loads(gzip.decompress((ROOT/'data/curated/OPARA-TXCD-100.json.gz').read_bytes()))
            self.assertEqual(len(record['rows']),1438)
            for actual,original in zip(record['rows'],source['rows']):
                for key,value in actual.items():self.assertEqual(value,original[key])
            self.assertEqual(sum(r['axial_strain']<=.01 for r in record['rows']),95)
            self.assertEqual(record['provenance'],source['provenance'])
            self.assertEqual(bundle(destination),manifest)
            self.assertEqual((destination/manifest['path']).read_bytes(),raw)
    def test_website_wires_explorer_assets(self):
        text=(ROOT/'tools/build_web.py').read_text()
        for name in ['ensemble.mjs','ensemble-plots.mjs','ensemble-queue.mjs','ensemble-view.mjs','ensemble-worker.mjs','ensemble.css']:
            self.assertIn(name,text)
        self.assertIn('bundle_ensemble(dest)',text)
        html=(ROOT/'web/index.html').read_text()
        for token in ['href="#ensemble"','id="ensemble"','src="ensemble-view.mjs"','href="ensemble.css"']:
            self.assertIn(token,html)

    def test_plotly_is_bundled_with_exact_bytes_and_license(self):
        with tempfile.TemporaryDirectory() as temporary:
            destination=Path(temporary)
            bundle(destination)
            notice=json.loads((destination/'vendor/plotly-NOTICE.json').read_text())
            self.assertEqual(notice['version'],'4.1.1')
            self.assertEqual(notice['license'],'MIT')
            for name,receipt in notice['files'].items():
                content=(destination/'vendor'/name).read_bytes()
                self.assertEqual(hashlib.sha256(content).hexdigest(),receipt['sha256'])
                self.assertEqual(len(content),receipt['size_bytes'])
                self.assertEqual(content,(ROOT/'web/vendor'/name).read_bytes())
            self.assertIn('MIT License',(destination/'vendor/plotly-LICENSE.txt').read_text())
            self.assertTrue((destination/'vendor/plotly-basic-4.1.1.min.js').read_text().startswith('/**\n* plotly.js (basic - minified) v4.1.1'))
