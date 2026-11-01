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
        for name in ['ensemble.mjs','ensemble-queue.mjs','ensemble-view.mjs','ensemble-worker.mjs','ensemble.css']:
            self.assertIn(name,text)
        self.assertIn('bundle_ensemble(dest)',text)
        html=(ROOT/'web/index.html').read_text()
        for token in ['href="#ensemble"','id="ensemble"','src="ensemble-view.mjs"','href="ensemble.css"']:
            self.assertIn(token,html)

    def test_retired_pages_cannot_reappear_through_the_release_packager(self):
        text=(ROOT/"tools/build_web.py").read_text()
        self.assertNotIn("bundle_power_creep(dest",text)
        manifest=json.loads((ROOT/"catalogue/manifest.json").read_text())
        for entry in manifest["models"]:
            if entry.get("public_timed_laboratory") is True:
                self.assertNotIn(entry.get("timed_laboratory"),["j2.html","sls.html","power-creep.html"])
