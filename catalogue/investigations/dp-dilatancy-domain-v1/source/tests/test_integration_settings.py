"""Offline verification of captured settings responses and legacy compatibility."""
import copy
import gzip
import json
import unittest
from tools.verify_integration_settings import ROOT,RAW,DEFAULT_RAW,verify,verify_default

class IntegrationSettingsTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=json.loads(gzip.decompress((ROOT/RAW).read_bytes()))
  cls.defaults=json.loads(gzip.decompress((ROOT/DEFAULT_RAW).read_bytes()))
 def test_legacy_responses_unchanged(self):
  prior=json.loads(gzip.decompress((ROOT/'catalogue/investigations/linearization-api-v1/responses.json.gz').read_bytes()))
  self.assertEqual(self.defaults,prior)
  self.assertEqual(verify_default(self.defaults)['cases'],21)
 def test_configured_refinement_budgets_and_provenance(self):
  report=verify(self.rows)
  self.assertEqual((report['cases'],report['bounded_rollback_cases'],report['invalid_requests']),(30,5,14))
  self.assertLess(report['rate_errors'][-1],report['rate_errors'][0]/100)
  self.assertLess(report['implicit_root_errors'][-1],report['implicit_root_errors'][0])
 def test_corrupted_settings_results_rejected(self):
  for mutation in (lambda r:r[0]['response']['integration_settings'].__setitem__('rate_tolerance',1),
                   lambda r:r[0]['response']['state_tangent'][6].__setitem__(0,1),
                   lambda r:r[6]['response']['state'].__setitem__(6,2),
                   lambda r:r[7]['response']['diagnostics'].__setitem__('substeps',3)):
   rows=copy.deepcopy(self.rows);mutation(rows)
   with self.assertRaises(ValueError):verify(rows)
 def test_incomplete_nonfinite_and_false_success_rejected(self):
  with self.assertRaises(ValueError):verify(self.rows[:-1])
  for mutation in (lambda r:r[0]['response']['state'].__setitem__(0,float('nan')),
                   lambda r:r[0]['response']['state'].pop(),
                   lambda r:r[-1].__setitem__('returncode',0)):
   rows=copy.deepcopy(self.rows);mutation(rows)
   with self.assertRaises(ValueError):verify(rows)

if __name__=='__main__':unittest.main()
