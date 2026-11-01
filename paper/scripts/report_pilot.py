"""Generate local development diagnostics, never a publication leaderboard."""
import argparse
import copy
import json
import math
import os
from pathlib import Path
import sys

PAPER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAPER))
os.environ.setdefault('MPLCONFIGDIR', str(PAPER/'.cache/matplotlib'))

from analysis.common import ROOT, digest, read_json, write_json
from analysis.reservations import assert_development_ids

LABELS = {'linear-elastic': 'Elastic baseline', 'drucker-prager': 'Drucker–Prager',
          'hypoplastic-sand-vw96': 'Hypoplasticity (4 fitted constants)'}
COLORS = {'linear-elastic': '#8a6b32', 'drucker-prager': '#466e9c', 'hypoplastic-sand-vw96': '#238276'}


def display_root(score):
    return 'incomplete' if score is None else f'{math.sqrt(score):.6g}'


def evaluation_score(predictions, expected_ids=None):
    if expected_ids is not None:
        ids = [p.get("experiment_id") for p in predictions]
        if len(ids) != len(expected_ids) or set(ids) != set(expected_ids):
            return None
    if not predictions or any(p.get('status') != 'success' or not p.get('metrics') for p in predictions):
        return None
    return sum(sum(m['scaled_mse'] for m in p['metrics'].values())/len(p['metrics'])
               for p in predictions)/len(predictions)


def summaries(report):
    rows = []
    config = report['config']
    for calibration in report['calibrations']:
        mid, package = calibration['model'], calibration['package']
        fits = calibration['fits']
        chosen = next(f for f in fits if f['seed'] == calibration['selected_seed'])
        selected = [p for p in report['predictions'] if p['model'] == mid and p['package'] == package and p.get('selected')]
        scores = []
        for fit in fits:
            predictions = [p for p in report['predictions'] if p['model'] == mid and p['package'] == package and p.get('seed') == fit['seed']]
            scores.append({'seed': fit['seed'], 'evaluation_objective': evaluation_score(predictions, config['evaluation_ids'])})
        model = next(m for m in config['models'] if m['id'] == mid)
        boundaries = []
        for name, definition in model['fit'].items():
            lo, hi = definition['bounds']
            value = chosen['best']['parameters'][name]
            if min(abs(value-lo), abs(value-hi))/(hi-lo) < 1e-6:
                boundaries.append(name)
        rows.append({'model': mid, 'package': package, 'selected_seed': chosen['seed'],
                     'calibration_objective': chosen['best']['objective'],
                     'selected_evaluation_objective': evaluation_score(selected, config['evaluation_ids']),
                     'start_evaluation_scores': scores,
                     'termination_counts': {reason: sum(f['termination'] == reason for f in fits)
                                            for reason in ('budget_limit', 'step_threshold')},
                     'attempted_parameter_vectors': sum(f['evaluation_count'] for f in fits),
                     'failed_parameter_vectors': sum(not t['completed'] for f in fits for t in f['trace']),
                     'selected_parameters_at_bounds': boundaries,
                     'evaluation_completed': sum(p.get('status') == 'success' for p in selected),
                     'evaluation_scheduled': len(config['evaluation_ids'])})
    return rows


