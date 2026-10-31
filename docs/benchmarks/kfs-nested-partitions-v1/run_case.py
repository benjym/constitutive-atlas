"""Eight bounded nested-count replays; the only command overlay changes --steps."""
import argparse
import importlib.util
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
SPEC=importlib.util.spec_from_file_location('nested_partition_diagnostic',HERE.parent/'kfs-partition-diagnostic-v1/analyze.py')
D=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(D)
REF=D.A;P=REF.BASE;R=P.RUN;OLD=P.OLD


def schedule(directory):
    ledger=OLD.loads((directory/'processes.json').read_bytes());rows=[]
    for receipt in ledger[1:]:
        raw=OLD.loads((directory/receipt['stdout']).read_bytes());command=receipt['command']
        count=int(command[command.index('--steps')+1]);target=float(command[command.index('--target')+1])
        OLD.require(raw['steps']==count and raw['target']==target and len(raw['points'])==count+1,'baseline echo differs')
        OLD.require(all(p['substeps']==2 and p['rejected']==0 for p in raw['points'][1:]),'baseline is not rejection-free')
        rows.append({'steps':count,'target':target,'axial_coordinates':[p['strain'][0] for p in raw['points']]})
    return rows


def encoded(value):return __import__('json').dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def inputs(fine,coarse,prior):
    freeze=OLD.loads((HERE/'freeze.json').read_bytes())
    for name,key in [('policy.json','policy_sha256'),('run_case.py','runner_sha256'),('assess.py','assessor_sha256')]:
        OLD.require(OLD.digest((HERE/name).read_bytes())==freeze[key],name+' changed')
    policy=OLD.loads((HERE/'policy.json').read_bytes())
    for name,sha in policy['input_sha256'].items():OLD.require(OLD.digest((ROOT/name).read_bytes())==sha,'input changed: '+name)
    diagnostic=D.analyze(fine,coarse,prior)
    OLD.require(diagnostic==OLD.loads((HERE.parent/'kfs-partition-diagnostic-v1/results.json').read_bytes()),'baseline diagnostic differs')
    OLD.require(diagnostic['native_process_receipts_reconstructed']==policy['baseline_native_process_receipts'],'baseline receipt count differs')
    oldpolicy,_,report,states=R.inputs();schedules={}
    expected=[]
    for ci,baseline in policy['baselines'].items():
        index=int(ci);directory=fine/f"case-{baseline['fine_case_index']:02d}"
        for name,key in [('prediction.json','prediction_sha256'),('processes.json','ledger_sha256')]:
            OLD.require(OLD.digest((directory/name).read_bytes())==baseline[key],'baseline changed')
        schedules[index]=schedule(directory)
        OLD.require(OLD.digest(encoded(schedules[index]))==baseline['schedule_sha256'],'baseline schedule differs')
        for multiplier in (2,4):expected.append({'index':len(expected),'coarse_case_index':index,'multiplier':multiplier})
    OLD.require(expected==policy['cases'],'case coverage/order differs')
    return policy,freeze,oldpolicy,report,states,schedules


class NestedCounts:
    def __init__(self,tracker,baseline,multiplier,tolerance):
        OLD.require(type(multiplier) is int and multiplier in (2,4),'invalid nested multiplier')
        self.tracker=tracker;self.baseline=baseline;self.multiplier=multiplier;self.tolerance=tolerance
        self.overlays=[];self.caller_points=0;self.substeps=0;self.rejected=0
        self.rejection_free=True;self.maximum_knot_difference=0.

    def run(self,command,**kwargs):
        if '--describe' in command:return self.tracker.run(command,**kwargs)
        index=len(self.overlays);OLD.require(index<len(self.baseline),'extra native segment')
        row=self.baseline[index]
        OLD.require(command.count('--steps')==1 and command.count('--target')==1,'ambiguous command overlay')
        position=command.index('--steps')+1;target=float(command[command.index('--target')+1])
        OLD.require(int(command[position])==row['steps'] and target==row['target'],'archived request differs from baseline')
        count=row['steps']*self.multiplier
        OLD.require(1<=count<=5000,'nested caller count exceeds native limit')
        actual=list(command);actual[position]=str(count)
        self.overlays.append({'segment_index':index,'requested_steps':row['steps'],'actual_steps':count,'target':target})
        process=self.tracker.run(actual,**kwargs);raw=OLD.loads(process.stdout)
        OLD.require(raw['steps']==count and raw['target']==target and len(raw['points'])==count+1,'nested native echo differs')
        for i,coordinate in enumerate(row['axial_coordinates']):
            difference=abs(raw['points'][i*self.multiplier]['strain'][0]-coordinate)
            self.maximum_knot_difference=max(self.maximum_knot_difference,difference)
            OLD.require(difference<=self.tolerance,'requested caller knots are not nested')
        for point in raw['points'][1:]:
            substeps=point['substeps'];rejected=point['rejected']
            OLD.require(type(substeps) is int and type(rejected) is int and substeps>0 and rejected>=0,'invalid counters')
            self.caller_points+=1;self.substeps+=substeps;self.rejected+=rejected
            self.rejection_free &= substeps==2 and rejected==0
        return process

    def finish(self):OLD.require(len(self.overlays)==len(self.baseline),'missing native segments')

    def diagnostics(self):
        return {'caller_points':self.caller_points,'reported_substeps':self.substeps,
                'reported_rejected':self.rejected,'rejection_free_two_substep_gate':self.rejection_free,
                'maximum_nested_axial_knot_difference':self.maximum_knot_difference}


