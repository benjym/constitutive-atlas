"""Stdlib source-distinguishing algebra only; no constitutive solver/imports."""
import importlib.util,json,math,unittest
from pathlib import Path
P=Path(__file__).with_name('fixtures.py');spec=importlib.util.spec_from_file_location('hca_ingestion_fixtures',P);f=importlib.util.module_from_spec(spec);spec.loader.exec_module(f)
class HCAReconciliation(unittest.TestCase):
 def test_frozen_reproduction(self):self.assertEqual(f.study(),json.loads(P.with_name('fixtures.json').read_text()))
 def test_orthonormal_cartesian_and_symmetric_skew_projectors(self):
  b=f.basis()
  for i,u in enumerate(b):
   for j,v in enumerate(b):self.assertAlmostEqual(math.fsum(x*y for x,y in zip(u,v)),float(i==j),places=14)
  S=[[0.]*9 for _ in range(9)];K=[[0.]*9 for _ in range(9)]
  for u in b[:6]:S=f.add(S,f.outer(u,u))
  for u in b[6:]:K=f.add(K,f.outer(u,u))
  self.assertLess(f.norm(f.combine(f.add(S,K),f.eye(9),1,-1)),2e-15)
  self.assertAlmostEqual(f.inner(S,K),0.,places=14)
 def test_all_four_initialization_variants_distinguished(self):
  r=f.study()['identities'];a=r['literal_J9_over3'];b=r['restricted_I6_over3'];c=r['renormalized_I6_over_sqrt6'];d=r['sphere6_average_I6_over6']
  self.assertEqual(a['full_norm'],1.);self.assertAlmostEqual(b['full_norm'],math.sqrt(6)/3)
  self.assertEqual(a['vertical_contraction'],b['vertical_contraction']);self.assertNotEqual(a['full_norm'],b['full_norm'])
  self.assertAlmostEqual(c['vertical_contraction'],1/math.sqrt(6));self.assertAlmostEqual(d['vertical_contraction'],1/6)
  self.assertGreater(a['fpi_uniform_Cpi1_4'],1.7);self.assertAlmostEqual(c['fpi_uniform_Cpi1_4'],1.,places=14)
 def test_sphere_second_moment_is_not_unit_normalized_mean(self):
  self.assertLess(f.study()['exact_second_moment_quadrature_error'],1e-15)
  self.assertAlmostEqual(f.study()['identities']['sphere6_average_I6_over6']['full_norm'],1/math.sqrt(6))
 def test_conditional_full9_reduction22_with_noncommuting_updates(self):
  for row in f.study()['full9_vs22_piecewise_angle_law']:
   self.assertLess(row['full_vs_22_error'],1e-14);self.assertAlmostEqual(row['full_norm'],1.,places=14);self.assertAlmostEqual(row['reduced_norm'],1.,places=14)
   self.assertLess(row['new_angle'],row['old_angle']);self.assertAlmostEqual(row['new_angle'],row['old_angle']*math.exp(-row['h']),places=14)
   self.assertGreater(row['antisymmetric_coefficient'],0.)
 def test_reduction_is_not_claimed_for_general_skew_or_cross_memory(self):
  b=f.basis()
  for pi in [f.outer(b[6],b[6]),f.add(f.outer(b[0],b[6]),f.outer(b[6],b[0]))]:
   B,c=f.reduce22(pi);self.assertGreater(f.norm(f.combine(pi,f.expand22(B,c),1,-1)),.1)
 def test_literal_operator_sign_differs_from_angle_ode(self):
  r=f.study()['angle_sign_witness'];self.assertAlmostEqual(r['literal_cosine'],-math.sin(.1),places=14)
  self.assertLess(r['literal_cosine'],0);self.assertGreater(r['literal_angle'],r['old_angle']);self.assertLess(r['eq24_integrated_angle'],r['old_angle'])
 def test_filter_source_rules_are_different(self):
  rows={r['angle_degrees']:r for r in f.study()['filter_witnesses']}
  self.assertEqual((rows[0.]['eq36'],rows[0.]['figure22']),(True,False));self.assertEqual((rows[15.]['eq36'],rows[15.]['figure22']),(True,True));self.assertEqual((rows[30.]['eq36'],rows[30.]['figure22']),(False,True))
 def test_filter_strict_radius_and_undefined_current_step(self):
  for mode in('eq36','figure22'):
   self.assertFalse(f.decision([1e-5,0,0,0,0,0],[1.,0,0,0,0,0],mode));self.assertFalse(f.decision([0.]*6,[1.,0,0,0,0,0],mode))
   self.assertIsNone(f.decision([2e-5,0,0,0,0,0],[0.]*6,mode))
  for R,d in [([0.]*5,[1.]*6),([True]*6,[1.]*6),([math.nan]*6,[1.]*6)]:
   with self.assertRaises(ValueError):f.decision(R,d,'eq36')
 def test_matched_angle_branch_identity(self):
  b=f.basis();pi=f.outer(b[2],b[2]);self.assertEqual(f.toward_by_angle_law(pi,pi,.1),pi)
if __name__=='__main__':unittest.main()
