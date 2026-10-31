"""One frozen refinement replay per call, using the prior archived adapter."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SPEC=importlib.util.spec_from_file_location('coarse_initialization_summary',HERE.parent/'kfs-locked-initialization-sensitivity-v1/summarize.py')
BASE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BASE)
OLD=BASE.RUNNER


def inputs(coarse_directory):
    content=(HERE/'policy.json').read_bytes()
    freeze=OLD.loads((HERE/'freeze.json').read_bytes())
    OLD.require(OLD.digest(content)==freeze['policy_sha256'],'refinement policy changed')
    for name,key in (('run_case.py','runner_sha256'),('assess.py','assessor_sha256')):
        OLD.require(OLD.digest((HERE/name).read_bytes())==freeze[key],'refinement source changed')
    policy=OLD.loads(content)
    for path,expected in policy['input_sha256'].items():
        OLD.require(OLD.digest((ROOT/path).read_bytes())==expected,'input changed: '+path)
    coarse=BASE.summarize(coarse_directory)
    OLD.require(json.dumps(coarse,indent=2,allow_nan=False)+'\n'==(ROOT/policy['coarse_results']).read_text(),
                'coarse evidence differs')
    for index,expected in policy['coarse_prediction_sha256'].items():
        OLD.require(OLD.digest((coarse_directory/f'case-{int(index):02d}'/'prediction.json').read_bytes())==expected,
                    'coarse curve changed')
    oldpolicy,_,report,states=OLD.load_inputs()
    return policy,freeze,oldpolicy,report,states


def run(index, output, coarse_directory):
    policy,freeze,oldpolicy,report,states=inputs(coarse_directory)
    OLD.require(type(index) is int and 0<=index<len(policy['cases']),'invalid index')
    for previous in range(index):
        result=OLD.loads((output/f'case-{previous:02d}'/'summary.json').read_bytes())
        OLD.require(result['status']=='success' and result['policy_sha256']==freeze['policy_sha256'],
                    'previous replay failed or differs')
    record=policy['cases'][index];case=record['case']
    OLD.require(case==oldpolicy['cases'][record['coarse_case_index']],'case identity differs')
    experiment,rows,saved=OLD.prepare_case(case,oldpolicy,report,states)
    directory=output/f'case-{index:02d}';directory.mkdir(parents=True,exist_ok=False)
    tracker=OLD.RecordedProcesses(directory,oldpolicy['catalogue_hash'])
    summary={'record':record,'status':'failed','policy_sha256':freeze['policy_sha256'],
             'runner_sha256':freeze['runner_sha256']}
    OLD.write(directory/'summary.json',summary)
    try:
        adapter=OLD.adapter_class(tracker)(ROOT/'paper/results/pilot-matched96/solver/atlas_solver',
                                          [case['model']],ROOT/'paper/results/pilot-matched96/models')
        OLD.require(adapter.solver_hash==oldpolicy['solver_sha256'],'solver differs')
        prediction=adapter.replay(case['model'],case['parameters'],experiment,
                                  [r['axial_strain'] for r in rows],record['maximum_increment'],
                                  policy['timeout_per_replay_seconds'])
        OLD.write(directory/'prediction.json',prediction)
        OLD.require(prediction['status']=='success' and prediction['completed_observations']==len(rows),
                    'incomplete or failed replay: '+prediction['message'])
        summary['metrics']={c:OLD.compare_acquisition_linear(rows,prediction,c,saved['metrics'][c]['scale'])
                            for c in oldpolicy['channels']}
        summary['native_calls']=prediction['native_calls']
        summary['maximum_radial_stress_drift_Pa']=prediction['maximum_radial_stress_drift_Pa']
        summary['prediction_sha256']=OLD.digest((directory/'prediction.json').read_bytes())
        summary['status']='success'
    except Exception as exc:
        summary['error']=str(exc)
        raise
    finally:
        summary['processes']=len(tracker.records)
        summary['process_receipts_sha256']=OLD.digest((directory/'processes.json').read_bytes()) if tracker.records else None
        OLD.write(directory/'summary.json',summary)
    print(json.dumps({'index':index,'status':summary['status'],'processes':summary['processes']},indent=2))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--coarse-dir',type=Path,required=True)
    args=parser.parse_args();run(args.case,args.output_dir,args.coarse_dir)


if __name__=='__main__':main()
