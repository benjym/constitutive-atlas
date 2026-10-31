"""One serial archived calibration fit; responses and full trace stay private."""
import argparse
import importlib
import importlib.util
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SPEC=importlib.util.spec_from_file_location('locked_native_for_calibration',HERE.parent/'kfs-locked-initialization-sensitivity-v1/run_case.py')
OLD=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(OLD)


def strip_elapsed(value):
    if isinstance(value,dict):return {k:strip_elapsed(v) for k,v in value.items() if k!='elapsed_seconds'}
    if isinstance(value,list):return [strip_elapsed(v) for v in value]
    return value


class CalibrationProcesses(OLD.RecordedProcesses):
    context=None
    def run(self,command,**kwargs):
        record={'index':len(self.records),'command':command,'context':self.context,
                'returncode':None,'accepted':False}
        kwargs['check']=False
        try:
            process=subprocess.run(command,**kwargs)
            stdout,stderr=process.stdout,process.stderr;record['returncode']=process.returncode
        except subprocess.TimeoutExpired as exc:
            record['error']='timeout';self.retain(record,exc.stdout or b'',exc.stderr or b'');raise
        except OSError as exc:
            record['error']=str(exc);self.retain(record,b'',b'');raise
        try:
            raw=OLD.loads(stdout)
            if '--describe' in command:
                OLD.require(process.returncode==0 and raw['sha256']==self.catalogue_hash,'describe failure')
                record['accepted']=True
            else:
                OLD.require(raw.get('catalogue_hash')==self.catalogue_hash and type(raw.get('ok')) is bool,
                            'invalid native contract or catalogue')
                record['accepted']=process.returncode==0 and raw['ok'] is True
                record['native_outcome']='success' if record['accepted'] else 'constitutive_failure'
        except (ValueError,KeyError,TypeError) as exc:
            record['error']=str(exc);raise ValueError(str(exc)) from exc
        finally:self.retain(record,stdout,stderr)
        return process


def inputs():
    content=(HERE/'policy.json').read_bytes();freeze=OLD.loads((HERE/'freeze.json').read_bytes())
    OLD.require(OLD.digest(content)==freeze['policy_sha256'],'policy changed')
    OLD.require(OLD.digest((HERE/'run_fit.py').read_bytes())==freeze['runner_sha256'],'runner changed')
    policy=OLD.loads(content)
    _,_,report,states=OLD.load_inputs() # Shared allocation and exact parameter-accounting gates.
    for path,expected in policy['input_sha256'].items():
        OLD.require(OLD.digest((ROOT/path).read_bytes())==expected,'input changed: '+path)
    config=report['config'];model=next(m for m in config['models'] if m['id']==policy['model']['id'])
    OLD.require(policy['model']==model and policy['calibration_ids']==config['packages']['density3'],
                'model or calibration package differs')
    for field in ('objective','optimizer','steps','samples','maximum_axial_strain'):
        OLD.require(policy[field]==config[field],'historical calibration policy differs: '+field)
    OLD.require(policy['timeout_seconds_per_test']==config['timeout_seconds'],'timeout differs')
    return policy,freeze,report,states


def prepare(policy,report,states,scenario,pilot):
    prepared=[]
    for eid in policy['calibration_ids']:
        content=(ROOT/'paper/results/pilot-matched96/experiments'/(eid+'.json')).read_bytes()
        OLD.require(OLD.digest(content)==policy['experiment_sha256'][eid]==report['experiment_sha256'][eid],
                    'experiment bytes differ')
        experiment=OLD.loads(content)
        OLD.require(experiment['id']==eid and experiment['initial']['void_ratio']==states[eid]['file_initial']['e'] and
                    experiment['initial']['effective_stress']==states[eid]['file_initial']['sigma'],'initial state differs')
        if scenario=='original_table_disputed_e0' and eid=='KFS-TMD13':
            value=policy['initialization'][scenario][eid]
            OLD.require(value==states[eid][scenario]['e'],'alternative scenario differs')
            experiment['initial']['void_ratio']=value
        prepared.append(pilot.prepare_experiment(experiment,report['config']))
    return prepared


