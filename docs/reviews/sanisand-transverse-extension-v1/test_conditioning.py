import unittest
from decimal import Decimal as D
from conditioning import condition

class ConditioningTests(unittest.TestCase):
 def test_diagonal(self):
  r=condition([[1.,0.],[0.,2.]]);self.assertEqual(D(r['infinity_condition_estimate']),D(2));self.assertEqual(D(r['inverse_residual_at_70digits']),0)
 def test_rotated(self):
  self.assertEqual(D(condition([[1.,1.],[1.,-1.]])['infinity_condition_estimate']),D(2))
 def test_singular(self):self.assertIsNone(condition([[1.,1.],[1.,1.]]))
 def test_ill_conditioned(self):
  r=condition([[1.,0.],[0.,1e-20]]);self.assertTrue(D(r['infinity_condition_estimate'])>D('9.99e19'));self.assertTrue(D(r['inverse_residual_at_70digits'])<D('1e-60'))
if __name__=='__main__':unittest.main()
