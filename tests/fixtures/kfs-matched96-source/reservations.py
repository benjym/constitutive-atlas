"""Keep reserved evaluation responses out of paper development commands."""
from .common import ROOT, read_json

POLICY_PATH = ROOT/'paper/study/reservations.json'


def load_policy(path=POLICY_PATH):
    policy = read_json(path)
    if policy.get('paper_reservation_version') != 1 or policy.get('state') != 'reserved_before_additional_response_analysis':
        raise ValueError('unsupported reservation policy; no final-evaluation release is implemented')
    rows = policy['experiments']
    if len({r['id'] for r in rows}) != len(rows):
        raise ValueError('duplicate reservation ID')
    if any(r['role'] not in ('development', 'reserved_final') for r in rows):
        raise ValueError('unknown experiment role')
    return policy


def assert_development_ids(ids, policy=None):
    policy = load_policy() if policy is None else policy
    roles = {r['id']: r['role'] for r in policy['experiments']}
    for identifier in ids:
        if roles.get(identifier) == 'reserved_final':
            raise ValueError(f'{identifier}: reserved final evaluation response cannot be used in development')
        if identifier.startswith('KFS-') and identifier not in roles:
            raise ValueError(f'{identifier}: assign a study role before development use')


def select_members(names, ids, policy=None):
    """Resolve allowlisted IDs using member names, before reading response bytes."""
    from pathlib import PurePosixPath
    import re
    assert_development_ids(ids, policy)
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate requested test')
    selected = {}
    for name in names:
        base = PurePosixPath(name).name
        if re.fullmatch(r'TMD[0-9]+\.dat', base, re.IGNORECASE):
            identifier = 'KFS-'+base[:-4].upper()
            if identifier in ids:
                if identifier in selected:
                    raise ValueError(f'{identifier}: ambiguous archive member')
                selected[identifier] = name
    if set(selected) != set(ids):
        raise ValueError('requested development tests are missing from archive')
    return selected
