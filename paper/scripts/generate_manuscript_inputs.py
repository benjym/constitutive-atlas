"""Generate manuscript inputs from reviewed-scope annotations and frozen pilot records."""
import argparse
from collections import Counter
import os
from pathlib import Path
import sys

PAPER=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PAPER))
os.environ.setdefault('MPLCONFIGDIR',str(PAPER/'.cache/matplotlib'))
from analysis.annotations import validate_model_annotations
from analysis.common import ROOT,digest,read_json,write_json
from analysis.contrasts import design_contrasts
from analysis.pilot import validate_config
from analysis.source_reviews import validate_source_reviews
from analysis.survey_discovery import audit_searches, validate_title_screening
from plot_compression_sensitivity import load_checked_report

LABELS={'linear-elastic':'Elastic baseline','drucker-prager':'Drucker--Prager',
        'hypoplastic-sand-vw96':'Hypoplasticity (4 fitted)','hypoplastic-sand-igs97':'Hypoplasticity + IGS',
        'modified-cam-clay':'Modified Cam Clay','terracotta-2024-fig1':'Terracotta Fig. 1'}


def input_key(path):
    path=path.resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--annotations',type=Path,default=PAPER/'study/model_annotations.json')
    parser.add_argument('--contrasts',type=Path,default=PAPER/'results/contrasts-matched/contrasts.json')
    parser.add_argument('--pilot-report',type=Path,action='append')
    parser.add_argument('--compression-report',type=Path,default=PAPER/'results/compression-sensitivity-v1/report.json')
    parser.add_argument('--output',type=Path,default=PAPER/'article/generated')
    args=parser.parse_args()
    survey_protocol=PAPER/'study/survey_protocol.json'
    survey_searches=PAPER/'study/survey_searches.json'
    survey_screening=PAPER/'study/survey_screening.json'
    survey_scope=PAPER/'study/survey_scope_decisions.json'
    survey=audit_searches(survey_searches,survey_protocol)
    survey_batches=read_json(survey_searches)['batches']
    title_rows=validate_title_screening(read_json(survey_screening),read_json(survey_protocol),
                                      survey['queue'],survey_batches)
    title_counts=Counter(row['decision'] for row in title_rows)
    records=validate_model_annotations(read_json(args.annotations))
    source_directory=PAPER/'study/source_formulations'
    source_reviews=validate_source_reviews(source_directory)
    source_publications={r['model_id']:r['publication_id'] for r in source_reviews}
    for model_id,publication_id in {'norsand-1993':'doi:10.1680/geot.1993.43.1.91',
                                    'hca-sand-2005':'doi:10.1016/j.compgeo.2005.03.002'}.items():
        if source_publications.get(model_id)!=publication_id:
            raise ValueError('manuscript source example lacks its reviewed publication record')
    contrast=read_json(args.contrasts)
    if contrast['kind']!='matched_count_development_contrasts':
        raise ValueError('paired matched-count diagnostic required')
    paths=args.pilot_report or [PAPER/'results/pilot-matched96/report.json',PAPER/'results/pilot-matched384/report.json']
    runs={}
    inputs={input_key(args.annotations):digest(args.annotations),input_key(args.contrasts):digest(args.contrasts)}
    for record in records:
        inputs.update(record.get('source_reconciliation', {}).get('inputs_sha256', {}))
        for evidence in record.get('numerical_evidence', []):
            inputs[evidence['path']]=evidence['sha256']
    for path in (survey_protocol,survey_searches,survey_screening,survey_scope):
        inputs[input_key(path)]=digest(path)
    for batch in survey_batches:
        for field in ('raw_path','headers_path'):
            path=ROOT/batch[field]
            inputs[input_key(path)]=digest(path)
    survey_directory=(ROOT/survey_batches[0]['raw_path']).parent
    for name in ('protocol.json','fetch_script.py'):
        path=survey_directory/name
        inputs[input_key(path)]=digest(path)
    for path in sorted(source_directory.glob('*.json')):
        inputs[input_key(path)]=digest(path)
    for review in source_reviews:
        source=review['source']
        inputs.update(review.get('normalization_audit',{}).get('inputs_sha256',{}))
        for snapshot in (source,source.get('bibliographic_crosscheck',{})):
            local=snapshot.get('local_copy')
            if local and (ROOT/local).exists():
                inputs[local]=digest(ROOT/local)
    for path in paths:
        report=read_json(path)
        validate_config(report['config'])
        if report['input_integrity']!='verified_unchanged':
            raise ValueError('completed frozen pilot required')
        directory=path.parent
        if digest(directory/'solver/atlas_solver')!=report['solver_sha256']:
            raise ValueError('frozen pilot executable changed')
        for mid,sha in report['model_sha256'].items():
            if digest(directory/'models'/f'{mid}.json')!=sha:
                raise ValueError('frozen model changed')
        for eid,sha in report['experiment_sha256'].items():
            if digest(directory/'experiments'/f'{eid}.json')!=sha:
                raise ValueError('frozen experiment changed')
        for name,sha in report['code_sha256'].items():
            if digest(directory/'source'/name)!=sha:
                raise ValueError('frozen paper code changed')
        budget=report['config']['optimizer']['max_evaluations']
        if budget in runs:
            raise ValueError('duplicate pilot budget')
        runs[budget]=report
        inputs[input_key(path)]=digest(path)
        packaged=next(r for r in contrast['results'] if r['budget']==budget)
        recomputed=design_contrasts(report)
        if digest(path)!=packaged['report_sha256'] or any(recomputed[key]!=packaged[key] for key in ('summaries','per_test','same_seed_search_sensitivity')):
            raise ValueError('contrast values differ from frozen source report')
    if set(runs)!={r['budget'] for r in contrast['results']}:
        raise ValueError('all contrast budgets must have matching frozen reports')
    reference=next(iter(runs.values()))['config']
    compression=load_checked_report(args.compression_report)
    inputs[input_key(args.compression_report)]=digest(args.compression_report)
    compression_config=compression['config']
    compression_threshold=min(compression['protocol']['minimum_axial_stresses_Pa'])
    compression_rows=[r for r in compression['summary'] if r['minimum_stress_Pa']==compression_threshold]
    if any(r['comparison_status']!='complete_development_sensitivity' for r in compression['summary']):
        raise ValueError('manuscript compression table requires explicit incomplete-case handling')
    starts={r['actual_initial_axial_stress_Pa'] for r in compression['records'] if r['minimum_stress_Pa']==compression_threshold}
    if len(starts)!=1:
        raise ValueError('use per-test actual starts before generating a common start macro')
    args.output.mkdir(parents=True,exist_ok=True)
    macros={'AnnotatedFormulationCount':len(records),'PilotModelCount':len(reference['models']),
            'SurveyOccurrenceCount':survey['counts']['returned_occurrences'],
            'SurveyPublicationCount':len(survey['queue']),
            'SurveyTitleDecisionCount':len(title_rows),
            'SurveyUntitledCount':len(survey['queue'])-len(title_rows),
            'SurveyRetrieveCount':title_counts['retrieve_full_text'],
            'SurveyBackgroundCount':title_counts['background_or_infrastructure'],
            'SurveyUnresolvedCount':title_counts['unresolved'],
            'SurveyOutsideScopeCount':title_counts['exclude_outside_geomaterial_scope'],
            'PilotEvaluationTestCount':len(reference['evaluation_ids']),'PilotMaximumStrainPercent':100*reference['maximum_axial_strain'],
            'PilotCalibrationSamples':reference['samples'],'PilotVolumeScale':reference['objective']['volumetric_strain_scale'],
            'PilotStartCount':len(reference['optimizer']['seeds']),
            'CompressionReplayCount':len(compression['records']),
            'CompressionStartThresholdCount':len(compression['protocol']['minimum_axial_stresses_Pa']),
            'CompressionStartThresholdKPa':compression_threshold/1000,
            'CompressionObservedStartKPa':next(iter(starts))/1000,
            'CompressionCoarseIncrement':compression_config['maximum_increments'][0],
            'CompressionFineIncrement':compression_config['maximum_increments'][1]}
    macro_text='\n'.join('\\newcommand{\\'+name+'}{'+f'{value:g}'+'}' for name,value in macros.items())+'\n'
    macro_text+='\\newcommand{\\CompressionStressRatios}{'+', '.join(f'{value:g}' for value in compression_config['initial_radial_to_axial_stress_ratios'])+'}\n'
    (args.output/'paper_inputs.tex').write_text(macro_text)
    rows=[]
    for model in records:
        scope=model['component_count_scope']
        kind='3D / RI' if scope['kinematics']=='small_strain_3d_symmetric' else 'Axi. / time'
        label='Hypoplasticity (base)' if model['model_id']=='hypoplastic-sand-vw96' else LABELS[model['model_id']]
        rows.append(f"{label} & {kind} & {model['counts']['declared_parameters']} & {model['counts']['material_constants']} & {scope['stored_stress_components']} & {scope['persistent_internal_components']} "+r'\\')
    (args.output/'survey_table.tex').write_text('\n'.join(rows)+'\n')
    rows=[]
    for result in contrast['results']:
        for row in result['summaries']:
            if row['group']=='all_evaluation_tests' and row['stress_weight']==.5:
                if not row['complete']:
                    raise ValueError('manuscript pilot table requires explicit incomplete-case handling')
                rows.append(f"{result['budget']} & {LABELS[row['model_id']]} & {row['reference_root_error']:.4f} & {row['alternative_root_error']:.4f} & {row['root_error_change']:+.4f} "+r'\\')
    (args.output/'pilot_table.tex').write_text('\n'.join(rows)+'\n')
    rows=[]
    compression_labels={'linear-elastic':'Elastic baseline','hypoplastic-sand-vw96':'Base hypoplasticity'}
    for row in compression_rows:
        refinement=row['maximum_step_refinement_difference_Pa']
        refinement_text=r'$<0.01$' if 0<refinement<.005 else f'{refinement:.2f}'
        rows.append(f"{row['experiment_id'].removeprefix('KFS-')} & {compression_labels[row['model_id']]} & {row['maximum_initial_stress_scenario_difference_Pa']/1000:.2f} & {row['maximum_coordinate_scenario_difference_Pa']/1000:.2f} & {refinement_text} "+r'\\')
    (args.output/'compression_table.tex').write_text('\n'.join(rows)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    models=reference['models']
    fig,axes=plt.subplots(1,len(models),figsize=(10.2,3.7),squeeze=False,layout='constrained')
    for ax,model in zip(axes[0],models):
        for result in contrast['results']:
            rows=[r for r in result['summaries'] if r['model_id']==model['id'] and r['group']=='all_evaluation_tests']
            if not all(r['complete'] for r in rows):
                raise ValueError('incomplete contrast cannot be silently plotted')
            ax.plot([r['stress_weight'] for r in rows],[r['root_error_change'] for r in rows],marker='o',label=f"Budget {result['budget']}")
        ax.axhline(0,color='#666666',linewidth=.7)
        ax.set(title=LABELS[model['id']].replace('--','–'),xlabel='Stress weight',xticks=[.25,.5,.75])
        ax.grid(alpha=.2)
        ax.spines[['top','right']].set_visible(False)
    axes[0,0].set_ylabel('Root error change: density3 − pressure3')
    axes[0,-1].legend(frameon=False,fontsize=8)
    fig.savefig(args.output/'matched-design.png',dpi=200)
    plt.close(fig)
    manifest={'paper_record_version':1,'kind':'development_manuscript_inputs','inputs_sha256':inputs,
              'survey_scope_decision_id':read_json(survey_scope)['scope_decision_id'],
              'assisted_title_screening':{'decisions':len(title_rows),'by_decision':dict(title_counts),
                    'remaining_without_title_decision':len(survey['queue'])-len(title_rows),
                    'qualification':'Bounded development pilot; no formulation admission or independent review.'},
              'source_reviews':{r['model_id']:{'status':r['status'],'publication_id':r['publication_id'],
                    'local_source_available':bool(r['source']['local_copy'] and (ROOT/r['source']['local_copy']).exists()),
                    'reviewed_source_sha256':r['source']['sha256'],
                    'benchmark_admission':r['paper_interpretation']['benchmark_admission']} for r in source_reviews},
              'generator_sha256':digest(__file__),'current_annotation_definition_sha256':{m['model_id']:m['definition_sha256_at_annotation'] for m in records},
              'analysis_sha256':{str(p.relative_to(ROOT)):digest(p) for p in [PAPER/'analysis/annotations.py',PAPER/'analysis/source_reviews.py',PAPER/'analysis/survey_discovery.py',PAPER/'analysis/contrasts.py',PAPER/'scripts/run_compression_sensitivity.py',PAPER/'scripts/plot_compression_sensitivity.py']},
              'pilot_model_sha256':{str(b):r['model_sha256'] for b,r in runs.items()},
              'compression_model_sha256':compression['model_sha256'],
              'outputs_sha256':{p.name:digest(p) for p in args.output.iterdir() if p.suffix in ('.tex','.png')},
              'limitations':'Current annotation snapshots and historical pilot implementations are distinct; independent review and final study gates remain open.'}
    write_json(args.output/'manifest.json',manifest)
    print('Generated manuscript inputs:',args.output)


if __name__=='__main__':
    main()
