"""Source-bound archived numerical replay; no executable or build calls."""
import unittest
from pathlib import Path
from atlas.evidence import verify_manifest_files
from atlas.model import all_models
from tools import barodesy2017_rate_study as rates
from tools import barodesy2017_material_ad as ad
ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'catalogue/investigations/barodesy2017-runtime-v1'
class RuntimeEvidence(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.manifest=verify_manifest_files(ROOT,str((PACKET/'manifest.json').relative_to(ROOT)))
 def test_bounded_scope_and_no_public_admission(self):
  self.assertFalse(self.manifest['public_admission']);self.assertFalse(self.manifest['complete_model'])
  self.assertNotIn(rates.catalogue()[0]['id'],{m['id'] for m in all_models()})
 def test_rates_fresh_native_and_relocated_wasm(self):
  native=rates.assess(rates.read(PACKET/'rates-native.json'),check_artifacts=False)
  wasm=rates.assess(rates.read(PACKET/'rates-wasm.json'),check_artifacts=False,native_report_path=PACKET/'rates-native.json')
  for r in (native,wasm):
   self.assertEqual((r['cases'],r['support_cases'],r['invalids']),(111,3,16));self.assertFalse(r['artifacts_verified_now']);self.assertTrue(r['fresh_reference_verified'])
 def test_material_ad_fresh_native_and_relocated_wasm(self):
  native=ad.assess(rates.read(PACKET/'ad-native.json'),check_artifacts=False)
  wasm=ad.assess(rates.read(PACKET/'ad-wasm.json'),check_artifacts=False,native_report_path=PACKET/'ad-native.json')
  for r in (native,wasm):
   self.assertEqual((r['regular_cases'],r['invalid_recovery_pairs']),(21,20));self.assertFalse(r['artifacts_verified_now']);self.assertTrue(r['regular_instantaneous_material_AD_validated']);self.assertFalse(r['zero_hydro_derivatives'])
if __name__=='__main__':unittest.main()
