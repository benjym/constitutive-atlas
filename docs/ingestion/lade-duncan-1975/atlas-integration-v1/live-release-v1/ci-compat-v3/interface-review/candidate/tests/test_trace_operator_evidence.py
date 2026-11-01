"""Retained operator evidence and adversarial assessment checks, without builds."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
import tempfile
import shutil
from atlas.evidence import checked_receipt

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "catalogue/investigations/tensor-trace-operator-v1"
spec = importlib.util.spec_from_file_location("trace_operator_assessor", STUDY / "assess.py")
assessor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(assessor)


class TraceOperatorEvidence(unittest.TestCase):
    def test_complete_retained_evidence(self):
        # Reproduce the immutable study against its exact source context.
        protocol = json.loads((STUDY / 'protocol.json').read_text())
        with tempfile.TemporaryDirectory() as directory:
            context = Path(directory)
            for path, expected in protocol['inputs'].items():
                source = checked_receipt(ROOT, (STUDY / 'protocol.json').relative_to(ROOT), path, expected)
                target = context / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, target)
            prior_root = assessor.ROOT
            try:
                assessor.ROOT = context
                actual = assessor.assess()
            finally:
                assessor.ROOT = prior_root
        self.assertTrue(actual["pass"], actual)
        self.assertEqual(actual, json.loads((STUDY / "assessment.json").read_text()))

    def test_missing_corrupt_and_duplicate_rows_and_derivatives_reject(self):
        original = json.loads((STUDY / "native/observe.stdout.txt").read_text())
        corpus = json.loads((ROOT / "docs/reviews/tensor-trace-accuracy-v1/corpus.json").read_text())
        for mutation in ("missing", "duplicate", "wrong-bit", "wrong-status", "seed", "count", "failure"):
            with self.subTest(mutation=mutation):
                observed = copy.deepcopy(original)
                if mutation == "missing": observed["records"].pop()
                elif mutation == "duplicate": observed["records"][1] = observed["records"][0]
                elif mutation == "wrong-bit": observed["records"][0]["result_bits"] = "0000000000000000"
                elif mutation == "wrong-status": observed["records"][0]["ok"] = False
                elif mutation == "seed": observed["jet_derivative_bits"][37] = "0000000000000000"
                elif mutation == "count": observed["checks"] -= 1
                else: observed["failures"] = 1
                self.assertTrue(assessor.assess_observation(observed, corpus))
