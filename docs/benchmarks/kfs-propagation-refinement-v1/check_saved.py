"""Exact saved scalar replay and copied-record corruption witnesses; no native calls."""
import argparse
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('propagation_refinement_saved_assessor',HERE/'assess.py')
A=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(A)
OLD=A.OLD


def check(directory,coarse_directory,prior_directory):
    result=A.assess(directory,coarse_directory,prior_directory)
    OLD.require(result==OLD.loads((HERE/'results.json').read_bytes()),'saved scalar result differs')
    negatives=[]
    for variant in ('altered_command','false_success_nonzero','altered_prediction','altered_score'):
        with tempfile.TemporaryDirectory(prefix='atlas-propagation-corruption-') as temporary:
            scratch=Path(temporary)
            for index in range(1,32):(scratch/f'case-{index:02d}').symlink_to(directory/f'case-{index:02d}',target_is_directory=True)
            path=scratch/'case-00';path.mkdir()
            for original in (directory/'case-00').iterdir():
                if original.name in ('summary.json','prediction.json','processes.json'):shutil.copy2(original,path/original.name)
                else:(path/original.name).symlink_to(original)
            summary=OLD.loads((path/'summary.json').read_bytes())
            ledger=OLD.loads((path/'processes.json').read_bytes())
            if variant=='altered_command':
                command=ledger[1]['command'];command[command.index('--target')+1]='0.099'
            elif variant=='false_success_nonzero':ledger[1]['returncode']=23
            elif variant=='altered_prediction':
                prediction=OLD.loads((path/'prediction.json').read_bytes())
                prediction['points'][1]['q']+=1
                OLD.write(path/'prediction.json',prediction)
                summary['prediction_sha256']=OLD.digest((path/'prediction.json').read_bytes())
            else:summary['metrics']['q']['scaled_mse']+=.1
            OLD.write(path/'processes.json',ledger)
            summary['process_receipts_sha256']=OLD.digest((path/'processes.json').read_bytes())
            OLD.write(path/'summary.json',summary)
            try:A.assess(scratch,coarse_directory,prior_directory)
            except ValueError as exc:negatives.append({'variant':variant,'rejected':True,'reason':str(exc)})
            else:raise ValueError('corruption accepted: '+variant)
    return {'exact_scalar_replay':True,'new_native_process_receipts_reconstructed':result['new_native_process_receipts'],
            'coarse_native_process_receipts_reconstructed':result['coarse_native_process_receipts_reconstructed'],
            'gate_passed':result['gate_passed'],
            'failed_checks':sum(not (c['both_below_separation_threshold'] and c['adjacent_change_nonincreasing']) for c in result['checks']),
            'negative_controls':negatives,'new_native_calls':0}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True);parser.add_argument('--coarse-dir',type=Path,required=True)
    parser.add_argument('--prior-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=check(args.private_dir.resolve(),args.coarse_dir.resolve(),args.prior_dir.resolve())
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(result,indent=2))
