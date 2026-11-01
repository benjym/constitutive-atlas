import copy,tempfile,unittest
from pathlib import Path
from test_qualification import Fixture
from parity import compare
class ParityTests(unittest.TestCase):
 def setUp(self):
  self.t=tempfile.TemporaryDirectory();self.addCleanup(self.t.cleanup);self.f=Fixture(Path(self.t.name));self.n=self.f.data;self.w=copy.deepcopy(self.n);self.w['backend']='wasm'
 def audit(self):return compare(self.n,self.w,self.f.rows,1e-7)
 def test_exact(self):self.assertTrue(self.audit()['native_wasm_parity_pass'])
 def test_stress_poison(self):
  self.w['rows'][0]['calls'][0]['response']['state'][0]+=1.;self.assertRaisesRegex(ValueError,'state parity',self.audit)
 def test_history_poison(self):
  self.w['rows'][0]['restart_fresh'][0]['response']['state'][8]+=1e-6;self.assertRaisesRegex(ValueError,'state parity',self.audit)
 def test_wrong_loading(self):
  self.w['rows'][0]['calls'][0]['request']['strain'][0]+=.1;self.assertRaisesRegex(ValueError,'literal',self.audit)
 def test_missing(self):self.w['rows'].pop();self.assertRaisesRegex(ValueError,'coverage',self.audit)
if __name__=='__main__':unittest.main()
