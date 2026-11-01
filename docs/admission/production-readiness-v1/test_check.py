"""Negative checks for stale evidence and accidental scientific promotion."""
import contextlib
import copy
import hashlib
import importlib.util
import io
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('admission_preflight', HERE / 'check.py')
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class AdmissionPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.work = CHECK.read_json(HERE / 'work-packages.json')
        cls.decisions = CHECK.read_json(HERE / 'decisions-template.json')
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        for name in cls.work['inputs']:
            target = cls.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(CHECK.ROOT / name, target)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def assess(self, work=None, decisions=None):
        return CHECK.assess(self.root, work or self.work, decisions or self.decisions)

    def test_intact_packet_remains_blocked_and_cli_gate_is_nonzero(self):
        result = self.assess()
        self.assertEqual(result['packet_integrity'], 'passed')
        self.assertEqual(result['scientific_admission'], 'blocked')
        self.assertEqual(result['unsigned_decision_count'], 17)
        self.assertEqual(result['compiled_calls'], 0)
        with patch.object(sys, 'argv', ['check.py', '--repo', str(self.root), '--require-admitted']):
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(CHECK.main(), 2)

    def test_changed_definition_and_damaged_report_reject(self):
        for name in ('models/linear-elastic.json',
                     'catalogue/evidence/reports/modified-cam-clay-scalar-v2.json'):
            target = self.root / name
            original = target.read_bytes()
            try:
                target.write_bytes(original + b'\n')
                with self.assertRaisesRegex(ValueError, 'pinned input changed'):
                    self.assess()
            finally:
                target.write_bytes(original)

    def test_stale_review_rejects_even_with_new_container_hash(self):
        work = copy.deepcopy(self.work)
        ref = work['models'][0]['pending_review']
        target = self.root / ref['path']
        original = target.read_bytes()
        try:
            review = CHECK.read_json(target)
            review['model']['definition_sha256'] = '0' * 64
            target.write_text(CHECK.json.dumps(review))
            digest = hashlib.sha256(target.read_bytes()).hexdigest()
            work['inputs'][ref['path']] = ref['sha256'] = digest
            with self.assertRaisesRegex(ValueError, 'stale review binding'):
                self.assess(work=work)
        finally:
            target.write_bytes(original)

    def test_unsigned_work_or_decision_cannot_claim_acceptance(self):
        work = copy.deepcopy(self.work)
        work['models'][0]['scientific_review_complete'] = True
        with self.assertRaisesRegex(ValueError, 'claims scientific acceptance'):
            self.assess(work=work)
        decisions = copy.deepcopy(self.decisions)
        decisions['answers']['linear-elastic'][0]['decision'] = 'accepted'
        with self.assertRaisesRegex(ValueError, 'unsigned decision template changed'):
            self.assess(decisions=decisions)
        work = copy.deepcopy(self.work)
        work['models'][0]['proposed_scope']['experimental_validation'] = True
        with self.assertRaisesRegex(ValueError, 'unsupported scope promotion'):
            self.assess(work=work)

    def test_paths_and_ambiguous_json_reject(self):
        with self.assertRaisesRegex(ValueError, 'unsafe packet input path'):
            CHECK.within(self.root, '../unowned.json')
        target = self.root / 'malformed.json'
        for text in ('{"ok":true,"ok":false}', '{"x":1e999}', '{"x":NaN}'):
            target.write_text(text)
            with self.assertRaises(ValueError):
                CHECK.read_json(target)


if __name__ == '__main__':
    unittest.main()
