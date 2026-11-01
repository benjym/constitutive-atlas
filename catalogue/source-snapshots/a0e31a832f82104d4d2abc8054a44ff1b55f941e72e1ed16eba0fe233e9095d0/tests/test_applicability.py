"""Applicability inventory integrity, not scientific suitability testing."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from atlas.applicability import load_matrix, validate_matrix
from atlas.model import ROOT

MATRIX = ROOT/'catalogue/applicability/kfs-development-v1.json'

class ApplicabilityMatrixTests(unittest.TestCase):
    def setUp(self): self.matrix = json.loads(MATRIX.read_bytes())

    def test_complete_current_inventory_with_no_eligibility_promotion(self):
        report = load_matrix(MATRIX)
        self.assertEqual(report['model_count'], 9)
        self.assertEqual(report['whole_test_count'], 11)
        self.assertEqual(report['assessment_counts'], {'not_assessed': 8, 'conditional_development_evidence': 1})
        self.assertEqual(report['scientific_eligibility'], 'undetermined')
        self.assertEqual(report['independent_review'], 'pending')
        self.assertEqual(report['matrix_sha256'], hashlib.sha256(MATRIX.read_bytes()).hexdigest())
        row = next(r for r in self.matrix['rows'] if r['assessment'] != 'not_assessed')
        self.assertEqual(row['model']['id'], 'hypoplastic-sand-vw96')
        self.assertTrue(any('TMD7' in x and '2%' in x for x in row['limitations']))

    def test_missing_duplicate_unknown_and_stale_model_rows_reject(self):
        for mutation in ['missing', 'duplicate', 'unknown', 'stale']:
            matrix = copy.deepcopy(self.matrix)
            if mutation == 'missing': matrix['rows'].pop()
            elif mutation == 'duplicate': matrix['rows'].append(matrix['rows'][0])
            elif mutation == 'unknown': matrix['rows'][0]['model']['id'] = 'unknown'
            else: matrix['rows'][0]['model']['sha256'] = '0'*64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): validate_matrix(matrix)

    def test_changed_allocation_and_source_bytes_cannot_inherit_assessment(self):
        for target in ['allocation', 'source']:
            matrix = copy.deepcopy(self.matrix)
            record = matrix['dataset']['allocation'] if target == 'allocation' else matrix['rows'][0]['evidence'][0]
            record['sha256'] = '0'*64
            with self.subTest(target=target), self.assertRaisesRegex(ValueError, 'identity mismatch'):
                validate_matrix(matrix)

    def test_unsupported_eligibility_review_and_omitted_conditions_reject(self):
        for mutation in ['eligible', 'accepted', 'reviewer', 'no_conditions', 'status']:
            matrix = copy.deepcopy(self.matrix)
            if mutation == 'eligible': matrix['rows'][0]['scientific_eligibility'] = 'eligible'
            elif mutation == 'accepted': matrix['independent_review'] = 'accepted'
            elif mutation == 'reviewer': matrix['reviewer'] = 'unassigned person'
            elif mutation == 'no_conditions': matrix['rows'][0]['prerequisites'] = []
            else: matrix['rows'][0]['assessment'] = 'validated'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError): validate_matrix(matrix)

    def test_unsafe_private_and_missing_evidence_pins_reject(self):
        for path in ['docs/../../outside', '/private/tmp/source', 'data/raw/source.dat', 'docs/missing-source.md']:
            matrix = copy.deepcopy(self.matrix); matrix['rows'][0]['evidence'][0]['path'] = path
            with self.subTest(path=path), self.assertRaises((ValueError, FileNotFoundError)):
                validate_matrix(matrix)
        self.matrix['rows'][0]['evidence'] = []
        with self.assertRaises(ValueError): validate_matrix(self.matrix)

    def test_checker_reads_only_explicit_source_study_and_model_metadata(self):
        allowed = {MATRIX}
        allowed.update(ROOT/r['model']['path'] for r in self.matrix['rows'])
        for r in self.matrix['rows']: allowed.update(ROOT/e['path'] for e in r['evidence'])
        allowed.update(ROOT/self.matrix['dataset'][name]['path'] for name in ['allocation', 'reservations'])
        original = Path.read_bytes; opened = []
        def read(path):
            self.assertIn(path, allowed, 'unexpected response/other file access')
            opened.append(path); return original(path)
        before = copy.deepcopy(self.matrix)
        with patch.object(Path, 'read_bytes', read): report = load_matrix(MATRIX)
        self.assertEqual(report['response_files_read'], 0)
        self.assertEqual(set(opened), allowed)
        self.assertEqual(self.matrix, before)

    def test_cli_failure_and_strict_duplicate_keys(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d)/'matrix.json'
            path.write_text('{"schema_version":"0.1","schema_version":"0.1"}')
            result = subprocess.run([sys.executable, '-B', str(ROOT/'tools/check_applicability.py'), str(path)], capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, '')
            self.assertIn('duplicate', result.stderr)

if __name__ == '__main__': unittest.main()