def compute(record,policy,oldpolicy,report,states,baseline,tracker):
    case=oldpolicy['cases'][record['coarse_case_index']]
    experiment,rows,saved=R.prepare(case,oldpolicy,report,states)
    overlay=NestedCounts(tracker,baseline,record['multiplier'],policy['nested_knot_absolute_tolerance'])
    prediction=R.predict(case,dict(oldpolicy,maximum_increment=policy['baseline_increment']),experiment,rows,overlay)
    overlay.finish()
    OLD.require(prediction['status']=='success' and prediction['completed_observations']==len(rows),'failed or incomplete replay')
    OLD.require(overlay.substeps==prediction['diagnostics']['substeps'] and overlay.rejected==prediction['diagnostics']['rejected'],
                'nested aggregate diagnostics differ')
    scales={'q':sum(experiment['initial']['effective_stress'][:3])/3,'volumetric_strain':oldpolicy['volumetric_strain_scale']}
    summary={'record':record,'status':'success','native_calls':prediction['native_calls'],'observations':len(rows),
             'diagnostics':overlay.diagnostics(),
             'metrics':{c:OLD.compare_acquisition_linear(rows,prediction,c,scales[c]) for c in oldpolicy['channels']}}
    return prediction,summary,overlay.overlays


def run(index,output,fine,coarse,prior):
    policy,freeze,oldpolicy,report,states,schedules=inputs(fine,coarse,prior)
    OLD.require(type(index) is int and 0<=index<len(policy['cases']),'invalid case index')
    for previous in range(index):
        s=OLD.loads((output/f'case-{previous:02d}'/'summary.json').read_bytes())
        OLD.require(s['status']=='success' and s['policy_sha256']==freeze['policy_sha256'],'previous case failed or changed')
    record=policy['cases'][index];directory=output/f'case-{index:02d}';directory.mkdir(parents=True,exist_ok=False)
    tracker=OLD.RecordedProcesses(directory,oldpolicy['catalogue_hash'])
    summary={'record':record,'status':'failed','policy_sha256':freeze['policy_sha256'],'runner_sha256':freeze['runner_sha256']}
    OLD.write(directory/'summary.json',summary)
    try:
        prediction,evidence,overlays=compute(record,policy,oldpolicy,report,states,schedules[record['coarse_case_index']],tracker)
        OLD.write(directory/'prediction.json',prediction);OLD.write(directory/'overlays.json',overlays)
        summary.update(evidence)
        summary['prediction_sha256']=OLD.digest((directory/'prediction.json').read_bytes())
        summary['overlays_sha256']=OLD.digest((directory/'overlays.json').read_bytes())
    except Exception as exc:
        summary['status']='failed';summary['error']=str(exc);raise
    finally:
        summary['processes']=len(tracker.records)
        summary['process_receipts_sha256']=OLD.digest((directory/'processes.json').read_bytes()) if tracker.records else None
        OLD.write(directory/'summary.json',summary)
    print(f"nested {index}: success, {summary['native_calls']} segments, rejection-free={summary['diagnostics']['rejection_free_two_substep_gate']}",flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case',type=int,required=True);parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--fine-dir',type=Path,required=True);parser.add_argument('--coarse-dir',type=Path,required=True)
    parser.add_argument('--prior-dir',type=Path,required=True);args=parser.parse_args()
    run(args.case,args.output_dir,args.fine_dir,args.coarse_dir,args.prior_dir)
