#!/usr/bin/env python3
"""New exact scalar identity, independent of Atlas and constitutive host choices."""
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import json


def embed(x):
    a,b,c,d=x
    return [[a,c,d],[c,b,0],[d,0,b]]


def product(x,y):
    a,b,c,d=x;e,f,g,h=y
    return [a*e+c*g+d*h,b*f+c*g,a*g+c*f,d*e+b*h]


def trace(x):
    return x[0]+2*x[1]


def multiply(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def cartesian_cubic(x):
    a=embed(x);cube=multiply(multiply(a,a),a)
    return sum(cube[i][i] for i in range(3))


def run():
    count=0
    for k in range(1,101):
        x=[Q(k+2,7),Q(3-k,11),Q(k-8,13),Q(k+4,17)]
        true=cartesian_cubic(x)
        defect=trace(x)*(x[2]**2-x[3]**2)
        assert trace(product(product(x,x),x))-true==defect
        assert trace(product(x,product(x,x)))-true==defect
        count+=2
        # Normalized deviator has zero reduced trace; keep exact arithmetic.
        mean=trace(x)/3;dev=[x[0]-mean,x[1]-mean,x[2],x[3]]
        assert trace(dev)==0
        assert trace(product(product(dev,dev),dev))==cartesian_cubic(dev)
        assert trace(product(dev,product(dev,dev)))==cartesian_cubic(dev)
        # Rotation in tangential plane preserves c²+d² and diagonal pair.
        # Rational 3/5,4/5 rotation avoids trigonometric roundoff.
        a,b,c,d=dev;rot=[a,b,Q(3,5)*c-Q(4,5)*d,Q(4,5)*c+Q(3,5)*d]
        assert cartesian_cubic(rot)==cartesian_cubic(dev)
        assert trace(product(product(rot,rot),rot))==trace(product(product(dev,dev),dev))
        count+=5
    x=[Q(2),Q(3),Q(5),Q(7)]
    assert product(x,x)==[78,34,25,35]
    assert embed(product(x,x))!=multiply(embed(x),embed(x))
    count+=2
    return {'identity':'reduced-cubic-trace-v2','passed':True,'exact_checks':count,
            'general_defect':'trace(X)*(X3**2-X4**2)',
            'trace_free_defect':0,'both_associations_checked':True,
            'original_nonclosure_witness_preserved':True,
            'constitutive_host_verified':False,'compiled_calls':0,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}


if __name__=='__main__':
    print(json.dumps(run(),indent=2))
