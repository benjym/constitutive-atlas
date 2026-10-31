"""Independent reference/protocol tests only; no generated solver execution."""
import copy,json,math,pathlib,unittest
from tools import reference_barodesy2017_wider_paths as r
class WiderPaths(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.study=r.study()
 def test_scalar_both_sign_rate_matches_cartesian(self):
  for c in r.scalar_cases():
   z=c['initial'];p=c['parameters']
   for dv in(.003,-.003):
    a=r.scalar.scalar_rate(z[0],z[6],dv,p);b=r.cartesian.rate({'sigma':z[:6],'e':z[6]},[dv/3]*3+[0.]*3,p,140)
    self.assertLess(math.hypot(*(x-y for x,y in zip(a['sigma_rhs'],b['sigma_rhs'])))/max(1.,math.hypot(*b['sigma_rhs'])),1e-12)
    self.assertAlmostEqual(a['e_rhs'],b['e_rhs'],delta=1e-15)
 def test_exact_scalar100160_and_RK4(self):
  for c in self.study['scalar_cases']:
   self.assertEqual(c['maximum_exact_precision_difference'],0.)
   errors=[max(abs(x['state'][0]-y[0])for x,y in zip(g['trajectory'],c['branch_exact_160']))for g in c['scalar_rk4_grids']]
   for a,b in zip(errors,errors[1:]):self.assertLess(b,a)
   if errors[-1]>1e-7:self.assertTrue(8<errors[-2]/errors[-1]<24)
 def test_reversal_not_NCL_or_universal_unload_slope(self):
  c=r.scalar_cases()[1];z=r.scalar_segment(c['initial'],.01,c['parameters']);s=r.scalar.scalar_slope(z[0],z[6],c['parameters'],-1)
  self.assertGreater(abs(s-1/c['parameters']['kappa_star']),1e-3)
  actual=r.scalar_segment(z,-.004,c['parameters']);ncl=z[0]*math.exp(-.004/c['parameters']['lambda_star']);self.assertGreater(abs(actual[0]-ncl),1.)
 def test_scalar_closed_form_forward_slopes_both_signs(self):
  for c in r.scalar_cases()[::2]:
   z=c['initial'];p=c['parameters']
   for sign in(1,-1):
    h=sign*1e-7;a=r.scalar_segment(z,h,p);fd=math.log(a[0]/z[0])/h;want=r.scalar.scalar_slope(z[0],z[6],p,sign)
    self.assertLess(abs(fd-want)/max(1.,abs(want)),1e-5)
 def test_tensor_final_refinement_predeclared(self):
  for c in self.study['tensor_cases']:
   self.assertTrue(8<c['observed_last_ratio']<24);self.assertLess(c['successive_stress_endpoint_differences_pa'][-1],2e-6)
   for g in c['grids']:
    self.assertGreater(g['stage_support']['minimum_e'],0.);self.assertGreater(g['stage_support']['minimum_pressure'],0.);self.assertTrue(all(v>0 for v in g['stage_support']['minimum_cartesian_leading_minors']))
 def test_full7_void_independent_closure(self):
  for c in self.study['tensor_cases']:self.assertLess(max(c['final_RK4_void_errors']),1e-14)
 def test_rotation_covariance_full_path(self):
  a,b=self.study['tensor_cases'];q=[[1/3,2/3,2/3],[2/3,1/3,-2/3],[-2/3,2/3,-1/3]]
  for x,y in zip(a['grids'][-1]['trajectory'],b['grids'][-1]['trajectory']):
   want=r.cartesian.rotate(x[:6],q);self.assertLess(math.hypot(*(v-w for v,w in zip(y[:6],want)))/max(1.,math.hypot(*want)),1e-13);self.assertLess(abs(x[6]-y[6]),1e-14)
 def test_actual_loading_decimal_disclosed(self):
  for c in self.study['tensor_cases']:
   for g in c['grids']:
    self.assertEqual(len(g['actual_loading']),len(c['increments']))
    for record,inc in zip(g['actual_loading'],c['increments']):
     self.assertEqual(len(record['target_residual_decimal']),6)
 def test_reference_failure_does_not_mutate_supplied_parent(self):
  c=r.tensor_cases()[0];initial=c['initial'].copy();before=initial.copy()
  with self.assertRaises(ValueError):r.rk4_tensor(initial,[[.9,.9,.9,0.,0.,0.]],c['parameters'],8)
  self.assertEqual(initial,before)
 def test_scalar_zero_is_identity(self):
  c=r.scalar_cases()[0];self.assertEqual(r.scalar_segment(c['initial'],0.,c['parameters']),c['initial'])
 def test_protocol_was_predeclared(self):
  p=pathlib.Path(r.__file__).parents[1]/'catalogue/investigations/barodesy2017-wider-reference-v1/protocol.json';x=json.loads(p.read_text());self.assertEqual(x['rk4_grids'],list(r.GRIDS));self.assertFalse(x['public_AD_or_integration_validated'])
 def test_entire_retained_reference_recomputed(self):
  p=pathlib.Path(r.__file__).parents[1]/'catalogue/investigations/barodesy2017-wider-reference-v1/reference.json';before=p.read_bytes();self.assertEqual(json.loads(before),self.study);self.assertEqual(p.read_bytes(),before)
if __name__=='__main__':unittest.main()
