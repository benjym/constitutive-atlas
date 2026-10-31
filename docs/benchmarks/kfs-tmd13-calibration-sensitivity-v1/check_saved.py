"""Saved calibration audit and copied-corruption witnesses; no native calls."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('tmd13_saved_assessor',HERE/'assess.py')
MODULE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(MODULE)


def write(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def check(directory):
    result=MODULE.assess(directory)
    if json.dumps(result,indent=2,allow_nan=False)+'\n'!=(HERE/'results.json').read_text():
        raise ValueError('saved scalar reconstruction differs')
    controls=[]
    for variant in ('failed_process_marked_success','failed_candidate_removed','native_parameters_changed','selected_objective_changed'):
        with tempfile.TemporaryDirectory(prefix='tmd13-calibration-negative-') as temporary:
            scratch=Path(temporary);case=scratch/'fit-00';case.mkdir()
            original=directory/'fit-00'
            for source in original.iterdir():
                if source.name not in ('summary.json','processes.json','candidates.jsonl'):
                    (case/source.name).symlink_to(source)
            summary=json.loads((original/'summary.json').read_text())
            ledger=json.loads((original/'processes.json').read_text())
            journal=(original/'candidates.jsonl').read_bytes()
            if variant=='failed_process_marked_success':
                next(r for r in ledger if r.get('native_outcome')=='constitutive_failure')['accepted']=True
            elif variant=='failed_candidate_removed':
                rows=[json.loads(line) for line in journal.splitlines()]
                rows=[r for r in rows if r['completed']]
                journal=('\n'.join(json.dumps(r) for r in rows)+'\n').encode()
            elif variant=='native_parameters_changed':
                command=ledger[1]['command'];command[command.index('--parameters')+1]='0,0,0'
            else:summary['best_objective']+=0.001
            write(case/'processes.json',ledger);(case/'candidates.jsonl').write_bytes(journal)
            summary['process_receipts_sha256']=hashlib.sha256((case/'processes.json').read_bytes()).hexdigest()
            summary['candidate_journal_sha256']=hashlib.sha256(journal).hexdigest();write(case/'summary.json',summary)
            try:MODULE.assess(scratch)
            except ValueError as exc:controls.append({'variant':variant,'rejected':True,'reason':str(exc)})
            else:raise ValueError('corruption accepted: '+variant)
    return {'exact_scalar_replay':True,'candidate_evaluations_verified':result['candidate_evaluations_verified'],
            'native_process_receipts_verified':result['native_processes_verified'],
            'file_control_traces_reproduced':3,'negative_controls':controls,'new_native_calls':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--private-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();result=check(args.private_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
