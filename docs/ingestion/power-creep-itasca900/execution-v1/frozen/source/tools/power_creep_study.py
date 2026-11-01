"""Frozen analytical qualification of a declarative power-creep research model.

This is a reference/observer/assessor, not a constitutive integration kernel.
No model expressions or generated headers are imported for the reference laws.
Prepare inputs and freeze them BEFORE compiling or observing any backend.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'docs/ingestion/power-creep-itasca900/execution-v1'
MODEL = ROOT / 'models/research/power-creep/power-creep-itasca900-both-active-ode.json'
MODEL_ID = 'power-creep-itasca900-both-active-ode'
# K,G,p_ref,b1,n1,b2,n2,time_scale. Independent illustrative study constants.
DEFAULT_P = [20e6, 12e6, 1e6, .002, 1., .001, 3., 1.]
ZERO = [0.]*6
INITIAL = [1200000., 900000., 900000., 0., 0., 0.]


def dumps(x):
    return json.dumps(x, indent=2, allow_nan=False) + '\n'


def read(path):
    return json.loads(Path(path).read_text(), parse_constant=lambda x: (_ for _ in ()).throw(ValueError(x)))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def csv(values):
    return ','.join(format(x, '.17g') for x in values)


def cartesian(sigma):
    r = math.sqrt(2)
    return [[sigma[0], sigma[3]/r, sigma[5]/r],
            [sigma[3]/r, sigma[1], sigma[4]/r],
            [sigma[5]/r, sigma[4]/r, sigma[2]]]


def mandel(a):
    return [a[0][0], a[1][1], a[2][2], math.sqrt(2)*a[0][1],
            math.sqrt(2)*a[1][2], math.sqrt(2)*a[0][2]]


def reference_rate(sigma, d, p):
    """Direct Cartesian source Eq3, using A_i=b_i/p_ref^n_i, q in Pa."""
    k, g, pref, b1, n1, b2, n2, _ = p
    a = cartesian(sigma)
    strain = cartesian(d)
    mean = sum(a[i][i] for i in range(3))/3
    volume = sum(strain[i][i] for i in range(3))
    s = [[a[i][j] - (mean if i == j else 0) for j in range(3)] for i in range(3)]
    q = math.sqrt(1.5*sum(x*x for row in s for x in row))
    f = (b1/pref**n1)*q**n1 + (b2/pref**n2)*q**n2
    creep = [[1.5*f*x/q if q else 0. for x in row] for row in s]
    out = [[(k*volume if i == j else 0) + 2*g*(strain[i][j] -
           (volume/3 if i == j else 0) - creep[i][j]) for j in range(3)] for i in range(3)]
    return mandel(out), mandel(creep), q, f


def decay_exact(t, p=DEFAULT_P):
    # qdot=-a*q-b*q^3 for n1=1,n2=3. Mean pressure constant.
    g, pref, b1, b2 = p[1], p[2], p[3], p[5]
    q0 = 300000.
    a, b = 3*g*b1/pref, 3*g*b2/pref**3
    if b == 0:
        q = q0*math.exp(-a*t)
    elif a == 0:
        q = q0/math.sqrt(1+2*b*q0*q0*t)
    else:
        e = math.exp(-a*t)
        q = q0*e/math.sqrt(1+b/a*q0*q0*(1-e*e))
    return [1e6+2*q/3, 1e6-q/3, 1e6-q/3, 0., 0., 0.]


def integration_request(name, p=None, initial=None, d=None, duration=5., **changes):
    p, initial, d = list(p or DEFAULT_P), list(initial or INITIAL), list(d or ZERO)
    args = [MODEL_ID, csv(p), csv(initial), csv(d), 7., duration,
            1e-8, 1e-11, 1e-12, .1, 200000]
    options = ['--mode', 'integrate-time', '--model', MODEL_ID, '--parameters', csv(p),
               '--initial', csv(initial), '--strain-rate', csv(d), '--start-time', '7',
               '--duration', str(duration), '--rtol', '1e-8', '--atol', '1e-11',
               '--min-time-step', '1e-12', '--max-time-step', '.1', '--max-substeps', '200000']
    for key, value in changes.items():
        index, option = {'budget': (10, '--max-substeps'), 'start': (4, '--start-time')}[key]
        args[index] = value
        options[options.index(option)+1] = str(value)
    return {'id': name, 'function': 'atlas_integrate_time', 'types': ['string']*4+['number']*7,
            'args': args, 'command': options, 'ok': True, 'checks': []}


def assertion(path, value, atol=1e-8, rtol=1e-11):
    return {'path': path, 'value': value, 'atol': atol, 'rtol': rtol}


def prepare():
    out = PACKET / 'study.json'
    if out.exists():
        raise FileExistsError('Do not overwrite frozen inputs; create a new study identity.')
    requests = []
    for index, (z, d, p) in enumerate([
        (INITIAL, ZERO, DEFAULT_P),
        ([1e6]*3+[0]*3, ZERO, DEFAULT_P),
        (ZERO, [.001, -.0003, .0002, .0004, -.0007, .0001], DEFAULT_P),
        ([1.3e6, .8e6, -.2e6, 2e5, -3e5, 1e5], [.001, -.0005, 0, .0002, 0, -.0001], DEFAULT_P),
        ([-x for x in INITIAL], ZERO, DEFAULT_P),
        ([0, 0, 0, 2e5, 0, 0], ZERO, DEFAULT_P),
        (INITIAL, ZERO, [20e6, 12e6, 1e6, .002, 1.5, .001, 2.2, 1]),
        (INITIAL, [.001, .001, .001, 0, 0, 0], [20e6, 12e6, 1e6, 0, 1, 0, 3, 1]),
    ]):
        expected, _, _, _ = reference_rate(z, d, p)
        requests.append({'id': f'rate-{index}', 'function': 'atlas_evaluate_time',
                         'types': ['string']*4+['number'], 'args': [MODEL_ID, csv(p), csv(z), csv(d), 7.],
                         'command': ['--mode', 'evaluate-time', '--model', MODEL_ID, '--parameters', csv(p),
                                     '--initial', csv(z), '--strain-rate', csv(d), '--start-time', '7'],
                         'ok': True, 'checks': [assertion(['values'], expected, 1e-7)]})
    for label, p in [('mixed-13', DEFAULT_P),
                     ('linear', [20e6, 12e6, 1e6, .002, 1, 0, 3, 1]),
                     ('cubic', [20e6, 12e6, 1e6, 0, 1, .001, 3, 1])]:
        r = integration_request('hold-'+label, p=p)
        r['checks'] = [assertion(['state'], decay_exact(5., p), .06, 0), assertion(['time'], 12., 0, 0)]
        requests.append(r)
    r = integration_request('hydro-hold', initial=[1e6]*3+[0]*3)
    r['checks'] = [assertion(['state'], [1e6]*3+[0]*3, 0, 0)]
    requests.append(r)
    # A linear two-component law at constant D has exact affine relaxation.
    p = [20e6, 12e6, 1e6, .002, 1, .001, 1, 1]
    d = [.001, -.0002, -.0001, .0004, -.0003, .0002]
    lam = 3*p[1]*(p[3]+p[5])/p[2]
    volume = sum(d[:3])
    s0 = [200000., -100000., -100000., 0, 0, 0]
    dd = [x-(volume/3 if i < 3 else 0) for i, x in enumerate(d)]
    expected = [(1e6+p[0]*volume*5 if i < 3 else 0)
                + s0[i]*math.exp(-lam*5) + 2*p[1]*dd[i]*(1-math.exp(-lam*5))/lam for i in range(6)]
    r = integration_request('constant-rate-linear', p=p, d=d)
    r['checks'] = [assertion(['state'], expected, .06, 0)]
    requests.append(r)
    r = integration_request('volume-elastic', initial=[1e6]*3+[0]*3, d=[.001]*3+[0]*3)
    r['checks'] = [assertion(['state'], [1.3e6]*3+[0]*3, 1e-6, 0)]
    requests.append(r)
    # Failure must discard earlier accepted substeps and restore the incoming clock.
    r = integration_request('budget-rollback', duration=5., budget=2)
    r['ok'] = False
    r['checks'] = [assertion(['state'], INITIAL, 0, 0), assertion(['time'], 7., 0, 0)]
    r['minimum_substeps'] = 2
    requests.append(r)
    for name, duration in [('zero-duration', 0.), ('negative-duration', -1.)]:
        r = integration_request(name, duration=duration)
        r['ok'] = False
        r['checks'] = [assertion(['state'], INITIAL, 0, 0), assertion(['time'], 7., 0, 0)]
        requests.append(r)
    r = integration_request('unsupported-sublinear-exponent', p=[20e6, 12e6, 1e6, .002, .5, .001, 3, 1])
    r['ok'] = False
    requests.append(r)
    r = integration_request('missing-explicit-state')
    r['args'][2] = ''
    r['command'][r['command'].index('--initial')+1] = ''
    r['ok'] = False
    requests.append(r)
    r = integration_request('recovery-after-failures')
    r['checks'] = [assertion(['state'], decay_exact(5.), .06, 0)]
    requests.append(r)
    # Fully coupled Newton schedule tests; all six stress components held.
    for name, z in [('creep', INITIAL), ('creep-general-tensor', [1.3e6, .8e6, .9e6, 2e5, -1e5, 3e5]),
                    ('hydrostatic-creep', [1e6]*3+[0]*3)]:
        r = schedule_request(name, z, stress=True)
        _, c, _, _ = reference_rate(z, ZERO, DEFAULT_P)
        r['checks'] = [assertion(['points', -1, 'state'], z, .01, 0),
                       assertion(['points', -1, 'strain'], [5*x for x in c], 1e-10, 0),
                       assertion(['points', -1, 'time'], 5., 0, 0)]
        requests.append(r)
    r = schedule_request('schedule-nonlinear-relaxation', INITIAL)
    r['checks'] = [assertion(['points', -1, 'state'], decay_exact(5.), 15., 0)]
    requests.append(r)
    r = schedule_request('schedule-load-from-hydrostatic', [1e6]*3+[0]*3)
    # Pure volumetric target: all components strain-controlled, origin AD path.
    r['args'][5] = csv([5., 4]+[v for _ in range(3) for v in [0, 1, .001]]+[0, 0, 0]*3)
    r['command'][r['command'].index('--segments')+1] = r['args'][5]
    r['checks'] = [assertion(['points', -1, 'state'], [1.3e6]*3+[0]*3, 1e-5, 0)]
    requests.append(r)
    # Uniaxial loading crosses q=0 smoothly; use the exactly soluble n1=n2=1 law.
    r = schedule_request('schedule-deviator-from-origin', [1e6]*3+[0]*3)
    r['args'][1] = csv(p)
    r['command'][r['command'].index('--parameters')+1] = csv(p)
    d2 = [.001, -.0005, -.0005, 0, 0, 0]
    r['args'][5] = csv([5., 4]+[v for value in d2 for v in [0, 1, value]])
    r['command'][r['command'].index('--segments')+1] = r['args'][5]
    expected = [(1e6 if i < 3 else 0)+2*p[1]*d2[i]*(1-math.exp(-lam*5))/lam for i in range(6)]
    r['checks'] = [assertion(['points', -1, 'state'], expected, 15., 0)]
    requests.append(r)
    # A same-instance successful replay follows every backend's failures.
    replay = copy.deepcopy(requests[0]);replay['id'] = 'rate-replay'
    requests.append(replay)
    data = {'study_id': 'power-creep-continuous-v1', 'policy': {
        'source_scope': 'Both components active, n>=1, no threshold events, dry zero-spin small strain',
        'rate_budget': '1e-7 Pa/s + 1e-11 relative',
        'midpoint_hold_budget': '0.06 Pa absolute', 'schedule_state_budget': '15 Pa absolute',
        'creep_strain_budget': '1e-10 absolute',
        'parity': '1e-8 absolute + 1e-10 relative for physical state/time/strain/rate/observables; diagnostic counts may differ',
        'gate_policy': 'Every request, expected return status, frozen check, diagnostic bound and source hash must pass. Never modify this study after observation.'},
        'model_sha256': sha(MODEL), 'requests': requests}
    out.write_text(dumps(data))
    print(f'Prepared {len(requests)} requests; no backend called.')


def schedule_request(name, z, stress=False):
    wire = [5., 4]+[v for _ in range(6) for v in [int(stress), 0, 0]]
    args = [MODEL_ID, csv(DEFAULT_P), csv(z), csv(ZERO), csv(ZERO), csv(wire), name,
            0., 1e-7, 1e-10, 1e-12, .1, 200000, 1e-10, 40]
    command = ['--mode', 'schedule', '--model', MODEL_ID, '--parameters', args[1],
               '--initial', args[2], '--initial-strain', args[3], '--initial-strain-rate', args[4],
               '--segments', args[5], '--segment-ids', name, '--start-time', '0',
               '--rtol', '1e-7', '--atol', '1e-10', '--min-time-step', '1e-12',
               '--max-time-step', '.1', '--max-substeps', '200000',
               '--nonlinear-tolerance', '1e-10', '--max-iterations', '40']
    return {'id': name, 'function': 'atlas_run_schedule', 'types': ['string']*7+['number']*8,
            'args': args, 'command': command, 'ok': True, 'checks': []}


def verify_freeze():
    freeze = read(PACKET / 'freeze.json')
    for name, digest in freeze['files'].items():
        if sha(PACKET / name) != digest:
            raise ValueError(f'Frozen artifact changed: {name}')
    if sha(__file__) != freeze['files']['frozen/source/tools/power_creep_study.py']:
        raise ValueError('Running study tool differs from its frozen copy')
    if sha(MODEL) != read(PACKET/'study.json')['model_sha256']:
        raise ValueError('Current runnable definition differs from frozen study')
    return freeze


def collect(solver, destination):
    verify_freeze()
    destination.mkdir(parents=True, exist_ok=True)
    study = read(PACKET/'study.json')
    for request in study['requests']:
        result = subprocess.run([str(solver.resolve())]+request['command'],
                                capture_output=True, text=True, timeout=60)
        (destination/(request['id']+'.stdout')).write_text(result.stdout)
        (destination/(request['id']+'.stderr')).write_text(result.stderr)
        (destination/(request['id']+'.process.json')).write_text(dumps({
            'returncode': result.returncode, 'command': [str(solver.resolve())]+request['command'],
            'binary_sha256': sha(solver)}))
        read(destination/(request['id']+'.stdout'))
    print(f'Retained {len(study["requests"])} native responses.')


def compare_number(actual, expected, atol, rtol):
    if isinstance(expected, list):
        if not isinstance(actual, list) or len(actual) != len(expected):
            raise AssertionError('array shape mismatch')
        for a, b in zip(actual, expected):compare_number(a, b, atol, rtol)
    else:
        if type(actual) not in (int, float) or not math.isfinite(actual):
            raise AssertionError(f'nonfinite/non-number: {actual}')
        if abs(actual-expected) > atol+rtol*abs(expected):
            raise AssertionError(f'{actual} != {expected}; budget {atol+rtol*abs(expected)}')


def physical(value):
    if isinstance(value, dict):
        return {k: physical(v) for k,v in value.items() if k in
                {'time', 'state', 'strain', 'strain_rate', 'observables', 'points', 'values', 'ok', 'side'}}
    if isinstance(value, list):return [physical(v) for v in value]
    return value


def parity(a, b):
    if isinstance(a, dict):
        if a.keys() != b.keys():raise AssertionError('parity keys differ')
        for k in a:parity(a[k], b[k])
    elif isinstance(a, list):
        if len(a) != len(b):raise AssertionError('parity array lengths differ')
        for x,y in zip(a,b):parity(x,y)
    elif type(a) in (float, int):compare_number(a,b,1e-8,1e-10)
    elif a != b:raise AssertionError('parity metadata differs')


def assess(directory, native=None):
    verify_freeze()
    study = read(PACKET/'study.json')
    results = []
    for r in study['requests']:
        try:
            d = read(directory/(r['id']+'.stdout'))
            if d.get('ok') is not r['ok']:raise AssertionError(d.get('message'))
            if 'catalogue_hash' in d and d['catalogue_hash'] != read(PACKET/'frozen/generated/models.json')['sha256']:
                raise AssertionError('wrong compiled catalogue identity')
            process = read(directory/(r['id']+'.process.json'))
            if process['returncode'] != (0 if r['ok'] else 1):raise AssertionError('process status mismatch')
            for c in r['checks']:
                v = d
                for key in c['path']:v = v[key]
                compare_number(v,c['value'],c['atol'],c['rtol'])
            if d.get('substeps',0) < r.get('minimum_substeps',0):raise AssertionError('late failure did not perform expected partial work')
            if r['ok']:
                for point in d.get('points',[]):
                    if point['nonlinear_residual_norm'] > 1e-10 or point['temporal_error_norm'] > 1:
                        raise AssertionError('schedule diagnostic bound exceeded')
                if d.get('temporal_error_norm',0) > 1:raise AssertionError('ODE diagnostic bound exceeded')
            if native:parity(physical(d),physical(read(native/(r['id']+'.stdout'))))
            results.append({'id':r['id'],'passed':True})
        except (AssertionError, KeyError, ValueError, OSError, TypeError) as exc:
            results.append({'id':r['id'],'passed':False,'failure':str(exc)})
    report = {'study_id':study['study_id'],'passed':all(r['passed'] for r in results),
              'requests':len(results),'results':results,'native_wasm_parity':bool(native),
              'model_sha256':study['model_sha256'],'study_sha256':sha(PACKET/'study.json'),
              'limitations':'Prospective bounded analytical/source/transaction qualification, not vendor or scientific admission.'}
    print(dumps(report),end='')
    if not report['passed']:raise SystemExit(1)


def main():
    p=argparse.ArgumentParser()
    p.add_argument('mode', choices=['prepare','native','assess','verify-freeze'])
    p.add_argument('--solver', type=Path)
    p.add_argument('--output', type=Path)
    p.add_argument('--native', type=Path)
    a=p.parse_args()
    if a.mode=='prepare':prepare()
    elif a.mode=='verify-freeze':verify_freeze();print('Exact freeze verified.')
    elif a.mode=='native':collect(a.solver,a.output)
    else:assess(a.output,a.native)


if __name__=='__main__':main()
