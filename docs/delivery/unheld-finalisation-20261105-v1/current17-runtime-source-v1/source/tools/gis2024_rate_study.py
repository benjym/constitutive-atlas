"""Check the flattened14-state common-engine rate against a Cartesian oracle."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess

from atlas.initialization import canonical_hash
from atlas.model import ROOT,load
from tools.clay2013_integration_study import request,native_call
from tools.reference_gis2024_coupled import coupled_rates

MODEL_PATH=ROOT/'models/research/gis2024/hp-extracted-asbs-gis-2024-research.json'
REFERENCE_PATH=ROOT/'catalogue/investigations/gis2024-coupled-rates-v1/reference.json'

def make_request(case,model):
    state=case['state'];initial=state['sigma']+[state['e']]+state['h']+[state['Omega']]
    r=request(model,initial,case['de'],1e-8,stress_scale=sum(state['sigma'][:3])/3)
    r['parameters']=[r['parameters'][i] if name=='p_scale' else case['parameters'][name] for i,name in enumerate(model['parameters'])]
    return r

def assess(records,model,cases):
    expected={case['id']:case for case in cases};seen=set();maximum=[0.]*14
    for record in records:
        name=record['case']
        if name not in expected or name in seen:raise ValueError('unexpected/duplicate rate case')
        seen.add(name);case=expected[name]
        if record['request']!=make_request(case,model):raise ValueError('rate request mismatch')
        a=record['response']
        if a.get('ok') is not True:raise ValueError('rate evaluation failed')
        target=coupled_rates(case['state'],case['de'],case['parameters'])['derivative']
        values=a.get('values')
        if not isinstance(values,list) or len(values)!=14:raise ValueError('14 rate components required')
        for i,(x,y) in enumerate(zip(values,target,strict=True)):
            if type(x) not in (int,float) or not math.isfinite(x):raise ValueError('nonfinite rate')
            error=abs(x-y);maximum[i]=max(maximum[i],error)
            bound=max(1e-8,2e-10*abs(y)) if i<6 else 1e-14
            if error>bound:raise ValueError(f'{name}: rate component{i} mismatch')
    if seen!=set(expected):raise ValueError('incomplete rate matrix')
    return maximum

def run(solver):
    model=load(MODEL_PATH);cases=json.loads(REFERENCE_PATH.read_text())['cases']
    described=subprocess.run([str(solver),'--describe'],capture_output=True,text=True,timeout=30,check=True)
    descriptor=json.loads(described.stdout)
    if descriptor['models']!=[model] or descriptor['sha256']!=canonical_hash([model]):raise ValueError('runtime catalogue mismatch')
    records=[]
    for case in cases:
        r=make_request(case,model);records.append(dict(case=case['id'],request=r,response=native_call(solver,r,mode='evaluate')))
    maximum=assess(records,model,cases)
    return dict(version='gis2024-coupled-rate-0.1',scope='Instantaneous zero-spin rates only; no finite integration or admission',model_sha256=canonical_hash(model),catalogue_hash=descriptor['sha256'],native_sha256=hashlib.sha256(Path(solver).read_bytes()).hexdigest(),records=records,maximum_absolute_errors=maximum)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--solver',type=Path,default=ROOT/'build/atlas_gis2024_solver');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=run(a.solver);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n');print(f"Verified {len(report['records'])} native14-state rates")
