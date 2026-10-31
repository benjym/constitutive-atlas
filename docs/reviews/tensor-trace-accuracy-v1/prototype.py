"""Bounded three-binary64 trace design prototype; no Atlas imports.

Bit integer fallback is executable specification for a fixed-limb C++ fallback.
Independent expected values in fixtures.py use Fraction, not this decoder/rounder.
"""
import math
import struct

VERSION='three-binary64-exact-rne-with-eft-fastpath-design-v1'
def bits(x):return struct.unpack('>Q',struct.pack('>d',x))[0]
def frombits(x):return struct.unpack('>d',struct.pack('>Q',x))[0]
def check(x):
    if type(x)is not float or not math.isfinite(x):raise ValueError('finite binary64 required')

def units(x):
    """Exact signed integer coefficient of2**-1074."""
    b=bits(x);fraction=b&((1<<52)-1);exponent=(b>>52)&2047
    n=fraction if exponent==0 else ((1<<52)|fraction)<<(exponent-1)
    return -n if b>>63 else n

def rounded(n):
    """Integer multiple2**-1074 -> nearest-even binary64, finite only."""
    if n==0:return 0.0
    sign=1<<63 if n<0 else 0;n=abs(n)
    if n<(1<<52):return frombits(sign|n)
    shift=max(0,n.bit_length()-53);q=n>>shift
    if shift:
        remainder=n-(q<<shift);half=1<<(shift-1)
        if remainder>half or(remainder==half and q&1):q+=1
    if q==(1<<53):q>>=1;shift+=1
    exponent=shift+1
    if exponent>=2047:raise OverflowError('exact trace rounds outside finite binary64')
    return frombits(sign|(exponent<<52)|(q-(1<<52)))

def twosum(a,b):
    s=a+b
    if not math.isfinite(s):return None
    z=s-a;u=s-z;v=a-u;w=b-z;e=v+w
    if not all(math.isfinite(x)for x in(z,u,v,w,e)):return None
    return s,e

def sum3(a,b,c,diagnostic=False):
    for x in(a,b,c):check(x)
    # TwoSum uses round-to-nearest, binary64 and gradual underflow. No fast-math.
    # Returning when both residuals are zero proves the exact result, rather
    # than assuming an arbitrary compensated final addition is correctly rounded.
    first=twosum(a,b)
    if first is not None:
        second=twosum(first[0],c)
        if second is not None and first[1]==0 and second[1]==0:
            out=second[0] if second[0]!=0 else 0.0
            return (out,'exact-eft')if diagnostic else out
        # Exact expansion: exactsum = h + low + tail. Certify h when
        # 2*max(abs(low),abs(tail)) is strictly inside both rounding midpoints.
        if second is not None:
            residual=twosum(first[1],second[1])
            finish=twosum(second[0],residual[0])if residual is not None else None
            if finish is not None:
                h,tail=finish;low=residual[1]
                if tail==0 and low==0:
                    out=h if h!=0 else 0.0
                    return(out,'exact-expansion')if diagnostic else out
                neighbors=[math.nextafter(h,-math.inf),math.nextafter(h,math.inf)]
                if h!=0 and all(math.isfinite(x)for x in neighbors):
                    gap=min(abs(h-x)for x in neighbors)
                    if max(abs(low),abs(tail)) < gap*.25:
                        return(h,'certified-expansion')if diagnostic else h
    out=rounded(units(a)+units(b)+units(c))
    return(out,'integer-fallback')if diagnostic else out

def jet_trace(values,derivatives):
    if len(values)!=3 or len(derivatives)!=3 or any(len(row)!=38 for row in derivatives):raise ValueError('three diagonals and38 directions required')
    # Candidate-only construction: failure never exposes a partially filled Jet.
    v=sum3(*values)
    d=[sum3(*(derivatives[i][j]for i in range(3)))for j in range(38)]
    return v,d
