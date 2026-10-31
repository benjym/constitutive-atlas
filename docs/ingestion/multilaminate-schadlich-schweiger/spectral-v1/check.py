"""Independent matrix/coordinate witnesses; not an author-code or material runtime."""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path

TOL = 1e-12  # Fixed before observations; all floating witnesses use O(1) compliance.
SOURCE_SHA = '43d9a82e21523d303a684776580f57943277bc5fa9cb4d77648494e9daa876a9'

def eye(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]

def tr(a):
    return list(map(list, zip(*a)))

def mm(a, b):
    return [[sum(x*y for x, y in zip(row, col)) for col in zip(*b)] for row in a]

def mv(a, v):
    return [sum(x*y for x, y in zip(row, v)) for row in a]

def err(a, b):
    return max(abs(x-y) for ar, br in zip(a, b) for x, y in zip(ar, br))

def inverse(a):
    n = len(a)
    b = [list(row)+unit for row, unit in zip(a, eye(n))]
    for k in range(n):
        j = max(range(k, n), key=lambda i: abs(b[i][k]))
        if b[j][k] == 0:
            raise ValueError('singular; no pseudoinverse substituted')
        b[k], b[j] = b[j], b[k]
        pivot = b[k][k]
        b[k] = [x/pivot for x in b[k]]
        for i in range(n):
            if i != k:
                scale = b[i][k]
                b[i] = [x-scale*y for x, y in zip(b[i], b[k])]
    return [row[n:] for row in b]

def compliance(Eh, Ev, G, nhv, nhh):
    return [[1/Eh, -nhv/Eh, -nhh/Eh, 0, 0, 0],
            [-nhv/Eh, 1/Ev, -nhv/Eh, 0, 0, 0],
            [-nhh/Eh, -nhv/Eh, 1/Eh, 0, 0, 0],
            [0, 0, 0, 1/(2*G), 0, 0],
            [0, 0, 0, 0, 1/(2*G), 0],
            [0, 0, 0, 0, 0, (1+nhh)/Eh]]

def spectrum(Eh, Ev, G, nhv, nhh, theta=None):
    # Eigenvalues from the independently reduced symmetric 2x2 normal block.
    a, d, b = (1-nhh)/Eh, 1/Ev, -math.sqrt(2)*nhv/Eh
    delta = math.hypot(a-d, 2*b)
    lam = [(1+nhh)/Eh, (a+d-delta)/2, (a+d+delta)/2, 1/(2*G)]
    if theta is None:
        theta = math.atan2(-2*b, d-a)/2 if delta else 0.0
    c, s, root = math.cos(theta), math.sin(theta), math.sqrt(2)
    v2, v3 = [c/root, s, c/root, 0, 0, 0], [-s/root, c, -s/root, 0, 0, 0]
    e1 = [[0.0]*6 for _ in range(6)]
    e1[0][0] = e1[2][2] = 0.5
    e1[0][2] = e1[2][0] = -0.5
    e1[5][5] = 1
    e4 = [[0.0]*6 for _ in range(6)]
    e4[3][3] = e4[4][4] = 1
    projectors = [e1, [[x*y for y in v2] for x in v2],
                  [[x*y for y in v3] for x in v3], e4]
    reconstruction = [[sum(l*e[i][j] for l, e in zip(lam, projectors))
                       for j in range(6)] for i in range(6)]
    return lam, projectors, reconstruction

def printed_D_angle(Eh, Ev, nhv, nhh):
    diff = (1-nhh)/Eh-1/Ev
    if diff == 0:
        return math.pi/4 if nhv > 0 else -math.pi/4
    return (math.pi/2 if diff > 0 else 0)+math.atan((-2*math.sqrt(2)*nhv/Eh)/diff)/2

