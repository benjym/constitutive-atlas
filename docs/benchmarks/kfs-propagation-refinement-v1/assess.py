"""Reconstruct all refinement receipts and apply prospectively fixed gates."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('propagation_refinement_runner',HERE/'run_case.py')
RUN=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(RUN)
OLD=RUN.OLD;BASE=RUN.BASE


def gate(coarse_medium,medium_fine,signal,policy):
    for value in (coarse_medium,medium_fine,signal):
        OLD.require(type(value) in (int,float) and math.isfinite(value) and value>=0,'invalid refinement magnitude')
    OLD.require(signal>0,'zero calibration signal cannot define relative separation')
    threshold=policy['separation_fraction']*signal
    return {'coarse_to_medium':coarse_medium,'medium_to_fine':medium_fine,
            'coarse_calibration_response_shift':signal,'threshold':threshold,
            'both_below_separation_threshold':max(coarse_medium,medium_fine)<=threshold,
            'adjacent_change_nonincreasing':medium_fine<=coarse_medium+policy['nonincrease_absolute_floor']}


def assess(directory,coarse_directory,prior_directory):
    policy,freeze,oldpolicy,report,states=RUN.inputs(coarse_directory,prior_directory)
    curves={};records=[]
    for record in policy['cases']:
        path=directory/f"case-{record['index']:02d}"
        summary=OLD.loads((path/'summary.json').read_bytes())
        OLD.require(summary['record']==record and summary['status']=='success' and
                    summary['policy_sha256']==freeze['policy_sha256'] and
                    summary['runner_sha256']==freeze['runner_sha256'],'failed or changed summary')
        tracker=BASE.SavedProcesses(path,summary,oldpolicy['catalogue_hash'])
        prediction,evidence=RUN.compute(record,oldpolicy,report,states,tracker,prior_directory)
        tracker.finish()
        content=(path/'prediction.json').read_bytes()
        OLD.require(OLD.digest(content)==summary['prediction_sha256'],'prediction changed')
        OLD.require(BASE.without_elapsed(prediction)==BASE.without_elapsed(OLD.loads(content)),
                    'native receipts do not reconstruct prediction')
        OLD.require(all(summary[k]==v for k,v in evidence.items()),'saved evidence differs')
        curves[(record['coarse_case_index'],record['maximum_increment'])]=prediction
        records.append(summary)
    coarse=OLD.loads((RUN.ROOT/policy['coarse_results']).read_bytes())
    for case in oldpolicy['cases']:
        index=case['index']
        curves[(index,policy['coarse_increment'])]=OLD.loads((coarse_directory/f'case-{index:02d}'/'prediction.json').read_bytes())
    checks=[]
    for case in oldpolicy['cases']:
        index=case['index'];paired=next(c['index'] for c in oldpolicy['cases'] if
           c['experiment_id']==case['experiment_id'] and c['evaluation_scenario']==case['evaluation_scenario'] and
           c['calibration_scenario']!=case['calibration_scenario'])
        levels=[curves[(index,step)] for step in [policy['coarse_increment'],*policy['fine_increments']]]
        for channel in oldpolicy['channels']:
            scale=coarse['cases'][index]['metrics'][channel]['scale']
            def rms(reference,prediction):
                return OLD.compare_acquisition_linear(reference['points'],prediction,channel,scale)['rmse']/scale
            signal=rms(levels[0],curves[(paired,policy['coarse_increment'])])
            checks.append({'coarse_case':case,'channel':channel,
                           **gate(rms(levels[0],levels[1]),rms(levels[1],levels[2]),signal,policy['gate'])})
    panels=[];effects=[]
    for step in [policy['coarse_increment'],*policy['fine_increments']]:
        if step==policy['coarse_increment']:summaries=coarse['cases']
        else:
            summaries=[]
            for row in records:
                if row['record']['maximum_increment']==step:
                    summaries.append(dict(row,record=oldpolicy['cases'][row['record']['coarse_case_index']]))
        values,changes=BASE.aggregate(summaries,oldpolicy)
        panels.extend(dict(value,maximum_increment=step) for value in values)
        effects.append(dict(changes,maximum_increment=step))
    passed=all(row['both_below_separation_threshold'] and row['adjacent_change_nonincreasing'] for row in checks)
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],
            'runner_sha256':freeze['runner_sha256'],'assessor_sha256':freeze['assessor_sha256'],
            'gate_passed':passed,'checks':checks,'panels':panels,'effects':effects,'cases':records,
            'new_replays':len(records),'new_native_segment_calls':sum(r['native_calls'] for r in records),
            'new_native_process_receipts':sum(r['processes'] for r in records),
            'coarse_native_process_receipts_reconstructed':coarse['native_process_receipts_verified'],
            'new_fits':0,'builds':0,'scientific_admission':False}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True);parser.add_argument('--coarse-dir',type=Path,required=True)
    parser.add_argument('--prior-dir',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();result=assess(args.private_dir,args.coarse_dir,args.prior_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('checks','cases','panels','effects')},indent=2))
    raise SystemExit(0 if result['gate_passed'] else 1)
