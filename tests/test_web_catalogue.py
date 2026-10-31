"""Run pure browser catalogue contract tests without a solver or browser."""
from pathlib import Path
import shutil
import subprocess
import unittest
ROOT=Path(__file__).resolve().parents[1]
class CatalogueBrowserContracts(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'),'Node.js is required for browser module tests')
    def test_navigation_evidence_identity_and_safe_rendering(self):
        result=subprocess.run(['node','--test','tests/test_catalogue_browser.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node.js is required for browser module tests')
    def test_legacy_and_v03_state_controls(self):
        result=subprocess.run(['node','--test','tests/test_state_contract_browser.mjs'],cwd=ROOT,capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)

    @unittest.skipUnless(shutil.which('node'),'Node.js is required for browser module tests')
    def test_app_is_syntactically_valid_as_an_es_module(self):
        result=subprocess.run(['node','--input-type=module','--check'],input=(ROOT/'web/app.js').read_text(),capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)
