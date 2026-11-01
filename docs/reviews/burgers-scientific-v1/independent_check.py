"""Original review calculations; stdlib only, no Atlas/reference.py imports.

An affine matrix exponential in strain-scaled variables checks the saved
two-exponential references. Exact rational tensor work checks thermodynamics.
Only reads existing evidence; prints JSON and never calls compiled software.
"""
from decimal import Decimal as Q, localcontext
from fractions import Fraction as F
from pathlib import Path
import json, random

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = ROOT / 'docs/ingestion/burgers-itasca900/integration-v1'

def num(x):
    return Q.from_float(float(x))

def matmul(a, b):
    return [[sum(a[i][k]*b[k][j] for k in range(4)) for j in range(4)] for i in range(4)]

def exp_action(a, h, y):
    """Taylor/scaling/squaring; no eigenvalues or shifted steady-state formula."""
    a = [[x*h for x in row] for row in a]
    norm = max(sum(abs(x) for x in row) for row in a)
    scale = 0
    while norm > Q('0.25'):
        norm /= 2
        scale += 1
    a = [[x / (2**scale) for x in row] for row in a]
    term = [[Q(i == j) for j in range(4)] for i in range(4)]
    total = [row[:] for row in term]
    for n in range(1, 300):
        term = [[x/n for x in row] for row in matmul(term, a)]
        total = [[total[i][j]+term[i][j] for j in range(4)] for i in range(4)]
        if max(abs(x) for row in term for x in row) < Q('1e-100'):
            break
    else:
        raise AssertionError('Taylor truncation budget exhausted')
    for _ in range(scale):
        total = matmul(total, total)
    return [sum(total[i][j]*y[j] for j in range(4)) for i in range(4)]

def deviator(x):
    mean = sum(x[:3])/3
    return [v-(mean if j < 3 else 0) for j, v in enumerate(x)]

def advance(state, strain, rates, params, kinds, h):
    bulk, gm, gk, em, ek = map(num, params)
    s = deviator(state[:6]); p = sum(state[:3])/3
    d = deviator(rates); mean = sum(rates[:3])/3
    out_s, out_k, out_e = [], [], []
    for j in range(6):
        z = Q(0)
        if kinds[j] == 'strain':
            a = [[-gm/ek-gm/em, gk/ek, z, d[j]],
                 [gm/ek, -gk/ek, z, z],
                 [z, z, z, rates[j]], [z, z, z, z]]
            pressure = p + 3*bulk*mean*h
        else:
            # x=S/(2Gm). e_dot=x_dot+k_dot+Gm*x/etaM.
            a = [[z, z, z, d[j]/(2*gm)],
                 [gm/ek, -gk/ek, z, z],
                 [gm/ek+gm/em, -gk/ek, z, d[j]/(2*gm)],
                 [z, z, z, z]]
            pressure = p + mean*h
        x, k, e, one = exp_action(a, h, [s[j]/(2*gm), state[6+j], strain[j], Q(1)])
        assert abs(one-1) < Q('1e-90')
        if kinds[j] == 'stress' and j < 3:
            e += (pressure-p)/(3*bulk)
        out_s.append(2*gm*x + (pressure if j < 3 else 0))
        out_k.append(k); out_e.append(e)
    return out_s+out_k, out_e

