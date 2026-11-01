"""Plot pinned first-loading development scenarios at the lowest start threshold."""
import argparse
import itertools
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from run_compression_sensitivity import summarize, validate_config


def load_checked_report(path):
    """Shared integrity/admission boundary for development figures and tables."""
    report = read_json(path)
    directory = path.parent
    if (report['kind'] != 'fixed_parameter_oedometer_initialization_development_diagnostic'
            or report['config']['phase'] != 'development_only_not_calibration_admission'
            or report['input_integrity'] != 'verified'):
        raise ValueError('unsupported compression diagnostic')
    validate_config(report['config'])
    for name, sha in report['input_sha256'].items():
        if digest(directory/'inputs'/name) != sha:
            raise ValueError('archived input changed')
    if digest(directory/'solver/atlas_solver') != report['solver_sha256']:
        raise ValueError('archived solver changed')
    for model, sha in report['model_sha256'].items():
        if digest(directory/'models'/f'{model}.json') != sha:
            raise ValueError('archived model changed')
    baseline = read_json(directory/'inputs'/report['config']['baseline_report'])
    if (baseline['solver_sha256'] != report['solver_sha256'] or
            any(baseline['model_sha256'][m] != sha for m, sha in report['model_sha256'].items())):
        raise ValueError('compression implementation differs from its declared frozen baseline')
    parameters = {m['id']: m['baseline_parameters'] for m in baseline['config']['models']}
    if any(r['parameters'] != parameters[r['model_id']] for r in report['records']):
        raise ValueError('compression record does not use the declared fixed baseline constants')
    summary = summarize(report['records'], report['config'])
    if summary != report['summary']:
        raise ValueError('stored summary differs from recomputed paired contrasts')
    protocol, config = report['protocol'], report['config']
    expected = set(itertools.product(protocol['experiment_ids'], config['model_ids'],
                                    protocol['minimum_axial_stresses_Pa']))
    if {(r['experiment_id'], r['model_id'], r['minimum_stress_Pa']) for r in summary} != expected:
        raise ValueError('missing scheduled model, experiment or threshold')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, default=ROOT/'paper/results/compression-sensitivity-v1/report.json')
    args = parser.parse_args()
    report = load_checked_report(args.report)
    directory = args.report.parent
    protocol, config = report['protocol'], report['config']
    threshold = min(protocol['minimum_axial_stresses_Pa'])
    fine = min(config['maximum_increments'])
    selected = [r for r in report['records'] if r['minimum_stress_Pa'] == threshold and r['maximum_increment'] == fine]
    if any(r['prediction']['status'] != 'success' for r in selected):
        raise ValueError('selected figure panel incomplete; inspect retained failure report')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    fig, axes = plt.subplots(2, 2, figsize=(9, 7.4), squeeze=False)
    colors = ['#0072B2', '#D55E00', '#009E73']
    styles = {'engineering_increment': '-', 'log_height_increment': '--'}
    model_names = {'linear-elastic': 'Elastic diagnostic baseline', 'hypoplastic-sand-vw96': 'Base hypoplastic baseline'}
    for i, identifier in enumerate(protocol['experiment_ids']):
        source = directory/'inputs'/protocol['data_directory']/'normalized'/f'{identifier}.json'
        rows_by_line = {r['source_line']: r for r in read_json(source)['rows']}
        for j, model in enumerate(config['model_ids']):
            ax = axes[i, j]
            group = [r for r in selected if r['experiment_id'] == identifier and r['model_id'] == model]
            source_lines = group[0]['source_lines']
            rows = [rows_by_line[line] for line in source_lines]
            x = [100*r['axial_strain'] for r in rows]
            for record in group:
                if record['source_lines'] != source_lines:
                    raise ValueError('curve panel has unmatched observation rows')
                color = colors[config['initial_radial_to_axial_stress_ratios'].index(record['initial_stress_ratio'])]
                ax.plot(x, [p['axial_stress']/1000 for p in record['prediction']['points']],
                        color=color, linestyle=styles[record['coordinate']], linewidth=1.2)
            ax.plot(x, [r['axial_stress']/1000 for r in rows], color='#222222', marker='.',
                    linestyle=':', markersize=3, linewidth=1.3, zorder=5)
            ax.set(title=f'{identifier} · {model_names[model]}', xlabel='Recorded engineering axial strain (%)',
                   ylabel='Axial stress (kPa)')
            ax.grid(alpha=.2)
    handles = [Line2D([], [], color=colors[i], label=f'Initial radial/axial stress = {ratio:g}')
               for i, ratio in enumerate(config['initial_radial_to_axial_stress_ratios'])]
    handles += [Line2D([], [], color='#666666', linestyle=style, label=label)
                for style, label in [('-', 'Engineering increments'), ('--', 'Log height increments')]]
    handles += [Line2D([], [], color='#222222', linestyle=':', marker='.', label='Measured response')]
    fig.suptitle('First-loading development sensitivity · fixed baseline constants', fontsize=13, y=.98)
    fig.legend(handles=handles, loc='lower center', ncol=3, fontsize=8, bbox_to_anchor=(.5, .055))
    fig.text(.5, .018, 'Lowest declared threshold: 1 kPa; observed start: 1.548 kPa. Assumed initial lateral stress; no calibration or model ranking.\n'
             'Curves use the finer numerical resolution. Log height mapping does not establish finite-strain stress-law validity.',
             ha='center', fontsize=8)
    fig.tight_layout(rect=(0, .15, 1, .95))
    png = directory/'first-loading-sensitivity.png'
    pdf = directory/'first-loading-sensitivity.pdf'
    fig.savefig(png, dpi=180)
    fig.savefig(pdf)
    plt.close(fig)
    write_json(directory/'figure-provenance.json', dict(report_sha256=digest(args.report),
        plot_script_sha256=digest(__file__), start_threshold_Pa=threshold, maximum_increment=fine,
        png_sha256=digest(png), pdf_sha256=digest(pdf), input_integrity='verified_archived_inputs_and_recomputed_summary'))
    print(png)


if __name__ == '__main__':
    main()
