import copy,json,unittest
from tools.barodesy2017_reference_check import fresh_cases,verify_reference
class FreshReference(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.ref=fresh_cases()
 def test_fresh_complete(self):self.assertEqual(verify_reference(self.ref)['cases'],111)
 def test_corruptions(self):
  mutations=[lambda r:r['cases'][0]['oracle']['sigma_rhs'].__setitem__(0,0.),lambda r:r['cases'][0]['request']['state']['sigma'].__setitem__(0,1001.),lambda r:r['cases'][0]['precision_refinement'].__setitem__('rate_absolute_max',1.),lambda r:r['cases'][0]['oracle'].__setitem__('branch','regular'),lambda r:r['cases'][0]['request']['increment'].__setitem__(3,False),lambda r:r.__setitem__('version','changed'),lambda r:r['formula_source'].__setitem__('selected','Appendix6p'),lambda r:r['rejected_cases'][0].__setitem__('message','forged'),lambda r:r['cases'].__setitem__(1,copy.deepcopy(r['cases'][0])),lambda r:r['cases'].pop()]
  for i,mutate in enumerate(mutations):
   with self.subTest(case=i):
    r=copy.deepcopy(self.ref);mutate(r)
    with self.assertRaises(ValueError):verify_reference(r)
if __name__=='__main__':unittest.main()
