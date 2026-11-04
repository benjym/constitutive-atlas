#!/usr/bin/env python3
"""Portable fresh-build Hill behavioral qualifier; immutable references stay read-only."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / 'docs/ingestion/hill-abaqus2025/execution-v1'
LOW_NEWTON = '1e-11,1e-6,1,0,1,0'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--solver', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    # Never permit accidental overwrite of reviewed evidence, even through symlinks.
    if output == EVIDENCE.resolve() or EVIDENCE.resolve() in output.parents:
        parser.error('output must not be inside immutable execution-v1')
    output.mkdir(parents=True, exist_ok=True)
    refs = json.loads((EVIDENCE / 'references.json').read_text())
    negatives = json.loads((EVIDENCE / 'negative-requests.json').read_text())
    frozen = json.loads((EVIDENCE.parent / 'ci-v1/frozen-inputs.json').read_text())
    for name, expected in frozen.items():
        assert digest(ROOT / name) == expected, 'immutable qualifier input changed: ' + name
    assert len(refs['cases']) == 31 and sum(len(c['increments']) for c in refs['cases']) == 41
    model = ROOT / 'models/research/hill' / (refs['model'] + '.json')
    assert digest(model) == refs['model_sha256'], 'source model differs from frozen references'
    spec = importlib.util.spec_from_file_location('hill_frozen_assessor', EVIDENCE / 'qualify.py')
    assessor = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(assessor)
    calls = []

    def save(name, value):
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False) + '\n')

    def call(parameters, initial, strain, settings=None):
        csv = lambda values: ','.join(format(x, '.17g') for x in values)
        command = [str(args.solver.resolve()), '--mode', 'integrate', '--model', refs['model'],
                   '--parameters', csv(parameters), '--initial', csv(initial), '--strain', csv(strain),
                   '--integration-settings', settings or refs['settings']]
        result = subprocess.run(command, capture_output=True, text=True, timeout=60)
        calls.append({'command': command, 'returncode': result.returncode,
                      'stdout': result.stdout, 'stderr': result.stderr})
        save('native-calls.json', calls)  # preserve failures before parsing/assessment
        return json.loads(result.stdout, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))

    raw = []
    for case in refs['cases']:
        runs = []
        for _ in range(2):
            state = case['initial']
            rows = []
            for increment in case['increments']:
                row = call(case['parameters'], state, increment)
                rows.append(row)
                if row.get('ok') is not True:
                    break
                state = row['state']
            runs.append(rows)
        raw.append({'id': case['id'], 'runs': runs})
        save('native-raw.json', raw)
    assessment = assessor.assess(raw)
    save('native-assessment.json', assessment)

    good = next(case for case in refs['cases'] if case['id'] == 'elastic-0--1')
    valid = lambda: call(good['parameters'], good['initial'], good['increments'][0])
    baseline = valid()
    assert baseline['ok'] is True
    negative_rows = []
    for case in negatives['cases']:
        failed = call(case['parameters'], case['initial'], case['strain'])
        recovered = valid()
        negative_rows.append({'id': case['id'], 'failed': failed, 'recovered': recovered})
        save('native-negative-raw.json', negative_rows)
        assert failed['ok'] is False, case['id']
        if case['id'] == 'outside-yield':
            assert failed['state'] == case['initial'], 'admissibility failure must roll back'
        else:
            assert 'state' not in failed, 'parameter prevalidation must reject before state response'
        assert recovered == baseline, 'post-rejection recovery differs'

    plastic = next(case for case in refs['cases'] if case['id'] == 'mixed-nonproportional')
    before = call(plastic['parameters'], plastic['initial'], plastic['increments'][0])
    failed = call(plastic['parameters'], plastic['initial'], plastic['increments'][0], LOW_NEWTON)
    after = call(plastic['parameters'], plastic['initial'], plastic['increments'][0])
    save('native-rollback-raw.json', {'before': before, 'failed': failed, 'after': after})
    assert before['ok'] is True and failed['ok'] is False
    assert failed['state'] == plastic['initial'], 'material failure must return complete parent'
    assert after == before, 'post-material-failure recovery differs'
    report = dict(assessment, qualification='fresh-build bounded behavior; not new scientific approval',
                  cases=len(raw), increments=sum(len(c['increments']) for c in refs['cases']),
                  negative_cases=len(negative_rows), full_state_rollback=True, exact_recovery=True,
                  solver_sha256=digest(args.solver.resolve()), model_sha256=digest(model),
                  references_sha256=digest(EVIDENCE / 'references.json'),
                  policy_sha256=digest(EVIDENCE / 'POLICY.md'),
                  negative_requests_sha256=digest(EVIDENCE / 'negative-requests.json'),
                  assessor_sha256=digest(EVIDENCE / 'qualify.py'))
    save('report.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
