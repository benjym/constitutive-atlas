"""Independent axial OCC rank/cone checks; not a material update or oracle."""
import json
import math
from fractions import Fraction
from pathlib import Path


def rank(rows):
    a = [[Fraction(x) for x in row] for row in rows]
    r = 0
    for col in range(len(a[0])):
        pivot = next((i for i in range(r, len(a)) if a[i][col]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        d = a[r][col]
        a[r] = [x / d for x in a[r]]
        for i in range(len(a)):
            if i != r:
                d = a[i][col]
                a[i] = [x - d*y for x, y in zip(a[i], a[r])]
        r += 1
        if r == len(a):
            break
    return r


def checks():
    M, p, pc = 1.2, 60000., 100000.
    h = M*p*math.log(p/pc)
    # At fixed pressure/packing, distinct interior q values have identical zero
    # distortion. A strain increment therefore does not identify q uniquely.
    interior = [0., 1000., -1000., 20000.]
    assert all(abs(q)+h < 0 for q in interior)
    # abs(q)+h <= 0 is exactly the intersection of these two smooth faces.
    for q in [-50000., -1000., 0., 1000., 50000.]:
        assert math.isclose(max(q+h, -q+h), abs(q)+h, abs_tol=1e-10)
    # At the corner, f_p=M and the two face normals are (M,+/-1).
    # Positive combinations include pure volume and both limiting directions.
    cones = []
    for ap, am in [(1., 0.), (0., 1.), (.5, .5), (.8, .2)]:
        evp, es = M*(ap+am), ap-am
        assert evp >= M*abs(es)-1e-15
        cones.append({'a_plus': ap, 'a_minus': am,
                      'plastic_volume': evp, 'distortion': es,
                      'corner_power_minus_smooth_dissipation_over_p':
                          evp-M*abs(es)})
    # Dimensionless/scaled local predictor equations, unknowns dp,dq,dc,a+,a-.
    # Constants are normalized to one; every nonzero scaling preserves rank.
    # bulk + plastic volume; zero recoverable shear; hardening; a+=0; a-=0.
    a = [[1, 0, 0, 1, 1], [0, 0, 0, 1, -1],
         [0, 0, 1, -1, -1], [0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]
    r = rank(a)
    nonzero_distortion_rhs = [0, 1, 0, 0, 0]
    augmented = rank([row+[rhs] for row, rhs in zip(a, nonzero_distortion_rhs)])
    assert (r, augmented) == (4, 5)
    # Existing sqrt algebra expresses complementarity for positive slack y=-f.
    for multiplier, slack in [(0., 2.), (3., 0.), (0., 0.)]:
        assert math.sqrt(multiplier**2+slack**2)-multiplier-slack == 0
    return {'passed': True, 'scope': 'algebra only; no production model',
            'interior_q_Pa': interior, 'interior_yield_values_Pa': [abs(q)+h for q in interior],
            'corner_cone_samples': cones,
            'predictor_unknown_count': 5, 'predictor_rank': r,
            'predictor_nonzero_distortion_augmented_rank': augmented,
            'interpretation': 'zero-multiplier predictor is inconsistent for nonzero distortion; zero distortion leaves q undetermined',
            'compiled_calls': 0}


if __name__ == '__main__':
    Path(__file__).with_name('constraint-results.json').write_text(
        json.dumps(checks(), indent=2, allow_nan=False)+'\n')
