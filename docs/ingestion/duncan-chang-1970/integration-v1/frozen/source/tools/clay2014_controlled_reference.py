"""Prospective controlled-mesh hydro reference. No Atlas or integration imports.

The failed adaptive-tolerance experiment supplies only its already published
inputs. Decimal scalar closed forms are evaluated from the original parent at
two precisions; no compiled observations enter protocol/reference generation.
"""
import argparse
from decimal import Decimal, localcontext
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'clay2014-controlled-resolution-protocol-v1'
HISTORICAL = 'catalogue/investigations/clay2014-paths-v1/native.json'
HISTORICAL_SHA = '8f9971fd1e620f54b9fbcf1dd886ca87b7a75f572690fb0de846ed3eca2cdb11'
MODEL = 'models/research/clay2014/hypoplastic-clay-2014-printed-am-proposed-alpha-fixed-plane.json'
MODEL_SHA = '9077e7d5d7cdb42a7cc5c2ab49c29c1643543c54310caad26c17b5f256236de5'
FACTORS = (1, 2, 4, 8)
POLICY = {
    'settings': [2e-10, 1e-4, 45, 20, 20000, 11],
    'required_fractions': [0.5, 0.5],
    'required_rejected': 0,
    'caller_stress_relative_bound': 1e-4,
    'caller_void_absolute_bound': 5e-8,
    'endpoint_successor_error_factor': 0.35,
    'stress_floor_relative': 5e-12,
    'void_floor_absolute': 5e-13,
    'endpoint_allowance': '2*(fixed floor + maximum adjacent endpoint reference uncertainty)',
    'reference_precisions': [90, 140],
    'reference_uncertainty': 'absolute precision difference plus binary64 rounding difference; empirical, not a rigorous bound',
    'reference_stress_uncertainty_limit_Pa': 1e-7,
    'reference_void_uncertainty_limit': 1e-15,
    'parity_scaled_bound': 5e-11,
    'claims': {'scientific_admission': False, 'full_model_validation': False,
               'original_failed_study_replaced': False, 'rigorous_error_bound': False},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda _: require(False, 'nonfinite JSON'))


def binary(value):
    require(type(value) in (int, float) and math.isfinite(value), 'finite numeric input')
    return Decimal.from_float(float(value))


def sine(value):
    """Taylor sum in active Decimal context; bounded source angle only."""
    require(0 < value < 1, 'bounded source friction angle')
    term = total = value
    for k in range(1, 1000):
        term *= -value * value / Decimal((2*k)*(2*k+1))
        updated = total + term
        if updated == total:
            return total
        total = updated
    raise ValueError('Decimal sine did not converge')


def inputs(root=ROOT):
    root = Path(root)
    require(sha(root/HISTORICAL) == HISTORICAL_SHA, 'historical input bytes changed')
    require(sha(root/MODEL) == MODEL_SHA, 'source model bytes changed')
    report = read(root/HISTORICAL)
    groups = [g for g in report['records'] if g['case'] == 'isotropic-ratios-hydro-reversal'
              and g['partitions'] == 7 and g['tolerance'] == 1e-4]
    require(len(groups) == 1, 'single historical input group')
    calls = groups[0]['calls']
    require(len(calls) == 21, 'three original segments times seven caller pieces')
    first = calls[0]['request']
    require(first['settings'] == POLICY['settings'], 'historical settings identity')
    for call in calls:
        r = call['request']
        require(r['model'] == first['model'] and r['parameters'] == first['parameters'], 'fixed source identity')
        d = r['strain']
        require(d[0] == d[1] == d[2] and not any(d[3:]) and d[0] != 0, 'hydro loading only')
    p = first['parameters']; z = first['initial']
    require(len(p) == 17 and p[0] == 1000 and p[7:10] == [1, 1, 1]
            and p[6] == 0 and p[13] == .3, 'selected isotropic source specialization')
    require(z[:3] == [1e5]*3 and z[3:6] == [0]*3 and z[6] == .65, 'fixed original parent')
    return {'model': first['model'], 'parameters': p, 'initial': z,
            'base_increments': [c['request']['strain'] for c in calls]}


