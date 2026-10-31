"""Regression suggestions: exact-zero cases intentionally fail old verifier.
Run after analytic void-row hardening. Synthetic FD mock is NOT AD evidence.
"""
import copy,math,unittest
from tools import barodesy2017_material_ad as a
class Boundaries(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m,cls.h=a.rate.catalogue();cls.w=a.rate.wire(a.selected()[1],cls.m);cls.fd=a.difference_reference(cls.w,cls.m);co,fi=cls.fd['scaled_columns_by_step'][-2:];s=cls.fd['state_loading_scales']
  j=[[(4*fi[k][i]-co[k][i])/3/s[k]for k in range(13)]for i in range(7)];j[6]=[0.]*6+[-sum(cls.w['increment'][:3])]+[-(1+cls.w['state'][6])]*3+[0.]*3
  cls.r=a.rate.envelope(cls.w,cls.h,cls.fd['primal'])|{'jacobian':j,'columns':a.COLUMNS}
 def test_stress_state_void_column_must_be_exact_zero(self):
  r=copy.deepcopy(self.r);r['jacobian'][6][0]=1e-12
  with self.assertRaises(ValueError):a.assess_case(r,self.w,self.h,self.fd)
 def test_loading_shear_void_columns_must_be_exact_zero(self):
  for k in (10,11,12):
   with self.subTest(column=k):
    r=copy.deepcopy(self.r);r['jacobian'][6][k]=1e-12
    with self.assertRaises(ValueError):a.assess_case(r,self.w,self.h,self.fd)
 def test_void_loading_normal_four_ulp_boundary(self):
  r=copy.deepcopy(self.r);x=r['jacobian'][6][7]
  for _ in range(5):x=math.nextafter(x,math.inf)
  r['jacobian'][6][7]=x
  with self.assertRaises(ValueError):a.assess_case(r,self.w,self.h,self.fd)
if __name__=='__main__':unittest.main()
