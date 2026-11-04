"""Regression proposal: reject unsupported arithmetic or preserve exact transport."""
import unittest
from decimal import Decimal,localcontext
from fractions import Fraction
from tools import reference_barodesy2017_caller_points as r
class ExactLoading(unittest.TestCase):
 def test_widely_scaled_cumulative_is_exact_or_explicitly_rejected(self):
  increments=[[2.**500,0.,0.,0.,0.,0.],[2.**-100,0.,0.,0.,0.,0.]]
  try:pieces,points=r.split_path(increments,1)
  except (ValueError,ArithmeticError):return
  expected=sum((Fraction(x[0])for x in increments),Fraction())
  actual=Fraction(Decimal(points[-1]['cumulative_strain_decimal'][0]))
  self.assertEqual(actual,expected,'silent rounding of supposedly exact accumulated loading')
if __name__=='__main__':unittest.main()
