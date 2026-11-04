"""Independent caller-point evidence only; no generated solver."""
import copy,json,math,pathlib,unittest
from unittest.mock import patch
from decimal import Decimal,localcontext
from fractions import Fraction
from tools import reference_barodesy2017_caller_points as r
class CallerPoints(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.study=r.study()
 def test_all_original_loading_exactly_preserved(self):
  for c in r.base.scalar_cases()+r.base.tensor_cases():
   pieces,points=r.split_path(c['increments'],7)
   with localcontext()as ctx:
    ctx.prec=180
    for k,inc in enumerate(c['increments']):
     for j,x in enumerate(inc):self.assertEqual(sum((Decimal.from_float(p[j])for p in pieces[k*7:k*7+7]),Decimal(0)),Decimal.from_float(x))
   self.assertEqual([i for i,p in enumerate(points,1)if p['original_endpoint']],[7,14,21])
 def test_exact_cumulative_wide_binary64_span(self):
  increments=[[2.**500,0,0,0,0,0],[2.**-100,0,0,0,0,0]]
  _,points=r.split_path(increments,1)
  self.assertEqual(Fraction(Decimal(points[-1]['cumulative_strain_decimal'][0])),sum((Fraction.from_float(x[0])for x in increments),Fraction(0)))
 def test_tiny_unpartitioned_increment_exact(self):
  pieces,points=r.split_path([[1e-100,0,0,0,0,0]],1)
  self.assertEqual(pieces[0][0],1e-100);self.assertEqual(Fraction(Decimal(points[-1]['cumulative_strain_decimal'][0])),Fraction.from_float(1e-100))
 def test_every_callerpoint_has_reference(self):
  for c in self.study['scalar_cases']+self.study['tensor_cases']:self.assertEqual(len(c['points']),1+3*c['partitions']);self.assertEqual([p['index']for p in c['points']],list(range(len(c['points']))))
 def test_scalar_rounding_refinement_and_same_original_knots(self):
  for a,b in zip(self.study['scalar_cases'][::2],self.study['scalar_cases'][1::2]):
   self.assertEqual(a['partitions'],1);self.assertEqual(b['partitions'],7);self.assertEqual(b['maximum_precision_stress_difference_pa'],0.)
   for j in range(4):self.assertEqual(a['points'][j]['state160'],b['points'][7*j]['state160'])
 def test_tensor_eligibility_all_callerpoints(self):
  for c in self.study['tensor_cases']:
   self.assertTrue(c['reference_eligible']);self.assertLess(c['maximum_callerpoint_stress_differences_pa'][-1],c['stress_reference_eligibility_limit_pa']);self.assertLess(c['maximum_callerpoint_void_differences'][-1],c['void_reference_eligibility_limit'])
 def test_matching_physical_RK4_mesh(self):
  for a,b in zip(self.study['tensor_cases'][::2],self.study['tensor_cases'][1::2]):
   self.assertEqual([g['steps_per_segment']for g in a['grids']],[28,56,112]);self.assertEqual([g['steps_per_segment']for g in b['grids']],[4,8,16])
   for j in range(4):
    x,y=a['points'][j]['state'],b['points'][7*j]['state'];self.assertLess(math.hypot(*(u-v for u,v in zip(x[:6],y[:6]))),1e-7);self.assertLess(abs(x[6]-y[6]),1e-14)
 def test_fixed_original_stress_scales(self):
  for c in self.study['scalar_cases']+self.study['tensor_cases']:self.assertEqual(c['initial_stress_scale_pa'],max(1.,math.hypot(*c['initial'][:6])))
 def test_reversal_keeps_order(self):
  c=next(x for x in self.study['scalar_cases']if 'reversal'in x['id']and x['partitions']==7)
  self.assertGreater(c['points'][7]['display_strain'][0],c['points'][14]['display_strain'][0]);self.assertEqual([p['original_segment']for p in c['points'][1:]],sum(([j]*7 for j in(1,2,3)),[]))
 def test_no_mutation_split(self):
  c=r.base.tensor_cases()[0];before=copy.deepcopy(c);r.split_path(c['increments'],7);self.assertEqual(c,before)
 def test_frozen_reference_matches(self):
  self.assertTrue(r.FROZEN.is_file());self.assertEqual(json.loads(r.FROZEN.read_text()),self.study)
 def test_scalar_eligibility_rejects_corrupt_precision_outputs(self):
  original=r.base.scalar_path_actual_mandel
  def corrupt(initial,inc,p,precision):
   states=original(initial,inc,p,precision)
   if precision==100:states[1][6]+=.01
   return states
  with patch.object(r.base,'scalar_path_actual_mandel',side_effect=corrupt):
   with self.assertRaises(ValueError):r.scalar_case(r.base.scalar_cases()[0],7)
 def test_protocol_constants_bound(self):
  p=json.loads(r.PROTOCOL.read_text());self.assertEqual(p['stress_scaled_bounds'],list(r.STRESS_BOUNDS));self.assertEqual(p['void_absolute_bounds'],list(r.VOID_BOUNDS))
 def test_constitutive_dependencies_pinned(self):
  self.assertEqual(set(self.study['constitutive_dependency_sha256']),{'tools/reference_barodesy2017.py','tools/barodesy2017_isotropic_reference.py'})
if __name__=='__main__':unittest.main()