def projection(n, s, t, literal=False):
    """Raw stress projection independently derived from n.S.n and s/t.S.n."""
    x, y, z = n
    p = [[F(1, 3)]*3+[0]*3,
         [x*x-F(1, 3), y*y-F(1, 3), z*z-F(1, 3), 2*x*y, 2*y*z, (1 if literal else 2)*x*z],
         [n[j]*s[j] for j in range(3)]+[0]*3,
         [0]*3+[x*s[1]+y*s[0], y*s[2]+z*s[1], z*s[0]+x*s[2]],
         [n[j]*t[j] for j in range(3)]+[0]*3,
         [0]*3+[x*t[1]+y*t[0], y*t[2]+z*t[1], z*t[0]+x*t[2]]]
    return p

def deg(x, lo, hi):
    if not 0 < lo < hi:
        raise ValueError('requires 0 < onset < end')
    if x < 0:
        raise ValueError('distance cannot be negative')
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    return math.log(x/lo)/math.log(hi/lo)

def run():
    checks = []
    witnesses = [(10., 5., 3., .2, .1), (5., 10., 2., .1, .2),
                 (10., 10., 10/2.4, .2, .2), (10., 10., 3., 0., 0.)]
    max_reconstruction = 0
    for params in witnesses:
        C = compliance(*params)
        lam, es, recon = spectrum(*params)
        assert min(lam) > 0
        assert err(recon, C) < TOL
        max_reconstruction = max(max_reconstruction, err(recon, C))
        assert err([[sum(e[i][j] for e in es) for j in range(6)] for i in range(6)], eye(6)) < TOL
        for i, e in enumerate(es):
            assert err(mm(e, e), e) < TOL
            for j, f in enumerate(es):
                if i != j:
                    assert err(mm(e, f), [[0]*6 for _ in range(6)]) < TOL
        theta = printed_D_angle(params[0], params[1], params[3], params[4])
        assert err(spectrum(*params, theta=theta)[2], C) < TOL
    checks.append(dict(id='A1-A3-projectors-and-D-angle-reconstruction', status='pass',
                       witnesses=4, max_absolute_error=max_reconstruction,
                       limitation='D angle differs from printed A2; no author program executed'))
    failures = []
    for params in witnesses[:3]:
        Eh, Ev, G, nhv, nhh = params
        theta = math.atan((-2*math.sqrt(2)*nhv/Ev)/((1-nhh)/Eh+1/Ev))/2
        # Check both eigenpair branch assignments; adding pi only changes vector sign.
        errors = [err(spectrum(*params, theta=theta+k*math.pi/2)[2], compliance(*params)) for k in [0, 1]]
        assert min(errors) > 1e-4
        failures.append(dict(parameters=list(params), best_branch_absolute_error=min(errors)))
    checks.append(dict(id='literal-A2-reconstruction', status='retained_source_failure', witnesses=failures))
    # Exact physical projection and distinct engineering/Kelvin compliance relation.
    n, s, t = [F(-2,3), F(2,3), F(1,3)], [F(2,15), F(-1,3), F(14,15)], [F(11,15), F(2,3), F(2,15)]
    assert mm([n,s,t], tr([n,s,t])) == eye(3)
    raw = projection(n,s,t)
    assert err(mm(raw,inverse(raw)), eye(6)) == 0
    stress = [F(0)]*5+[F(1)]
    literal, physical = mv(projection(n,s,t,literal=True), stress), mv(raw, stress)
    assert literal[1] == F(-2,9) and physical[1] == F(-4,9)
    checks.append(dict(id='Eq104-xz-normal-versus-tensor-traction', status='retained_source_failure',
                       printed=str(literal[1]), physical_and_D=str(physical[1])))
    singulars = [(list(map(F,[1,0,0])), list(map(F,[0,1,0])), list(map(F,[0,0,1]))),
                 ([F(3,5), F(4,5), F(0)], [F(-4,5), F(3,5), F(0)], list(map(F,[0,0,1])))]
    for basis in singulars:
        try:
            inverse(projection(*basis))
        except ValueError:
            pass
        else:
            raise AssertionError('expected a singular source projection')
    checks.append(dict(id='axis-and-coordinate-plane-singularity', status='pass', witnesses=2,
                       limitation='Axis avoidance alone does not establish invertibility; quadrature rotation still unspecified'))
    # Candidate Kelvin projection used only as an explicit coordinate witness.
    P = [[float(x)/(math.sqrt(2) if j >= 3 else 1) for j,x in enumerate(row)] for row in raw]
    for params in witnesses:
        C = compliance(*params); local = mm(mm(P,C),inverse(P))
        assert err(mm(local,P),mm(P,C)) < TOL
    E, nu = 10., .2
    C = compliance(E,E,E/(2*(1+nu)),nu,nu)
    local = mm(mm(P,C),inverse(P))
    expected = [[((1-2*nu)/E if i == 0 else (1+nu)/E) if i == j else 0 for j in range(6)] for i in range(6)]
    assert err(local,expected) < TOL
    engineering = [[C[i][j]*(math.sqrt(2) if i >= 3 else 1)*(math.sqrt(2) if j >= 3 else 1) for j in range(6)] for i in range(6)]
    assert abs(engineering[3][3]-1/(E/(2*(1+nu)))) < TOL
    checks.append(dict(id='explicit-Kelvin-similarity-and-isotropic-limit', status='pass', witnesses=4,
                       limitation='Candidate coordinate conversion only; printed raw/Kelvin assembly not declared reconciled'))
    for x, expected in [(0,0), (1e-5,0), (1e-4,.5), (1e-3,1), (1,1)]:
        assert abs(deg(x,1e-5,1e-3)-expected) < TOL
    for lo, hi in [(0,1), (1,1), (2,1)]:
        try: deg(1,lo,hi)
        except ValueError: pass
        else: raise AssertionError('invalid thresholds accepted')
    # Figure29 labels nu_vh, whereas D190 interpolates nu_hv. Reciprocity makes them distinct.
    Eh0, Ev0, nhv0, Eu, nur = F(20), F(10), F(1,10), F(5), F(1,5)
    Eh, Ev, nhv = (Eh0+Eu)/2, (Ev0+Eu)/2, (nhv0+nur)/2
    nvh_from_D = nhv*Ev/Eh
    nvh_from_figure_interpolation = (nhv0*Ev0/Eh0+nur)/2
    assert nvh_from_D == F(9,100) and nvh_from_figure_interpolation == F(1,8)
    checks.append(dict(id='log-degradation-endpoints-and-Poisson-label', status='pass_with_retained_source_ambiguity',
                       D_midpoint_nu_vh=str(nvh_from_D), figure_linear_nu_vh=str(nvh_from_figure_interpolation),
                       limitation='No choice of interpolated Poisson ratio silently adopted'))
    p0, p, pref, m = 100., 225., 100., .5
    isotropic_factors = [(p/pref)**m, (p/pref)**m,
                         (p0/p0)**m*(p/pref)**m, (math.sqrt(p0*p0)/p0)**m*(p/pref)**m]
    assert all(x == 1.5 for x in isotropic_factors)
    u, centre, shift = [F(1),F(2),F(3)], [F(1),F(-1),F(-1)], [F(7),F(11),F(13)]
    norm2 = lambda a,b: sum((x-y)**2 for x,y in zip(a,b))
    assert norm2(u,centre) == 25
    assert norm2([x+y for x,y in zip(u,shift)],[x+y for x,y in zip(centre,shift)]) == 25
    checks.append(dict(id='pressure-branch-isotropic-collapse-and-Eq111-distance', status='pass',
                       limitation='No stress-floor, full contour event algorithm or model integration checked'))
    return {'scope':'Seven independent witness groups; retained failures are findings, not waived gates.',
            'floating_absolute_tolerance':TOL, 'source_sha256':SOURCE_SHA, 'checks':checks,
            'executable_model':False, 'scientific_admission':False}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source',type=Path)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    if args.source:
        assert hashlib.sha256(args.source.read_bytes()).hexdigest() == SOURCE_SHA
    report = json.dumps(run(),indent=2)+'\n'
    if args.output: args.output.write_text(report)
    else: print(report,end='')
