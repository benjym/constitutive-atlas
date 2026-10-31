"""Frozen factorial evaluation at calibration-only selected parameters."""
import argparse
import importlib.util
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SPEC=importlib.util.spec_from_file_location('propagation_old_runner',HERE.parent/'kfs-locked-initialization-sensitivity-v1/run_case.py')
OLD=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(OLD)
MODEL='hypoplastic-sand-vw96'
FILE='file_initial'
ALT='original_table_disputed_e0'


def inputs():
    freeze=OLD.loads((HERE/'freeze.json').read_bytes())
    for filename,key in [('policy.json','policy_sha256'),('run_case.py','runner_sha256')]:
        OLD.require(OLD.digest((HERE/filename).read_bytes())==freeze[key],filename+' changed')
    policy=OLD.loads((HERE/'policy.json').read_bytes())
    _,_,report,states=OLD.load_inputs() # allocation/parameter checks before response access
    for name,sha in policy['input_sha256'].items():
        OLD.require(OLD.digest((ROOT/name).read_bytes())==sha,'input changed: '+name)
    selection=OLD.loads((ROOT/policy['calibration_results']).read_bytes())['selected']
    OLD.require(policy['selected']==selection,'calibration selections changed')
    allocation=OLD.loads((ROOT/'studies/kfs-development-v1/allocation.json').read_bytes())
    OLD.require(policy['evaluation_ids']==allocation['evaluation_ids'],'evaluation allocation changed')
    expected=[]
    for calibration in (FILE,ALT):
        for eid in policy['evaluation_ids']:
            scenarios=(FILE,ALT) if eid in policy['disputed_evaluation_ids'] else (FILE,)
            for scenario in scenarios:
                expected.append({'index':len(expected),'calibration_scenario':calibration,
                                 'evaluation_scenario':scenario,'experiment_id':eid})
    OLD.require(policy['cases']==expected,'case coverage/order differs')
    return policy,freeze,report,states


def prepare(record,policy,report,states):
    eid=record['experiment_id']
    content=(ROOT/'paper/results/pilot-matched96/experiments'/(eid+'.json')).read_bytes()
    OLD.require(OLD.digest(content)==policy['experiment_sha256'][eid]==report['experiment_sha256'][eid],
                'experiment changed')
    experiment=OLD.loads(content)
    OLD.require(experiment['id']==eid,'experiment identity differs')
    state=states[eid][record['evaluation_scenario']]
    OLD.require(state['sigma']==experiment['initial']['effective_stress'] and
                states[eid][FILE]['e']==experiment['initial']['void_ratio'],'initial state differs')
    experiment['initial']['void_ratio']=state['e']
    rows=[]
    for row in experiment['rows']:
        if row['axial_strain']>policy['maximum_axial_strain']:break
        rows.append(row)
    saved=[p for p in report['predictions'] if p.get('selected') is True and
           (p['model'],p['package'],p['experiment_id'])==(MODEL,'density3',eid)]
    OLD.require(len(saved)==1,'missing historical selected control')
    saved=saved[0]
    OLD.require([r['axial_strain'] for r in rows]==[p['axial_strain'] for p in saved['points']],
                'evaluation window differs')
    OLD.require(saved['parameters']==policy['selected'][FILE]['parameters'],'historical vector differs')
    return experiment,rows,saved


def predict(record,policy,experiment,rows,tracker):
    adapter=OLD.adapter_class(tracker)(ROOT/'paper/results/pilot-matched96/solver/atlas_solver',
                                       [MODEL],ROOT/'paper/results/pilot-matched96/models')
    OLD.require(adapter.solver_hash==policy['solver_sha256'],'solver changed')
    return adapter.replay(MODEL,policy['selected'][record['calibration_scenario']]['parameters'],
                          experiment,[r['axial_strain'] for r in rows],
                          policy['maximum_increment'],policy['timeout_per_case_seconds'])


def evidence(record,policy,experiment,rows,saved,prediction,prior_directory):
    OLD.require(prediction['status']=='success' and prediction['completed_observations']==len(rows),
                'unsuccessful or partial prediction')
    control=None
    if record['calibration_scenario']==FILE:
        if record['evaluation_scenario']==FILE:
            OLD.require(prediction['points']==saved['points'],'historical file control differs')
            control='historical_selected_points'
        else:
            index=policy['prior_alternative_case_indices'][record['experiment_id']]
            path=prior_directory/f'case-{index:02d}'/'prediction.json'
            content=path.read_bytes()
            OLD.require(OLD.digest(content)==policy['prior_prediction_sha256'][str(index)],'prior control changed')
            prior=OLD.loads(content)
            OLD.require(prediction['points']==prior['points'],'prior alternative control differs')
            control='prior_locked_alternative_points'
    scales={'q':sum(experiment['initial']['effective_stress'][:3])/3,
            'volumetric_strain':policy['volumetric_strain_scale']}
    return {'record':record,'status':'success','control':control,
            'observations':len(rows),'native_calls':prediction['native_calls'],
            'maximum_radial_stress_drift_Pa':prediction['maximum_radial_stress_drift_Pa'],
            'metrics':{c:OLD.compare_acquisition_linear(rows,prediction,c,scales[c]) for c in policy['channels']}}


def run(index,output,prior_directory):
    policy,freeze,report,states=inputs()
    OLD.require(type(index) is int and 0<=index<len(policy['cases']),'invalid case index')
    for previous in range(index):
        summary=OLD.loads((output/f'case-{previous:02d}'/'summary.json').read_bytes())
        OLD.require(summary['status']=='success' and summary['policy_sha256']==freeze['policy_sha256'],
                    'previous case failed or changed')
    record=policy['cases'][index];experiment,rows,saved=prepare(record,policy,report,states)
    directory=output/f'case-{index:02d}';directory.mkdir(parents=True,exist_ok=False)
    tracker=OLD.RecordedProcesses(directory,policy['catalogue_hash'])
    summary={'record':record,'status':'failed','policy_sha256':freeze['policy_sha256'],
             'runner_sha256':freeze['runner_sha256']}
    OLD.write(directory/'summary.json',summary)
    try:
        prediction=predict(record,policy,experiment,rows,tracker)
        OLD.write(directory/'prediction.json',prediction)
        summary.update(evidence(record,policy,experiment,rows,saved,prediction,prior_directory))
        summary['prediction_sha256']=OLD.digest((directory/'prediction.json').read_bytes())
    except Exception as exc:
        summary['status']='failed';summary['error']=str(exc);raise
    finally:
        summary['processes']=len(tracker.records)
        summary['process_receipts_sha256']=OLD.digest((directory/'processes.json').read_bytes()) if tracker.records else None
        OLD.write(directory/'summary.json',summary)
    print(f"case {index:02d}: success, {summary['native_calls']} segments, control={summary['control']}",flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--prior-dir',type=Path,required=True);args=parser.parse_args()
    run(args.case,args.output_dir,args.prior_dir)
