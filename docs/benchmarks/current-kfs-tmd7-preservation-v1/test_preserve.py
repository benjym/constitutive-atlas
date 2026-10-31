"""Preservation verifier failure cases; synthetic files, no solver or measurements."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location('tmd7_preservation', HERE / 'preserve.py')
P = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(P)


class Preservation(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'copy'
        (self.root / 'payload/current').mkdir(parents=True)
        (self.root / 'payload/current/result').write_bytes(b'original synthetic evidence')
        self.document = {'id': 'current-kfs-tmd7-private-preservation-v1', 'files': [
            {'original_path': '/unused/original', 'stored_path': 'payload/current/result',
             'bytes': 27, 'sha256': hashlib.sha256(b'original synthetic evidence').hexdigest()}]}
        # Correct size comes from the independent literal fixture, not implementation output.
        self.document['files'][0]['bytes'] = len(b'original synthetic evidence')
        self.expected = self.write_inventory()

    def write_inventory(self):
        raw = json.dumps(self.document).encode()
        (self.root / 'inventory.json').write_bytes(raw)
        return hashlib.sha256(raw).hexdigest()

    def test_valid_copy_and_existing_destination_never_overwritten(self):
        self.assertEqual(len(P.verify(self.root, self.expected)['files']), 1)
        before = (self.root / 'inventory.json').read_bytes()
        with self.assertRaisesRegex(ValueError, 'already exists'):
            P.capture(self.root)
        self.assertEqual((self.root / 'inventory.json').read_bytes(), before)

    def test_changed_payload_rejected(self):
        (self.root / 'payload/current/result').write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'stored file changed'):
            P.verify(self.root, self.expected)

    def test_changed_inventory_rejected_against_retained_external_hash(self):
        self.document['files'] = []
        self.write_inventory()
        with self.assertRaisesRegex(ValueError, 'inventory differs'):
            P.verify(self.root, self.expected)

    def test_unlisted_file_rejected(self):
        (self.root / 'extra').write_text('unexpected')
        with self.assertRaisesRegex(ValueError, 'unlisted'):
            P.verify(self.root, self.expected)

    def test_rebound_traversal_or_duplicate_paths_rejected(self):
        self.document['files'][0]['stored_path'] = '../outside'
        with self.assertRaisesRegex(ValueError, 'unsafe stored path'):
            P.verify(self.root, self.write_inventory())
        self.document['files'][0]['stored_path'] = 'payload/current/result'
        self.document['files'].append(dict(self.document['files'][0]))
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            P.verify(self.root, self.write_inventory())

    def test_symlink_escape_rejected(self):
        target = self.root / 'payload/current/result'
        target.unlink()
        outside = Path(self.temp.name) / 'outside'
        outside.write_bytes(b'original synthetic evidence')
        target.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, 'unsafe stored file'):
            P.verify(self.root, self.expected)


if __name__ == '__main__':
    unittest.main()
