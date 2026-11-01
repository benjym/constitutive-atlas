import copy,unittest
from assess import coordinates
class CoordinateAuditTests(unittest.TestCase):
 def fixture(self):
  s={'variation':['1','0','0'],'normalized_variation':['1','0','0'],'decimal_exponent':0,'base_state_cartesian':['0']*27}
  return {'status':'completed','method':'power10-homogeneous-variation-v2','precision':80,'samples':[copy.deepcopy(s) for _ in range(17)]}
 def test_valid(self):coordinates(self.fixture())
 def test_missing_sample(self):
  r=self.fixture();r['samples'].pop()
  with self.assertRaisesRegex(ValueError,'coverage'):coordinates(r)
 def test_wrong_exponent(self):
  r=self.fixture();r['samples'][-1]['decimal_exponent']=1
  with self.assertRaisesRegex(ValueError,'reconstruction'):coordinates(r)
 def test_nonfinite(self):
  r=self.fixture();r['samples'][-1]['base_state_cartesian'][0]='NaN'
  with self.assertRaisesRegex(ValueError,'nonfinite'):coordinates(r)
 def test_asymmetric_base(self):
  r=self.fixture();r['samples'][-1]['base_state_cartesian'][4]='1'
  with self.assertRaisesRegex(ValueError,'symmetry'):coordinates(r)
if __name__=='__main__':unittest.main()