def plots(report, rows, output, comparison=None, report_dir=None, plot_package=None):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    config = report['config']
    assert_development_ids(config['evaluation_ids'])
    package = plot_package or list(config['packages'])[-1]
    if package not in config['packages']:
        raise ValueError('unknown response-plot calibration package')
    identifiers = config['evaluation_ids']
    replay = 'evaluation_protocol' in config
    curve_artifacts = []
    for offset in range(0, len(identifiers), 3):
        page_ids = identifiers[offset:offset+3]
        fig, axes = plt.subplots(2, len(page_ids), figsize=(5.1*len(page_ids), 7),
                                 squeeze=False, layout='constrained')
        for column, eid in enumerate(page_ids):
            source = report_dir/'experiments'/f'{eid}.json' if report_dir is not None else Path('')
            if not source.is_file():
                source = ROOT/config['experiment_paths'][eid]
            if digest(source) != report['experiment_sha256'][eid]:
                raise ValueError('observations changed since pilot')
            experiment = read_json(source)
            assert_development_ids([experiment['id']])
            if experiment['id'] != eid:
                raise ValueError('plotted observation identity mismatch')
            measured = []
            for observation in experiment['rows']:
                if observation['axial_strain'] > config['maximum_axial_strain']:
                    break
                measured.append(observation)
            def coordinates(points):
                if not replay:
                    return [p['axial_strain']*100 for p in points]
                travel = [0.]
                for a, b in zip(points, points[1:]):
                    travel.append(travel[-1]+abs(b['axial_strain']-a['axial_strain'])*100)
                return travel
            for row, (channel, factor, label) in enumerate([
                    ('q', .001, 'Deviator stress (kPa)'),
                    ('volumetric_strain', 100, 'Volumetric strain (%)')]):
                ax = axes[row, column]
                ax.scatter(coordinates(measured), [r[channel]*factor for r in measured],
                           s=9, color='#333333', label='Measured', zorder=4)
                for prediction in report['predictions']:
                    if prediction['package'] != package or prediction.get('experiment_id') != eid or not prediction.get('selected'):
                        continue
                    mid = prediction['model']
                    if prediction['status'] != 'success':
                        ax.text(.03, .95-.06*len(ax.texts), f'{LABELS.get(mid,mid)}: incomplete',
                                transform=ax.transAxes, va='top', fontsize=8)
                        continue
                    points = prediction['points']
                    ax.plot(coordinates(points), [p[channel]*factor for p in points],
                            color=COLORS.get(mid), label=LABELS.get(mid,mid), linewidth=1.6)
                ax.set(xlabel='Absolute axial-strain travel (%)' if replay else 'Axial strain (%)', ylabel=label)
                if row == 0:
                    ax.set_title(eid)
                ax.grid(alpha=.2)
                ax.spines[['top', 'right']].set_visible(False)
        axes[0, 0].legend(frameon=False, fontsize=8)
        fig.suptitle(f'Development evaluation after {package} calibration\nPreviously inspected tests; partial hypoplastic calibration', fontsize=12)
        filename = 'development-curves.png' if len(identifiers) <= 3 else f'development-curves-{offset//3+1}.png'
        fig.savefig(output/filename, dpi=180)
        plt.close(fig)
        curve_artifacts.append(filename)

    fig, grid = plt.subplots(1, len(config['models']), figsize=(3.9*len(config['models']), 4),
                             layout='constrained', sharey=True, squeeze=False)
    axes = grid[0]
    for ax, model in zip(axes, report['config']['models']):
        mid = model['id']
        own = [row for row in rows if row['model'] == mid]
        for i, row in enumerate(own):
            scores = [math.sqrt(s['evaluation_objective']) for s in row['start_evaluation_scores'] if s['evaluation_objective'] is not None]
            offsets = [(j-(len(scores)-1)/2)*.08 for j in range(len(scores))]
            ax.scatter([i+o for o in offsets], scores, color=COLORS.get(mid), alpha=.5, s=30)
        if all(r['selected_evaluation_objective'] is not None for r in own):
            ax.plot(range(len(own)), [math.sqrt(r['selected_evaluation_objective']) for r in own],
                    color=COLORS.get(mid), marker='o', label='Selected by calibration')
        if comparison:
            others = [row for row in comparison if row['model'] == mid]
            if all(r['selected_evaluation_objective'] is not None for r in others):
                ax.plot(range(len(others)), [math.sqrt(r['selected_evaluation_objective']) for r in others],
                        color='#333333', linestyle='--', marker='x', label='Larger budget, selected')
        ax.set_xticks(range(len(own)), [r['package'] for r in own])
        ax.set_title(LABELS.get(mid, mid), fontsize=10)
        ax.set_xlabel('Calibration information package')
        ax.set_yscale('log')
        ax.grid(alpha=.2)
        ax.spines[['top', 'right']].set_visible(False)
    axes[0].set_ylabel('Root mean scaled squared error\nDevelopment evaluation tests')
    axes[-1].legend(frameon=False, fontsize=8)
    fig.suptitle('Development diagnostics: starts and calibration budget\nFixed constants and prior information differ across formulations', fontsize=12)
    fig.savefig(output/'development-data-budget.png', dpi=180)
    plt.close(fig)
    return curve_artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=PAPER/'results/pilot-frozen96/report.json')
    parser.add_argument('--comparison', type=Path)
    parser.add_argument('--plot-package', help='response-curve package; defaults to last configured package')
    parser.add_argument('--output', type=Path, default=PAPER/'results/diagnostics')
    args = parser.parse_args()
    report = read_json(args.report)
    if report.get('input_integrity') != 'verified_unchanged':
        raise ValueError('only completed, integrity-checked reports may be summarized')
    assert_development_ids(report['config']['experiment_paths'])
    rows = summaries(report)
    other_rows = None
    other = None
    if args.comparison:
        other = read_json(args.comparison)
        if other.get('input_integrity') != 'verified_unchanged':
            raise ValueError('comparison report is incomplete')
        a, b = copy.deepcopy(report['config']), copy.deepcopy(other['config'])
        a['optimizer'].pop('max_evaluations')
        b['optimizer'].pop('max_evaluations')
        if a != b or report['model_sha256'] != other['model_sha256'] or report['experiment_sha256'] != other['experiment_sha256'] or report['solver_sha256'] != other['solver_sha256']:
            raise ValueError('budget comparison requires the same scientific inputs and solver')
        method_files = lambda run: {p: sha for p, sha in run['code_sha256'].items()
                                   if p.startswith('paper/analysis/') or p == 'paper/scripts/run_pilot.py'}
        if method_files(report) != method_files(other):
            raise ValueError('budget comparison requires the same analysis implementation')
        other_rows = summaries(other)
    args.output.mkdir(parents=True, exist_ok=True)
    curve_artifacts = plots(report, rows, args.output, other_rows, args.report.parent, args.plot_package)
    import matplotlib
    result = {'paper_record_version': 1, 'kind': 'development_diagnostics', 'report_sha256': digest(args.report),
              'comparison_sha256': digest(args.comparison) if args.comparison else None,
              'generator_sha256': digest(__file__), 'matplotlib_version': matplotlib.__version__,
              'summaries': rows, 'budget_comparison': other_rows, 'curve_artifacts': curve_artifacts,
              'response_plot_package': args.plot_package or list(report['config']['packages'])[-1]}
    write_json(args.output/'summary.json', result)
    lines = ['# Development pilot diagnostics', '', report['config']['claim'], '',
             'These results exercise calibration and transfer on the configured development tests. '
             'They do not compare complete model calibration under equal prior information. '
             'Search variability is not parameter uncertainty.', '',
             '| Model | Package | Calibration objective | Evaluation root scaled MSE | Starts at budget limit | Bound hits in selected fit |',
             '| --- | --- | ---: | ---: | ---: | --- |']
    for row in rows:
        score = row['selected_evaluation_objective']
        lines.append(f"| {LABELS.get(row['model'], row['model'])} | {row['package']} | {row['calibration_objective']:.6g} | " +
                     display_root(score) + f" | {row['termination_counts']['budget_limit']} | {', '.join(row['selected_parameters_at_bounds']) or 'none'} |")
    if 'evaluation_protocol' in report['config']:
        lines += ['', 'Calibration uses uniform-strain monotonic metrics; evaluation uses acquisition-order drained replay with trapezoidal endpoint errors over absolute axial-strain travel. All evaluation tests use that same protocol. Aggregate evaluation scores cannot be compared directly with the earlier pressure pilot. Initialization uses measured file void ratio and effective stress; source disagreement is examined in the separate fixed-parameter sensitivity diagnostic.']
    lines += ['', 'The evaluation summary gives equal weight to tests and channels. Stress is scaled by initial mean '
              'effective pressure and volume strain by 0.01. The selected seed minimizes calibration error only. '
              'An optimizer step threshold establishes termination, not a global optimum.', '',
              '## Physical errors by development test', '',
              '| Model | Package | Test | Stress RMSE in kPa | Volume RMSE in percentage points |',
              '| --- | --- | --- | ---: | ---: |']
    for p in report['predictions']:
        if p.get('selected') and p.get('metrics'):
            lines.append(f"| {LABELS.get(p['model'], p['model'])} | {p['package']} | {p['experiment_id']} | "
                         f"{p['metrics']['q']['rmse']/1000:.6g} | {p['metrics']['volumetric_strain']['rmse']*100:.6g} |")
    lines += ['', '## Completion and numerical refinement', '']
    for row in rows:
        lines.append(f"- {LABELS.get(row['model'], row['model'])} {row['package']}: {row['evaluation_completed']}/{row['evaluation_scheduled']} "
                     f"selected evaluation runs completed; {row['failed_parameter_vectors']}/{row['attempted_parameter_vectors']} failed calibration parameter vectors.")
    changes = [math.sqrt(m['scaled_mse']) for p in report['predictions'] if p.get('selected')
               for ref in p.get('refinement', []) if ref.get('changes_from_previous')
               for m in ref['changes_from_previous'].values()]
    if changes:
        lines += ['', f'Maximum normalized RMS change between adjacent tested evaluation resolutions: {max(changes):.6g}. '
                  'This checks selected prediction paths, not all calibration trials or source correctness.']
    if other:
        lines += ['', '## Calibration budget sensitivity', '',
                  f"Parameter-vector budget per start: {report['config']['optimizer']['max_evaluations']} versus {other['config']['optimizer']['max_evaluations']}.", '',
                  '| Model | Package | Calibration objective with larger budget | Evaluation root scaled MSE with larger budget | Starts at larger budget limit |',
                  '| --- | --- | ---: | ---: | ---: |']
        for row in other_rows:
            score = row['selected_evaluation_objective']
            lines.append(f"| {LABELS.get(row['model'], row['model'])} | {row['package']} | {row['calibration_objective']:.6g} | " +
                         display_root(score) + f" | {row['termination_counts']['budget_limit']} |")
        lines += ['', 'Compare objective changes and variability before attributing any difference to model mechanisms. '
                  'A lower calibration objective need not lower evaluation error. Complete start-level records and parameters are retained in the JSON reports.']
    lines += ['', '## Artifacts', '']
    lines += [f'- `{name}`: measured and selected predictions after {result["response_plot_package"]} calibration.' for name in curve_artifacts]
    lines += ['- `development-data-budget.png`: evaluation sensitivity to calibration package, starts, and optional larger budget.',
              '- `summary.json`: generated metrics and report hashes.', '',
              'All artifacts remain local; data release terms must be reviewed before distribution.', '']
    (args.output/'report.md').write_text('\n'.join(lines))
    print('Diagnostic report:', args.output/'report.md')


if __name__ == '__main__':
    main()
