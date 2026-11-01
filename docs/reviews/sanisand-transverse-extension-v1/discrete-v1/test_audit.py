import unittest
from decimal import Decimal as D
from audit import inverse2,symmetric

class DiscreteAuditTests(unittest.TestCase):
 def test_independent_known_inverse(self):
  det,inverse=inverse2([[D(2),D(1)],[D(1),D(1)]]);self.assertEqual(det,D(1));self.assertEqual(inverse,[[D(1),D(-1)],[D(-1),D(2)]])
 def test_singular_map(self):self.assertEqual(inverse2([[D(1),D(1)],[D(1),D(1)]]),(D(0),None))
 def test_symmetric_state_requires_all_tensors(self):
  z=[0.]*26;self.assertTrue(symmetric(z));z[14]=1e-30;self.assertFalse(symmetric(z))
 def test_shear_rejected(self):
  z=[0.]*26;z[3]=1e-30;self.assertFalse(symmetric(z))
if __name__=='__main__':unittest.main()
