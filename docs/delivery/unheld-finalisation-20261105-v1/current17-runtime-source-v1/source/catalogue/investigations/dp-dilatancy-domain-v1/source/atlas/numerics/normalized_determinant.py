"""Correctly rounded det(A)/trace(A)^3 from original finite Mandel inputs.

No normalized tensor components, rounded determinant or rounded trace/cube.
The unchanged determinant rounding routine accepts exact rational radical
coefficients, including a non-dyadic quotient denominator.
"""
from fractions import Fraction as F
import math
from .determinant import rounded

VERSION='mandel-normalized-determinant-exact-quotient-rne-v1-candidate'

def normalized_determinant(values):
 if len(values)!=6:raise ValueError('normalized determinant requires six Mandel components')
 for value in values:
  if type(value)not in(int,float):raise ValueError('normalized determinant requires finite real components')
  try:valid=math.isfinite(value)
  except OverflowError:valid=False
  if not valid:raise ValueError('normalized determinant requires finite real components')
 x,y,z,u,v,w=[F.from_float(float(t))for t in values]
 trace=x+y+z
 if not trace:raise ValueError('normalized determinant requires nonzero exact trace')
 cube=trace**3
 try:return rounded((x*y*z-(x*v*v+y*w*w+z*u*u)/2)/cube,u*v*w/(2*cube))
 except ValueError:raise ValueError('normalized determinant final result overflows binary64')from None
