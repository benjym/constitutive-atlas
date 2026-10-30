import json,unittest,hashlib
from decimal import Decimal as D,localcontext
from pathlib import Path
from tools.clay2013_invariant_reference import generate
from atlas.model import ROOT
P=ROOT/'catalogue/investigations/clay2013-algebra-v1'
class Identities(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.d=json.loads((P/'invariants.json').read_text())
 def test_reproducible(self):self.assertEqual(self.d,generate())
 def test_record_integrity(self):
  record=json.loads((P/'manifest.json').read_text())
  self.assertEqual(record['source_sha256'],'21834ab9da81ec2cdebdf3a3d7f97b691d47bf481a24432bc0562aca9f503281')
  self.assertFalse(record['complete_model']);self.assertEqual(record['scientific_review'],'pending')
  required={'tools/inspect_clay2013_rate.py','tools/reference_clay2013_cartesian.py',
            'tools/clay2013_invariant_reference.py','tests/test_clay2013_rate.py','tests/test_clay2013_invariants.py',
            'catalogue/source-audits/clay-hypoplasticity-2013-rate.json','catalogue/investigations/clay2013-algebra-v1/invariants.json',
            'docs/models/clay2013-source-rate.md','docs/models/clay2013-cartesian-source-note.md','docs/reviews/clay2013-algebra-review.md'}
  self.assertEqual(set(record['files']),required)
  for name,digest in record['files'].items():self.assertEqual(hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),digest,name)
 def test_Fm_forms_and_strict_spd_examples(self):
  for r in self.d['fixtures']:
   with self.subTest(case=r['name']):
    self.assertLess(D(r['absolute_formula_difference']),D('1e-165'))
    self.assertGreater(D(r['denominator']),0)
    self.assertGreaterEqual(D(r['Fm_stable']),0)
    self.assertLess(D(r['Fm_stable']),1)
 def test_isotropic_and_Lode_endpoint_limits(self):
  with localcontext() as c:
   c.prec=180
   for r in self.d['fixtures']:
    if r['isotropic']:
     self.assertEqual(D(r['Fm_stable']),0);self.assertIsNone(r['lode_cosine'])
     self.assertEqual(D(r['direction_distance_to_isotropic']),0)
    if r['name'].startswith('axisymmetric'):
     expected=-1 if D(r['deviation'])>0 else 1
     self.assertLess(abs(D(r['lode_cosine'])-expected),D('1e-165'))
     ratio=D(r['direction_distance_to_isotropic'])/abs(D(r['deviation']))
     self.assertTrue(D('3.7')<ratio<D('4.3'))
 def test_floating_point_exact_isotropic_counterexample(self):
  row=next(x for x in self.d['float_exact_isotropic_edges'] if x['p']==.3)
  self.assertNotEqual(row['j2'],0);self.assertLess(row['lode_cosine'],-1)
if __name__=='__main__':unittest.main()
