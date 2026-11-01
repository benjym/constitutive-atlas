"""Challenge saved-reference coverage and integrity; no candidate or oracle runs."""
import copy,importlib.util,unittest
from pathlib import Path
P=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('independent_assessor',P/'assess.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
class ReferenceTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.original={n:a.read(P/f'reference-{n}.json.gz')for n in a.NAMES}
 def test_original(self):self.assertTrue(a.assess(P,self.original)['reference_adequacy_pass'])
 def reject(self,change):
  docs=copy.deepcopy(self.original);change(docs)
  with self.assertRaises(ValueError):a.assess(P,docs)
 def test_missing_case(self):self.reject(lambda d:d['p80-t12']['cases'].pop())
 def test_missing_precision(self):self.reject(lambda d:d.pop('p50-t12'))
 def test_missing_full_state(self):self.reject(lambda d:d['p80-t12']['cases'][0]['samples'][-1]['state'].pop())
 def test_changed_response(self):self.reject(lambda d:d['p80-t12']['cases'][0]['samples'][-1]['state'].__setitem__(0,'999999'))
 def test_forged_yield_diagnostic(self):self.reject(lambda d:d['p80-t12']['cases'][0]['samples'][-1]['diagnostics'].__setitem__('yield_Pa','123'))
 def test_failed_case_not_omitted(self):self.reject(lambda d:d['p80-t12']['cases'][0].__setitem__('status','failed'))
 def test_changed_strain_control(self):self.reject(lambda d:d['p80-t12']['cases'][0]['samples'][-1]['strain'].__setitem__(0,'.3'))
if __name__=='__main__':unittest.main()
