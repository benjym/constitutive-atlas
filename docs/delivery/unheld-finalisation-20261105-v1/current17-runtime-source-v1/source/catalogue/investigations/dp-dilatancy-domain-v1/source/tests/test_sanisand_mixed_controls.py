"""Mixed-control research evidence checks; no compiler or native invocation."""
import copy
import gzip
import json
import unittest

from atlas.model import defaults, load
from tools.verify_sanisand_mixed_controls import MODEL, RAW, ROOT, elastic_reference, verify


def rows():return json.loads(gzip.decompress((ROOT/RAW).read_bytes()))


class SANISANDMixedControlTests(unittest.TestCase):
    def test_complete_native_matrix_and_refinement(self):
        result=verify(rows())
        self.assertEqual(result['records'],898)
        self.assertEqual(result['cyclic_increments'],896)
        self.assertEqual(result['cyclic_memory_resets'],18)
        self.assertEqual(result['native_direct_replay_assertions'],898)
        self.assertEqual(result['elastic_analytical_cases'],2)
        for error in result['largest_control_residual_pa'].values():self.assertLess(error,.001)

    def test_independent_elastic_references_reject_wrong_response(self):
        parameters=defaults(load(ROOT/MODEL))
        for row in [r for r in rows() if not r['steps']]:
            elastic_reference(row,parameters)
            altered=copy.deepcopy(row);altered['state'][0]+=1
            with self.assertRaises(ValueError):elastic_reference(altered,parameters)
            altered=copy.deepcopy(row);altered['increment'][1]+=1e-7
            with self.assertRaises(ValueError):elastic_reference(altered,parameters)

    def test_control_and_memory_corruption_are_rejected(self):
        original=rows()
        changed=copy.deepcopy(original);changed[0]['control_residual']=1
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['request']*=2
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[1]['prepared'][19]+=.01
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['replay_equal']=False
        with self.assertRaises(ValueError):verify(changed)

    def test_incomplete_or_unrecorded_partition_is_rejected(self):
        original=rows()
        with self.assertRaises(ValueError):verify(original[:-1])
        changed=copy.deepcopy(original);changed[0]['fractions']=[.5,.5]
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[1]['before'][0]+=.01
        with self.assertRaises(ValueError):verify(changed)


if __name__=='__main__':unittest.main()
