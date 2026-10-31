"""Construct two qualified initialization-metadata scenarios; no model execution."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from tools.check_study_parameters import check as check_parameters
from tools.strict_observation_json import loads
HERE = Path(__file__).resolve().parent


def sha(content):
    return hashlib.sha256(content).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def audit():
    content = (HERE/'policy.json').read_bytes()
    freeze = loads((HERE/'freeze.json').read_bytes())
    require(sha(content) == freeze['policy_sha256'], 'policy bytes changed')
    require(sha((HERE/'audit.py').read_bytes()) == freeze['audit_sha256'], 'audit bytes changed')
    policy = loads(content)
    base = ROOT/'studies/kfs-development-v1'
    checked = check_parameters(base/'parameters-v1/parameter-policy.json',base/'allocation.json',
                               base/'reservation-policy.json',base/'parameters-v1/models')
    for path, expected in policy['input_sha256'].items():
        require(sha((ROOT/path).read_bytes()) == expected, 'input bytes changed: '+path)
    source = policy['source']
    require(sha((ROOT/source['private_path']).read_bytes()) == source['sha256'], 'primary source changed')
    allocation = loads((ROOT/policy['allocation']).read_bytes())
    ids = set(allocation['evaluation_ids']).union(*map(set,allocation['calibration_packages'].values()))
    require(ids == set(policy['experiment_sha256']), 'scenario coverage differs from allocation')
    require('KFS-TMD13' in allocation['calibration_packages']['density3'] and
            'KFS-TMD13' not in allocation['calibration_packages']['pressure3'] and
            {'KFS-TMD12','KFS-TMD14'} <= set(allocation['evaluation_ids']), 'affected roles changed')
    conflicts = loads((ROOT/'paper/study/metadata_conflicts.json').read_bytes())
    conflicts = {r['experiment_id']:r for r in conflicts['experiments']}
    overrides = policy['scenarios']['original_table_disputed_e0']['void_ratio_overrides']
    require(set(overrides) == {'KFS-TMD12','KFS-TMD13','KFS-TMD14'}, 'disputed scenario changed')
    for eid, value in overrides.items():
        require(value == conflicts[eid]['original_void_ratio'], 'original-table value differs')
    report = loads((ROOT/'paper/results/pilot-matched96/report.json').read_bytes())
    require(report['config']['packages'] == allocation['calibration_packages'] and
            report['config']['evaluation_ids'] == allocation['evaluation_ids'], 'historical allocation differs')
    records = []
    for eid in sorted(ids):
        # Whole files are hashed/decoded; response rows are not analyzed or exported.
        content = (ROOT/'paper/results/pilot-matched96/experiments'/(eid+'.json')).read_bytes()
        require(sha(content) == policy['experiment_sha256'][eid] == report['experiment_sha256'][eid],
                'experiment bytes changed: '+eid)
        experiment = loads(content)
        require(experiment['id'] == eid and experiment['protocol'] == 'drained-triaxial', 'wrong experiment')
        initial = experiment['initial']
        stress, e = initial['effective_stress'], initial['void_ratio']
        require(len(stress) == 6 and all(type(v) in (int,float) and math.isfinite(v) for v in stress),
                'invalid measured effective stress')
        require(type(e) in (int,float) and math.isfinite(e) and e > 0, 'invalid file void ratio')
        if eid in overrides:
            require(e == conflicts[eid]['file_initial_void_ratio'], 'conflict register/file disagreement')
            require(round(e,3) == conflicts[eid]['later_void_ratio'], 'later rounded value differs')
        alternative = overrides.get(eid,e)
        records.append({'experiment_id':eid,
                        'calibration_packages':[p for p,members in allocation['calibration_packages'].items() if eid in members],
                        'evaluation':eid in allocation['evaluation_ids'],
                        'file_initial':{'sigma':stress,'e':e},
                        'original_table_disputed_e0':{'sigma':list(stress),'e':alternative},
                        'delta_e':alternative-e})
    changed = {r['experiment_id'] for r in records if r['delta_e'] != 0}
    require(changed == set(overrides), 'unexpected scenario differences')
    require(all(r['file_initial']['sigma'] == r['original_table_disputed_e0']['sigma'] for r in records),
            'scenario changed recorded stress')
    # This binds only the existing base-law study, not more complex history states.
    for mid in report['model_sha256']:
        content = (base/'parameters-v1/models'/(mid+'.json')).read_bytes()
        require(sha(content) == report['model_sha256'][mid], 'definition differs')
        model = loads(content)
        fields = model['state']
        require([(f['name'],f['shape']) for f in fields[:2]] == [('sigma','sym'),('e','scalar')],
                'unsupported state binding')
        require(all(f['name'] == 'gamma' and f['shape'] == 'scalar' and f.get('transient') is True
                    for f in fields[2:]), 'unprovided history state')
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],
            'audit_sha256':freeze['audit_sha256'],'parameter_accounting_id':checked['id'],
            'experiments':len(records),'scenarios':2,'initial_state_assignments':2*len(records),
            'changed_void_ratio_ids':sorted(changed),'changed_stress_components':0,
            'new_fits':0,'new_solver_calls':0,'scientific_admission':False,
            'source_disagreement_resolved':False,'records':records}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    result = audit()
    with args.output.open('x') as stream:
        stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'records'},indent=2))


if __name__ == '__main__':main()
