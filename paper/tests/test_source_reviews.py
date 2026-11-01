import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json
from analysis.source_reviews import validate_source_reviews


class SourceReviewIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'catalogue').mkdir()
        (self.root/'catalogue/manifest.json').write_text(json.dumps({'models': [{'id': 'norsand-1993'}]}))
        self.directory = self.root/'reviews'
        self.directory.mkdir()
        self.record = read_json(ROOT/'paper/study/source_formulations/norsand-1993.json')

    def validate(self):
        (self.directory/'review.json').write_text(json.dumps(self.record))
        return validate_source_reviews(self.directory, self.root)

    def test_review_does_not_require_executable_definition(self):
        records = self.validate()
        self.assertEqual(records[0]['paper_interpretation']['survey_admission'], 'pending')
        self.assertIsNone(records[0]['paper_interpretation']['independent_material_dimension'])

    def test_source_replacement_is_detected(self):
        pdf = self.root/'source.pdf'
        pdf.write_bytes(b'original source snapshot')
        self.record['source'].update(local_copy='source.pdf', sha256=digest(pdf))
        self.validate()
        pdf.write_bytes(b'replacement source')
        with self.assertRaisesRegex(ValueError, 'source bytes differ'):
            self.validate()

    def test_unpinned_local_source_is_rejected(self):
        self.record['source']['local_copy'] = 'source.pdf'
        with self.assertRaisesRegex(ValueError, 'supplied together'):
            self.validate()

    def test_unknown_atlas_identity_is_rejected(self):
        self.record['model_id'] = 'invented'
        with self.assertRaisesRegex(ValueError, 'known atlas identity'):
            self.validate()

    def test_claim_without_locator_is_rejected(self):
        self.record['claims'][0]['locator'] = ''
        with self.assertRaisesRegex(ValueError, 'evidence locators'):
            self.validate()

    def test_normalization_audit_needs_pinned_source(self):
        self.record['normalization_audit'] = {'source_sha256': None, 'inputs_sha256': {}}
        with self.assertRaisesRegex(ValueError, 'different source snapshot'):
            self.validate()

    def test_changed_derivation_requires_review(self):
        source = self.root/'source.pdf'
        source.write_bytes(b'reviewed source')
        derivation = self.root/'derivation.md'
        derivation.write_text('reviewed derivation')
        self.record['source'].update(local_copy='source.pdf', sha256=digest(source))
        self.record['normalization_audit'] = {
            'source_sha256': digest(source), 'inputs_sha256': {'derivation.md': digest(derivation)}}
        self.validate()
        derivation.write_text('changed transformation')
        with self.assertRaisesRegex(ValueError, 'audit input changed'):
            self.validate()


if __name__ == '__main__':
    unittest.main()
