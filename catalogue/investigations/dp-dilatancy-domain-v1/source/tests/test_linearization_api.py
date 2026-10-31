"""Offline checks of retained native linearization JSON; no native execution."""
import copy
import gzip
import json
import unittest

from tools.verify_linearization_api import RAW,ROOT,verify


def rows():return json.loads(gzip.decompress((ROOT/RAW).read_bytes()))


class LinearizationAPITests(unittest.TestCase):
    def test_native_matrix_and_compatibility(self):
        result=verify(rows())
        self.assertEqual(result['cases'],21)
        self.assertEqual(result['matrix_parity_cases'],11)
        self.assertTrue(result['existing_integrate_compatible'])

    def test_singular_derivative_preserves_update_and_cli_success(self):
        original=rows();singular=next(r for r in original if r['name']=='singular')
        self.assertTrue(singular['response']['ok'])
        self.assertFalse(singular['response']['tangent_ok'])
        self.assertIsNone(singular['response']['state_tangent'])
        self.assertEqual(singular['returncode'],0)
        changed=copy.deepcopy(original);next(r for r in changed if r['name']=='singular')['returncode']=1
        with self.assertRaises(ValueError):verify(changed)

    def test_corrupt_layout_policy_or_matrix_is_rejected(self):
        original=rows()
        changed=copy.deepcopy(original);changed[0]['response']['state_tangent'][0][0]+=1
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['response']['state_fields'][0]['offset']=1
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);changed[0]['response']['branch_policy']='all_branches_smooth'
        with self.assertRaises(ValueError):verify(changed)

    def test_unparsed_request_cannot_publish_state(self):
        original=rows()
        changed=copy.deepcopy(original);next(r for r in changed if r['name']=='bad-csv')['response']['state']=[0]*6
        with self.assertRaises(ValueError):verify(changed)
        changed=copy.deepcopy(original);next(r for r in changed if r['name']=='inadmissible-parent')['response']['state'][0]=0
        with self.assertRaises(ValueError):verify(changed)
        with self.assertRaises(ValueError):verify(original[:-1])


if __name__=='__main__':unittest.main()
