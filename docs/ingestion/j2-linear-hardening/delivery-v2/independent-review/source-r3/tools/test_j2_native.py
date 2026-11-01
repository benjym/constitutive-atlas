"""Qualify the dedicated common-engine J2 target against frozen source references."""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from tools.study_j2 import assess_rows
from tools.run_j2 import run
BASE=ROOT/'docs/ingestion/j2-linear-hardening/execution-v2'
spec=importlib.util.spec_from_file_location('j2_history_assessor',BASE/'check_paths.py')
history=importlib.util.module_from_spec(spec);spec.loader.exec_module(history)

def qualify(solver,output):
    solver=Path(solver).resolve();output=Path(output);output.mkdir(parents=True,exist_ok=True)
    reports={}
    for label,name in [('main','references.json'),('defaults','default-references.json')]:
        cases=json.loads((BASE/name).read_text())['cases'];rows=[]
        for c in cases:
            calls=[]
            for _ in range(2):
                r=subprocess.run([str(solver),*c['argv']],capture_output=True,text=True,timeout=30)
                calls.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
            rows.append(dict(id=c['id'],calls=calls))
            (output/(label+'-raw.json')).write_text(json.dumps(rows,indent=2)+'\n')
        reports[label]=assess_rows(cases,rows)
    paths=json.loads((BASE/'paths.json').read_text())+[json.loads((ROOT/'docs/ingestion/j2-linear-hardening/delivery-v1/preset-references.json').read_text())]
    raw=[]
    for path in paths:
        raw.append(dict(id=path['id'],repeats=[run(solver,path),run(solver,path)]))
        (output/'paths-raw.json').write_text(json.dumps(raw,indent=2)+'\n')
    reports['paths_and_public_preset']=history.assess(paths,raw)
    (output/'assessment.json').write_text(json.dumps(reports,indent=2)+'\n')
    return reports
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--solver',required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();print(json.dumps(qualify(a.solver,a.output),indent=2))
