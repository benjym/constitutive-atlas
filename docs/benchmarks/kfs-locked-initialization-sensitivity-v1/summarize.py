"""Verify private replay receipts and export scalar sensitivity evidence only."""
import argparse
import importlib.util
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('locked_sensitivity_runner',HERE/'run_case.py')
RUNNER=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RUNNER)


def summarize(directory):
    policy, freeze, report, states = RUNNER.load_inputs()
    RUNNER.require(RUNNER.digest((HERE/'summarize.py').read_bytes()) == freeze['summarizer_sha256'],
                   'summarizer changed')
    records=[]
    for index,case in enumerate(policy['cases']):
        path=directory/f'case-{index:02d}'
        summary=RUNNER.loads((path/'summary.json').read_bytes())
        RUNNER.require(summary['case']==case and summary['status']=='success' and
                       summary['policy_sha256']==freeze['policy_sha256'] and
                       summary['runner_sha256']==freeze['runner_sha256'],'case differs or failed')
        ledger_bytes=(path/'processes.json').read_bytes()
        RUNNER.require(RUNNER.digest(ledger_bytes)==summary['process_receipts_sha256'],'process ledger changed')
        ledger=RUNNER.loads(ledger_bytes)
        RUNNER.require(len(ledger)==summary['processes']==summary['native_calls']+1,'process count differs')
        for number,receipt in enumerate(ledger):
            RUNNER.require(receipt['index']==number and receipt['returncode']==0 and
                           receipt['accepted'] is True,'native process not accepted')
            for name in ('stdout','stderr'):
                RUNNER.require(RUNNER.digest((path/receipt[name]).read_bytes())==receipt[name+'_sha256'],
                               'raw process output changed')
            raw=RUNNER.loads((path/receipt['stdout']).read_bytes())
            if number==0:
                RUNNER.require(raw['sha256']==policy['catalogue_hash'],'describe identity mismatch')
            else:
                RUNNER.require(raw.get('ok') is True and raw['catalogue_hash']==policy['catalogue_hash'],
                               'native output unsuccessful')
        prediction=RUNNER.loads((path/'prediction.json').read_bytes())
        experiment,rows,saved=RUNNER.prepare_case(case,policy,report,states)
        RUNNER.require(prediction['status']=='success' and len(prediction['points'])==len(rows),
                       'incomplete prediction')
        if case['scenario']=='file_initial':
            RUNNER.require(prediction['points']==saved['points'] and
                           summary['file_control_exact_numeric_reproduction'] is True,
                           'saved control differs')
        for channel in policy['channels']:
            scale=saved['metrics'][channel]['scale']
            metric=RUNNER.compare_acquisition_linear(rows,prediction,channel,scale)
            RUNNER.require(metric==summary['metrics'][channel],'saved metric differs')
            delta=RUNNER.compare_acquisition_linear(saved['points'],prediction,channel,scale)
            RUNNER.require(delta==summary['response_change_from_saved'][channel],'saved response delta differs')
        records.append(summary)
    reference=RUNNER.loads((RUNNER.ROOT/policy['reference_panel']).read_bytes())
    panels=[]
    for package in ('pressure3','density3'):
        for scenario in ('file_initial','original_table_disputed_e0'):
            values=[]
            for original in reference['records']:
                if (original['model'],original['package'])!=('hypoplastic-sand-vw96',package):
                    continue
                replacement=next((r for r in records if r['case']['package']==package and
                                  r['case']['scenario']==scenario and
                                  r['case']['experiment_id']==original['experiment_id']),None)
                values.extend((replacement['metrics'][c]['scaled_mse'] if replacement else
                               original['channels'][c]['new']['scaled_mse']) for c in policy['channels'])
            RUNNER.require(len(values)==12,'six-test panel incomplete')
            panels.append({'package':package,'scenario':scenario,
                           'root_scaled_mse':math.sqrt(math.fsum(values)/len(values))})
    contrasts=[]
    for scenario in ('file_initial','original_table_disputed_e0'):
        scores={p['package']:p['root_scaled_mse'] for p in panels if p['scenario']==scenario}
        contrasts.append({'scenario':scenario,'density_minus_pressure':scores['density3']-scores['pressure3']})
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],'runner_sha256':freeze['runner_sha256'],
            'summarizer_sha256':freeze['summarizer_sha256'],'cases':records,'panels':panels,'contrasts':contrasts,
            'native_processes':sum(r['processes'] for r in records),
            'native_segment_calls':sum(r['native_calls'] for r in records),
            'file_controls_exact_numeric_reproduction':4,'all_cases_successful':True,
            'scientific_admission':False,'new_fits':0,'builds':0,
            'initialization_conflict_resolved':False,'calibration_state_uncertainty_propagated':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=summarize(args.private_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))


if __name__=='__main__':main()