def archived_tools(tracker):
    Adapter=OLD.adapter_class(tracker)
    reservations=importlib.import_module('frozen_kfs_native.reservations')
    original_load=reservations.load_policy
    reservations.load_policy=lambda path=ROOT/'paper/results/pilot-matched96/reservation-policy.json':original_load(path)
    return Adapter,importlib.import_module('frozen_kfs_native.pilot')


def run(index,output):
    policy,freeze,report,states=inputs()
    OLD.require(type(index) is int and 0<=index<len(policy['runs']),'invalid run index')
    for previous in range(index):
        result=OLD.loads((output/f'fit-{previous:02d}'/'summary.json').read_bytes())
        OLD.require(result['status']=='completed' and result['policy_sha256']==freeze['policy_sha256'],
                    'previous fit aborted or differs')
    record=policy['runs'][index]
    directory=output/f'fit-{index:02d}';directory.mkdir(parents=True,exist_ok=False)
    tracker=CalibrationProcesses(directory,report['catalogue_hash'])
    summary={'record':record,'status':'failed','policy_sha256':freeze['policy_sha256'],
             'runner_sha256':freeze['runner_sha256']}
    OLD.write(directory/'summary.json',summary)
    try:
        # adapter_class loads only exact archived code. Instantiate after preparing metadata.
        Adapter,pilot=archived_tools(tracker)
        pilot.validate_config(report['config'])
        prepared=prepare(policy,report,states,record['scenario'],pilot)
        adapter=Adapter(ROOT/'paper/results/pilot-matched96/solver/atlas_solver',[policy['model']['id']],
                        ROOT/'paper/results/pilot-matched96/models')
        OLD.require(adapter.solver_hash==report['solver_sha256'],'solver differs')
        completed=[0];simulate=adapter.simulate
        def tracked_simulate(mid,parameters,experiment,*args):
            tracker.context={'candidate':completed[0]+1,'experiment_id':experiment['id']}
            return simulate(mid,parameters,experiment,*args)
        adapter.simulate=tracked_simulate
        def checkpoint(row):
            with (directory/'candidates.jsonl').open('a') as stream:
                stream.write(json.dumps(row,allow_nan=False)+'\n')
            completed[0]=row['evaluation']
            if completed[0]%16==0:print('fit',index,'candidate',completed[0],flush=True)
        fit=pilot.calibrate(policy['model'],prepared,report['config'],adapter,record['seed'],checkpoint)
        adapter.verify_unchanged();OLD.write(directory/'fit.json',fit)
        if record['scenario']=='file_initial':
            calibration=next(c for c in report['calibrations'] if
                             (c['model'],c['package'])==(policy['model']['id'],'density3'))
            oldfit=next(f for f in calibration['fits'] if f['seed']==record['seed'])
            OLD.require(strip_elapsed(fit)==strip_elapsed(oldfit),'file control trace differs')
            summary['exact_numeric_control_trace']=True
        summary.update(status='completed',fit_status=fit['status'],evaluation_count=fit['evaluation_count'],
                       failed_candidates=sum(not r['completed'] for r in fit['trace']),
                       termination=fit['termination'],best_evaluation=fit['best']['evaluation'],
                       best_objective=fit['best']['objective'],best_parameters=fit['best']['parameters'],
                       fit_sha256=OLD.digest((directory/'fit.json').read_bytes()),
                       candidate_journal_sha256=OLD.digest((directory/'candidates.jsonl').read_bytes()))
        print('fit',index,'completed','best calibration objective',summary['best_objective'],flush=True)
    except Exception as exc:
        summary['error']=str(exc);raise
    finally:
        summary['native_processes']=len(tracker.records)
        summary['process_receipts_sha256']=OLD.digest((directory/'processes.json').read_bytes()) if tracker.records else None
        OLD.write(directory/'summary.json',summary)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fit',type=int,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    args=parser.parse_args();run(args.fit,args.output_dir)


if __name__=='__main__':main()
