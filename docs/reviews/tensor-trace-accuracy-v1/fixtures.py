"""Independent exact-input Fraction oracle and deterministic design corpus."""
from fractions import Fraction
import itertools
import json
import math
import random
import struct
import sys
import prototype

def rational(xs):
    if any(type(x)is not float or not math.isfinite(x)for x in xs):raise ValueError('finite binary64 only')
    q=sum((Fraction.from_float(x)for x in xs),Fraction())
    try:y=float(q)
    except OverflowError:raise OverflowError('final exact sum overflow')
    if not math.isfinite(y):raise OverflowError('final exact sum overflow')
    return y if y!=0 else 0.0

def inputs():
    tiny=math.ulp(0.);maximum=sys.float_info.max;minimum=sys.float_info.min
    base=[('sand-cancellation',[500.,1e-130,-500.]),('unit-residual',[1.,2.**-54,-1.]),('subnormal-residual',[1.,tiny,-1.]),('max-subnormal-residual',[maximum,tiny,-maximum]),('finite-intermediate-overflow',[maximum,maximum,-maximum]),('negative-finite-overflow',[-maximum,-maximum,maximum]),('true-overflow',[maximum,maximum,0.]),('negative-overflow',[-maximum,-maximum,0.]),('overflow-midpoint',[maximum,2.**970,0.]),('below-overflow-midpoint',[maximum,math.nextafter(2.**970,0.),0.]),('normal-tie-even',[1.,2.**-53,0.]),('normal-tie-odd',[math.nextafter(1.,math.inf),2.**-53,0.]),('normal-tie-negative',[-1.,-2.**-53,0.]),('double-residual',[1.,2.**-53,2.**-54]),('subnormal-sum',[tiny,tiny,-tiny]),('normal-subnormal-boundary',[minimum,-math.nextafter(minimum,0.),-tiny]),('subnormal-positive',[tiny,tiny,tiny]),('subnormal-negative',[-tiny,-tiny,-tiny]),('all-minus-zero',[-0.,-0.,-0.]),('mixed-zero',[0.,-0.,0.]),('exact-cancel',[-1.,1.,-0.]),('ordinary',[.001,-.0003,.0002])]
    out=[]
    for name,xs in base:
        for j,perm in enumerate(dict.fromkeys(itertools.permutations(xs))):out.append((name+'-p'+str(j),list(perm)))
    return out

def build():
    rows=[];paths={}
    for name,xs in inputs():
        try:expected=rational(xs)
        except OverflowError:
            try:prototype.sum3(*xs)
            except OverflowError:pass
            else:raise AssertionError('overflow accepted')
            row={'id':name,'inputs_hex':[x.hex()for x in xs],'ok':False,'reason':'finite final overflow'}
        else:
            actual,path=prototype.sum3(*xs,diagnostic=True)
            assert prototype.bits(actual)==prototype.bits(expected),(name,actual,expected)
            paths[path]=paths.get(path,0)+1
            exact=sum((Fraction.from_float(x)for x in xs),Fraction())
            row={'id':name,'inputs_hex':[x.hex()for x in xs],'ok':True,'expected_hex':expected.hex(),'expected_bits':f'{prototype.bits(expected):016x}','exact_numerator':str(exact.numerator),'exact_denominator':str(exact.denominator),'prototype_path':path}
        rows.append(row)
    return {'version':'trace-exact-input-fraction-corpus-v1','rounding':'nearest ties even; final finite only; exactzero positive','records':rows,'paths':paths,'compiled_execution':False}

def random_check(count=12000):
    rng=random.Random(20261031);fallback=0
    for _ in range(count):
        xs=[]
        for j in range(3):
            b=rng.getrandbits(64)
            if (b>>52)&2047==2047:b^=1<<52
            xs.append(struct.unpack('>d',struct.pack('>Q',b))[0])
        try:y=rational(xs)
        except OverflowError:
            try:prototype.sum3(*xs)
            except OverflowError:continue
            raise AssertionError('random overflow accepted')
        z,path=prototype.sum3(*xs,diagnostic=True);assert prototype.bits(z)==prototype.bits(y)
        fallback+=path=='integer-fallback'
    return {'seed':20261031,'trials':count,'fallbacks':fallback,'performance_benchmark':False}

if __name__=='__main__':print(json.dumps(build(),indent=2,allow_nan=False))
