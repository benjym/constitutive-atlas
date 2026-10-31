"""Input identity checks for the bounded TMD2 command; no native execution."""
import hashlib
import shutil
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from tools.benchmark_tmd2 import normalize, semantic_hash, SEMANTIC_SHA, verify_process_observations

class Tmd2InputIdentity(unittest.TestCase):
    def test_timestamp_only_is_excluded_from_content_identity(self):
        data={'provenance':{'normalized_at':'old','member_sha256':'abc'},'rows':[{'q':1}]}
        changed=json.loads(json.dumps(data));changed['provenance']['normalized_at']='new'
        self.assertEqual(semantic_hash(data),semantic_hash(changed))
        changed['rows'][0]['q']=2
        self.assertNotEqual(semantic_hash(data),semantic_hash(changed))
        changed=json.loads(json.dumps(data));changed['provenance']['member_sha256']='def'
        self.assertNotEqual(semantic_hash(data),semantic_hash(changed))

    def test_archive_mismatch_is_rejected_before_parsing(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'changed.zip';path.write_bytes(b'changed original archive')
            with patch('tools.benchmark_tmd2.zipfile.ZipFile') as reader:
                with self.assertRaisesRegex(ValueError,'checksum mismatch'):normalize(path)
                reader.assert_not_called()

    def test_pinned_local_original_reconstructs_content(self):
        source=Path(__file__).resolve().parents[1]/'data/raw/KFS-TMD1-5.zip'
        if not source.exists():self.skipTest('private original source archive unavailable')
        record=normalize(source)
        self.assertEqual(semantic_hash(record),SEMANTIC_SHA)
        self.assertEqual(record['id'],'KFS-TMD2')
        self.assertEqual(record['rows'][0]['q'],-153.04999999999998)
        self.assertEqual(record['provenance']['redistribution'],'not-reviewed; local research copy only')

class Tmd2ProcessEvidence(unittest.TestCase):
    """Saved native responses only; never execute a material or compiler."""
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        source = Path(__file__).resolve().parents[1] / 'docs/benchmarks/kfs-tmd2-research-range-v1'
        self.inputs = source / 'inputs'
        self.observations = self.root / 'observations'
        shutil.copytree(source / 'observations', self.observations)
        self.folder = self.observations / 'tmd2-400'
        self.receipt_path = self.folder / 'receipt.json'
        self.receipt = json.loads(self.receipt_path.read_text())

    def save_receipt(self):
        self.receipt_path.write_text(json.dumps(self.receipt))

    def check(self):
        return verify_process_observations(self.inputs, self.observations)

    def test_saved_successful_frame(self):
        self.assertEqual(self.check(), ['tmd2-400', 'tmd2-800', 'tmd2-1600'])

    def test_nonzero_signal_missing_and_noninteger_exit_rejected(self):
        for code in [23, -9, None, False, True, 0.0, '0']:
            with self.subTest(code=repr(code)):
                self.receipt['returncode'] = code
                self.save_receipt()
                with self.assertRaisesRegex(ValueError, 'integer zero process returncode'):
                    self.check()
        self.receipt.pop('returncode')
        self.save_receipt()
        with self.assertRaisesRegex(ValueError, 'integer zero process returncode'):
            self.check()

    def test_each_receipt_binding_rejected(self):
        for key in ['artifact_sha256', 'freeze_sha256', 'stdout_sha256', 'stderr_sha256']:
            original = self.receipt[key]
            with self.subTest(key=key):
                self.receipt[key] = '0' * 64
                self.save_receipt()
                with self.assertRaisesRegex(ValueError, key + ' mismatch'):
                    self.check()
            self.receipt[key] = original

    def test_changed_stream_bytes_rejected(self):
        for filename in ['stdout.json', 'stderr.txt']:
            path = self.folder / filename
            original = path.read_bytes()
            with self.subTest(filename=filename):
                path.write_bytes(original + b' ')
                with self.assertRaisesRegex(ValueError, 'sha256 mismatch'):
                    self.check()
            path.write_bytes(original)

    def test_exit_success_cannot_override_response_failure_or_truthy_nonboolean(self):
        path = self.folder / 'stdout.json'
        original = json.loads(path.read_text())
        for ok in [False, 1, 'true', None]:
            with self.subTest(ok=repr(ok)):
                response = dict(original, ok=ok)
                path.write_text(json.dumps(response))
                self.receipt['stdout_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                self.save_receipt()
                with self.assertRaisesRegex(ValueError, 'response ok=true'):
                    self.check()

    def test_duplicate_keys_and_nonfinite_unused_numbers_rejected(self):
        path = self.folder / 'stdout.json'
        original = path.read_text()
        for extra in ['"ok":true,', '"unused":1e999,']:
            with self.subTest(extra=extra):
                path.write_text('{' + extra + original.lstrip()[1:])
                self.receipt['stdout_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
                self.save_receipt()
                with self.assertRaises(ValueError):
                    self.check()


if __name__=='__main__':unittest.main()