def schedule(data, factor):
    require(type(factor) is int and factor in FACTORS, 'declared dyadic factor')
    total = [Fraction() for _ in range(6)]
    rows = []
    for index, inc in enumerate(data['base_increments']):
        piece = [v/factor for v in inc]
        require(all(Fraction(v)*factor == Fraction(w) for v, w in zip(piece, inc)), 'exact dyadic split')
        for sub in range(factor):
            total = [a+Fraction(b) for a, b in zip(total, piece)]
            rows.append({'segment': index//7+1, 'base_piece': index%7+1,
                         'subpiece': sub+1, 'increment': piece.copy(),
                         'physical_endpoint': index%7 == 6 and sub == factor-1,
                         'cumulative_loading_exact': [[str(x.numerator), str(x.denominator)] for x in total]})
    return rows


def trajectory(data, factor, precision):
    """Exact scalar ODE solution sampled at caller points, rounded in Decimal.

    With v positive in compression, pe'=pe*v/lambda and
    y=(pe/p)^alpha obeys y'=-alpha/2*(1/kappa-1/lambda)*(y-sign(v))*v.
    Specific volume is (1+e0)*exp(-cumulative v).
    """
    with localcontext() as ctx:
        ctx.prec = precision
        p = [binary(x) for x in data['parameters']]
        z = [binary(x) for x in data['initial']]
        la, ka = p[3], p[4]
        s = sine(p[2])
        af = Decimal(3).sqrt()*(3-s)/(2*Decimal(2).sqrt()*s)
        alpha = (((la-ka)/(la+ka)*(3+af*af)/(af*Decimal(3).sqrt())).ln()/Decimal(2).ln())
        require(alpha > 0, 'positive source exponent')
        pe0 = p[0]*((p[5]-(1+z[6]).ln())/la).exp()
        y = ((pe0/z[0]).ln()*alpha).exp()
        out = []
        for knot in schedule(data, factor):
            # All dyadic divisions are exact; Decimal represents the original
            # binary64 increment, not its short decimal display.
            v = sum((binary(x) for x in knot['increment'][:3]), Decimal())
            sign = Decimal(1 if v > 0 else -1)
            y = sign+(y-sign)*(-alpha/2*(1/ka-1/la)*v).exp()
            num, den = knot['cumulative_loading_exact'][0]
            volume = 3*Decimal(num)/Decimal(den)
            pe = pe0*(volume/la).exp()
            pressure = pe*(-y.ln()/alpha).exp()
            void = (1+z[6])*(-volume).exp()-1
            require(y > 0 and pressure > 0 and void >= 0, 'scalar reference support')
            out.append((pressure, void))
        return out


def build(root=ROOT):
    data = inputs(root)
    groups = []
    for factor in FACTORS:
        low = trajectory(data, factor, POLICY['reference_precisions'][0])
        high = trajectory(data, factor, POLICY['reference_precisions'][1])
        points = []
        with localcontext() as ctx:
            ctx.prec = 160
            for knot, a, b in zip(schedule(data, factor), low, high):
                target = [float(x) for x in b]
                uncertainty = [float(abs(x-y)+abs(binary(t)-y)) for x,y,t in zip(a,b,target)]
                require(uncertainty[0] <= POLICY['reference_stress_uncertainty_limit_Pa']
                        and uncertainty[1] <= POLICY['reference_void_uncertainty_limit'], 'reference precision gate')
                points.append(knot | {'target': [target[0]]*3+[0.0]*3+[target[1]],
                                      'decimal140': [str(x) for x in b],
                                      'reference_uncertainty': {'stress': math.sqrt(3)*uncertainty[0], 'e': uncertainty[1]}})
        groups.append({'factor': factor, 'call_count': len(points),
                       'effective_midpoint_steps_per_segment': 14*factor, 'points': points})
    return {'version': VERSION, 'generator_sha256': sha(__file__),
            'input_pins': {HISTORICAL: HISTORICAL_SHA, MODEL: MODEL_SHA},
            'scope': 'Isotropic hydrostatic numerical mechanism only; printed-Am/proposed-Eq49 zero-spin no-IGS research variant.',
            'provenance': 'Prospective follow-up to the retained failed adaptive-tolerance study; factor1 baseline already observed, refined factors unobserved at protocol freeze.',
            'policy': POLICY, 'input': data,
            'stress_scale_Pa': math.hypot(*data['initial'][:6]),
            'groups': groups, 'actual_calls_per_backend': sum(g['call_count'] for g in groups)}


def verify(document, root=ROOT):
    require(canonical(document) == canonical(build(root)), 'protocol/reference differs from fresh pinned replay')
    return document


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'fresh output required')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(build(), indent=2, allow_nan=False)+'\n')
