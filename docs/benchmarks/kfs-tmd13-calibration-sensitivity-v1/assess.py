"""Reconstruct every calibration objective from private native responses; no solver."""
import argparse
import importlib.util
import json
from pathlib import Path
import types

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('tmd13_fit_runner',HERE/'run_fit.py')
RUN=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(RUN)
OLD=RUN.OLD


def choose_start(summaries,scenario):
    successful=[s for s in summaries if s['record']['scenario']==scenario and s['fit_status']=='success']
    return min(successful,key=lambda s:s['best_objective']) if successful else None


def assess(directory):
    policy,freeze,report,states=RUN.inputs()
    OLD.require(OLD.digest((HERE/'assess.py').read_bytes())==freeze['assessor_sha256'],'assessor changed')
    _,pilot=RUN.archived_tools(types.SimpleNamespace(run=None)) # Load Python source only.
    definition=OLD.loads((RUN.ROOT/'paper/results/pilot-matched96/models/hypoplastic-sand-vw96.json').read_bytes())
    summaries=[];processes=0;candidate_count=0
    for record in policy['runs']:
        path=directory/f"fit-{record['index']:02d}"
        summary=OLD.loads((path/'summary.json').read_bytes())
        OLD.require(summary['record']==record and summary['status']=='completed' and
                    summary['policy_sha256']==freeze['policy_sha256'] and
                    summary['runner_sha256']==freeze['runner_sha256'],'fit failed or changed')
        contents={name:(path/name).read_bytes() for name in ('fit.json','candidates.jsonl','processes.json')}
        for name,key in (('fit.json','fit_sha256'),('candidates.jsonl','candidate_journal_sha256'),('processes.json','process_receipts_sha256')):
            OLD.require(OLD.digest(contents[name])==summary[key],'private fit evidence changed: '+name)
        fit=OLD.loads(contents['fit.json']);ledger=OLD.loads(contents['processes.json'])
        journal=[OLD.loads(line) for line in contents['candidates.jsonl'].splitlines()]
        OLD.require(journal==fit['trace'],'candidate journal differs from final fit')
        OLD.require(len(journal)==fit['evaluation_count']==summary['evaluation_count'] and
                    len(journal)<=policy['optimizer']['max_evaluations'],'budget/count mismatch')
        OLD.require(len(ledger)==1+len(journal)*len(policy['calibration_ids'])==summary['native_processes'],
                    'missing native test attempts')
        raw_outputs=[]
        for index,receipt in enumerate(ledger):
            OLD.require(receipt['index']==index,'process order differs')
            for stream in ('stdout','stderr'):
                OLD.require(OLD.digest((path/receipt[stream]).read_bytes())==receipt[stream+'_sha256'],'raw output changed')
            if receipt.get('error')=='timeout':
                OLD.require(receipt['accepted'] is False,'timeout marked successful');raw_outputs.append(None);continue
            OLD.require('error' not in receipt,'aborted transport cannot form completed fit')
            raw=OLD.loads((path/receipt['stdout']).read_bytes());raw_outputs.append(raw)
            if index==0:
                OLD.require(receipt['returncode']==0 and raw['sha256']==report['catalogue_hash'] and receipt['accepted'] is True,
                            'describe failed or changed')
            else:
                OLD.require(type(raw.get('ok')) is bool and raw['catalogue_hash']==report['catalogue_hash'],
                            'invalid native response contract')
                OLD.require(receipt['accepted']==(receipt['returncode']==0 and raw['ok'] is True),
                            'native failure/success classification differs')
        prepared=RUN.prepare(policy,report,states,record['scenario'],pilot)
        for number,row in enumerate(journal,1):
            OLD.require(row['evaluation']==number and len(row['tests'])==len(prepared),'candidate coverage differs')
            metrics=[]
            for position,item in enumerate(prepared):
                index=1+(number-1)*len(prepared)+position;receipt=ledger[index];raw=raw_outputs[index]
                eid=item['experiment']['id'];test=row['tests'][position]
                OLD.require(receipt['context']=={'candidate':number,'experiment_id':eid} and test['experiment_id']==eid,
                            'candidate/test context differs')
                command=receipt['command']
                def argument(name):return command[command.index(name)+1]
                expected_state=item['experiment']['initial']['effective_stress']+[item['experiment']['initial']['void_ratio']]
                OLD.require(argument('--parameters')==','.join(str(row['parameters'][n]) for n in definition['parameters']) and
                            argument('--initial')==','.join(map(str,expected_state)) and
                            argument('--target')==repr(item['target']) and argument('--steps')==str(policy['steps']) and
                            argument('--protocol')=='1','native candidate/input binding differs')
                if raw is None:prediction={'status':'timeout','points':[]}
                else:
                    prediction={'status':'success' if receipt['accepted'] else 'integration_failure',
                                'points':[{'axial_strain':p['strain'][0],'q':p['q_signed'],
                                           'volumetric_strain':sum(p['strain'][:3])} for p in raw.get('points',[])]}
                measured=pilot.score_prediction(item,prediction,policy['samples'])
                OLD.require(measured==test['metrics'] and prediction['status']==test['status'],
                            'candidate metric or failure status differs')
                metrics.append(measured)
            completed=all(m is not None for m in metrics)
            objective=(sum(sum(c['scaled_mse'] for c in m.values())/2 for m in metrics)/len(metrics)
                       if completed else policy['optimizer']['failure_objective'])
            OLD.require(row['completed'] is completed and row['objective']==objective,'candidate objective differs')
        best=min(journal,key=lambda r:r['objective'])
        OLD.require(fit['best']==best and best['objective']==summary['best_objective'] and
                    best['parameters']==summary['best_parameters'],'best calibration candidate differs')
        if record['scenario']=='file_initial':
            previous=next(c for c in report['calibrations'] if (c['model'],c['package'])==(policy['model']['id'],'density3'))
            expected=next(f for f in previous['fits'] if f['seed']==record['seed'])
            OLD.require(RUN.strip_elapsed(fit)==RUN.strip_elapsed(expected) and summary['exact_numeric_control_trace'] is True,
                        'file control not reproduced')
        summaries.append(summary);processes+=len(ledger);candidate_count+=len(journal)
    selected={}
    for scenario in ('file_initial','original_table_disputed_e0'):
        chosen=choose_start(summaries,scenario)
        selected[scenario]=None if chosen is None else {'seed':chosen['record']['seed'],
            'fit_index':chosen['record']['index'],'parameters':chosen['best_parameters'],
            'calibration_objective':chosen['best_objective'],'termination':chosen['termination'],
            'fit_sha256':chosen['fit_sha256']}
    return {'id':policy['id'],'policy_sha256':freeze['policy_sha256'],'runner_sha256':freeze['runner_sha256'],
            'assessor_sha256':freeze['assessor_sha256'],'fits':summaries,'selected':selected,
            'native_processes_verified':processes,'candidate_evaluations_verified':candidate_count,
            'file_control_traces_reproduced':3,'new_fits':6,'evaluation_replays':0,'builds':0,
            'scientific_admission':False,'scope':'calibration-state sensitivity; no evaluation response claim'}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--private-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();result=assess(args.private_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ('selected','native_processes_verified','candidate_evaluations_verified')},indent=2))


if __name__=='__main__':main()
