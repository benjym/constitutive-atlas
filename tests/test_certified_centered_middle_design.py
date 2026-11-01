"""Independent source-only centered-middle proof/oracle regression checks."""
from pathlib import Path
import importlib.util,json,unittest
from unittest.mock import patch
from atlas.model import ROOT
P=ROOT/'docs/reviews/certified-centered-middle-v1'
def module(n,p):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
class CenteredMiddleDesignTests(unittest.TestCase):
 def test_saved_proof_corpus_without_material_processes(self):
  with patch('subprocess.run',side_effect=AssertionError('material calls forbidden')):a=module('middle_verify',P/'verify.py').verify()
  self.assertEqual(a['literal_cases'],1160);self.assertEqual(a['known_expected'],773);self.assertEqual(a['failed_reversal'],{'upper':False,'lower_via_negation':True})
 def test_repeated_positive_root_requires_multiplicity(self):
  e=module('middle_roots',P/'exact.py');p=e.mul(e.mul([e.Q(1),e.Q(1)],[e.Q(-2),e.Q(1)]),[e.Q(-2),e.Q(1)])
  self.assertEqual(e.positive_distinct(p),1);self.assertEqual(e.positive_with_multiplicity(p),2)
 def test_strict_boundary_zero_and_negation(self):
  e=module('middle_boundary',P/'exact.py')
  for fn in [e.invariant_middle_gt,e.sturm_middle_gt]:
   self.assertFalse(fn([-2.,1.,1.,0.,0.,0.],3.));self.assertTrue(fn([-2.,1.,1.,0.,0.,0.],2.));self.assertFalse(fn([2.,-1.,-1.,0.,0.,0.],2.));self.assertFalse(fn([1.,1.,1.,0.,0.,0.],-0.))
 def test_radical_and_extreme_cases_are_actually_in_frozen_corpus(self):
  d=json.loads((P/'inputs.json').read_text())['cases'];self.assertEqual(sum(all(float.fromhex(x)!=0 for x in c['mandel'][3:])for c in d),220);self.assertEqual(sum(c['group']=='original-tresca-trial'for c in d),61)
