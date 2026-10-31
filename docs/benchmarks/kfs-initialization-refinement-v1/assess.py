"""Audit private refinement responses and apply frozen output-separation gates."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('initialization_refinement_runner',HERE/'run_case.py')
RUN=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(RUN)
OLD=RUN.OLD


def separation_gate(coarse_medium,medium_fine,signal,policy):
    for value in (coarse_medium,medium_fine,signal):
        OLD.require(type(value) in (int,float) and math.isfinite(value) and value>=0,'invalid refinement magnitude')
    OLD.require(signal>0,'zero initialization signal cannot define relative separation')
    threshold=policy['gate']['separation_fraction']*signal
    return {'coarse_to_medium':coarse_medium,'medium_to_fine':medium_fine,
            'coarse_initialization_signal':signal,'threshold':threshold,
            'both_below_separation_threshold':max(coarse_medium,medium_fine)<=threshold,
            'adjacent_change_nonincreasing':medium_fine<=coarse_medium+policy['gate']['nonincrease_absolute_floor']}


def assess(directory,coarse_directory):
    policy,freeze,oldpolicy,report,states=RUN.inputs(coarse_directory)
    predictions={};summaries=[]
    for record in policy['cases']:
        index=record['index'];path=directory/f'case-{index:02d}'
        summary=OLD.loads((path/'summary.json').read_bytes())
        OLD.require(summary['record']==record and summary['status']=='success' and
                    summary['policy_sha256']==freeze['policy_sha256'] and
                    summary['runner_sha256']==freeze['runner_sha256'],'case failed or changed')
        ledger_bytes=(path/'processes.json').read_bytes();ledger=OLD.loads(ledger_bytes)
        OLD.require(OLD.digest(ledger_bytes)==summary['process_receipts_sha256'],'ledger changed')
        OLD.require(len(ledger)==summary['processes']==summary['native_calls']+1,'process count differs')
        for i,receipt in enumerate(ledger):
            OLD.require(receipt['index']==i and receipt['returncode']==0 and receipt['accepted'] is True,
                        'native process failed')
            for name in ('stdout','stderr'):
                OLD.require(OLD.digest((path/receipt[name]).read_bytes())==receipt[name+'_sha256'],'raw output changed')
            raw=OLD.loads((path/receipt['stdout']).read_bytes())
            if i==0:OLD.require(raw['sha256']==oldpolicy['catalogue_hash'],'catalogue changed')
            else:OLD.require(raw.get('ok') is True and raw['catalogue_hash']==oldpolicy['catalogue_hash'],'native output failed')
        content=(path/'prediction.json').read_bytes()
        OLD.require(OLD.digest(content)==summary['prediction_sha256'],'prediction changed')
        prediction=OLD.loads(content)
        _,rows,saved=OLD.prepare_case(record['case'],oldpolicy,report,states)
        for channel in oldpolicy['channels']:
            metric=OLD.compare_acquisition_linear(rows,prediction,channel,saved['metrics'][channel]['scale'])
            OLD.require(metric==summary['metrics'][channel],'metric changed')
        predictions[(record['coarse_case_index'],record['maximum_increment'])]=prediction
        summaries.append(summary)
    coarse=OLD.loads((RUN.ROOT/policy['coarse_results']).read_bytes())
    checks=[];signals=[]
    for index,case in enumerate(oldpolicy['cases']):
        curves=[OLD.loads((coarse_directory/f'case-{index:02d}'/'prediction.json').read_bytes()),
                predictions[(index,0.0001)],predictions[(index,0.00005)]]
        paired_alt=index+1 if case['scenario']=='file_initial' else index
        signal_summary=coarse['cases'][paired_alt]
        for channel in oldpolicy['channels']:
            scale=signal_summary['metrics'][channel]['scale']
            cm=OLD.compare_acquisition_linear(curves[0]['points'],curves[1],channel,scale)['rmse']/scale
            mf=OLD.compare_acquisition_linear(curves[1]['points'],curves[2],channel,scale)['rmse']/scale
            signal=math.sqrt(signal_summary['response_change_from_saved'][channel]['scaled_mse'])
            checks.append({'coarse_case_index':index,'package':case['package'],
                           'experiment_id':case['experiment_id'],'scenario':case['scenario'],'channel':channel,
                           **separation_gate(cm,mf,signal,policy)})
        if case['scenario']=='file_initial':
            for step,curve in zip((0.0002,0.0001,0.00005),curves):
                alternative=(OLD.loads((coarse_directory/f'case-{index+1:02d}'/'prediction.json').read_bytes())
                             if step==0.0002 else predictions[(index+1,step)])
                signals.append({'package':case['package'],'experiment_id':case['experiment_id'],
                                'maximum_increment':step,'normalized_rms_initialization_shift':{
                                    c:OLD.compare_acquisition_linear(curve['points'],alternative,c,
                                       signal_summary['metrics'][c]['scale'])['rmse']/signal_summary['metrics'][c]['scale']
                                    for c in oldpolicy['channels']}})
    passed=all(c['both_below_separation_threshold'] and c['adjacent_change_nonincreasing'] for c in checks)
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],'runner_sha256':freeze['runner_sha256'],
            'assessor_sha256':freeze['assessor_sha256'],'gate_passed':passed,'checks':checks,
            'initialization_shifts':signals,'cases':summaries,'new_replays':len(summaries),
            'new_native_segment_calls':sum(s['native_calls'] for s in summaries),
            'new_native_processes':sum(s['processes'] for s in summaries),
            'new_fits':0,'builds':0,'scientific_admission':False,'tmd13_calibration_propagated':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True);parser.add_argument('--coarse-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=assess(args.private_dir,args.coarse_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('gate_passed','new_replays','new_native_segment_calls','new_native_processes')},indent=2))
    raise SystemExit(0 if result['gate_passed'] else 1)


if __name__=='__main__':main()
