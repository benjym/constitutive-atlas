"""Check deterministic scalar replay and rejection witnesses; never run a solver."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('saved_locked_summary',HERE/'summarize.py')
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def write(path, value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def check(directory):
    result=MODULE.summarize(directory)
    expected=(HERE/'results.json').read_text()
    if json.dumps(result,indent=2,allow_nan=False)+'\n' != expected:
        raise ValueError('deterministic scalar replay differs')
    controls=[]
    for variant in ('nonzero_exit','duplicate_json','changed_control_point','changed_metric'):
        with tempfile.TemporaryDirectory(prefix='kfs-receipt-negative-') as temporary:
            scratch=Path(temporary)
            case=scratch/'case-00'
            shutil.copytree(directory/'case-00',case)
            summary=json.loads((case/'summary.json').read_text())
            ledger=json.loads((case/'processes.json').read_text())
            if variant=='nonzero_exit':
                ledger[1]['returncode']=23
            elif variant=='duplicate_json':
                path=case/ledger[1]['stdout']
                text=path.read_text()
                # Keep the original payload, but duplicate a key in the root object.
                text=text[:text.rfind('}')]+',"ok":true'+text[text.rfind('}'):]
                path.write_text(text)
                ledger[1]['stdout_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            elif variant=='changed_control_point':
                path=case/'prediction.json';prediction=json.loads(path.read_text())
                prediction['points'][-1]['q']+=1
                write(path,prediction)
            else:
                summary['metrics']['q']['scaled_mse']+=0.001
            write(case/'processes.json',ledger)
            summary['process_receipts_sha256']=hashlib.sha256((case/'processes.json').read_bytes()).hexdigest()
            write(case/'summary.json',summary)
            try:
                MODULE.summarize(scratch)
            except ValueError as exc:
                controls.append({'variant':variant,'rejected':True,'reason':str(exc)})
            else:
                raise ValueError('corruption accepted: '+variant)
    return {'exact_scalar_replay':True,'saved_cases':8,'raw_process_receipts_verified':result['native_processes'],
            'negative_controls':controls,'new_native_calls':0}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=check(args.private_dir)
    with args.output.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
