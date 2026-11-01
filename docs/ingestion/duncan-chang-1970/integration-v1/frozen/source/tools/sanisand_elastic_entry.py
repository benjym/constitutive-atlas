"""Research reference for original SANISAND elasticity and first yield.

Exact straight-strain-path elasticity, using source Eq. (3) and the explicitly
project-inferred constant-solid-volume closure. Not a plastic material update.
"""
import math

from atlas.dsl import I, Sym, ValidationError, dev, dot, trace


def _check_tensor(value):
    if not isinstance(value, Sym) or len(value.v) != 6 or any(not math.isfinite(x) for x in value.v):
        raise ValidationError('finite six-component Mandel tensor required')


def elastic_point(sigma, e, strain, fraction=1., *, G0=125., nu=.05, p_at=1e5):
    """Return exact elastic stress/void ratio at fraction of one straight path.

    Audit domain: 0<e<2.97 throughout; compression positive; zero spin.
    No clipping, pressure floor, history assignment or input mutation.
    """
    _check_tensor(sigma)
    _check_tensor(strain)
    if any(not math.isfinite(x) for x in (e, fraction, G0, nu, p_at)):
        raise ValidationError('finite elastic inputs required')
    p0 = trace(sigma)/3
    if not (p0 > 0 and 0 < e < 2.97 and 0 <= fraction <= 1 and
            G0 > 0 and p_at > 0 and -1 < nu < .5):
        raise ValidationError('outside elastic reference audit domain')
    x = fraction*trace(strain)
    try:
        ef = e+(1+e)*math.expm1(-x)
        if not 0 < ef < 2.97:
            raise ValueError('void ratio leaves audit domain')
        # J/x: average of f(e)=(2.97-e)^2/(1+e) over volumetric strain.
        def exprel(v):
            return math.expm1(v)/v if v else 1.
        # A rearranged average also avoids cancellation as e approaches 2.97.
        # q=exprel(x)-1; even=exprel(x)+exprel(-x)-2.
        if abs(x) < .1:
            q = sum(x**k/math.factorial(k+1) for k in range(1, 20))
            even = sum(2*x**k/math.factorial(k+1) for k in range(2, 20, 2))
        else:
            q = exprel(x)-1
            even = exprel(x)+exprel(-x)-2
        gap = 2.97-e
        average = gap*gap/(1+e)*(1+q)+2*gap*q+(1+e)*even
        a = 2*(1+nu)/(3*(1-2*nu))
        u0 = math.sqrt(p0/p_at)
        du = a*G0/2*x*average
        u = u0+du
        if u <= 0 or average <= 0:
            raise ValueError('elastic pressure reaches a singular boundary')
        dp = p_at*du*(2*u0+du)
        # Avoid subtracting pressures or dividing by a vanishing volume change.
        average_G = p_at*G0/2*(2*u0+du)*average
        stress = sigma+I*dp+dev(strain)*(2*fraction*average_G)
        if not math.isfinite(ef) or any(not math.isfinite(v) for v in stress.v):
            raise ValueError('nonfinite elastic result')
        return stress, ef
    except (ValueError, OverflowError, ZeroDivisionError) as exc:
        raise ValidationError('elastic path leaves reference domain') from exc


def first_yield(sigma, e, alpha, strain, *, m=.01, fraction_tolerance=1e-12,
                yield_tolerance=1e-12, max_iterations=80, **elastic):
    """Bracket the first outward elastic intersection; return None if absent.

    Returns lower/upper path fractions, endpoint stresses and signed dimensionless
    yield residuals. The lower endpoint is elastic, upper is on/outside the cone.
    Tolerances are numerical choices, not values prescribed by the source paper.
    No alpha_in reset or plastic continuation is inferred.
    """
    _check_tensor(alpha)
    if (not math.isfinite(m) or m <= 0 or
        not math.isfinite(fraction_tolerance) or not 0 < fraction_tolerance < 1 or
        not math.isfinite(yield_tolerance) or yield_tolerance < 0 or
        type(max_iterations) is not int or max_iterations < 1 or
        abs(trace(alpha)) > 1e-12*max(1., max(abs(v) for v in alpha.v))):
        raise ValidationError('invalid first-yield reference controls or backstress')
    radius = math.sqrt(2/3)*m
    def point(t):
        stress, void = elastic_point(sigma, e, strain, t, **elastic)
        y = dev(stress)/(trace(stress)/3)-alpha
        residual = math.sqrt(dot(y, y))-radius
        return dict(fraction=t, sigma=stress, e=void, residual=residual, y=y)
    start, end = point(0.), point(1.)
    if start['residual'] > yield_tolerance*radius:
        raise ValidationError('first-yield search requires elastic/cone initial state')
    # r follows a straight segment in tensor space as 1/p changes monotonically;
    # at zero volume strain it is affine in path fraction. The elastic cone is
    # convex, so interior endpoints cannot hide an intervening plastic excursion.
    if end['residual'] < 0:
        return None
    chord = end['y']-start['y']
    if (start['residual'] >= 0 and dot(start['y'], chord) >= 0):
        if dot(chord, chord) == 0:
            return None
        return dict(lower=start, upper=start, iterations=0, kind='initial-outward')
    if dot(chord, chord) == 0:
        return None
    if start['residual'] > 0:
        # A tolerance-admitted exterior start cannot furnish a signed bracket.
        raise ValidationError('slightly exterior start needs explicit projection policy')
    lower, upper = start, end
    for iteration in range(1, max_iterations+1):
        if upper['fraction']-lower['fraction'] <= fraction_tolerance:
            return dict(lower=lower, upper=upper, iterations=iteration-1, kind='bracketed')
        middle = point((lower['fraction']+upper['fraction'])/2)
        if middle['residual'] >= 0:
            upper = middle
        else:
            lower = middle
    raise ValidationError('first-yield bracket did not reach requested tolerance')
