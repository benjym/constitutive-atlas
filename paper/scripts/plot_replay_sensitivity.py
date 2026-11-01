"""Plot initial-state and step-refinement differences from archived replays."""
import argparse
import os
from pathlib import Path
import sys

PAPER = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PAPER))
os.environ.setdefault('MPLCONFIGDIR', str(PAPER/'.cache/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis.common import digest, read_json
from analysis.reservations import assert_development_ids

COLORS = ['#3b6d95', '#b27831', '#26846b']
LABELS = {'linear-elastic': 'Elastic baseline', 'drucker-prager': 'Drucker–Prager',
          'hypoplastic-sand-vw96': 'Hypoplasticity'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    report = read_json(args.report)
    if report['kind'] != 'fixed_parameter_initial_state_development_diagnostic' or report['input_integrity'] != 'verified':
        raise ValueError('verified replay diagnostic required')
    config = report['config']
    assert_development_ids(config['experiment_ids'])
    for name, sha in report['input_sha256'].items():
        if digest(args.report.parent/'inputs'/name) != sha:
            raise ValueError('archived diagnostic input changed')
    fine, coarse = min(config['maximum_increments']), max(config['maximum_increments'])
    fig, axes = plt.subplots(2, len(config['experiment_ids']), figsize=(11, 6.4),
                             squeeze=False, layout='constrained')
    incomplete = []
    for column, eid in enumerate(config['experiment_ids']):
        for mid, color in zip(config['model_ids'], COLORS):
            group = [r for r in report['records'] if r['experiment_id'] == eid and r['model_id'] == mid]
            if len(group) != 4 or any(r['prediction']['status'] != 'success' for r in group):
                incomplete.append(f'{eid}/{mid}')
                continue
            selected = {(r['scenario'], r['maximum_increment']): r for r in group}
            file_points = selected['file', fine]['prediction']['points']
            table_points = selected['original_table', fine]['prediction']['points']
            coarse_points = selected['file', coarse]['prediction']['points']
            travel = [0.]
            for a, b in zip(file_points, file_points[1:]):
                travel.append(travel[-1]+abs(b['axial_strain']-a['axial_strain']))
            for row, (channel, factor, label) in enumerate([
                    ('q', .001, 'Change in q (kPa)'),
                    ('volumetric_strain', 100., 'Change in volume strain (percentage points)')]):
                ax = axes[row, column]
                ax.plot([x*100 for x in travel], [(b[channel]-a[channel])*factor for a,b in zip(file_points,table_points)],
                        color=color, label=LABELS.get(mid,mid), linewidth=1.7)
                ax.plot([x*100 for x in travel], [(b[channel]-a[channel])*factor for a,b in zip(file_points,coarse_points)],
                        color=color, linestyle=':', linewidth=1.1)
                ax.set(xlabel='Absolute axial-strain travel (%)', ylabel=label)
        for ax in axes[:, column]:
            ax.grid(alpha=.2)
            ax.spines[['top','right']].set_visible(False)
            ax.axhline(0, color='#888888', linewidth=.5, zorder=0)
        axes[0,column].set_title(eid)
    axes[0,0].legend(frameon=False, fontsize=8)
    fig.suptitle('Initial-state sensitivity with fixed earlier C2 parameters\nSolid: original-table e₀ minus file e₀; dotted: coarse minus fine replay (file e₀)', fontsize=12)
    fig.supxlabel('Development diagnostic; first 2% axial strain; recorded order preserved. Dotted lines show numerical sensitivity, not uncertainty.', fontsize=9)
    path = args.report.parent/'initial-state-sensitivity.png'
    fig.savefig(path,dpi=180)
    plt.close(fig)
    print(path)
    if incomplete:
        print('Incomplete cases omitted from lines:', ', '.join(incomplete))


if __name__ == '__main__':
    main()
