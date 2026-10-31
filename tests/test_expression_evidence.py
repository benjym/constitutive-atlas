"""Exact retained acceptance journals; no compiled execution by these tests."""
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'catalogue/investigations'
STUDY=BASE/'expression-finiteness-v2'
spec=importlib.util.spec_from_file_location('expression_assessment',STUDY/'assess.py')
ASSESSOR=importlib.util.module_from_spec(spec)
spec.loader.exec_module(ASSESSOR)

class ExpressionEvidence(unittest.TestCase):
    def test_complete_ordered_typed_observations(self):
        result=ASSESSOR.assess()
        self.assertTrue(result['pass'])
        self.assertEqual(result['rows_per_backend'],1620)
        self.assertEqual(result,json.loads((STUDY/'assessment.json').read_text()))

    def test_failed_harness_and_unchanged_acceptance_retained(self):
        old=BASE/'expression-finiteness-v1'
        receipt=json.loads((old/'native/receipt.json').read_text())
        self.assertEqual([x['exit_code']for x in receipt['commands']],[0,2])
        self.assertFalse((old/'native/observe.stdout.txt').exists())
        self.assertEqual((old/'expected.json').read_bytes(),(STUDY/'expected.json').read_bytes())
        for p in (old/'frozen').rglob('*'):
            if p.is_file():self.assertEqual(p.read_bytes(),(STUDY/p.relative_to(old)).read_bytes())

    def test_missing_duplicate_wrong_type_or_extra_field_rejected(self):
        for mutation in ('missing','duplicate','numeric-bool','extra-field'):
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory()as tmp:
                copy=Path(tmp)/'study'
                shutil.copytree(STUDY,copy)
                p=copy/'native/observe.stdout.txt'
                rows=json.loads(p.read_text())
                if mutation=='missing':rows.pop()
                elif mutation=='duplicate':rows.append(rows[0])
                elif mutation=='numeric-bool':rows[0]['ok']=int(rows[0]['ok'])
                else:rows[0]['extra']=True
                p.write_text(json.dumps(rows))
                self.assertFalse(ASSESSOR.assess(copy)['pass'])
