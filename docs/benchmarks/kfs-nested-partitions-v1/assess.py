"""Reconstruct modified commands and apply the separately frozen nested-count gates."""
import argparse
import importlib.util
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('nested_partition_runner',HERE/'run_case.py')
RUN=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(RUN)
OLD=RUN.OLD


def assess(directory,fine,coarse,prior):
    policy,freeze,oldpolicy,report,states,schedules=RUN.inputs(fine,coarse,prior)
    records=[];curves={}
    for record in policy['cases']:
        path=directory/f"case-{record['index']:02d}"
        summary=OLD.loads((path/'summary.json').read_bytes())
        OLD.require(summary['record']==record and summary['status']=='success' and
                    summary['policy_sha256']==freeze['policy_sha256'] and summary['runner_sha256']==freeze['runner_sha256'],
                    'case failed or changed')
        tracker=RUN.P.SavedProcesses(path,summary,oldpolicy['catalogue_hash'])
        prediction,evidence,overlays=RUN.compute(record,policy,oldpolicy,report,states,schedules[record['coarse_case_index']],tracker)
        tracker.finish()
        content=(path/'prediction.json').read_bytes();overlay_bytes=(path/'overlays.json').read_bytes()
        OLD.require(OLD.digest(content)==summary['prediction_sha256'] and
                    OLD.digest(overlay_bytes)==summary['overlays_sha256'],'saved output changed')
        OLD.require(RUN.P.without_elapsed(prediction)==RUN.P.without_elapsed(OLD.loads(content)),
                    'native receipts do not reconstruct prediction')
        OLD.require(overlays==OLD.loads(overlay_bytes),'modified caller schedule differs')
        OLD.require(all(summary[k]==v for k,v in evidence.items()),'saved evidence differs')
        records.append(summary);curves[(record['coarse_case_index'],record['multiplier'])]=prediction
    checks=[]
    for ci,baseline in policy['baselines'].items():
        index=int(ci);base=OLD.loads((fine/f"case-{baseline['fine_case_index']:02d}"/'prediction.json').read_bytes())
        for channel in oldpolicy['channels']:
            scale=next(r['metrics'][channel]['scale'] for r in records if r['record']['coarse_case_index']==index)
            def rms(reference,prediction):return OLD.compare_acquisition_linear(reference['points'],prediction,channel,scale)['rmse']/scale
            first=rms(base,curves[(index,2)]);second=rms(curves[(index,2)],curves[(index,4)])
            check=RUN.REF.gate(first,second,policy['calibration_signals'][ci][channel],policy['gate'])
            checks.append({'coarse_case':oldpolicy['cases'][index],'channel':channel,**check,
                           'descriptive_second_to_first_ratio':second/first if first else None})
    numerical_pass=all(c['both_below_separation_threshold'] and c['adjacent_change_nonincreasing'] for c in checks)
    diagnostic_pass=all(r['diagnostics']['rejection_free_two_substep_gate'] for r in records)
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],'runner_sha256':freeze['runner_sha256'],
            'assessor_sha256':freeze['assessor_sha256'],'gate_passed':numerical_pass and diagnostic_pass,
            'numerical_gate_passed':numerical_pass,'rejection_free_gate_passed':diagnostic_pass,
            'checks':checks,'cases':records,'new_replays':len(records),
            'new_native_segment_calls':sum(r['native_calls'] for r in records),
            'new_native_process_receipts':sum(r['processes'] for r in records),
            'baseline_native_process_receipts_reconstructed':policy['baseline_native_process_receipts'],
            'original_refinement_gate_remains_failed':True,'new_fits':0,'builds':0,'scientific_admission':False,
            'scope':'four-case rejection-free nested caller regime; not a new six-test panel, causal proof, asymptotic order or source/binary identity'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True);parser.add_argument('--fine-dir',type=Path,required=True)
    parser.add_argument('--coarse-dir',type=Path,required=True);parser.add_argument('--prior-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=assess(args.private_dir,args.fine_dir,args.coarse_dir,args.prior_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('checks','cases')},indent=2))
    raise SystemExit(0 if result['gate_passed'] else 1)
