"""Bounded original Mašín 2005 algebra checks; not a constitutive integrator."""
import argparse
import hashlib
import json
import math
from pathlib import Path

MAIN_SHA = '8650dd58a4b5725dc0176ab9cf3a034ed211847b840524254876c2652bdf9ff3'
SOM_SHA = '549e337e39505ba2757da6f4ab95a00c702d08952fbd9e2c48c8022be2e4189a'


def coefficients(phi, lam, kap, r):
    values = (phi, lam, kap, r)
    if any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in values):
        raise ValueError('finite numeric parameters required')
    if not (0 < phi < math.pi / 2 and 0 < kap < lam and r > 0):
        raise ValueError('outside bounded diagnostic support')
    a = math.sqrt(3) * (3 - math.sin(phi)) / (2 * math.sqrt(2) * math.sin(phi))
    Q = 3 + a * a
    alpha = math.log(((lam - kap) / (lam + kap)) * Q / (a * math.sqrt(3))) / math.log(2)
    b = 2 ** alpha * a * math.sqrt(3)
    delta = Q - b
    c1 = 2 * delta / (9 * r)
    c2 = 1 + (1 - c1) * 3 / (a * a)
    return dict(a=a, Q=Q, alpha=alpha, b=b, delta=delta, c1=c1, c2=c2)


def ncl_void(p, N, lam, pr=1000.0):
    return math.expm1(N - lam * math.log(p / pr))


def equivalent_pressure(e, N, lam, pr=1000.0):
    return pr * math.exp((N - math.log1p(e)) / lam)


def isotropic_rate(p, e, volumetric_direction, N, lam, kap, r, phi):
    """Compression-positive p derivative, from Appendix C, not printed Eq38."""
    c = coefficients(phi, lam, kap, r)
    pe = equivalent_pressure(e, N, lam)
    fd = (2 * p / pe) ** c['alpha']
    Yi = math.sqrt(3) * c['a'] / c['Q']
    pdot = p * c['Q'] / (lam * c['delta']) * (volumetric_direction - fd * Yi * abs(volumetric_direction))
    return pdot, -(1 + e) * volumetric_direction


def cartesian(mandel):
    xx, yy, zz, xy, yz, xz = mandel
    s = math.sqrt(2)
    return [[xx, xy / s, xz / s], [xy / s, yy, yz / s], [xz / s, yz / s, zz]]


def contraction(A, B):
    return sum(A[i][j] * B[i][j] for i in range(3) for j in range(3))


