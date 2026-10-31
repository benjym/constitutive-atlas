import json
import os
from pathlib import Path
import unittest
import probe

HERE=Path(__file__).resolve().parent


class AuditWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo=Path(os.environ['ATLAS_REPO']) if 'ATLAS_REPO' in os.environ else next((p for p in HERE.parents if(p/'atlas/model.py').is_file()),None)
        if cls.repo is None:raise RuntimeError('ATLAS_REPO required outside checkout')
        cls.result=probe.run(cls.repo.resolve())

    def test_exact_reviewed_replay(self):
        self.assertEqual(self.result,json.loads((HERE/'evidence.json').read_text()))

    def test_indefinite_and_rankloss_are_real_dsl_counterexamples(self):
        a,b=self.result['witnesses']
        for w in (a,b):
            self.assertTrue(w['dsl_accepted'])
            self.assertGreater(w['computed_detH'],0)
            self.assertTrue(w['independent_oracle_rejected'])
            self.assertFalse(w['prospective_conservative_guard_accepts'])
            self.assertTrue(w['prepared_parent_unchanged'])
        self.assertEqual(a['state7'][2],0.)
        self.assertLess(b['state7'][2],0.)
        self.assertTrue(b['actual_normalized_H_determinant'].startswith('-'))

    def test_printed_plus_algebra_matches_unloading_not_counterfactual_minus(self):
        c=self.result['eq38_source_check']
        self.assertAlmostEqual(c['plus_unloading_coefficient'],c['expected_inverse_kappa'],places=12)
        self.assertAlmostEqual(c['counterfactual_minus_coefficient'],c['expected_inverse_lambda'],places=12)
        self.assertGreater(abs(c['plus_unloading_coefficient']-c['counterfactual_minus_coefficient']),1.)
        # This is algebra accompanying visual inspection, not OCR/automated sign proof.

    def test_proposed_interior_does_not_remove_original_comparison_cases(self):
        self.assertEqual(self.result['existing_corpus_count'],41)
        self.assertEqual(self.result['existing_corpus_passing_prospective_guard_count'],41)

if __name__=='__main__':unittest.main()
