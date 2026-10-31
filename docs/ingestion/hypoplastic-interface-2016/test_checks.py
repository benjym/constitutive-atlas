import json,unittest
from pathlib import Path
import checks
class InterfaceSourceChecks(unittest.TestCase):
 def test_retained_algebra(self):self.assertEqual(checks.run(),json.loads(Path(__file__).with_name('check-results.json').read_text()))
 def test_product_is_not_full_tensor_closure(self):
  x=[2,3,5,7];self.assertNotEqual(checks.embed(checks.reduced_dot(x,x)),checks.mul(checks.embed(x),checks.embed(x)))
 def test_no_source_or_executable_promotion(self):
  root=Path(__file__).parent;a=json.loads((root/'source-audit.json').read_text());self.assertFalse(a['source_complete']);self.assertFalse(a['original2016_equations_visually_verified']);self.assertTrue(a['thesis_kinematics_operators_visually_verified'])
  ledger=json.loads((root/'schema-integration-ledger.json').read_text());self.assertIn('full rate draft',ledger['not_supported'])
if __name__=='__main__':unittest.main()
