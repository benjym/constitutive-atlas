"""Offline checks of retained full-update directional and rotation evidence."""
import copy
import gzip
import json
import math
import unittest
from tools.verify_tangent_geometry import ROOT,RAW,Q,ROTATION,rotate,verify

class TangentGeometryTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.rows=json.loads(gzip.decompress((ROOT/RAW).read_bytes()))
 def test_retained_refinement_and_rotation_scope(self):
  report=verify(self.rows)
  self.assertEqual((report['native_requests'],report['directional_entries'],report['same_partition_rotation_cases']),(49,288,6))
  self.assertEqual(report['individual_steps_above_tolerance'],1)
  self.assertLess(report['largest_finest_directional_error'],1e-5)
  self.assertFalse(report['rotations'][4]['same_partition'])
 def test_directional_corruption_rejected(self):
  rows=copy.deepcopy(self.rows);rows[6]['response']['state'][0]+=1000
  with self.assertRaisesRegex(ValueError,'directional'):verify(rows)
 def test_rotated_tangent_corruption_rejected(self):
  rows=copy.deepcopy(self.rows);rows[0]['response']['state_tangent'][0][0]+=1e8
  with self.assertRaisesRegex(ValueError,'covariance'):verify(rows)
 def test_incomplete_nonfinite_and_changed_partition_rejected(self):
  with self.assertRaises(ValueError):verify(self.rows[:-1])
  for mutate in (lambda d:d['state'].pop(),lambda d:d['state'].__setitem__(0,float('nan')),lambda d:d['diagnostics'].__setitem__('increment_fractions',[.5,.5])):
   rows=copy.deepcopy(self.rows);mutate(rows[0]['response'])
   with self.assertRaises(ValueError):verify(rows)
 def test_mandel_rotation_is_proper_and_preserves_contraction(self):
  for i in range(6):
   for j in range(6):self.assertAlmostEqual(sum(Q[k][i]*Q[k][j] for k in range(6)),float(i==j),places=14)
  r=ROTATION
  determinant=sum(r[0][i]*(r[1][(i+1)%3]*r[2][(i+2)%3]-r[1][(i+2)%3]*r[2][(i+1)%3]) for i in range(3))
  self.assertAlmostEqual(determinant,1.,places=14)
  x=[1,2,-3,4,-2,6];y=[-2,1,5,-3,7,2]
  self.assertAlmostEqual(sum(a*b for a,b in zip(rotate(x),rotate(y))),sum(a*b for a,b in zip(x,y)),places=12)
  self.assertAlmostEqual(sum(rotate(x)[:3]),sum(x[:3]),places=14)

if __name__=='__main__':unittest.main()
