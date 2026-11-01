"""Independent diagonal source-law RK4; no Atlas/DSL/production imports.

Kolymbas2015 Eqs9,20,23,26,27,31 in original tension-positive tensors.
Diagonal exponentials use scalar math.exp. The model's matrix exponential,
Mandel algebra and adaptive midpoint implementation are never called.
"""
import json
import math
from pathlib import Path
import numpy as np

PARAMETERS = [-1.0246, 1., -2.3, 465000., 28., .87, .35]
INITIAL = [100000., 100000., 100000., .75, 0., 0., 0.]


def rate(y, compression_rate):
    c1, c2, c3, c4, c5, ec0, emin = PARAMETERS
    T = [-v for v in y[:3]]
    D = [-v for v in compression_rate]
    d = math.hypot(*D)
    if d == 0:
        return [0.] * 7
    normT = math.hypot(*T)
    delta = math.fsum(D) / d
    R = [-math.exp(c1 * math.exp(c2 * delta) * v / d) for v in D]
    normR = math.hypot(*R)
    h = -(c4 + c5 * normT) / (y[3] - emin)
    B = (ec0 - emin) / (ec0 + 1) * ((c4 + c5 * normT) / c4) ** (-(1 + emin) / c5)
    ec = (emin + B) / (1 - B)
    f, g = delta + c3 * ec, -c3 * y[3]
    return [-h * (f * R[i] / normR + g * T[i] / normT) * d for i in range(3)] + [(1 + y[3]) * math.fsum(D)] + list(compression_rate)


def advance(y, increment, n):
    y = list(y)
    v = [x / n for x in increment]
    for _ in range(n):
        k1 = rate(y, v)
        k2 = rate([a + b / 2 for a, b in zip(y, k1)], v)
        k3 = rate([a + b / 2 for a, b in zip(y, k2)], v)
        k4 = rate([a + b for a, b in zip(y, k3)], v)
        y = [a + (b + 2*c + 2*d + e)/6 for a, b, c, d, e in zip(y, k1, k2, k3, k4)]
    return y


def controlled(y, protocol, delta, n):
    if protocol in (0, 2, 4):
        return advance(y, [delta, -.5*delta if protocol == 2 else delta if protocol == 4 else 0., -.5*delta if protocol == 2 else delta if protocol == 4 else 0.], n)
    # Independent secant endpoint closure. Every trial starts from identical y.
    def trial(x):
        z = advance(y, [delta, x, x] if protocol == 1 else [x, -.5*x, -.5*x], n)
        residual = (z[1] + z[2])/2 - 100000 if protocol == 1 else z[0]-(z[1]+z[2])/2-(y[0]-(y[1]+y[2])/2)-delta
        return residual, z
    a, b = (0., -.2*delta) if protocol == 1 else (0., delta/1e7)
    fa, _ = trial(a)
    for _ in range(30):
        fb, z = trial(b)
        if abs(fb) < 1e-8:
            return z
        if fb == fa:
            raise ArithmeticError('independent mixed-control secant singularity')
        a, b, fa = b, b-fb*(b-a)/(fb-fa), fb
    raise ArithmeticError('independent mixed-control closure did not converge')


def cases():
    for protocol in range(5):
        for cyclic in (False, True):
            count = 128 if cyclic else 100
            target = 1000. if protocol == 3 else .01 if protocol == 1 and not cyclic else .002
            controls = [target*math.sin(2*math.pi*i/count) if cyclic else target*i/count for i in range(count+1)]
            yield dict(id=f'protocol-{protocol}-'+('cyclic' if cyclic else 'monotonic'), protocol=protocol, target=target, steps=count, cycles=int(cyclic), controls=controls)


def solve(case, subdivisions):
    y = list(INITIAL)
    points = [y]
    for left, right in zip(case['controls'], case['controls'][1:]):
        y = controlled(y, case['protocol'], right-left, subdivisions)
        points.append(y)
    return points


OBLIQUE_INITIAL = [120000., 90000., 70000., 15000.*math.sqrt(2), 6000.*math.sqrt(2), -8000.*math.sqrt(2), .75]
OBLIQUE_INCREMENTS = [[.001,-.0003,.0002,.0007,-.0002,.0005], [-.0003,.0005,0.,-.0002,.0004,-.0001], [0.]*6, [-.001,.0003,-.0002,-.0007,.0002,-.0005]]


def tensor_rate(y, d):
    """Independent Cartesian spectral theorem, unlike production polynomial expm."""
    r = math.sqrt(2.)
    def unpack(v):
        a,b,c,u,v,w = v
        return np.array([[a,u/r,w/r],[u/r,b,v/r],[w/r,v/r,c]])
    T, D = -unpack(y[:6]), -unpack(d)
    magnitude = float(np.linalg.norm(D))
    if magnitude == 0:
        return [0.]*7
    c1,c2,c3,c4,c5,ec0,emin = PARAMETERS
    normT = float(np.linalg.norm(T))
    delta = float(np.trace(D))/magnitude
    values, vectors = np.linalg.eigh(c1*math.exp(c2*delta)*D/magnitude)
    R = -(vectors*np.exp(values))@vectors.T
    h = -(c4+c5*normT)/(y[6]-emin)
    B = (ec0-emin)/(ec0+1)*((c4+c5*normT)/c4)**(-(1+emin)/c5)
    ec = (emin+B)/(1-B)
    out = -h*((delta+c3*ec)*R/np.linalg.norm(R)-c3*y[6]*T/normT)*magnitude
    return [float(out[0,0]),float(out[1,1]),float(out[2,2]),r*float(out[0,1]),r*float(out[1,2]),r*float(out[0,2]),(1+y[6])*float(np.trace(D))]


def tensor_advance(y, increment, n):
    y = np.array(y)
    v = np.array(increment)/n
    for _ in range(n):
        a = np.array(tensor_rate(y,v))
        b = np.array(tensor_rate(y+a/2,v))
        c = np.array(tensor_rate(y+b/2,v))
        d = np.array(tensor_rate(y+c,v))
        y = y+(a+2*b+2*c+d)/6
    return list(y)


def main():
    output = {}
    for case in cases():
        low, high = solve(case, 8), solve(case, 16)
        error = [max(abs(a[j]-b[j]) for a,b in zip(low,high)) for j in range(7)]
        assert max(error[:3]) <= .01 and max(error[3:]) <= 1e-10, error
        output[case['id']] = dict(case=case, points=high, refinement_maximum=error)
        print(case['id'], max(error[:3]), flush=True)
    Path(__file__).with_name('references.json').write_text(json.dumps(output, indent=2)+'\n')
    grids = []
    for n in (16,32):
        y = list(OBLIQUE_INITIAL)
        points = [y]
        for increment in OBLIQUE_INCREMENTS:
            y = tensor_advance(y,increment,n)
            points.append(y)
        grids.append(points)
    error = [max(abs(a[j]-b[j]) for a,b in zip(*grids)) for j in range(7)]
    assert max(error[:6]) <= .01 and error[6] <= 1e-10, error
    Path(__file__).with_name('oblique-reference.json').write_text(json.dumps(dict(initial=OBLIQUE_INITIAL,increments=OBLIQUE_INCREMENTS,points=grids[1],refinement_maximum=error,numpy_version=np.__version__),indent=2)+'\n')


if __name__ == '__main__':
    main()
