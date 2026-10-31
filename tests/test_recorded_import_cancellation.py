"""Exercise recorded-view asynchronous imports without a native/Wasm solver."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RecordedImportCancellation(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is required for browser module tests')
    def test_delayed_reads_cancel_and_supersede(self):
        result = subprocess.run(
            ['node', '--test', 'tests/test_recorded_import_cancellation.mjs'],
            cwd=ROOT, capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

if __name__ == '__main__':
    unittest.main()
