"""Retained native full-update tangent checks; no native invocation."""
import copy
import gzip
import json
import unittest

from tools.verify_update_tangent import RAW,ROOT,verify


def rows():return json.loads(gzip.decompress((ROOT/RAW).read_bytes()))


class UpdateTangentTests(unittest.TestCase):
    def test_retained_analytical_and_full_update_perturbations(self):
        result=verify(rows())
        self.assertEqual(result['finite_difference_entries'],720)
        self.assertEqual(result['analytical_entries'],228)
        self.assertLess(result['largest_normalized_fd_error'],1e-5)

    def test_cutbacks_and_strain_dependent_reset_have_coverage(self):
        records=rows()
        implicit=next(r for r in records if r['model']=='test-update-tangent-implicit')
        self.assertEqual(len(implicit['fractions']),2)
        rate=next(r for r in records if r['model']=='test-parent-reset-cutback' and r['fd_checked'])
        self.assertGreater(len(rate['fractions']),2)
        reset=next(r for r in records if r['model']=='test-update-tangent-reset')
        self.assertEqual(reset['tangent'][7],[1,1,1,0,0,0])
        boundary=next(r for r in records if not r['fd_checked'])
        self.assertTrue(boundary['reset_guard_at_zero'])
        self.assertEqual(boundary['tangent'][7],[0]*6)

    def test_wrong_tangent_shape_or_nonfinite_entries_are_rejected(self):
        original=rows()
        changed=copy.deepcopy(original);changed[0]['tangent'][0][0]*=1.01
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['tangent'][0].pop()
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['tangent'][0][0]=float('nan')
        with self.assertRaises(ValueError):verify(changed)

    def test_missing_cases_or_unexplained_branch_omissions_are_rejected(self):
        original=rows()
        with self.assertRaises(ValueError):verify(original[:-1])
        changed=copy.deepcopy(original);changed[0]['fd_checked']=False
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['fractions']=[.5]
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['fractions']=[float('nan')]
        with self.assertRaises(ValueError):verify(changed)


if __name__=='__main__':unittest.main()
