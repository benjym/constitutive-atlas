"""Exercise the shared browser import boundary without a compiled engine."""
import subprocess
import unittest
from atlas.model import ROOT

class StrictBrowserJSONTests(unittest.TestCase):
    def test_strict_browser_decoder(self):
        result = subprocess.run(['node', '--test', 'tests/test_strict_json.mjs'], cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
