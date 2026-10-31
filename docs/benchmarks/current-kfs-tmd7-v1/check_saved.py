"""Audit private native evidence against the public scalar result; no C++ calls."""
import argparse
import importlib.util
from pathlib import Path
HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location('current_tmd7_audit',HERE/'replay.py')
R=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(R)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--private-dir',type=Path,required=True);args=parser.parse_args()
    result=R.audit(args.private_dir)
    R.OLD.require(result==R.read(HERE/'results.json'),'public scalar result differs')
    print('PASS: complete prediction/command reconstruction;44current+44baseline receipts; scalar result exact; no native calls')
