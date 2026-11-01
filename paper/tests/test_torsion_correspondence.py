"""Acquisition fingerprints must include every channel and preserve order."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/audit_torsion_correspondence.py'
spec = importlib.util.spec_from_file_location('correspondence', SCRIPT)
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)


class FingerprintTests(unittest.TestCase):
    def test_one_changed_channel_invalidates_identity(self):
        first = reader.fingerprint([[1, 2, 3], [2, 4, 5]])
        changed = reader.fingerprint([[1, 2, 3], [2, 4, 5.000000000000001]])
        self.assertNotEqual(first, changed)

    def test_reordered_samples_are_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Nonsequential'):
            reader.fingerprint([[2, 4, 5], [1, 2, 3]])

    def test_decimal_spelling_and_signed_zero_do_not_create_aliases(self):
        self.assertEqual(reader.fingerprint([['1', '0.0', '2e0']]),
                         reader.fingerprint([[1, -0.0, 2.0]]))


if __name__ == '__main__':
    unittest.main()
