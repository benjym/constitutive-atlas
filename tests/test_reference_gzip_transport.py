import gzip
import unittest
from tests.reference_gzip_transport import canonical

class ReferenceGzipTransportTests(unittest.TestCase):
    def test_only_os_byte_changes_and_payload_is_preserved(self):
        expected = gzip.compress(b'original reference: 1.234567890123456789', mtime=0)
        expected = expected[:9] + b'\xff' + expected[10:]
        linux = expected[:9] + b'\x03' + expected[10:]
        self.assertEqual(canonical(linux), expected)
        self.assertEqual(canonical(expected), expected)
        self.assertEqual(gzip.decompress(canonical(linux)), gzip.decompress(expected))

    def test_changed_payload_is_never_repaired(self):
        original = canonical(gzip.compress(b'original', mtime=0))
        changed = canonical(gzip.compress(b'corrupted', mtime=0))
        self.assertNotEqual(original, changed)
        self.assertEqual(gzip.decompress(changed), b'corrupted')

    def test_other_header_changes_reject(self):
        data = canonical(gzip.compress(b'reference', mtime=0))
        for offset in (0, 2, 3, 4, 8, 9):
            corrupted = bytearray(data)
            corrupted[offset] ^= 1
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                canonical(corrupted)
