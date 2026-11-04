import copy
from fractions import Fraction
import json
import math
from pathlib import Path
import unittest
from unittest import mock
from tools import clay2014_path_reference as ref
from tools import reference_clay2014_cartesian as source

class PathReferenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.fresh=ref.build_reference()
 def test_full_frozen_replay(self):
  p=Path(ref.__file__).resolve().parents[1]/'evidence'/'reference.json'
  # Installed evidence path is explicit when tests are installed in repo.
  if not p.exists():p=Path(ref.__file__).resolve().parents[1]/'catalogue'/'investigations'/'clay2014-path-reference-v1'/'reference.json'
  self.assertEqual(json.loads(p.read_text()),self.fresh)
 def test_exact_actual_loading_and_input_preservation(self):
  for c in ref.inputs():
   original=copy.deepcopy(c)
   for n in(1,7):
    knots=ref.schedule(c['increments'],n)
    for segment,inc in enumerate(c['increments'],1):
     selected=[k for k in knots if k['segment']==segment]
     for j in range(6):self.assertEqual(sum((Fraction(k['increment'][j])for k in selected),Fraction()),Fraction(inc[j]))
    for k in knots:
     prefix=knots[:knots.index(k)+1]
     self.assertEqual([ref.unexact(x)for x in k['cumulative_loading_exact']],[sum((Fraction(p['increment'][j])for p in prefix),Fraction())for j in range(6)])
   self.assertEqual(c,original)
 def test_wide_and_tiny_exact_accumulation(self):
  incs=[[2.**500,0.,0.,0.,0.,0.],[2.**-100,0.,0.,0.,0.,0.]]
  rows=ref.schedule(incs,1)
  self.assertEqual(ref.unexact(rows[-1]['cumulative_loading_exact'][0]),Fraction(2.**500)+Fraction(2.**-100))
  self.assertEqual(ref.split_increment([1e-100]*6,1),[[1e-100]*6])
 def test_invalid_partition_or_loading(self):
  for n in(0,2,True,7.):
   with self.assertRaises(ValueError):ref.split_increment([0.]*6,n)
  for v in([0.]*5,[math.nan]*6,[True]*6):
   with self.assertRaises(ValueError):ref.split_increment(v,7)
 def test_stage_support_and_refinement(self):
  ref.validate(self.fresh)
  for c in self.fresh['cases']:
   self.assertEqual(len(c['caller_points']),3*c['caller_partitions'])
   for g in c['grids']:
    self.assertEqual(g['stage_domain']['rate_evaluations'],1+5*g['steps_per_piece']*len(c['caller_points']))
    self.assertGreater(g['stage_domain']['minimum']['normalized_stress_determinant'],64*math.ulp(1.))
 def test_scalar_independent_loading_sign_and_semigroup(self):
  c=next(c for c in ref.inputs()if c.get('scalar_isotropic'))
  one=ref.scalar_trajectory(c,1);seven=ref.scalar_trajectory(c,7)
  for segment in range(1,4):
   a=one[segment-1]['state'];b=seven[segment*7-1]['state']
   self.assertLess(math.hypot(*(x-y for x,y in zip(a[:6],b[:6]))),1e-8)
   self.assertLess(abs(a[6]-b[6]),1e-14)
  # Derivative independently from the closed formula, against source rate.
  z=c['initial'];p=c['parameters'];h=1e-7
  for sign in(-1,1):
   tiny=copy.deepcopy(c);tiny['increments']=[[sign*h/3]*3+[0.]*3]
   actual=ref.scalar_trajectory(tiny,1)[0]['state'];v=math.fsum(tiny['increments'][0][:3])
   oracle=source.evaluate({'parameters':p,'state':z,'increment':[sign/3]*3+[0.]*3})['expected']
   self.assertLess(abs((actual[0]-z[0])/abs(v)-oracle[0])/max(1,abs(oracle[0])),2e-5)
 def test_scalar_rejects_anisotropy_and_nonhydro(self):
  c=ref.inputs()[0]
  with self.assertRaises(ValueError):ref.scalar_trajectory(c,1)
  c=next(c for c in ref.inputs()if c.get('scalar_isotropic'));c['increments'][0][3]=.001
  with self.assertRaises(ValueError):ref.scalar_trajectory(c,1)
 def test_rotated_companion_is_actual_rotated_inputs(self):
  a,b=[c for c in ref.inputs()if c['id']in('oblique-reversal','rotated-oblique-reversal')]
  self.assertEqual(b['initial'][:6],source.to_mandel(source.rotate(source.from_mandel(a['initial'][:6]),ref.Q)))
  self.assertEqual(b['increments'],[source.to_mandel(source.rotate(source.from_mandel(v),ref.Q))for v in a['increments']])
  for row in self.fresh['covariance']:
   self.assertLess(max(e['stress_Pa']for e in row['errors']),2e-10*math.hypot(*a['initial'][:6]))
 def test_corrupted_shrink_and_volume_rejected(self):
  bad=copy.deepcopy(self.fresh);bad['cases'][0]['middle_fine'][0]['stress_Pa']=1e3
  with self.assertRaises(ValueError):ref.validate(bad)
  bad=copy.deepcopy(self.fresh);bad['cases'][0]['max_volume_error']=1.
  with self.assertRaises(ValueError):ref.validate(bad)
 def test_exact_replay_rejects_scientific_or_provenance_corruption(self):
  corruptions=[lambda d:d['cases'][0]['grids'][-1]['trajectory'][0]['state'].__setitem__(0,1.),lambda d:d.__setitem__('basis','cartesian'),lambda d:d.__setitem__('input_sha256','0'*64),lambda d:d['cases'][0].__setitem__('caller_partitions',True),lambda d:d['cases'][0]['grids'][0]['stage_domain'].__setitem__('rate_evaluations',-1)]
  with mock.patch.object(ref,'build_reference',return_value=self.fresh):
   for corrupt in corruptions:
    bad=copy.deepcopy(self.fresh);corrupt(bad)
    with self.assertRaises(ValueError):ref.checked_reference(bad)
 def test_dependency_mismatch_rejects_before_integration(self):
  with mock.patch.object(ref,'SOURCE_ORACLE_SHA256','0'*64):
   with self.assertRaises(ValueError):ref.study()

if __name__=='__main__':unittest.main()
