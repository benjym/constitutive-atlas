"""Report paired matched-count development contrasts and declared metric sensitivity."""
import argparse
import copy
import os
from pathlib import Path
import sys

PAPER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PAPER))
os.environ.setdefault('MPLCONFIGDIR',str(PAPER/'.cache/matplotlib'))
from analysis.common import digest, read_json, write_json
from analysis.contrasts import design_contrasts
from analysis.pilot import validate_config
from report_pilot import LABELS


def compatible(a,b):
    ca,cb=copy.deepcopy(a['config']),copy.deepcopy(b['config'])
    ca['optimizer'].pop('max_evaluations')
    cb['optimizer'].pop('max_evaluations')
    methods=lambda r:{p:h for p,h in r['code_sha256'].items() if p.startswith('paper/analysis/') or p=='paper/scripts/run_pilot.py'}
    if ca!=cb or methods(a)!=methods(b) or any(a[key]!=b[key] for key in ('experiment_sha256','model_sha256','solver_sha256','reservation_sha256')):
        raise ValueError('matched-design budget reports must share scientific inputs and analysis implementation')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,action='append',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    reports=[read_json(p) for p in args.report]
    for report in reports:
        if report.get('input_integrity')!='verified_unchanged':
            raise ValueError('completed integrity-checked runs required')
        validate_config(report['config'])
        compatible(reports[0],report)
    budgets=[r['config']['optimizer']['max_evaluations'] for r in reports]
    if len(budgets)!=len(set(budgets)):
        raise ValueError('duplicate budget reports')
    args.output.mkdir(parents=True,exist_ok=False)
    results=[]
    for path,report in zip(args.report,reports):
        results.append({'report_sha256':digest(path),'budget':report['config']['optimizer']['max_evaluations'],
                        **design_contrasts(report)})
    write_json(args.output/'contrasts.json',{'paper_record_version':1,'kind':'matched_count_development_contrasts',
        'direction':'density3 minus pressure3; negative error change favors density3',
        'generator_sha256':digest(__file__),'analysis_sha256':digest(PAPER/'analysis/contrasts.py'),
        'design':reports[0]['config']['calibration_design_contrast'],'results':results})
    lines=['# Matched-count calibration design: development comparison','',reports[0]['config']['claim'],'',
        'Both packages use three tests: pressure3 uses TMD2/3/4; density3 uses TMD3/8/13. '
        'Evaluation uses the same six separate development tests. Bounds, fitted/fixed constants, starts and numerical protocol are held fixed within a model. '
        'Negative changes favor density3. Test count does not equal preparation effort or parameter information.','',
        'Primary errors equally weight scaled stress and volume MSE, then equally weight tests before taking the square root. '
        'The 0.25/0.50/0.75 stress weights are declared evaluation-only sensitivity checks with fitted parameters held fixed. '
        'No confidence interval or independent-material inference is made.','',
        '| Budget per start | Model | Group | Stress weight | Pressure3 root error | Density3 root error | Change |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for result in results:
        for row in result['summaries']:
            if row['group']!='all_evaluation_tests' and row['stress_weight']!=.5:
                continue
            values=' | '.join(f'{row[k]:.6g}' for k in ('reference_root_error','alternative_root_error','root_error_change')) if row['complete'] else 'incomplete | incomplete | —'
            lines.append(f"| {result['budget']} | {LABELS.get(row['model_id'],row['model_id'])} | {row['group']} | {row['stress_weight']} | {values} |")
    lines+=['','## Per-test physical errors at the primary weight','',
        'Channel RMSEs do not depend on their subsequent aggregation weight. Changes are alternative minus reference.', '',
        '| Budget | Model | Test | Pressure3 stress RMSE (kPa) | Density3 stress RMSE (kPa) | Stress RMSE change (kPa) | Volume RMSE change (percentage points) |',
        '| --- | --- | --- | ---: | ---: | ---: | ---: |']
    for result in results:
        for row in result['per_test']:
            values=f"{row['q']['reference_rmse']/1000:.6g} | {row['q']['alternative_rmse']/1000:.6g} | {row['q']['rmse_change']/1000:.6g} | {row['volumetric_strain']['rmse_change']*100:.6g}" if row['complete'] else 'incomplete | incomplete | — | —'
            lines.append(f"| {result['budget']} | {LABELS.get(row['model_id'],row['model_id'])} | {row['experiment_id']} | {values} |")
    lines+=['','## Search sensitivity','',
        'The following pairs use the same initialization seed in both packages. These are optimization diagnostics, not statistical uncertainty intervals. The primary table instead uses each package\'s calibration-selected fit.', '',
        '| Budget | Model | Seed | Root error change |','| --- | --- | ---: | ---: |']
    for result in results:
        for row in result['same_seed_search_sensitivity']:
            value=f"{row['root_error_change']:.6g}" if row['complete'] else 'incomplete'
            lines.append(f"| {result['budget']} | {LABELS.get(row['model_id'],row['model_id'])} | {row['seed']} | {value} |")
    lines+=['','Results remain exploratory: the design follows inspected development outcomes; initial-state source conflicts, incomplete calibration-information parity and independent equation review remain unresolved. '
        'Density groups are descriptive cohorts, not verified independent batches. Runtime from potentially concurrent development jobs is not a controlled performance comparison.','',
        'See companion pilot reports for completion, numerical refinement, termination, bound hits and all start-level records.']
    (args.output/'report.md').write_text('\n'.join(lines)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    models=reports[0]['config']['models']
    fig,axes=plt.subplots(1,len(models),figsize=(11.5,4.5),squeeze=False,layout='constrained')
    for ax,model in zip(axes[0],models):
        for result in results:
            own=[r for r in result['summaries'] if r['model_id']==model['id'] and r['group']=='all_evaluation_tests']
            good=[r for r in own if r['complete']]
            ax.plot([r['stress_weight'] for r in good],[r['root_error_change'] for r in good],marker='o',label=f"Budget {result['budget']}")
        ax.axhline(0,color='#666666',linewidth=.8)
        ax.set(title=LABELS.get(model['id'],model['id']),xlabel='Stress weight in evaluation MSE',xticks=[.25,.5,.75])
        ax.grid(alpha=.2)
        ax.spines[['top','right']].set_visible(False)
    axes[0,0].set_ylabel('Root error change: density3 − pressure3')
    axes[0,-1].legend(frameon=False)
    fig.suptitle('Three calibration tests: pressure versus density coverage\nNegative favors density3; fixed fitted parameters in evaluation-weight sensitivity',fontsize=12)
    fig.savefig(args.output/'matched-count-weight-sensitivity.png',dpi=180)
    plt.close(fig)
    print('Matched-count report:',args.output/'report.md')


if __name__=='__main__':
    main()
