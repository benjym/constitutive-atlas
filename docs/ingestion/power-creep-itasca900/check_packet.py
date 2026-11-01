"""Independent Cartesian algebra/analytical checks; no Atlas evaluator or binaries.

Run from repository root. --verify-private additionally verifies the temporary
web extraction; a missing private file is reported as unavailable by default.
The checks freeze their tolerances here before their first execution.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
checks = []


def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)


def close(a, b):
    return math.isclose(a, b, rel_tol=2e-9, abs_tol=2e-10)


def dot(a, b):
    return sum(a[i][j] * b[i][j] for i in range(3) for j in range(3))


def trace(a):
    return sum(a[i][i] for i in range(3))


def dev(a):
    return [[a[i][j] - (trace(a) / 3 if i == j else 0)
             for j in range(3)] for i in range(3)]


def mises(s):
    return math.sqrt(1.5 * dot(s, s))


def intensity(q, a1, n1, r1, a2, n2, r2):
    return ((a1 * q**n1 if q >= r1 else 0)
            + (a2 * q**n2 if q <= r2 else 0))


def creep(s, f):
    q = mises(s)
    return [[1.5 * f * x / q for x in row] for row in s]


def rhs(sig, d, k, g, a, n):
    s = dev(sig)
    q = mises(s)
    c = creep(s, a * q**n) if q else [[0.0]*3 for _ in range(3)]
    dd = dev(d)
    return [[(k * trace(d) if i == j else 0)
             + 2*g*(dd[i][j] - c[i][j]) for j in range(3)] for i in range(3)]


def rotate(a):
    # Orthogonal, non-axis-aligned planar rotation; Q A Q^T.
    c, s = math.cos(0.37), math.sin(0.37)
    q = [[c, -s, 0], [s, c, 0], [0, 0, 1]]
    return [[sum(q[i][k]*a[k][l]*q[j][l]
                 for k in range(3) for l in range(3))
             for j in range(3)] for i in range(3)]


def matrices_close(a, b):
    return all(close(a[i][j], b[i][j]) for i in range(3) for j in range(3))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify-private', action='store_true')
    args = parser.parse_args()
    packet = json.loads((HERE / 'formulation-crosswalk.json').read_text())
    f = packet['formulation']
    # Validate only the formulation subsection, not this non-model crosswalk.
    schema = json.loads((ROOT / 'schemas/model-v0.3.schema.json').read_text())
    sys.path.insert(0, str(ROOT))
    from atlas.structure import check as structural_check
    structural_check(f, schema['oneOf'][2]['properties']['formulation'])
    schema_check = 'physical-time formulation subsection passed using atlas.structure'
    check('v0.3 explicit ODE profile', packet['schema_version'] == '0.3'
          and f['time_dependence'] == 'physical_time' and f['equation_form'] == 'ode'
          and 'integration' not in packet)
    check('ODE stress observable binding', f['stress'] == {
        'source': 'observable', 'name': 'stress', 'measure': 'cauchy', 'scope': 'effective'})
    check('ODE input declarations', set(f['inputs']['equation']) == {'time', 'strain_rate'}
          and set(f['inputs']['advance']) == {'start_time', 'duration'})
    check('persistent explicit stress initialization',
          packet['initialization']['required_state'] == ['sigma']
          and packet['state'][0]['semantics']['role'] == 'persistent')
    sig = [[12., 2., -1.], [2., 5., 3.], [-1., 3., 4.]]
    d = [[0.1, 0.03, -0.02], [0.03, -0.04, 0.01], [-0.02, 0.01, 0.02]]
    s = dev(sig)
    q = mises(s)
    c = creep(s, 0.7)
    check('creep is isochoric', close(trace(c), 0))
    check('equivalent creep intensity', close(math.sqrt(2*dot(c, c)/3), 0.7))
    check('dissipation sigma:Dc = q*f', close(dot(sig, c), q*0.7))
    mandel = [s[0][0], s[1][1], s[2][2], math.sqrt(2)*s[0][1],
              math.sqrt(2)*s[1][2], math.sqrt(2)*s[0][2]]
    check('Mandel contraction matches Cartesian', close(sum(x*x for x in mandel), dot(s, s)))
    r = rhs(sig, d, 7., 5., 0.02, 1.4)
    check('elastic volume only', close(trace(r), 3*7*trace(d)))
    check('sign conversion preserves law', matrices_close(
        rhs([[-x for x in row] for row in sig], [[-x for x in row] for row in d],
            7., 5., 0.02, 1.4), [[-x for x in row] for row in r]))
    check('fixed-frame rotational covariance', matrices_close(
        rhs(rotate(sig), rotate(d), 7., 5., 0.02, 1.4), rotate(r)))
    check('inclusive common threshold double activity',
          intensity(2., 3., 1., 2., 5., 1., 2.) == 16.)
    check('overlap interior adds both', intensity(2., 3., 1., 1., 5., 1., 3.) == 16.)
    check('low regime only second', intensity(0.5, 3., 1., 1., 5., 1., 3.) == 2.5)
    check('high regime only first', intensity(4., 3., 1., 1., 5., 1., 3.) == 12.)
    check('reversed thresholds leave gap', intensity(2., 3., 1., 3., 5., 1., 1.) == 0.)
    # Retain evidence of Eq (7)'s trace defect, not a rewritten equation.
    volume_rate = [[1. if i == j else 0. for j in range(3)] for i in range(3)]
    printed_trace = 2*5*trace(volume_rate)  # Dc is traceless.
    check('printed Eq7 trace-defect witness retained', printed_trace == 30.)
    hydro = [[9. if i == j else 0. for j in range(3)] for i in range(3)]
    z = [[0.]*3 for _ in range(3)]
    check('proposed n>0 zero-stress extension gives stationary hydro hold',
          rhs(hydro, z, 7., 5., 0.02, 1.4) == z)
    # At zero strain rate, fixed direction and one active mechanism:
    # qdot=-3*G*A*q^n. Check analytic histories by independent differentiation.
    for n in [1., 2., 3.]:
        g, a, q0, t, h = 2., 0.03, 4., 0.7, 1e-5
        def exact(x):
            if n == 1:
                return q0*math.exp(-3*g*a*x)
            return (q0**(1-n)+(n-1)*3*g*a*x)**(1/(1-n))
        q_t = exact(t)
        derivative = (exact(t+h)-exact(t-h))/(2*h)
        check(f'analytical hold derivative n={n:g}', close(derivative, -3*g*a*q_t**n))
        check(f'hold relaxes n={n:g}', 0 < q_t < q0)
    # Normalizing variable-exponent stress by p_ref fixes units of b_i.
    for n in [0.5, 1., 3.2]:
        a, p_ref, stress = 0.02, 11., 7.
        b = a*p_ref**n
        check(f'normalized power equivalence n={n:g}', close(a*stress**n, b*(stress/p_ref)**n))
    rec = json.loads((HERE / 'source-receipts.json').read_text())
    private = Path(rec['private_path'])
    private_status = 'unavailable: private extraction not present'
    if private.exists():
        check('exact private source receipt hash', hashlib.sha256(private.read_bytes()).hexdigest() == rec['sha256'])
        raw = json.loads(private.read_text())
        check('received equation and convention titles', all(t in raw for t in
              ['# Power Model', '# Sign Conventions', '# Notations', '(7)', '9.0.182']))
        private_status = 'verified extracted-text JSON; origin HTML not received'
    elif args.verify_private:
        raise FileNotFoundError(private)
    output = {'study_id': 'power-creep-itasca900-algebra-v1',
              'checks_passed': len(checks), 'checks': checks,
              'formulation_schema': schema_check, 'private_source': private_status,
              'scope': 'Cartesian algebra, branch witnesses and analytical hold identities only; no finite-step integration, Atlas material or vendor execution',
              'retained_findings': ['Eq7 deviator trace defect', 'Eq5 double activity at equal thresholds',
                                    'origin HTML HTTP403; extracted-text receipt only']}
    print(json.dumps(output, indent=2))


if __name__ == '__main__':
    main()
