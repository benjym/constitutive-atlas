"""Check representative schedules with the original independent assessors.

The manual research jobs still run the complete corpora. This selection keeps
public paths, refinement, restart, rollback, invalid input and recovery in CI.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
STUDIES = {
    'bingham': ('bingham-comsol63/execution-v5', {
        'zero-hold', 'public-relaxation', 'public-creep', 'public-rate',
        'noncoaxial-history', 'actual-state-restart', 'recovery-late-budget-rollback',
        'recovery-missing-state',
    }),
    'perzyna': ('perzyna-comsol63/execution-v2', {
        'public-relaxation', 'public-creep', 'public-rate', 'hydrostatic-rate',
        'noncoaxial-reversal-hold-n2', 'restart-parent', 'restart-child',
        'post-invalid-recovery',
    }),
}
COMMON = {'refinement-coarse', 'refinement-fine', 'late-budget-rollback', 'missing-state'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', choices=STUDIES)
    parser.add_argument('solver', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    folder, extra = STUDIES[args.study]
    base = ROOT / 'docs/ingestion' / folder
    module = importlib.util.spec_from_file_location('reference_study', base / 'study.py')
    study = importlib.util.module_from_spec(module)
    module.loader.exec_module(study)
    selected = COMMON | extra
    cases = [case for case in json.loads((base / 'cases.json').read_text())['cases'] if case['id'] in selected]
    if len(cases) != len(selected) or {c['id'] for c in cases} != selected:
        raise ValueError('Missing or duplicate selected reference schedule')
    args.output.mkdir(parents=True)
    rows = []
    for source in cases:
        case = study.resolve(source, rows)
        print(args.study + ': ' + case['id'], flush=True)
        row = {'id': case['id'], 'request': {key: case[key] for key in ('call', 'types', 'args', 'argv')},
               'calls': []}
        for _ in range(2):
            proc = subprocess.run([str(args.solver.resolve()), *case['argv']],
                                  capture_output=True, text=True, timeout=180)
            row['calls'].append({'returncode': proc.returncode, 'stdout': proc.stdout, 'stderr': proc.stderr})
        rows.append(row)
        (args.output / 'raw.json').write_text(json.dumps(rows) + '\n')
    report = study.assess(cases, rows)
    (args.output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f"{args.study}: {report['cases']} reference schedules passed")


if __name__ == '__main__':
    main()
