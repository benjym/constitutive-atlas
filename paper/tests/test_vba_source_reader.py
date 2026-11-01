"""MS-OVBA literal/copy-token boundary checks; no macro execution."""
import importlib.util
from pathlib import Path
import struct
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/read_torsion_vba.py'
spec = importlib.util.spec_from_file_location('vba_source', SCRIPT)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class DecompressionTests(unittest.TestCase):
    def test_overlapping_copy(self):
        # One literal A, then a distance-one/length-three copy: AAAA.
        container = b'\x01' + struct.pack('<H', 0xB003) + b'\x02A\x00\x00'
        self.assertEqual(reader.decompress(container), b'AAAA')

    def test_raw_chunk(self):
        raw = bytes(range(256)) * 16
        self.assertEqual(reader.decompress(b'\x01\xff\x3f' + raw), raw)

    def test_copy_cannot_refer_before_chunk(self):
        container = b'\x01' + struct.pack('<H', 0xB002) + b'\x01\x00\x00'
        with self.assertRaisesRegex(ValueError, 'Copy starts before'):
            reader.decompress(container)


if __name__ == '__main__':
    unittest.main()
