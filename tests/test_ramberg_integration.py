import unittest
from tools.check_native_fixture_contracts import PRIOR_THIRTEEN,DUNCAN,DUNCAN_HASH,RAMBERG,RAMBERG_HASH,OCC,check_recorded_failure
class RambergClosedCatalogue(unittest.TestCase):
 def test_prior_failure_is_preserved_only_for_exact_new_catalogue(self):
  definitions={**PRIOR_THIRTEEN,DUNCAN:DUNCAN_HASH,RAMBERG:RAMBERG_HASH}
  message='failed knot 1 residual 0.00086977407608239442 trials 1 de0 0.0001 de1 0\ndrained replay failed: '+OCC+' singular mixed-control system; last committed knot retained\n'
  self.assertIn('current-fifteen',check_recorded_failure(message,definitions))
  for bad in [{**definitions,RAMBERG:'0'*64},{**definitions,'linear-elastic':'0'*64},{**definitions,'unknown':'0'*64},{k:v for k,v in definitions.items() if k!=DUNCAN}]:
   with self.assertRaises(AssertionError):check_recorded_failure(message,bad)
