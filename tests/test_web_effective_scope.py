"""Run effective measurement consumer contracts in the normal Python suite."""
from pathlib import Path
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
class EffectiveScopeBrowserTests(unittest.TestCase):
    def test_browser_contract(self):
        result=subprocess.run(['node','--test','tests/test_effective_experiment_browser.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
