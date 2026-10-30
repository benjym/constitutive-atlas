import json,math,unittest
from pathlib import Path
from tools.clay2013_path_reference import study,rotate,cart,mand,RESOLUTIONS
class ClayCartesianPaths(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=study()
 def test_complete_three_grid_convergence(self):
  self.assertEqual(len(self.report['cases']),4)
  for c in self.report['cases']:
   self.assertEqual([g['steps_per_segment']for g in c['grids']],list(RESOLUTIONS))
   self.assertTrue(14<c['refinement_ratio']['stress']<18)
   self.assertLess(c['fine_difference']['stress'],5e-6)
   for g in c['grids']:
    self.assertEqual([r['segment']for r in g['trajectory']],[0,1,2,3])
    for r in g['trajectory']:self.assertTrue(all(math.isfinite(x)for x in r['state']))
 def test_exact_volume_relation_at_all_grid_endpoints(self):
  for c in self.report['cases']:
   initial=c['input']['initial'];inc=c['input']['increments']
   for g in c['grids']:
    x=0
    for row in g['trajectory']:
     j=row['segment']
     if j:x+=sum(inc[j-1][:3])
     expected=(1+initial[6])*math.exp(-x)-1
     self.assertLess(abs(row['state'][6]-expected),3e-15)
 def test_rotation_covariance_and_no_isotropic_path(self):
  for c in self.report['covariance']:self.assertLess(c['difference']['stress'],3e-10)
  for c in self.report['cases']:
   sig=c['input']['initial'][:6]
   self.assertTrue(any(x!=0 for x in sig[3:]))
   self.assertTrue(any(any(x!=0 for x in d[3:])for d in c['input']['increments']))
 def test_reproducible_retained_record(self):
  path=Path(__file__).resolve().parents[1]/'catalogue/investigations/clay-nonisotropic-v1/evidence.json'
  if not path.exists():self.skipTest('retained fixture not installed')
  self.assertEqual(self.report,json.loads(path.read_text()))
 def test_mandel_roundtrip_and_rotation_norm(self):
  a=[14000.,10000.,8000.,1200.,-700.,900.]
  for x,y in zip(a,mand(cart(a))):self.assertAlmostEqual(x,y)
  self.assertAlmostEqual(sum(x*x for x in a),sum(x*x for x in rotate(a)),delta=2e-7)
if __name__=='__main__':unittest.main()
