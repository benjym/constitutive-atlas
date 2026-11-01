"""Exact strict centered-middle decision for finite binary64 Mandel operands."""
from fractions import Fraction as F
import math
from .determinant import sign
VERSION='mandel-centered-middle-exact-v1'
def principal_centered_mid_gt(values,width):
    if len(values)!=6:raise ValueError('principal_centered_mid_gt requires six Mandel components')
    for x in (*values,width):
        try:valid=type(x) in (int,float) and math.isfinite(x)
        except OverflowError:valid=False
        if not valid:raise ValueError('principal_centered_mid_gt requires finite real operands')
    if width<0:raise ValueError('principal_centered_mid_gt requires nonnegative width')
    x=[F(float(v))for v in values];t=sum(x[:3]);a,b,c=[3*v-t for v in x[:3]];u,v,z=[3*y for y in x[3:]];w=F(float(width))
    j=(a*a+b*b+c*c+u*u+v*v+z*z)/2
    if j<=3*w*w:return False
    d=a*b*c-(a*v*v+b*z*z+c*u*u)/2;e=u*v*z/2
    return sign(d+j*w-w*w*w,e)<0
