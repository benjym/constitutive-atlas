"""Nearest-even binary64 determinant of exact orthonormal Mandel inputs.

Exact rational coefficients represent A+B*sqrt(2). An approximate floating
candidate is accepted only after exact algebraic rounding-interval comparisons.
"""
from fractions import Fraction as F
import math
import struct

VERSION='mandel-determinant-exact-radical-rne-v1-candidate'
MAX_BITS=0x7fefffffffffffff

def binary(bits):return struct.unpack('>d',struct.pack('>Q',bits))[0]
def bits(value):return struct.unpack('>Q',struct.pack('>d',value))[0]
def sign(a,b):
 if not a:return (b>0)-(b<0)
 if not b:return (a>0)-(a<0)
 if (a>0)==(b>0):return 1 if a>0 else -1
 relation=(a*a>2*b*b)-(a*a<2*b*b)
 return relation if a>0 else -relation

def rounded(a,b):
 direction=sign(a,b)
 if not direction:return 0.
 if direction<0:a,b=-a,-b
 def compare(t):return sign(a-t,b)
 def midpoint(low,high):return (F(binary(low))+(F(2)**1024 if high>MAX_BITS else F(binary(high))))/2
 if compare(midpoint(MAX_BITS,MAX_BITS+1))>=0:raise ValueError('determinant final result overflows binary64')
 def contains(candidate):
  if not 0<=candidate<=MAX_BITS:return False
  even=not candidate&1
  if candidate:
   lower=compare(midpoint(candidate-1,candidate))
   if lower<0 or lower==0 and not even:return False
  upper=compare(midpoint(candidate,candidate+1))
  return upper<0 or upper==0 and even
 try:guide=float(a)+math.sqrt(2)*float(b)
 except OverflowError:guide=math.inf
 if math.isfinite(guide)and guide>=0:
  raw=bits(guide)
  for candidate in range(max(0,raw-2),min(MAX_BITS,raw+2)+1):
   if contains(candidate):return math.copysign(binary(candidate),direction)if candidate else 0.
 lo,hi=0,MAX_BITS
 while lo<hi:
  middle=lo+(hi-lo)//2+1
  if compare(F(binary(middle)))>=0:lo=middle
  else:hi=middle-1
 relation=compare(midpoint(lo,lo+1));chosen=lo if relation<0 or relation==0 and not lo&1 else lo+1
 return math.copysign(binary(chosen),direction)if chosen else 0.

def determinant(values):
 if len(values)!=6:raise ValueError('determinant requires six Mandel components')
 for v in values:
  if type(v)not in(int,float):raise ValueError('determinant requires finite real components')
  try:valid=math.isfinite(v)
  except OverflowError:valid=False
  if not valid:raise ValueError('determinant requires finite real components')
 x,y,z,u,v,w=[F.from_float(float(t))for t in values]
 return rounded(x*y*z-(x*v*v+y*w*w+z*u*u)/2,u*v*w/2)
