import unittest
from pm4_order_witnesses import witnesses


class OrderWitnesses(unittest.TestCase):
    def test_anchor_snapshots_and_frozen_event(self):
        d = witnesses()['anchor_copy']
        self.assertTrue(d['step12_reversal'])
        self.assertEqual(d['simultaneous']['previous'], 0.4)
        self.assertEqual(d['simultaneous']['true'], 0.1)
        self.assertNotEqual(d['current_then_previous'], d['simultaneous'])
        self.assertNotEqual(d['duplicate_copy'], d['simultaneous'])
        self.assertFalse(d['recomputed_guard_after_reset'])

    def test_shared_lag_and_fabric_distinguishability(self):
        d = witnesses()
        lag = d['lag_scope']
        self.assertEqual(lag['correct_reads'][0], lag['correct_reads'][1])
        self.assertNotEqual(lag['correct_reads'], lag['wrong_early_publication_reads'])
        self.assertNotEqual(d['fabric_copy']['copy_old_result'], d['fabric_copy']['copy_updated_result'])
        self.assertIsNone(d['fabric_copy']['source_selected'])

    def test_equality_and_initial_ratio(self):
        d = witnesses()
        eq = d['equality_branch']
        self.assertFalse(eq['eq27_strict_branch'])
        self.assertTrue(eq['eq47_nonstrict_branch'])
        self.assertAlmostEqual(eq['eq47_ratio_branch_value'], 2.)
        self.assertEqual(d['initialized_ratio']['denominator'], 0.)
        self.assertFalse(d['initialized_ratio']['finite_source_branch_identified'])

    def test_transaction_and_basis(self):
        d = witnesses()
        self.assertTrue(d['transaction']['returned_parent_identical'])
        self.assertTrue(d['transaction']['parent_unchanged'])
        self.assertEqual(d['transaction']['published_events'], [])
        self.assertAlmostEqual(sum(d['basis_mandel'][:3]), 0.)
        self.assertAlmostEqual(sum(x*x for x in d['basis_mandel']), 1.)


if __name__ == '__main__':
    unittest.main()
