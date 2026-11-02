"""Whole-test development allocation checks; no response loading or release API."""
import re


def require(condition, message):
    if not condition:
        raise ValueError(message)


def identifiers(value, label):
    require(isinstance(value, list) and bool(value), label + ': nonempty whole-test ID list required')
    require(all(isinstance(v, str) and bool(v) for v in value), label + ': IDs must be nonempty strings')
    require(len(set(value)) == len(value), label + ': duplicate whole-test ID')
    return set(value)


def validate_allocation(plan, policy, *, policy_sha256):
    """Validate decoded metadata against the digest computed from policy bytes.

    This does not certify model applicability, prior exposure or a study freeze.
    Callers must compute policy_sha256 from the policy bytes they decoded.
    """
    keys = {'schema_version', 'kind', 'id', 'phase', 'grouping_unit',
            'evaluation_claim', 'calibration_packages', 'evaluation_ids',
            'reservation_policy', 'limitations'}
    require(isinstance(plan, dict) and set(plan) == keys, 'unsupported allocation fields; row/sample selectors are not accepted')
    for key, value in [('schema_version','0.1'), ('kind','whole-test-study-allocation'),
                       ('phase','development'), ('grouping_unit','whole_test'),
                       ('evaluation_claim','previously_exposed_development')]:
        require(plan[key] == value, 'unsupported ' + key)
    require(isinstance(plan['id'], str) and re.fullmatch(r'[a-z][a-z0-9-]*', plan['id']) is not None, 'invalid allocation ID')
    limitations = plan['limitations']
    require(isinstance(limitations, list) and bool(limitations)
            and all(isinstance(v, str) and bool(v) for v in limitations), 'explicit limitations required')
    binding = plan['reservation_policy']
    require(isinstance(binding, dict) and set(binding) == {'id','sha256'}, 'exact reservation-policy binding required')
    require(isinstance(binding['sha256'], str) and re.fullmatch(r'[a-f0-9]{64}', binding['sha256']) is not None, 'invalid reservation-policy SHA-256')
    require(binding['sha256'] == policy_sha256, 'reservation-policy bytes changed')
    require(isinstance(policy, dict) and type(policy.get('paper_reservation_version')) is int
            and policy['paper_reservation_version'] == 1, 'unsupported reservation-policy version')
    require(isinstance(binding['id'], str) and bool(binding['id']) and policy.get('id') == binding['id'], 'reservation-policy identity mismatch')
    experiments = policy.get('experiments')
    require(isinstance(experiments, list) and bool(experiments), 'reservation experiment registry required')
    roles = {}
    for entry in experiments:
        require(isinstance(entry, dict) and isinstance(entry.get('id'), str) and bool(entry['id']), 'invalid reservation experiment ID')
        name = entry['id']
        require(name not in roles, 'duplicate reservation experiment ID: ' + name)
        require(entry.get('role') in ('development', 'reserved_final'), 'unsupported reservation role: ' + name)
        roles[name] = entry['role']
    packages = plan['calibration_packages']
    require(isinstance(packages, dict) and bool(packages), 'nonempty calibration packages required')
    calibration = set()
    for name, ids in packages.items():
        require(isinstance(name, str) and re.fullmatch(r'[a-z][a-z0-9_-]*', name) is not None, 'invalid calibration package name')
        calibration.update(identifiers(ids, 'calibration package ' + name))
    evaluation = identifiers(plan['evaluation_ids'], 'evaluation')
    require(not calibration & evaluation, 'calibration/evaluation whole-test overlap: ' + ', '.join(sorted(calibration & evaluation)))
    for name in sorted(calibration | evaluation):
        require(name in roles, 'unknown whole-test ID: ' + name)
        require(roles[name] == 'development', 'reserved whole-test ID excluded: ' + name)
    return {'kind':'whole-test-allocation-check', 'id':plan['id'], 'passed':True,
            'phase':plan['phase'], 'evaluation_claim':plan['evaluation_claim'],
            'calibration_package_sizes':{name:len(ids) for name,ids in packages.items()},
            'calibration_union_ids':sorted(calibration), 'evaluation_ids':plan['evaluation_ids'],
            'reservation_policy_id':binding['id'], 'reservation_policy_sha256':policy_sha256,
            'reserved_ids_excluded':sorted(name for name,role in roles.items() if role == 'reserved_final'),
            'response_files_read':0, 'final_evaluation_release':False,
            'scientific_admission':False, 'limitations':plan['limitations']}
