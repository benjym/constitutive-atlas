"""Qualify the dedicated Kelvin–Voigt target against frozen independent references."""
import argparse, importlib.util, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'docs/ingestion/kelvin-voigt-comsol63/execution-v3'
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location('kelvin_study',BASE/'study.py')
study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
def main():
    p=argparse.ArgumentParser();p.add_argument('--solver',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    study.verify_freeze();cases=json.loads((BASE/'cases.json').read_text())['cases']
    a.output.parent.mkdir(parents=True,exist_ok=True)
    if a.output.exists():raise ValueError('Refuse to overwrite existing evidence')
    rows=study.collect_native(a.solver.resolve(),cases,a.output)
    report=study.assess(cases,rows)
    a.output.write_text(json.dumps(dict(report=report,capture=rows),indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':main()
