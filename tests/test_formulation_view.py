"""Discover the catalogue formulation browser contracts with the Python suite."""
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]

class FormulationViewContracts(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is required for browser module tests')
    def test_formulation_defaults_and_preparation_rendering(self):
        result = subprocess.run(['node', '--test', 'tests/test_formulation_view.mjs'],
                                cwd=ROOT, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
