"""Independent polynomial-GCD oracle for Python classifier; no discriminant."""
from fractions import Fraction as F
from pathlib import Path
import itertools,json,random,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[4]))
from atlas.numerics.spectral_multiplicity import repeated_extremes
from check_factorizations import q,add,neg,mul,characteristic

def inv(a):
    den=a[0]*a[0]-2*a[1]*a[1]
    assert den
    return (a[0]/den,-a[1]/den)
def trim(p):
    while p and p[-1]==q():p.pop()
    return p
def remainder(p,d):
    p=p[:]
    while len(p)>=len(d):
        factor=mul(p[-1],inv(d[-1]));offset=len(p)-len(d)
        for j,v in enumerate(d):p[j+offset]=add(p[j+offset],neg(mul(factor,v)))
        trim(p)
    return p
def gcd_degree(p):
    d=[mul(q(i),v)for i,v in enumerate(p)][1:]
    while d:p,d=d,remainder(p,d)
    return len(p)-1

rng=random.Random(38071)
count=0
for _ in range(160):
    m=[rng.randint(-8,8)*2.**rng.randint(-8,8)for _ in range(6)]
    expected=gcd_degree(characteristic(m))>0
    observed=any(repeated_extremes(m))
    assert expected==observed,(m,expected,observed)
    count+=1
for permutations in itertools.permutations(range(3)):
    for shift in (-9.,0.,13.):
        for scale in (-8.,.25,4.):
            # diagonal plus triple-shear exact eigensystems; isotropic shift
            for diag,shear,kind in [([3.,3.,1.],0.,'max'),([3.,1.,1.],0.,'min'),
                                    ([0.,0.,0.],1.,'min')]:
                m=[shift+scale*diag[i]for i in permutations]+[scale*shear]*3
                maximum=(kind=='max')==(scale>0)
                assert repeated_extremes(m)==(maximum,not maximum),m
                assert gcd_degree(characteristic(m))==1,m
                count+=1
print(json.dumps({'status':'pass','production_cases':count,
                  'oracle':'exact polynomial Euclidean gcd plus known eigensystems'},indent=2))
