import math,unittest
from fractions import Fraction as F
from tools.pm4silt_v1_inplane_fixture import invariants

class InplaneFixtureTests(unittest.TestCase):
 def test_independent_rational_oracle(self):
  a=invariants([100000.,50000.,30000.])
  self.assertEqual(a['p'],75000.);self.assertEqual(a['s'],[25000.,-25000.,30000.])
  expected=[F(1,3),F(-1,3),F(2,5)]
  self.assertEqual(a['r'],[float(x)for x in expected])
  self.assertAlmostEqual(a['r_double_contraction'],float(sum(x*x for x in expected[:2])+2*expected[2]**2),places=15)
 def test_rotation_and_scaling(self):
  a=invariants([100000.,50000.,30000.]);b=invariants([50000.,100000.,-30000.])
  self.assertEqual(a['p'],b['p']);self.assertEqual(a['r_double_contraction'],b['r_double_contraction'])
  c=invariants([200000.,100000.,60000.]);self.assertEqual(a['r'],c['r'])
 def test_zero_direction_is_finite_without_normal(self):
  a=invariants([80000.,80000.,0.]);self.assertEqual(a['r'],[0.,0.,0.]);self.assertEqual(a['r_double_contraction'],0.)
  self.assertNotIn('n',a)
 def test_domain_and_distinguishing_3d_fixture(self):
  self.assertNotEqual(invariants([100000.,50000.,30000.])['p'],(100000.+50000.+40000.)/3)
  for x in ([0.,0.,0.],[1.,float('nan'),0.],[1.,1.,float('inf')],[1.,1.], [True,1.,0.]):
   with self.assertRaises(ValueError):invariants(x)
if __name__=='__main__':unittest.main()
