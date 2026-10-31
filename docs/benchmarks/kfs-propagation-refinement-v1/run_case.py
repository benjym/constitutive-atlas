"""Serial refinement of the complete frozen calibration/evaluation factorial."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SPEC=importlib.util.spec_from_file_location('propagation_coarse_assessor',HERE.parent/'kfs-tmd13-evaluation-propagation-v1/assess.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
RUN=BASE.RUN;OLD=BASE.OLD


def inputs(coarse_directory,prior_directory):
    freeze=OLD.loads((HERE/'freeze.json').read_bytes())
    for filename,key in [('policy.json','policy_sha256'),('run_case.py','runner_sha256'),('assess.py','assessor_sha256')]:
        OLD.require(OLD.digest((HERE/filename).read_bytes())==freeze[key],filename+' changed')
    policy=OLD.loads((HERE/'policy.json').read_bytes())
    for filename,sha in policy['input_sha256'].items():
        OLD.require(OLD.digest((ROOT/filename).read_bytes())==sha,'input changed: '+filename)
    coarse=BASE.assess(coarse_directory,prior_directory)
    OLD.require(coarse==OLD.loads((ROOT/policy['coarse_results']).read_bytes()),'coarse evidence differs')
    for index,sha in policy['coarse_prediction_sha256'].items():
        OLD.require(OLD.digest((coarse_directory/f'case-{int(index):02d}'/'prediction.json').read_bytes())==sha,
                    'coarse curve changed')
    oldpolicy,_,report,states=RUN.inputs()
    expected=[]
    for case in oldpolicy['cases']:
        for step in policy['fine_increments']:
            expected.append({'index':len(expected),'coarse_case_index':case['index'],'maximum_increment':step})
    OLD.require(policy['cases']==expected,'refinement coverage/order differs')
    return policy,freeze,oldpolicy,report,states


def compute(record,oldpolicy,report,states,tracker,prior_directory):
    case=oldpolicy['cases'][record['coarse_case_index']]
    experiment,rows,saved=RUN.prepare(case,oldpolicy,report,states)
    settings=dict(oldpolicy,maximum_increment=record['maximum_increment'])
    prediction=RUN.predict(case,settings,experiment,rows,tracker)
    # Finer controls intentionally differ from coarse saved curves; require success/completion,
    # then independently reconstruct and compare all outputs in the assessor.
    OLD.require(prediction['status']=='success' and prediction['completed_observations']==len(rows),
                'failed or incomplete refinement replay')
    scales={'q':sum(experiment['initial']['effective_stress'][:3])/3,
            'volumetric_strain':oldpolicy['volumetric_strain_scale']}
    evidence={'record':record,'status':'success','observations':len(rows),
              'native_calls':prediction['native_calls'],
              'maximum_radial_stress_drift_Pa':prediction['maximum_radial_stress_drift_Pa'],
              'metrics':{c:OLD.compare_acquisition_linear(rows,prediction,c,scales[c]) for c in oldpolicy['channels']}}
    return prediction,evidence


def run(index,output,coarse_directory,prior_directory):
    policy,freeze,oldpolicy,report,states=inputs(coarse_directory,prior_directory)
    OLD.require(type(index) is int and 0<=index<len(policy['cases']),'invalid refinement index')
    for previous in range(index):
        summary=OLD.loads((output/f'case-{previous:02d}'/'summary.json').read_bytes())
        OLD.require(summary['status']=='success' and summary['policy_sha256']==freeze['policy_sha256'],
                    'previous case failed or differs')
    record=policy['cases'][index];directory=output/f'case-{index:02d}'
    directory.mkdir(parents=True,exist_ok=False)
    tracker=OLD.RecordedProcesses(directory,oldpolicy['catalogue_hash'])
    summary={'record':record,'status':'failed','policy_sha256':freeze['policy_sha256'],
             'runner_sha256':freeze['runner_sha256']}
    OLD.write(directory/'summary.json',summary)
    try:
        prediction,evidence=compute(record,oldpolicy,report,states,tracker,prior_directory)
        OLD.write(directory/'prediction.json',prediction);summary.update(evidence)
        summary['prediction_sha256']=OLD.digest((directory/'prediction.json').read_bytes())
    except Exception as exc:
        summary['status']='failed';summary['error']=str(exc);raise
    finally:
        summary['processes']=len(tracker.records)
        summary['process_receipts_sha256']=OLD.digest((directory/'processes.json').read_bytes()) if tracker.records else None
        OLD.write(directory/'summary.json',summary)
    print(f"refinement {index:02d}: success, {summary['native_calls']} segments",flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--coarse-dir',type=Path,required=True);parser.add_argument('--prior-dir',type=Path,required=True)
    args=parser.parse_args();run(args.case,args.output_dir,args.coarse_dir,args.prior_dir)
