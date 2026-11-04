"""Synthetic verifier controls, never actualAD evidence; no native/build calls."""
import copy,math,unittest
from tools import barodesy2017_material_ad as a
class Identities(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.m,cls.h=a.rate.catalogue();cls.w=a.rate.wire(a.selected()[1],cls.m);cls.fd=a.difference_reference(cls.w,cls.m);co,fi=cls.fd['scaled_columns_by_step'][-2:];s=cls.fd['state_loading_scales']
  j=[[(4*fi[k][i]-co[k][i])/3/s[k]for k in range(13)]for i in range(7)];j[6]=[0.]*6+[-sum(cls.w['increment'][:3])]+[-(1+cls.w['state'][6])]*3+[0.]*3
  cls.r=a.rate.envelope(cls.w,cls.h,cls.fd['primal'])|{'jacobian':j,'columns':a.COLUMNS}
 def test_control(self):
  m=a.assess_case(self.r,self.w,self.h,self.fd)
  self.assertLess(m['density_void_column_error'],a.IDENTITY_BUDGET);self.assertLess(m['pressure_density_scaling_error'],a.IDENTITY_BUDGET)
 def test_void_algebraic_zeros(self):
  for k in (0,5,10,11,12):
   with self.subTest(column=k):
    r=copy.deepcopy(self.r);r['jacobian'][6][k]=1e-12
    with self.assertRaisesRegex(ValueError,'exact zero'):a.assess_case(r,self.w,self.h,self.fd)
 def test_void_ulp_boundary(self):
  for steps in (4,5):
   r=copy.deepcopy(self.r);x=r['jacobian'][6][7]
   for _ in range(steps):x=math.nextafter(x,math.inf)
   r['jacobian'][6][7]=x
   if steps==4:a.assess_case(r,self.w,self.h,self.fd)
   else:
    with self.assertRaisesRegex(ValueError,'four ULP'):a.assess_case(r,self.w,self.h,self.fd)
 def test_density_identity_tighter_than_fd(self):
  r=copy.deepcopy(self.r);den=max(1.,math.hypot(*self.fd['primal']));r['jacobian'][0][6]+=den*1e-9
  with self.assertRaisesRegex(ValueError,'density void-column'):a.assess_case(r,self.w,self.h,self.fd)
 def test_pressure_scaling_identity_tighter_than_fd(self):
  # Multiplicative stress-direction rank1 perturbation commutes with rotations.
  r=copy.deepcopy(self.r);den=max(1.,math.hypot(*self.fd['primal']));sigma=self.w['state'][:6];ss=sum(v*v for v in sigma)
  for k in range(6):r['jacobian'][0][k]+=den*1e-9*sigma[k]/ss
  with self.assertRaisesRegex(ValueError,'pressure-density scaling'):a.assess_case(r,self.w,self.h,self.fd)
 def test_ad_primal_void_closure(self):
  # Independently enforce primal void closure alongside Jacobian identities.
  c=next(c for c in a.selected()if 'oedometric'in c['id']);w=a.rate.wire(c,self.m);fd=a.difference_reference(w,self.m);co,fi=fd['scaled_columns_by_step'][-2:];s=fd['state_loading_scales'];j=[[(4*fi[k][i]-co[k][i])/3/s[k]for k in range(13)]for i in range(7)];j[6]=[0.]*6+[-sum(w['increment'][:3])]+[-(1+w['state'][6])]*3+[0.]*3
  r=a.rate.envelope(w,self.h,fd['primal'])|{'jacobian':j,'columns':a.COLUMNS};r['values'][6]+=1e-10
  with self.assertRaisesRegex(ValueError,'void closure'):a.assess_case(r,w,self.h,fd)
if __name__=='__main__':unittest.main()
