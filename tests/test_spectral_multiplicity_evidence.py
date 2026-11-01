"""Saved independently reviewed generic backend gates remain reproducible."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

P=Path(__file__).resolve().parents[1]/'docs/reviews/spectral-multiplicity-v1'


class MultiplicityEvidence(unittest.TestCase):
    def test_saved_backend_independent_accuracy_and_recovery(self):
        spec=importlib.util.spec_from_file_location('multiplicity_assessor',P/'assess.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        refs=json.loads((P/'references.json').read_text())
        for backend in ('native','wasm'):
            with self.subTest(backend=backend):
                got=module.assess((P/(backend+'-responses-v4.jsonl')).read_text(),refs)
                self.assertEqual(got,json.loads((P/(backend+'-assessment-v4.json')).read_text()))
                self.assertEqual(got['accuracy_checks'],7153)

    def test_assessor_rejects_corrupted_outputs(self):
        result=subprocess.run([sys.executable,'-B',str(P/'check_assessor.py')],capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(result.stdout),json.loads((P/'assessor-checks.json').read_text()))
        self.assertEqual(json.loads(result.stdout)['corruptions_rejected'],17)
