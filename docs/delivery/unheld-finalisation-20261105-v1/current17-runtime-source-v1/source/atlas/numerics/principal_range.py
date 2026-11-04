"""Exact inclusive spectral-range decision for finite binary64 Mandel inputs."""
from fractions import Fraction as F
import math
from .determinant import sign
VERSION='mandel-principal-range-exact-v1'
def principal_range_le(values,width):
    if len(values)!=6:raise ValueError('principal_range_le requires six Mandel components')
    for x in (*values,width):
        try:valid=type(x) in (int,float) and math.isfinite(x)
        except OverflowError:valid=False
        if not valid:raise ValueError('principal_range_le requires finite real operands')
    if width<0:raise ValueError('principal_range_le requires nonnegative width')
    x=[F(float(v))for v in values];t=sum(x[:3]);a,b,c=[3*v-t for v in x[:3]];u,v,w=[3*v for v in x[3:]]
    j=(a*a+b*b+c*c+u*u+v*v+w*w)/2;q=(3*F(float(width)))**2
    if q<3*j:return False
    if q>=4*j:return True
    d=a*b*c-(a*v*v+b*w*w+c*u*u)/2;e=u*v*w/2
    h=((q-6*j)*q+9*j*j)*q-4*j*j*j+27*(d*d+2*e*e)
    return sign(h,54*d*e)>=0
