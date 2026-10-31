"""Audit two existing development snapshots; never build, fit or call a solver.

Run from the repository root. Requires the private/local paper pilot snapshots
and a diagnostics directory regenerated with the existing paper report command.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read(path):
    return json.loads(path.read_text())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--diagnostics', type=Path, required=True)
    args = parser.parse_args()
    root = Path.cwd()
    summary = read(args.diagnostics/'summary.json')
    require(summary == read(root/'paper/results/diagnostics-matched/summary.json'),
            'Regenerated summary differs from the retained development result')
    runs = []
    for budget, summary_key in ((96, 'report_sha256'), (384, 'comparison_sha256')):
        directory = root/f'paper/results/pilot-matched{budget}'
        report = read(directory/'report.json')
        require(digest(directory/'report.json') == summary[summary_key], 'Report hash mismatch')
        require(report['input_integrity'] == 'verified_unchanged', 'Incomplete historical run')
        require(report['config']['optimizer']['max_evaluations'] == budget, 'Budget mismatch')
        checked = 0
        for relative, expected in report['code_sha256'].items():
            require(digest(directory/'source'/relative) == expected, f'Code snapshot changed: {relative}')
            checked += 1
        for mid, expected in report['model_sha256'].items():
            require(digest(directory/'models'/f'{mid}.json') == expected, f'Model snapshot changed: {mid}')
            checked += 1
        require(digest(directory/'solver/atlas_solver') == report['solver_sha256'], 'Executable changed')
        require(digest(directory/'reservation-policy.json') == report['reservation_sha256'], 'Reservations changed')
        checked += 2
        policy = read(directory/'reservation-policy.json')
        roles = {e['id']: e['role'] for e in policy['experiments']}
        config = report['config']
        calibration_ids = set().union(*map(set, config['packages'].values()))
        evaluation_ids = set(config['evaluation_ids'])
        require(not calibration_ids & evaluation_ids, 'Calibration/evaluation overlap')
        for eid, expected in report['experiment_sha256'].items():
            require(roles[eid] == 'development', f'Reserved data included: {eid}')
            require(digest(directory/'experiments'/f'{eid}.json') == expected, f'Data snapshot changed: {eid}')
            checked += 1
        expected_pairs = {(m['id'], p) for m in config['models'] for p in config['packages']}
        require({(c['model'], c['package']) for c in report['calibrations']} == expected_pairs,
                'Calibration pairs missing')
        selected = [p for p in report['predictions'] if p.get('selected')]
        for mid, package in expected_pairs:
            predictions = [p for p in selected if (p['model'], p['package']) == (mid, package)]
            require(len(predictions) == len(evaluation_ids)
                    and {p['experiment_id'] for p in predictions} == evaluation_ids,
                    'Selected prediction coverage differs')
        require(all(p['status'] == 'success' for p in report['predictions']), 'Failed evaluation present')
        runs.append(dict(budget_per_start=budget, report_sha256=digest(directory/'report.json'),
                         snapshot_files_verified=checked, calibration_pairs=len(expected_pairs),
                         optimizer_starts=sum(len(c['fits']) for c in report['calibrations']),
                         selected_evaluations=len(selected), all_start_evaluations=len(report['predictions']),
                         failed_calibration_vectors=sum(not t['completed'] for c in report['calibrations']
                                                        for f in c['fits'] for t in f['trace']),
                         calibration_ids=sorted(calibration_ids), evaluation_ids=sorted(evaluation_ids)))
    archived = root/'paper/results/pilot-matched96/models/hypoplastic-sand-vw96.json'
    current = root/'models/hypoplastic-sand-vw96.json'
    old, new = read(archived), read(current)
    require(list(old['parameters']) == list(new['parameters']), 'VW96 parameter order changed')
    labels = [name for name in old['parameters']
              if old['parameters'][name].get('label') != new['parameters'][name].get('label')]
    stripped = []
    for model in (old, new):
        model = copy.deepcopy(model)
        model.pop('sources')
        for parameter in model['parameters'].values():
            parameter.pop('label', None)
        stripped.append(model)
    require(stripped[0] == stripped[1], 'VW96 has changes beyond parameter labels and source metadata')
    definition_review = dict(archived_sha256=digest(archived), current_sha256=digest(current),
                             changed_parameter_labels=labels, source_metadata_changed=old['sources'] != new['sources'],
                             all_other_definition_fields_equal=True, engine_equivalence_claimed=False)
    print(json.dumps(dict(id='kfs-development-checkpoint-v1', scope='saved snapshot integrity, diagnostic regeneration and VW96 definition metadata crosswalk only',
                         scientific_admission=False, new_solver_calls=0, new_fits=0,
                         vw96_definition_review=definition_review,
                         regenerated_summary_matches_retained=True,
                         summary_sha256=digest(args.diagnostics/'summary.json'), runs=runs), indent=2))


if __name__ == '__main__':
    main()
