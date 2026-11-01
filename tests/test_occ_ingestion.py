"""Regression of independently reviewed OCC exact-wire references and retained defects."""
import hashlib,json,math,unittest
from pathlib import Path
from atlas.model import load,evaluation_environment
ROOT=Path(__file__).resolve().parents[1]
MODEL=ROOT/'models/original-cam-clay-sw-electronic-log-recovery-v1.json'
class OriginalCamClay(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.model=load(MODEL);cls.requests=json.loads((ROOT/'docs/ingestion/original-cam-clay/execution-v2/requests.json').read_text())
 def environment(self,z,de):
  old={'sigma':z[:6],'v':z[6]};return evaluation_environment(self.model,old,old,de)
 def test_independent_exact_wire_corpus(self):
  self.assertEqual(hashlib.sha256(MODEL.read_bytes()).hexdigest(),self.requests['model_sha256'])
  for c in self.requests['cases']:
   with self.subTest(c['id']):
    e=self.environment(c['initial'],c['de']);actual=tuple(e['sigma_end'].v)+(e['v_end'],)
    self.assertEqual(len(actual),7)
    self.assertTrue(all(math.isfinite(v) for v in actual))
    self.assertLessEqual(max(abs(a-b)/max(1000. if i<6 else 1.,abs(b)) for i,(a,b) in enumerate(zip(actual,c['expected']))),2e-10)
    if not any(c['de']):self.assertEqual(list(actual),c['initial'])
 def test_unrepresentable_positive_pressure_rejected(self):
  c=self.requests['cases'][10]
  with self.assertRaises(ValueError):self.environment(c['initial'],[-.3333,-.3333,-.3333,0.,0.,0.])