def reference_checks():
    requests = json.loads((EVIDENCE/'requests.json').read_text())
    refs = json.loads((EVIDENCE/'references.json').read_text())
    count = 0; worst = Q(0)
    for case in requests['schedules']:
        spec = case['spec']; expected = refs[case['id']]
        state = list(map(num, spec['initial']))
        strain = list(map(num, spec['initial_strain']))
        points = [(state, strain)]
        for seg in spec['segments']:
            points.append((state, strain))
            kinds = [c['quantity'] for c in seg['controls']]
            assert len(set(kinds[:3])) == 1  # actual reference scope
            rates = []
            for j,c in enumerate(seg['controls']):
                old = (state if c['quantity']=='stress' else strain)[j]
                rates.append(Q(0) if c['kind']=='hold' else num(c['value']) if c['kind']=='rate' else (num(c['value'])-old)/num(seg['duration']))
            initial_state, initial_strain = state, strain
            for n in range(1, seg['samples']+1):
                # Match the frozen sample's binary64 physical time exactly.
                h = num(float(seg['duration'])*n/seg['samples'])
                state, strain = advance(initial_state, initial_strain, rates, spec['parameters'], kinds, h)
                points.append((state, strain))
        assert len(points) == len(expected)
        for (state, strain), ref in zip(points, expected):
            for actual, target in zip(state+strain, list(map(Q,ref['state']+ref['strain']))):
                error = abs(actual-target)/max(Q(1), abs(target))
                worst = max(worst, error)
                assert error < Q('1e-70'), (case['id'], error)
                count += 1
    return dict(schedule_points=sum(len(v) for v in refs.values()), scalars=count,
                maximum_scaled_difference=str(worst), acceptance='1e-70 * max(1, abs(reference))')

def exact_checks():
    rng = random.Random(901184)
    def vec(): return [F(rng.randint(-100,100),rng.randint(1,50)) for _ in range(6)]
    def dot(a,b): return sum(x*y*(1 if j<3 else 2) for j,(x,y) in enumerate(zip(a,b)))
    for _ in range(100):
        bulk,gm,gk,em,ek = [F(rng.randint(1,100),rng.randint(1,10)) for _ in range(5)]
        sig, k, d = vec(), deviator(vec()), vec()
        s = deviator(sig); p = sum(sig[:3])/3
        kd = [(x-2*gk*y)/(2*ek) for x,y in zip(s,k)]
        sd = [2*gm*(v-w-x/(2*em)) for v,w,x in zip(deviator(d),kd,s)]
        pd = bulk*sum(d[:3])
        power = dot(sig,d)
        ud = p*pd/bulk + dot(s,sd)/(2*gm) + 2*gk*dot(k,kd)
        diss = dot(s,s)/(2*em) + 2*ek*dot(kd,kd)
        assert power-ud == diss and diss >= 0
        # Reverse all mechanical signs: linear law is covariant, work invariant.
        assert [(-x+2*gk*y)/(2*ek) for x,y in zip(s,k)] == [-x for x in kd]
        # Characteristic polynomial lambda²+T lambda+P, T,P positive.
        t = gm/ek+gm/em+gk/ek; determinant = gm*gk/(em*ek)
        assert t > 0 and determinant > 0
        assert t*t-4*determinant == (gm/ek+gm/em-gk/ek)**2 + 4*gm*gk/(ek*ek)
        assert t*t-4*determinant > 0
    # Cartesian tensor shears map isometrically to Mandel: squared sqrt(2)
    # multiplier gives precisely the weight 2 used above, for all three shears.
    return dict(exact_cartesian_energy_sign_stability_cases=100, failures=0)

def saved_metrics():
    refs=json.loads((EVIDENCE/'references.json').read_text())
    result={}
    for backend in ['native','wasm']:
        calls={x['label']:x['response'] for x in json.loads((EVIDENCE/(backend+'-calls.json')).read_text())}
        refined={}
        for label in ['relaxation','relaxation-coarse']:
            actual=calls[label]['points'][-1]['state']; ref=list(map(float,refs[label][-1]['state']))
            refined[label]={name:max(abs(a-b) for a,b in zip(actual[sl],ref[sl])) for name,sl in [('stress_Pa',slice(0,6)),('kelvin_strain',slice(6,12))]}
        for field in ['stress_Pa','kelvin_strain']:
            assert refined['relaxation'][field] < refined['relaxation-coarse'][field]
        result[backend]=refined
    return result

def main():
    with localcontext() as ctx:
        ctx.prec=110
        return dict(identity='REV-burgers-scientific-v1-independent-check',
                    exact=exact_checks(), references=reference_checks(),
                    separated_refinement=saved_metrics(), compiled_calls=0)

if __name__=='__main__':
    print(json.dumps(main(),indent=2))
