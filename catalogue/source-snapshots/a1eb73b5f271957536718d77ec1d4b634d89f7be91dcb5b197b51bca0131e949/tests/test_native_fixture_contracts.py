"""Strict failure allocation rejects changed catalogue, branch or work signatures."""
import json,unittest
from atlas.model import ROOT
from tools.check_native_fixture_contracts import OCC,OCC_HASH,GIS_FAILURE,check_recorded_failure
class StrictFixtureContracts(unittest.TestCase):
 def test_historical_gis_signature_stays_exact(self):
  self.assertIn('historical',check_recorded_failure(GIS_FAILURE,{}))
  with self.assertRaises(AssertionError):check_recorded_failure('other failure\n',{})
 def test_current_occ_signature_and_catalogue_are_closed(self):
  definitions=json.loads((ROOT/'catalogue/laboratory-package-policy.json').read_text())['models']
  message='failed knot 1 residual 0.00086977407608239442 trials 1 de0 0.0001 de1 0\ndrained replay failed: '+OCC+' singular mixed-control system; last committed knot retained\n'
  self.assertEqual(definitions[OCC],OCC_HASH);self.assertIn('current-thirteen',check_recorded_failure(message,definitions))
  for bad in [message.replace('trials 1','trials 2'),message.replace('de1 0','de1 -0.00002'),message.replace('0.00086977407608239442','0'),GIS_FAILURE]:
   with self.subTest(message=bad),self.assertRaises(AssertionError):check_recorded_failure(bad,definitions)
  with self.assertRaises(AssertionError):check_recorded_failure(message,{**definitions,OCC:'0'*64})
