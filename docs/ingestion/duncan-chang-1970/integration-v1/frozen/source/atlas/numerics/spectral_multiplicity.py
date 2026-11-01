"""Exact repeated-extreme controls for finite stored binary64 Mandel tensors."""
from fractions import Fraction as F
import math
from .determinant import sign

VERSION = 'mandel-spectral-multiplicity-exact-v1'


def repeated_extremes(values):
    if len(values) != 6:
        raise ValueError('spectral multiplicity requires six Mandel components')
    for value in values:
        try:
            valid = type(value) in (int, float) and math.isfinite(value)
        except OverflowError:
            valid = False
        if not valid:
            raise ValueError('spectral multiplicity requires finite real components')
    x = [F(float(value)) for value in values]
    trace = sum(x[:3])
    a, b, c = [3*value-trace for value in x[:3]]
    u, v, w = [3*value for value in x[3:]]
    j = (a*a+b*b+c*c+u*u+v*v+w*w)/2
    if not j:
        return True, True
    r = a*b*c-(a*v*v+b*w*w+c*u*u)/2
    s = u*v*w/2
    if 4*j*j*j-27*(r*r+2*s*s) or r*s:
        return False, False
    direction = sign(r, s)
    return direction < 0, direction > 0
