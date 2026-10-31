"""Bounded independent equation witnesses, not a constitutive implementation."""
import argparse
from fractions import Fraction as F
import hashlib
import json
from math import isqrt
from pathlib import Path

SOURCE_SHA = '43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9'


def sqrt_exact(x):
    assert x >= 0
    n, d = isqrt(x.numerator), isqrt(x.denominator)
    assert n*n == x.numerator and d*d == x.denominator
    return F(n, d)


def cap(q, de, m, K=F(2), pref=F(100)):
    # Exact witnesses only at m=0 and 1/2; no proposed general update algorithm.
    if m == 0:
        out = q - K*pref*de
        assert out > 0
        return out
    assert m == F(1, 2)
    root = sqrt_exact(q) - K*sqrt_exact(pref)*de/2
    assert root > 0
    return root*root


def cone(g, t0=F(1, 10), u=F(4, 5), h=F(1, 50)):
    return t0 + (u-t0)*g/(h+g)


def cone_increment(t, dg, t0=F(1, 10), u=F(4, 5), h=F(1, 50)):
    return t + dg*(u-t)/(h*(u-t0)/(u-t)+dg)


def cubic(a, b, y, k):
    d = (a-b)**3
    return ((k*(a-b)-2*y)/d,
            (k*(-2*a*a+a*b+b*b)+3*(a+b)*y)/d,
            (k*(a**3+a*a*b-2*a*b*b)-6*a*b*y)/d,
            (k*(a*a*b*b-a**3*b)+y*(3*a*b*b-b**3))/d)


def corner(L, f):
    a, b, c, d = L
    det = a*d-b*c
    if det == 0:
        raise ValueError('singular source formula; no fallback inferred')
    return ((d*f[0]-b*f[1])/det, (a*f[1]-c*f[0])/det)


def run():
    checks = []
    # Eq23 -> Eq17 normal diagonal/off-diagonal and engineering shear.
    for E, nu in [(F(1000), F(1, 5)), (F(3000), F(1, 3)), (F(7), F(0))]:
        cn, ct = (1-2*nu)/E, (1+3*nu)/E
        assert (3*cn+2*ct)/5 == 1/E
        assert (cn-ct)/5 == -nu/E
        assert (4*cn+6*ct)/5 == 2*(1+nu)/E
    checks.append(dict(id='NT-elastic-reconstruction', status='pass', parameter_witnesses=3))
    cap_witnesses = []
    for m in [F(0), F(1, 2)]:
        first = cap(F(100), -F(1, 100), m)
        split = cap(first, -F(1, 50), m)
        whole = cap(F(100), -F(3, 100), m)
        assert split == whole and whole > 100
        assert cap(F(100), F(0), m) == 100
        cap_witnesses.append(dict(m=str(m), q_after=str(whole)))
    checks.append(dict(id='cap-transformed-composition-and-zero', status='pass', witnesses=cap_witnesses))
    for g in [F(0), F(1, 100), F(1, 30)]:
        for dg in [F(0), F(1, 200), F(1, 60)]:
            assert cone_increment(cone(g), dg) == cone(g+dg)
    checks.append(dict(id='cone-incremental-total-equivalence', status='pass', witnesses=9))
    g1, g2 = F(1, 100), F(1, 70)
    assert cone_increment(cone_increment(cone(0), g1), g2) == cone(g1+g2)
    checks.append(dict(id='cone-composition', status='pass'))
    t0, u, h, tmax = F(1, 10), F(4, 5), F(1, 50), F(3, 5)
    crossing = h*(tmax-t0)/(u-tmax)
    assert cone(crossing) == tmax and cone(2*crossing) > tmax
    checks.append(dict(id='cone-unclipped-maximum-crossing', status='pass', gamma_at_max=str(crossing),
                       gamma_twice_value=str(cone(2*crossing)), meaning='demonstrates missing operational saturation rule'))
    for a, b, y, k in [(F(10), F(25), F(-3), F(1)),
                        (F(10), F(25), F(-3), F(0)),
                        (F(3), F(7), F(-2), F(2, 5))]:
        A, B, C, D = cubic(a, b, y, k)
        p = lambda x: A*x**3+B*x*x+C*x+D
        dp = lambda x: 3*A*x*x+2*B*x+C
        assert p(a) == y and dp(a) == 0
        assert p(b) == 0 and dp(b) == k
        low = lambda x: y*(3*(x/a)**2-2*(x/a)**3)
        dlow = lambda x: y*(6*x/a**2-6*x*x/a**3)
        assert low(0) == 0 and dlow(0) == 0
        assert low(a) == p(a) and dlow(a) == dp(a)
    checks.append(dict(id='dilatancy-literal-cubic-endpoints-and-slopes', status='pass', witnesses=3))
    L = tuple(map(F, [4, 1, 2, 5]))
    for f in [(F(3), F(4)), (F(1), F(10))]:
        x, y = corner(L, f)
        assert L[0]*x+L[1]*y == f[0] and L[2]*x+L[3]*y == f[1]
    assert all(x > 0 for x in corner(L, (F(3), F(4))))
    assert corner(L, (F(1), F(10)))[0] < 0
    try:
        corner(tuple(map(F, [1, 2, 2, 4])), (F(1), F(1)))
    except ValueError:
        pass
    else:
        raise AssertionError('singular witness was not rejected')
    checks.append(dict(id='two-surface-linear-system', status='pass',
                       scope='positive and negative multiplier algebra; exact singular denominator rejected, no tolerance selected'))
    E, nu = F(1000), F(1, 5)
    K26 = E/(2*(1-2*nu))
    Cv31 = (1-2*nu)/E
    assert 1/K26 != Cv31 and (1/K26)/Cv31 == 2
    retained = dict(id='VD-Eq26-Eq31-equality', status='source_equality_fails',
                    E=str(E), nu=str(nu), inverse_K26=str(1/K26), Cv31=str(Cv31),
                    ratio=str((1/K26)/Cv31), correction_adopted=False)
    return dict(id='multilaminate-base-laws-v1', source_sha256=SOURCE_SHA,
                arithmetic='exact rational; no Atlas, author code or compiled backend',
                bounded_algebra_checks=checks, retained_source_questions=[retained],
                constitutive_validation=False, scientific_admission=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf', type=Path)
    args = parser.parse_args()
    if args.pdf:
        assert hashlib.sha256(args.pdf.read_bytes()).hexdigest() == SOURCE_SHA
    print(json.dumps(run(), indent=2, sort_keys=True)+'\n', end='')
