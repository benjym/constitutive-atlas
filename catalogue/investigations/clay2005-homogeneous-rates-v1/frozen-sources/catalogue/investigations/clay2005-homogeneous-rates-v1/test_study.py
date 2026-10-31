"""Prospective structural checks without material observations."""
import unittest,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from prepare import prepare,candidate_contract,OLD,read
class StudyContract(unittest.TestCase):
 def test_only_original_stress_ratio_changes(self):candidate_contract()
 def test_all_requests_and_gates_identical(self):
  new=prepare();old=read(OLD/'protocol.json')
  self.assertEqual(len(new['cases']),120)
  for field in ('cases','policy','finite_only_parity'):self.assertEqual(new[field],old[field])
 def test_cache_free_source_closure(self):
  p=prepare()
  self.assertFalse(any('__pycache__'in name or name.endswith(('.pyc','.pyo'))for name in p['files']))
  self.assertIn('atlas/evidence_sources.py',p['files'])
if __name__=='__main__':unittest.main()
