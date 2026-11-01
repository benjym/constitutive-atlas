"""Synthetic covariance checker tests; no compiled execution."""
import copy
import math
import unittest
from covariance import rotate,assess

class CovarianceTests(unittest.TestCase):
 def fixture(self):
  a={'ok':True,'values':[float(x) for x in range(26)],'directional':[float(2*x) for x in range(26)]}
  b={'ok':True,'values':rotate(a['values']),'directional':rotate(a['directional'])}
  req={'parents':[{}],'requests':[{'id':'synthetic','column':0},{}]}
  return req,[a,b]
 def test_rotation_is_involution(self):
  for n in [6,26]:self.assertEqual(rotate(rotate(list(range(n)))),list(range(n)))
 def test_scalar_fields_preserved(self):
  values=list(range(26));r=rotate(values);self.assertEqual(r[6],6);self.assertEqual(r[25],25)
 def test_positive_fixture(self):
  r,v=self.fixture();self.assertTrue(assess(r,v)['proper_rotation_covariance_pass'])
 def test_missing_response(self):
  r,v=self.fixture()
  with self.assertRaises(AssertionError):assess(r,v[:1])
 def test_bad_value(self):
  r,v=self.fixture();v[1]['values'][7]+=1
  with self.assertRaises(AssertionError):assess(r,v)
 def test_bad_derivative(self):
  r,v=self.fixture();v[1]['directional'][9]+=1
  with self.assertRaises(AssertionError):assess(r,v)
 def test_nonfinite(self):
  r,v=self.fixture();v[1]['values'][12]=math.nan
  with self.assertRaises(AssertionError):assess(r,v)
 def test_invalid_result(self):
  r,v=self.fixture();v[1]['ok']=False
  with self.assertRaises(AssertionError):assess(r,v)
if __name__=='__main__':unittest.main()
