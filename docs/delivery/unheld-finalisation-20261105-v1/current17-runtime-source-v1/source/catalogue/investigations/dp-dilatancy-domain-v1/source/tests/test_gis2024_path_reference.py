"""Pure-Python independent-path checks; no common engine/native/Wasm imports."""
import copy,hashlib,json,math,unittest
from pathlib import Path
from tools import gis2024_path_reference as g

class GISCartesianPaths(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.report=g.study()
 def test_complete_explicit_matrix_and_hashes(self):
  r=self.report;self.assertEqual(r['contract'],'gis2024-independent-cartesian-path-reference-v1');self.assertEqual(len(r['cases']),4)
  self.assertEqual(r['source_sha256'],g.SOURCE_SHA256)
  self.assertTrue(r['zero_spin']);self.assertEqual(r['resolutions'],[16,32,64])
  for c in r['cases']:
   v=c['input'];self.assertEqual(len(v['initial']),14);self.assertEqual(len(v['parameters']),18);self.assertEqual(v['parameters'],g.PARAMETERS)
   self.assertEqual(c['input_sha256'],g.digest(v));self.assertEqual(len(v['increments']),3)
   for d in v['increments']:self.assertEqual(len(d),6)
   for grid in c['grids']:
    self.assertEqual([r['segment']for r in grid['trajectory']],[0,1,2,3]);self.assertEqual(grid['trajectory'][0]['state'],v['initial'])
    for row in grid['trajectory']:self.assertEqual(len(row['state']),14);self.assertTrue(all(math.isfinite(x)for x in row['state']))
  for name,p in [('tools/gis2024_path_reference.py',g.__file__),('tools/reference_gis2024_coupled.py',g.reference.__file__),('tools/reference_gis2024_hp_host.py',g.reference.hp.__file__)]:self.assertEqual(r['dependency_sha256'][name],g.sha(p))
 def test_observed_smooth_three_grid_refinement_separate_channels(self):
  for c in self.report['cases']:
   for name,limit in [('stress',1e-6),('h',1e-12),('Omega',1e-10)]:
    self.assertGreater(c['fine_difference'][name],0);self.assertLess(c['fine_difference'][name],limit)
    self.assertGreater(c['refinement_ratio'][name],14);self.assertLess(c['refinement_ratio'][name],18)
    self.assertEqual(c['richardson_estimate'][name],c['fine_difference'][name]/15)
   self.assertLess(c['fine_difference']['e'],1e-14) # roundoff: do not assert an e order
 def test_stage_domains_and_fixed_branches(self):
  for c in self.report['cases']:
   for grid in c['grids']:
    d=grid['stage_diagnostics'];self.assertEqual(d['evaluations'],3*(4*grid['steps_per_segment']+1))
    self.assertTrue(all(x>0 and math.isfinite(x)for x in d['minima'].values()))
    self.assertGreater(d['minima']['radius_gap_min'],.7);self.assertGreater(d['minima']['rho_min'],.1)
    for segment in d['segments']:self.assertFalse(segment['branch_crossing_observed'])
    signs=[s['q_min']>0 for s in d['segments']]
    self.assertEqual(signs,[True,False,False]if c['input']['id'].startswith('shear-reversal')else[True]*3)
 def test_exact_volume_relation_every_endpoint(self):
  for c in self.report['cases']:
   for grid in c['grids']:self.assertLess(max(grid['exact_volume_absolute_errors']),1e-14)
 def test_rotation_covariance_all_state_groups(self):
  for r in self.report['covariance']:
   for name,tol in [('stress',1e-8),('e',1e-14),('h',1e-17),('Omega',1e-14)]:self.assertLess(r['difference'][name],tol)
 def test_tensor_basis_rotation_and_input_isolation(self):
  a=[1.,2.,4.,-.7,.2,1.3]
  for x,y in zip(a,g.mand(g.cart(a))):self.assertAlmostEqual(x,y,places=15)
  self.assertAlmostEqual(sum(x*x for x in a),sum(x*x for x in g.rotate(a)),places=13)
  for i in range(3):
   for j in range(3):self.assertAlmostEqual(sum(g.Q[i][k]*g.Q[j][k]for k in range(3)),float(i==j),places=15)
  c=g.cases()[0];before=copy.deepcopy(c);g.integrate(c,16);self.assertEqual(c,before)
 def test_selected_boundary_starts_and_invalid_steps_reject(self):
  for n in (0,-1,1.5,True,4097):
   with self.assertRaises(ValueError):g.integrate(g.cases()[0],n)
  for channel,value in [(13,0.),(13,1.)]:
   c=g.cases()[0];c['initial'][channel]=value
   with self.assertRaises(ValueError):g.integrate(c,16)
  c=g.cases()[0];c['initial'][7:13]=[g.PARAMETERS['R'],0.,0.,0.,0.,0.]
  with self.assertRaises(ValueError):g.integrate(c,16)
 def test_retained_reproduction(self):
  path=Path(g.__file__).resolve().parents[1]/'catalogue/investigations/gis2024-path-reference-v1/reference.json'
  archived=json.loads(path.read_text())
  # Source/protocol identity is exact. Numerics allow cross-platform roundoff;
  # all convergence/domain tests above are recomputed from the current oracle.
  for key in ('contract','basis','coordinate','zero_spin','source_sha256','resolutions','rotation','dependency_sha256'):
   self.assertEqual(self.report[key],archived[key])
  self.assertEqual(len(archived['cases']),len(self.report['cases']))
  for current,saved in zip(self.report['cases'],archived['cases']):
   self.assertEqual(current['input'],saved['input']);self.assertEqual(current['input_sha256'],saved['input_sha256'])
   self.assertEqual(len(saved['grids']),3)
   for a,b in zip(current['grids'],saved['grids']):
    self.assertEqual(a['steps_per_segment'],b['steps_per_segment'])
    err=g.differences(a['trajectory'],b['trajectory'])
    for channel,allowance in dict(stress=1e-6,e=1e-13,h=1e-15,Omega=1e-12).items():
     self.assertLessEqual(err[channel],allowance)


if __name__=='__main__':unittest.main()
