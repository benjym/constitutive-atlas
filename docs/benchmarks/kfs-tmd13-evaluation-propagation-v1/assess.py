"""Reconstruct native replay commands/predictions offline and report factorial errors."""
import argparse
import importlib.util
import math
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('propagation_runner',HERE/'run_case.py')
RUN=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(RUN)
OLD=RUN.OLD


def without_elapsed(value):
    if isinstance(value,dict):return {k:without_elapsed(v) for k,v in value.items() if k!='elapsed_seconds'}
    if isinstance(value,list):return [without_elapsed(v) for v in value]
    return value


class SavedProcesses:
    """Never launches a process: each requested command must equal the next receipt."""
    def __init__(self,directory,summary,catalogue_hash):
        self.directory=directory;self.catalogue_hash=catalogue_hash;self.index=0
        content=(directory/'processes.json').read_bytes()
        OLD.require(OLD.digest(content)==summary['process_receipts_sha256'],'ledger changed')
        self.records=OLD.loads(content)
        OLD.require(len(self.records)==summary['processes']==summary['native_calls']+1,'process count differs')

    def run(self,command,**kwargs):
        OLD.require(self.index<len(self.records),'missing native receipt')
        receipt=self.records[self.index]
        OLD.require(receipt['index']==self.index and receipt['command']==command,'native command/order differs')
        OLD.require(receipt['returncode']==0 and receipt['accepted'] is True,'unsuccessful process receipt')
        contents={}
        for name in ('stdout','stderr'):
            content=(self.directory/receipt[name]).read_bytes()
            OLD.require(OLD.digest(content)==receipt[name+'_sha256'],'raw output changed')
            contents[name]=content.decode()
        raw=OLD.loads(contents['stdout'])
        if '--describe' in command:OLD.require(raw['sha256']==self.catalogue_hash,'catalogue differs')
        else:OLD.require(raw.get('ok') is True and raw.get('catalogue_hash')==self.catalogue_hash,'native output unsuccessful')
        self.index+=1
        return subprocess.CompletedProcess(command,0,contents['stdout'],contents['stderr'])

    def finish(self):OLD.require(self.index==len(self.records),'unused native receipts')


def aggregate(records,policy):
    panels=[]
    for calibration in (RUN.FILE,RUN.ALT):
        for evaluation in (RUN.FILE,RUN.ALT):
            values=[];case_indices=[]
            for eid in policy['evaluation_ids']:
                scenario=evaluation if eid in policy['disputed_evaluation_ids'] else RUN.FILE
                matches=[r for r in records if r['record']['calibration_scenario']==calibration and
                         r['record']['evaluation_scenario']==scenario and r['record']['experiment_id']==eid]
                OLD.require(len(matches)==1,'missing or duplicate panel member')
                row=matches[0];case_indices.append(row['record']['index'])
                values.extend(row['metrics'][c]['scaled_mse'] for c in policy['channels'])
            OLD.require(len(values)==12 and all(math.isfinite(v) and v>=0 for v in values),'invalid panel')
            panels.append({'calibration_scenario':calibration,'evaluation_scenario':evaluation,
                           'root_scaled_mse':math.sqrt(math.fsum(values)/len(values)),
                           'case_indices':case_indices,'tests':6,'channel_scores':12})
    scores={(r['calibration_scenario'],r['evaluation_scenario']):r['root_scaled_mse'] for r in panels}
    a=scores[(RUN.FILE,RUN.FILE)];b=scores[(RUN.ALT,RUN.FILE)]
    c=scores[(RUN.FILE,RUN.ALT)];d=scores[(RUN.ALT,RUN.ALT)]
    return panels,{'calibration_only_change':b-a,'evaluation_only_change':c-a,
                   'combined_change':d-a,'interaction_in_root_error':d-b-c+a,
                   'definition':'signed differences of root mean scaled MSE, not variance decomposition'}


def assess(directory,prior_directory):
    policy,freeze,report,states=RUN.inputs()
    OLD.require(OLD.digest((HERE/'assess.py').read_bytes())==freeze['assessor_sha256'],'assessor changed')
    records=[]
    for record in policy['cases']:
        path=directory/f"case-{record['index']:02d}"
        summary=OLD.loads((path/'summary.json').read_bytes())
        OLD.require(summary['record']==record and summary['status']=='success' and
                    summary['policy_sha256']==freeze['policy_sha256'] and
                    summary['runner_sha256']==freeze['runner_sha256'],'summary failed or changed')
        tracker=SavedProcesses(path,summary,policy['catalogue_hash'])
        experiment,rows,saved=RUN.prepare(record,policy,report,states)
        prediction=RUN.predict(record,policy,experiment,rows,tracker);tracker.finish()
        content=(path/'prediction.json').read_bytes()
        OLD.require(OLD.digest(content)==summary['prediction_sha256'],'prediction changed')
        OLD.require(without_elapsed(prediction)==without_elapsed(OLD.loads(content)),
                    'native receipts do not reconstruct prediction')
        checked=RUN.evidence(record,policy,experiment,rows,saved,prediction,prior_directory)
        OLD.require(all(summary[k]==v for k,v in checked.items()),'saved evidence differs')
        records.append(summary)
    panels,effects=aggregate(records,policy)
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],
            'runner_sha256':freeze['runner_sha256'],'assessor_sha256':freeze['assessor_sha256'],
            'cases':records,'panels':panels,'effects':effects,'replays':len(records),
            'native_segment_calls':sum(r['native_calls'] for r in records),
            'native_process_receipts_verified':sum(r['processes'] for r in records),
            'historical_file_controls':sum(r['control']=='historical_selected_points' for r in records),
            'prior_alternative_controls':sum(r['control']=='prior_locked_alternative_points' for r in records),
            'new_fits':0,'builds':0,'scientific_admission':False,'source_conflict_resolved':False,
            'scope':'single-resolution archived development sensitivity at calibration-only selected vectors'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True);parser.add_argument('--prior-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=assess(args.private_dir,args.prior_dir)
    with args.output.open('x') as stream:stream.write(__import__('json').dumps(result,indent=2,allow_nan=False)+'\n')
    print(__import__('json').dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
