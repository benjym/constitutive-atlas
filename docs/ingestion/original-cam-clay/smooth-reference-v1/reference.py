"""One smooth OCC reference, not a general material update or production kernel."""
import argparse
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('occ_retained_analytical', HERE.parent / 'check_packet.py')
analytical = importlib.util.module_from_spec(spec)
spec.loader.exec_module(analytical)


def finite(value):
    if type(value) not in (int, float) or not math.isfinite(value):
        raise ValueError('finite real value required, excluding booleans')
    return value


def exact(coordinate, parameters):
    value = analytical.virgin_undrained(coordinate, p0=parameters['virgin_p0_Pa'],
        M=parameters['M'], lam=parameters['lambda'], kap=parameters['kappa'],
        Gamma=parameters['Gamma'], p_ref=parameters['p_ref_Pa'])
    return (value['p'], value['q'], math.log(value['p_c'] / parameters['p_ref_Pa'])), value['v']


def rates(state, parameters, volume):
    """Solve undrained volume, hardening and differentiated positive-q yield.

    c=ln(pc/p_ref). Intermediate RK stages use the literal yield gradient fp,
    rather than substituting its on-surface value M-q/p. This is the declared
    project off-surface stage extension, not a printed finite update algorithm.
    """
    p, q, c = map(finite, state)
    M, lam, kap, pref, volume = map(finite, (parameters['M'], parameters['lambda'],
        parameters['kappa'], parameters['p_ref_Pa'], volume))
    if not (M > 0 and lam > kap > 0 and pref > 0 and volume > 0 and p > 0 and 0 < q / p < M):
        raise ValueError('outside declared positive-q wet-side smooth domain')
    plastic_volume = M - q / p
    dp = -volume * p * plastic_volume / kap
    dc = volume * plastic_volume / (lam - kap)
    fp = M * (math.log(p / pref) - c + 1)
    dq = M * p * dc - fp * dp
    result = (dp, dq, dc)
    if not all(math.isfinite(v) for v in result):
        raise ValueError('nonfinite source-constraint derivative')
    return result


def integrate(policy, count):
    if type(count) is not int or count <= 0:
        raise ValueError('positive integer step count required')
    parameters, path = policy['parameters'], policy['path']
    start, end = path['start'], path['end']
    if not (0 < finite(start) < finite(end)):
        raise ValueError('positive smooth start and increasing interval required')
    state, volume = exact(start, parameters)
    h = (end - start) / count
    rows = [{'coordinate': start, 'state': list(state)}]
    def shifted(base, rate, scale):
        return tuple(x + scale * v for x, v in zip(base, rate))
    for index in range(count):
        k1 = rates(state, parameters, volume)
        k2 = rates(shifted(state, k1, h / 2), parameters, volume)
        k3 = rates(shifted(state, k2, h / 2), parameters, volume)
        k4 = rates(shifted(state, k3, h), parameters, volume)
        state = tuple(x + h * (a + 2*b + 2*c + d) / 6
                      for x, a, b, c, d in zip(state, k1, k2, k3, k4))
        rates(state, parameters, volume)  # Accepted grid point must stay in domain.
        rows.append({'coordinate': start + (end - start) * (index + 1) / count, 'state': list(state)})
    return {'steps': count, 'specific_volume': volume, 'rows': rows}


def assess(policy, paths):
    P, bounds = policy['parameters'], policy['policy']
    M, pref, scale = P['M'], P['p_ref_Pa'], bounds['pressure_error_scale_Pa']
    results = []
    for path, count in zip(paths, policy['path']['steps']):
        if path['steps'] != count or len(path['rows']) != count + 1:
            raise ValueError('unexpected reference grid')
        errors, yields, works, packing = [], [], [], []
        for index, row in enumerate(path['rows']):
            coordinate = policy['path']['start'] + (policy['path']['end'] - policy['path']['start']) * index / count
            if row['coordinate'] != coordinate:
                raise ValueError('reference coordinate changed')
            expected, volume = exact(coordinate, P)
            p, q, c = row['state']
            if path['specific_volume'] != volume:
                raise ValueError('undrained specific volume changed')
            rates(row['state'], P, volume)
            errors.append(max(abs(p-expected[0])/scale, abs(q-expected[1])/scale, abs(c-expected[2])))
            yields.append(abs(q + M*p*(math.log(p/pref)-c))/scale)
            works.append(abs(p*(M-q/p)+q-M*p)/scale)
            expected_c = 1 + (P['Gamma'] - volume - P['kappa']*math.log(p/pref))/(P['lambda']-P['kappa'])
            packing.append(abs(c - expected_c))
        results.append({'steps':count, 'maximum_scaled_state_error':max(errors),
            'maximum_scaled_yield_drift':max(yields), 'maximum_scaled_dissipation_residual':max(works),
            'maximum_packing_identity_drift':max(packing)})
    if len(paths) != len(policy['path']['steps']):
        raise ValueError('missing or extra refinement paths')
    ratios = [a['maximum_scaled_state_error']/b['maximum_scaled_state_error'] for a,b in zip(results,results[1:])]
    passed = (results[-1]['maximum_scaled_state_error'] <= bounds['finest_maximum_scaled_state_error']
        and all(r >= bounds['minimum_adjacent_error_improvement'] for r in ratios)
        and all(r['maximum_scaled_yield_drift'] <= bounds['maximum_scaled_yield_drift_all_resolutions']
            and r['maximum_scaled_dissipation_residual'] <= bounds['maximum_scaled_dissipation_residual'] for r in results))
    return {'passed':passed, 'paths':results, 'adjacent_error_improvement':ratios}


def run():
    policy = json.loads((HERE / 'prospective.json').read_text())
    paths = [integrate(policy, n) for n in policy['path']['steps']]
    return {'id':policy['id'], 'prospective_sha256':hashlib.sha256((HERE/'prospective.json').read_bytes()).hexdigest(),
        'assessment':assess(policy,paths), 'trajectories':paths, 'compiled_calls':0,
        'independent_scientific_review':False, 'general_material_update':False}


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    report=run()
    args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report['assessment'],indent=2))
    raise SystemExit(0 if report['assessment']['passed'] else 1)
