"""Separate prospectively frozen default-parameter qualification."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from tools.study_j2 import case, ZERO, dump, assess_rows, sha
BASE=Path(__file__).resolve().parent

def make():
    model=json.loads((ROOT/'models/research/j2/j2-linear-isotropic-hardening-be.json').read_text())
    p=[v['default'] for v in model['parameters'].values()]
    directions=[[2,-1,-1,0,0,0],[0,0,0,1,0,0],[.7,-.2,-.5,.6,-.4,.3]]
    rows=[]
    for alpha in (0,.01):
        for amp in (.0001,.003):
            for i,d in enumerate(directions):
                rows.append(case(f'default-alpha{alpha}-a{amp}-d{i}',[0]*6+[alpha,0],[amp*v for v in d],p))
    rows.extend([case('default-zero',ZERO,[0]*6,p),case('default-volume',ZERO,[.001]*3+[0]*3,p)])
    for label,de in [('elastic',[.0001,-.00005,-.00005,.00003,0,0]),('plastic',[.003,-.001,-.002,.001,-.002,.001])]:
        rows.append(case('default-tangent-'+label,ZERO,de,p,mode='linearize'))
    return dict(version='j2-default-supplement-1',cases=rows,parameters=p,
                policy='Separate default-only study frozen before default backend observations; original execution-v2 budgets unchanged. No full parameter-envelope claim.')

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('mode',choices=['freeze','native','assess']);ap.add_argument('path',nargs='?');a=ap.parse_args()
    if a.mode=='freeze':
        assert not (BASE/'default-references.json').exists()
        dump(BASE/'default-references.json',make())
        dump(BASE/'default-study-freeze.json',dict(files=[dict(path=str(p.relative_to(ROOT)),sha256=sha(p)) for p in [Path(__file__).resolve(),ROOT/'tools/study_j2.py',BASE/'default-references.json',ROOT/'models/research/j2/j2-linear-isotropic-hardening-be.json']]))
    else:
        cases=json.loads((BASE/'default-references.json').read_text())['cases']
        if a.mode=='native':
            rows=[]
            for c in cases:
                calls=[]
                for _ in range(2):
                    r=subprocess.run([a.path,*c['argv']],capture_output=True,text=True,timeout=30)
                    calls.append(dict(returncode=r.returncode,stdout=r.stdout,stderr=r.stderr))
                rows.append(dict(id=c['id'],calls=calls));dump(BASE/'native-default-raw.json',rows)
        else:rows=json.loads(Path(a.path).read_text())
        print(json.dumps(assess_rows(cases,rows),indent=2))
