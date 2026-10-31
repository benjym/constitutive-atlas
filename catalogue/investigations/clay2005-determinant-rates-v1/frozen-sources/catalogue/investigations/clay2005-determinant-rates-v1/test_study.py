"""Prospective tests concern reference assembly, never the material's answer."""
import unittest,json,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from prepare import prepare,candidate_contract,OLD,PACKET,read,sha
class StudyContract(unittest.TestCase):
 def test_only_determinant_and_description_change(self):candidate_contract()
 def test_original_calls_and_policies_identical(self):
  new=prepare();old=read(OLD/'protocol.json');self.assertEqual(new['cases'][:109],old['cases']);self.assertEqual(new['finite_only_parity'],old['finite_only_parity'])
  for key,value in old['policy'].items():self.assertEqual(new['policy'][key],value)
 def test_new_actual_input_references_and_budgets(self):
  p=prepare();f=read(PACKET/'prospective-freeze.json');r={c['id']:c for c in read(PACKET/'results.json')['cases']};self.assertEqual(len(p['cases']),120)
  for new,old in zip(p['cases'][109:],f['cases']):
   self.assertEqual(new['args'],old['args']);self.assertEqual(new['id'],'boundary-accuracy/'+old['id'])
   e=new['expectation'];v=list(map(float,r[old['id']]['precision_results']['240']['values']));self.assertEqual(e['values'],v)
   self.assertEqual(e['absolute_budgets'],[1e-10*max(1.,abs(x))for x in v[:6]]+[1e-15+2e-13*abs(v[6])]);self.assertEqual(e['parity_budgets'],e['absolute_budgets'])
 def test_independent_reference_replay_identical(self):
  receipt=read(HERE/'reference-replay.json');self.assertTrue(receipt['identical_retained_boundary_results']);self.assertTrue(receipt['identical_retained_normalization_results']);self.assertEqual(receipt['boundary_results_sha256'],sha(PACKET/'results.json'))
if __name__=='__main__':unittest.main()
