"""Rescore a pinned saved development run; never execute models or fit parameters."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from atlas.curve_metrics import METHOD, compare_acquisition_linear
from tools.check_study_parameters import check as check_parameters
from tools.strict_observation_json import loads

HERE = Path(__file__).resolve().parent


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def close(a, b, policy):
    return math.isclose(a, b, rel_tol=policy['relative_score_tolerance'],
                        abs_tol=policy['absolute_score_tolerance'])


def window(experiment, policy):
    require(experiment['protocol'] == 'drained-triaxial', 'wrong experimental protocol')
    stress = experiment['initial']['effective_stress']
    require(len(stress) == 6 and all(type(v) in (int, float) and math.isfinite(v)
                                   for v in stress), 'invalid initial stress')
    void = experiment['initial']['void_ratio']
    require(type(void) in (int, float) and math.isfinite(void) and void > 0,
            'invalid file initial void ratio')
    pressure = math.fsum(stress[:3])/3
    require(pressure > 0, 'nonpositive initial pressure')
    rows = []
    for row in experiment['rows']:
        x = row['axial_strain']
        require(type(x) in (int, float) and math.isfinite(x) and x >= 0,
                'invalid axial-strain coordinate')
        if x > policy['maximum_axial_strain']:
            break
        rows.append(row)
    require(len(rows) >= 2 and rows[0]['axial_strain'] == 0,
            'window must start at zero with two observations')
    return rows, {'q': pressure, 'volumetric_strain': policy['volumetric_strain_scale']}


def compare_channel(rows, prediction, channel, scale, policy):
    new = compare_acquisition_linear(rows, prediction, channel, scale)
    saved = prediction['metrics'][channel]
    require(saved['weighting'] == policy['legacy_method'] and saved['scale'] == scale,
            'legacy method or scale mismatch')
    require(saved['observations'] == len(rows) and
            saved['total_absolute_axial_strain_travel'] ==
            sum(abs(b['axial_strain']-a['axial_strain']) for a,b in zip(rows,rows[1:])),
            'legacy window mismatch')
    errors = [(p[channel]-r[channel])/scale for r,p in zip(rows,prediction['points'])]
    weights = [abs(b['axial_strain']-a['axial_strain']) for a,b in zip(rows,rows[1:])]
    travel = math.fsum(weights)
    legacy = math.fsum(w*(a*a+b*b)/2 for w,a,b in zip(weights,errors,errors[1:]))/travel
    gap = math.fsum(w*(a-b)**2/6 for w,a,b in zip(weights,errors,errors[1:]))/travel
    require(close(legacy, saved['scaled_mse'], policy), 'saved legacy score mismatch')
    require(close(legacy-new['scaled_mse'], gap, policy), 'quadrature-gap identity failed')
    return {'legacy_scaled_mse': legacy, 'new': new,
            'analytic_scaled_mse_gap': gap}


def assess(report, experiments, policy):
    require(policy['new_method'] == METHOD, 'new metric identity mismatch')
    config = report['config']
    require(report['input_integrity'] == 'verified_unchanged', 'historical run incomplete')
    require(config['packages'] == policy['packages'] and
            config['evaluation_ids'] == policy['evaluation_ids'] and
            config['maximum_axial_strain'] == policy['maximum_axial_strain'] and
            config['objective']['channels'] == policy['channels'] and
            config['objective']['q_scale'] == policy['q_scale'] and
            config['objective']['volumetric_strain_scale'] == policy['volumetric_strain_scale'],
            'historical task differs from frozen diagnostic')
    require(report['model_sha256'] == policy['model_sha256'], 'model identities differ')
    require(set(experiments) == set(policy['evaluation_ids']), 'experiment coverage mismatch')
    require(all(e['id'] == eid for eid,e in experiments.items()), 'experiment ID mismatch')
    selected = [p for p in report['predictions'] if p.get('selected') is True]
    expected = {(mid, package, eid) for mid in policy['model_sha256']
                for package in policy['packages'] for eid in policy['evaluation_ids']}
    keys = [(p['model'],p['package'],p['experiment_id']) for p in selected]
    require(len(keys) == len(set(keys)) and set(keys) == expected,
            'duplicate or missing selected prediction')
    calibrated = {}
    for entry in report['calibrations']:
        key = (entry['model'],entry['package'])
        require(key not in calibrated, 'duplicate calibration entry')
        fits = [f for f in entry['fits'] if f['seed'] == entry['selected_seed']]
        require(len(fits) == 1 and fits[0]['best']['completed'] is True,
                'missing successful selected fit')
        calibrated[key] = (entry['selected_seed'], fits[0]['best']['parameters'])
    require(set(calibrated) == {(m,p) for m,p,e in expected}, 'calibration coverage mismatch')
    records = []
    for prediction in selected:
        mid, package, eid = prediction['model'], prediction['package'], prediction['experiment_id']
        seed, parameters = calibrated[(mid,package)]
        require(prediction['seed'] == seed and prediction['parameters'] == parameters,
                'prediction parameters differ from locked selected fit')
        rows, scales = window(experiments[eid], policy)
        channels = {c: compare_channel(rows,prediction,c,scales[c],policy)
                    for c in policy['channels']}
        records.append({'model':mid, 'package':package, 'experiment_id':eid,
                        'channels':channels})
    aggregates, contrasts = [], []
    for mid in policy['model_sha256']:
        values = {}
        for package in policy['packages']:
            matched = [r for r in records if (r['model'],r['package']) == (mid,package)]
            old = math.sqrt(math.fsum(c['legacy_scaled_mse'] for r in matched
                                     for c in r['channels'].values())/(len(matched)*len(policy['channels'])))
            new = math.sqrt(math.fsum(c['new']['scaled_mse'] for r in matched
                                     for c in r['channels'].values())/(len(matched)*len(policy['channels'])))
            values[package] = (old,new)
            aggregates.append({'model':mid, 'package':package,
                               'legacy_root_scaled_mse':old, 'new_root_scaled_mse':new,
                               'relative_change':new/old-1 if old else None})
        contrasts.append({'model':mid,
                          'legacy_density_minus_pressure':values['density3'][0]-values['pressure3'][0],
                          'new_density_minus_pressure':values['density3'][1]-values['pressure3'][1]})
    return {'id':policy['id'], 'scope':policy['phase'], 'new_method':METHOD,
            'new_fits':0, 'new_solver_calls':0, 'scientific_admission':False,
            'selected_predictions':len(records), 'channel_comparisons':len(records)*len(policy['channels']),
            'aggregates':aggregates, 'contrasts':contrasts, 'records':records}


def run(root=ROOT, here=HERE):
    policy_bytes = (here/'policy.json').read_bytes()
    freeze = loads((here/'freeze.json').read_bytes())
    require(sha(policy_bytes) == freeze['policy_sha256'], 'frozen policy changed')
    require(sha((here/'assess.py').read_bytes()) == freeze['assessor_sha256'], 'frozen assessor changed')
    policy = loads(policy_bytes)
    # Metadata gates precede access to the saved report or experiment responses.
    base = root/'studies/kfs-development-v1'
    check_parameters(base/'parameters-v1/parameter-policy.json', base/'allocation.json',
                     base/'reservation-policy.json', base/'parameters-v1/models')
    for relative, expected in policy['input_sha256'].items():
        require(sha((root/relative).read_bytes()) == expected, 'input hash mismatch: '+relative)
    report = loads((root/policy['report']).read_bytes())
    allocation = loads((base/'allocation.json').read_bytes())
    require(policy['evaluation_ids'] == allocation['evaluation_ids'] and
            policy['packages'] == allocation['calibration_packages'], 'allocation changed')
    experiments = {}
    for eid, expected in policy['experiment_sha256'].items():
        require(eid in allocation['evaluation_ids'], 'experiment not authorized for this diagnostic')
        content = (root/'paper/results/pilot-matched96/experiments'/(eid+'.json')).read_bytes()
        require(sha(content) == expected == report['experiment_sha256'][eid], 'experiment hash mismatch')
        experiments[eid] = loads(content)
    result = assess(report, experiments, policy)
    result['policy_sha256'] = sha(policy_bytes)
    result['assessor_sha256'] = freeze['assessor_sha256']
    result['input_sha256'] = policy['input_sha256']
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run()
    with args.output.open('x') as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('selected_predictions','channel_comparisons','aggregates','contrasts')},indent=2))


if __name__ == '__main__':
    main()
