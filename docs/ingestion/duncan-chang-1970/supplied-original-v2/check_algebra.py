"""Exact source-coordinate algebra; no Atlas runtime or fitted observations."""
from fractions import Fraction as F
import json


def main():
    checks = 0

    def same(a, b):
        nonlocal checks
        assert a == b, (a, b)
        checks += 1

    # a,b are the original straight-line intercept and slope (Eq2).
    # Quotient differentiation produces a/(a+b*x)^2; independent
    # stress-based parameterization (Eq10) must recover that value.
    for a in (F(1, 7), F(1, 2000), F(1, 4480)):
        for b in (F(1, 16), F(3, 50), F(1, 99)):
            for x in (F(0), F(1, 10000), F(1, 100), F(1, 5)):
                d = x / (a + b*x)
                ei, du = 1/a, 1/b
                rf = F(91, 100)
                df = rf*du
                quotient_derivative = a/(a + b*x)**2
                same(quotient_derivative, ei*(1-rf*d/df)**2)
                same(d / (ei*(1-rf*d/df)), x)
                same(x/(1/ei + rf*x/df), d)
                same(1/(a+b*x), ei*(1-rf*d/df))  # secant vs tangent
                if x:
                    same(x/d, a+b*x)
                else:
                    same(quotient_derivative, ei)
    # Source Eq15a-f, independently invert isotropic stress =
    # 2G*strain + lambda*trace(strain)I, including Mandel shear slots.
    for e in (F(7), F(2000), F(30000)):
        for nu in (F(0), F(3, 10), F(12, 25)):
            g = e/(2*(1+nu))
            lam = e*nu/((1+nu)*(1-2*nu))
            for ds in ((F(1),)*3+(F(0),)*3,
                       (F(3), F(-2), F(7), F(4), F(-5), F(6)),
                       (F(0),)*3+(F(1), F(0), F(0))):
                de = [((1+nu)*ds[i]-nu*sum(ds[:3]))/e for i in range(3)]
                de += [(1+nu)*v/e for v in ds[3:]]
                tr = sum(de[:3])
                recovered = [2*g*de[i] + lam*tr for i in range(3)]
                recovered += [2*g*v for v in de[3:]]
                for value, wanted in zip(recovered, ds):
                    same(value, wanted)
            # Rational equality after cancelling sqrt2: engineering shear
            # /sqrt2 = Mandel strain; sqrt2*tau = Mandel stress.
            same(2*(1+nu)/e/2, (1+nu)/e)
            same(3*(1-2*nu)/e, 1/(e/(3*(1-2*nu))))
    # Branch-memory distinction. c=0, sin(phi)=1/2 -> Df=2*sigma3.
    # A: D=4,sigma3=4,S=1/2. B: D=3,sigma3=2,S=3/4.
    # B is below the historical D maximum although S increased.
    h = F(4)
    d_a, s3_a, d_b, s3_b = F(4), F(4), F(3), F(2)
    assert d_b < h and d_b/(2*s3_b) > d_a/(2*s3_a)
    checks += 1
    same(max(h, d_b), h)
    same(max(F(0), F(0)), F(0))
    print(json.dumps({'result': 'pass', 'exact_assertions': checks,
                      'groups': ['hyperbola/quotient derivative/inverse/transformed line',
                                 'six-component Hooke inverse',
                                 'engineering-to-Mandel shear factor',
                                 'hydrostatic compliance',
                                 'historical D versus normalized S',
                                 'hydrostatic zero-memory illustration'],
                      'constitutive_algorithm_qualified': False,
                      'compiled_calls': 0}, indent=2))


if __name__ == '__main__':
    main()
