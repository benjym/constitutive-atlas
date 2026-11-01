"""A reporting verdict cannot follow changed inputs or publish private siblings."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.build_tmd2_review import REVIEW, projection
from tools.build_benchmark import ROOT, PACKET, FILES, digest

class TMD2ReviewProjectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        target = self.root / REVIEW
        target.mkdir(parents=True)
        for name in ['manifest.json', 'decision.json', 'README.md']:
            shutil.copyfile(ROOT / REVIEW / name, target / name)
        self.assets = {name: (ROOT / PACKET / source).read_bytes() for name, source in FILES.items()}
        self.model_hash = '83777458ea437a3a7c1360117dbf435f7d763913cda399099ef2966e65a67e86'

    def test_exact_verdict_reasons_and_qualifications(self):
        assets, html = projection(self.root, self.assets, self.model_hash)
        self.assertEqual(set(assets), {'review/decision.json', 'review/review.md', 'review/review.html'})
        self.assertEqual(assets['review/decision.json'], (ROOT / REVIEW / 'decision.json').read_bytes())
        self.assertEqual(assets['review/review.md'], (ROOT / REVIEW / 'README.md').read_bytes())
        decision = json.loads(assets['review/decision.json'])
        for qualification in decision['remaining_qualifications']:
            self.assertIn(qualification, html)
        self.assertIn(digest(assets['review/decision.json']), html)
        self.assertIn('General IGS model admission', html)
        self.assertIn('experimental validation remain open', html)
        self.assertIn('../../tmd2.html', assets['review/review.html'].decode())

    def test_changed_review_or_manifest_rejected(self):
        for name in ['manifest.json', 'decision.json', 'README.md']:
            with self.subTest(name=name):
                path = self.root / REVIEW / name
                original = path.read_bytes()
                path.write_bytes(original + b' ')
                with self.assertRaisesRegex(ValueError, 'review .*mismatch'):
                    projection(self.root, self.assets, self.model_hash)
                path.write_bytes(original)

    def test_changed_benchmark_assets_rejected(self):
        for name in FILES:
            with self.subTest(name=name):
                changed = dict(self.assets)
                changed[name] += b' '
                with self.assertRaisesRegex(ValueError, '(scope|asset) mismatch'):
                    projection(self.root, changed, self.model_hash)

    def test_other_model_cannot_reuse_verdict(self):
        with self.assertRaisesRegex(ValueError, 'scope mismatch'):
            projection(self.root, self.assets, '0' * 64)

    def test_private_review_siblings_excluded(self):
        (self.root / REVIEW / 'private-measurements.json').write_text('PRIVATE_SENTINEL')
        (self.root / REVIEW / 'private-inputs.json').write_text('PRIVATE_SENTINEL')
        assets, html = projection(self.root, self.assets, self.model_hash)
        self.assertNotIn('PRIVATE_SENTINEL', html)
        self.assertTrue(all(b'PRIVATE_SENTINEL' not in raw for raw in assets.values()))