def run_checks():
    rows = []

    def near(name, actual, expected, rel=5e-13, floor=2e-14):
        good = math.isfinite(actual) and math.isfinite(expected) and abs(actual - expected) <= floor + rel * max(abs(actual), abs(expected))
        rows.append(dict(name=name, passed=good, actual=actual, expected=expected, relative_bound=rel, absolute_floor=floor))

    phi = math.radians(22.6)
    lam, kap, N, r = .11, .016, 1.375, .4
    c = coefficients(phi, lam, kap, r)
    a, Q, alpha, delta = (c[x] for x in ('a', 'Q', 'alpha', 'delta'))
    near('Eq29 c1/c2 spherical closure', 3 * c['c1'] + c['c2'] * a * a, Q)
    near('Eq41 alpha closure', 2 ** alpha * a * math.sqrt(3) / Q, (lam - kap) / (lam + kap))
    near('positive delta identity', delta, 2 * Q * kap / (lam + kap))
    fs = 3 * 500000 / (lam * delta)
    Ki = fs / 3 * delta
    Gi = 1.5 * fs * c['c1']
    near('Eqs43/44 Ki/Gi=r', Ki / Gi, r)
    near('normal loading bulk modulus', Ki, 500000 / lam)
    # Printed Eq80 at hatT=I/3 and F=1: every diagonal is -a/Q.
    mdiag = -a * (1 / 3 - (1 / 9) / (1 / a ** 2 + 1 / 3))
    near('Eq80 exact spherical m', mdiag, -a / Q)
    near('Eq81 spherical F limit', math.sqrt(2 / 2), 1.0)
    Yi = math.sqrt(3) * a / Q
    near('spherical flow norm equals Yi', math.sqrt(3) * abs(mdiag), Yi)
    near('spherical unit m diagonal', mdiag / (math.sqrt(3) * abs(mdiag)), -1 / math.sqrt(3))
    s = math.sin(phi)
    ratio = (1 + s) / (1 - s)
    # Source T=diag(-ratio,-1,-1); I2 is minus usual principal invariant.
    I1, I2, I3 = -ratio - 2, -(2 * ratio + 1), -ratio
    near('triaxial MN invariant', -I1 * I2 / I3, (9 - s * s) / (1 - s * s))
    Y = (Yi - 1) * ((I1 * I2 + 9 * I3) * (1 - s * s)) / (8 * I3 * s * s) + Yi
    near('Eq78 MN Y=1', Y, 1)
    for p in (100000.0, 500000.0, 1000000.0):
        e = ncl_void(p, N, lam)
        pe = equivalent_pressure(e, N, lam)
        near(f'NCL equivalent pressure {p:g}', pe, p)
        near(f'NCL fd=2^alpha {p:g}', (2 * p / pe) ** alpha, 2 ** alpha)
        load, edot = isotropic_rate(p, e, .003, N, lam, kap, r, phi)
        unload, _ = isotropic_rate(p, e, -.003, N, lam, kap, r, phi)
        near(f'NCL loading tangent {p:g}', load, p * .003 / lam)
        near(f'NCL unloading tangent {p:g}', unload, -p * .003 / kap)
        near(f'continuity sign {p:g}', edot, -(1 + e) * .003)
        V = .02
        p1, e1 = p * math.exp(V / lam), (1 + e) * math.exp(-V) - 1
        near(f'finite NCL compression {p:g}', ncl_void(p1, N, lam), e1)
    # Preserve the printed Eq38 conflict as a measured discrepancy, not a repair.
    rows.append(dict(name='printed Eq38 minus bracket disagrees with Eq40 unloading', passed=abs(1 / lam - 1 / kap) > 1, printed_Eq38_slope=1 / lam, AppendixC_Eq40_slope=1 / kap))
    # Reference-pressure shift is a change of parameter convention, not material.
    pr2 = 1.0
    N2 = N - lam * math.log(pr2 / 1000.0)
    near('N reference-pressure conversion', ncl_void(500000, N2, lam, pr2), ncl_void(500000, N, lam))
    # Isotropic A eigenvalue with fs embedded, companion Eqs29-33.
    sphere_A = fs * Q - 3 * 500000 / lam
    norm_Ainv_N = fs * Yi * Q / sphere_A
    near('isotropic SOM fd from A inverse', 1 / norm_Ainv_N, 2 ** alpha)
    # All three off-diagonal positions explicitly tested against real tensors.
    U, V = [1., 2., 3., 4., 5., 6.], [-2., 4., 1., -3., 2., 7.]
    near('Mandel Cartesian contraction', contraction(cartesian(U), cartesian(V)), sum(a * b for a, b in zip(U, V)))
    for k, (i, j) in enumerate(((0, 1), (1, 2), (0, 2)), 3):
        u = [0.] * 6
        u[k] = math.sqrt(2)
        near(f'Mandel pure shear slot {k}', cartesian(u)[i][j], 1.)
    pdot, edot = isotropic_rate(500000, ncl_void(500000, N, lam), 0, N, lam, kap, r, phi)
    near('zero direction p rate', pdot, 0)
    near('zero direction e rate', edot, 0)
    # After finite unloading density follows continuity; a global kappa line is false.
    p0 = 500000.0
    e0 = ncl_void(p0, N, lam)
    volume = -.01
    pk = p0 * math.exp(volume / kap)
    ek = (1 + e0) * math.exp(-volume) - 1
    actual_rate, _ = isotropic_rate(pk, ek, -1, N, lam, kap, r, phi)
    rows.append(dict(name='global kappa line is not a solution', passed=abs(actual_rate + pk / kap) > .01 * pk / kap, relative_mismatch=abs(actual_rate + pk / kap) / (pk / kap)))
    negative_alpha = coefficients(phi, .11, .10, r)['alpha']
    rows.append(dict(name='lambda>kappa alone does not guarantee alpha>0', passed=negative_alpha < 0, alpha=negative_alpha))
    return dict(version='clay2005-bounded-algebra-0.1', main_source_sha256=MAIN_SHA, som_source_sha256=SOM_SHA, source_selection='Appendix C and Eqs40-41; conflicting printed Eq38 retained in dossier', scope='No full nonisotropic stress-rate or integrator verification', checks=rows, passed=all(x['passed'] for x in rows), count=len(rows))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--main-source', type=Path)
    parser.add_argument('--som-source', type=Path)
    args = parser.parse_args()
    for path, expected in ((args.main_source, MAIN_SHA), (args.som_source, SOM_SHA)):
        if path is not None and hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            raise ValueError('source bytes do not match selected manuscript')
    report = run_checks()
    args.output.write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    if not report['passed']:
        raise SystemExit('bounded check failed')
    print(f"{report['count']} bounded checks passed")


if __name__ == '__main__':
    main()
