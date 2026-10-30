"""Bounded common-engine study against an independent exact isotropic solution."""
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
import math
from pathlib import Path
import subprocess

from atlas.model import ROOT, load
from atlas.initialization import canonical_hash
from tools.reference_clay2013_isotropic import advance

MODEL_PATH=ROOT/'models/research/clay2013/hypoplastic-clay-2013-research.json'
TOLERANCES=(1e-4,1e-6,1e-8)

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def csv(values):return ','.join(format(x,'.17g') for x in values)
def request(model,initial,strain,tolerance,budget=20000,stress_scale=None):
    result=dict(model=model['id'],parameters=[p['default'] for p in model['parameters'].values()],initial=list(initial),strain=list(strain),settings=[2e-10,tolerance,45,20,budget,11])
    if stress_scale is not None:result["parameters"][list(model["parameters"]).index("p_scale")]=stress_scale
    return result
def native_call(solver,r,mode='integrate'):
    args=[str(solver),'--mode',mode,'--model',r['model'],'--parameters',csv(r['parameters']),'--initial',csv(r['initial']),'--strain',csv(r['strain'])]
    if mode=='integrate':args+=['--integration-settings',csv(r['settings'])]
    elif mode=='evaluate':args+=['--current',csv(r['initial'])]
    result=subprocess.run(args,text=True,capture_output=True,timeout=30)
    response=json.loads(result.stdout)
    if result.returncode not in (0,1,2):raise ValueError('native process failure: '+result.stderr)
    return response

def expected(p,e,strain,model):
    # Sum exact input components, not the ideal decimal requested increment.
    with localcontext() as c:
        c.prec=90
        dx=sum((Decimal.from_float(x) for x in strain[:3]),Decimal(0))
        z=advance(p,e,dx,**{k:model['parameters'][k]['default'] for k in ('lambda_star','kappa_star','N')})
        return z

def metrics(state,reference):
    if len(state)!=7 or not all(type(x) in (float,int) and math.isfinite(x) for x in state):raise ValueError('invalid state')
    p=float(reference['p']);e=float(reference['e'])
    return dict(pressure_relative=max(abs(x-p) for x in state[:3])/p,void_ratio_absolute=abs(state[6]-e),isotropy=max(state[:3])-min(state[:3]),shear=max(map(abs,state[3:6])))

def strains(kind,n):
    result=[]
    for dx in {'compression':[.03],'unloading':[-.03],'reversal':[.02,-.03,.01]}[kind]:
        target=dx/3;used=0.
        for i in range(n):
            component=target-used if i==n-1 else target/n;used+=component
            result.append([component]*3+[0.]*3)
    return result

def assess(records,model):
    expected_keys={(p,kind,tol,n) for p in (10.,10000.,1000000.) for kind in ('compression','unloading','reversal') for tol in TOLERANCES for n in (1,)}
    expected_keys|={(10000.,kind,tol,7) for kind in ('compression','unloading','reversal') for tol in (1e-4,1e-8)}
    seen={};summary=[]
    for group in records:
        key=(group['pressure'],group['kind'],group['tolerance'],group['partitions'])
        if key not in expected_keys or key in seen:raise ValueError('unexpected/duplicate trajectory')
        seen[key]=group
        initial=[group['pressure']]*3+[0.,0.,0.,.8]
        if [r['request']['strain'] for r in group['calls']]!=strains(group['kind'],group['partitions']):raise ValueError('trajectory grid mismatch')
        p,e=Decimal.from_float(initial[0]),Decimal.from_float(.8)
        bound={1e-4:(.03,2e-5),1e-6:(.003,2e-6),1e-8:(.0003,2e-7)}[group['tolerance']]
        for record in group['calls']:
            r,a=record['request'],record['response']
            if r!=request(model,initial,r['strain'],group['tolerance'],stress_scale=group['pressure']):raise ValueError('request identity mismatch')
            if a.get('ok') is not True:raise ValueError('trajectory failed')
            for k in ('model','parameters','initial','strain'):
                if a.get(k)!=r[k]:raise ValueError('response echo mismatch: '+k)
            catalogue_hash=hashlib.sha256(json.dumps([model],sort_keys=True,separators=(',',':')).encode()).hexdigest()
            if a.get('catalogue_hash')!=catalogue_hash:raise ValueError('catalogue identity mismatch')
            settings=dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(('residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'),r['settings'])))
            if a.get('integration_settings')!=settings:raise ValueError('integration settings echo mismatch')
            z=expected(p,e,r['strain'],model);p,e=z['p'],z['e']
            error=metrics(a['state'],z)
            if error['pressure_relative']>bound[0] or error['void_ratio_absolute']>bound[1]:raise ValueError('call endpoint exceeds declared error bound')
            if error['isotropy']>1e-7 or error['shear']!=0:raise ValueError('lost isotropy')
            d=a['diagnostics']
            if any(type(d[k]) is not int or d[k]<0 for k in ('substeps','rejected','iterations')):raise ValueError('invalid diagnostics')
            if abs(sum(d['increment_fractions'])-1)>1e-12:raise ValueError('increment not covered')
            initial=a['state']
        error=metrics(initial,z)
        # Global endpoint bounds measured separately from local error criterion.
        bound={1e-4:(.03,2e-5),1e-6:(.003,2e-6),1e-8:(.0003,2e-7)}[group['tolerance']]
        if error['pressure_relative']>bound[0] or error['void_ratio_absolute']>bound[1]:raise ValueError(f'exact trajectory error exceeds declared bound {key}: {error}')
        summary.append(dict(key=list(key),errors=error,calls=len(group['calls']),substeps=sum(r['response']['diagnostics']['substeps'] for r in group['calls'])))
    if set(seen)!=expected_keys:raise ValueError('incomplete trajectory matrix')
    for p in (10.,10000.,1000000.):
        for kind in ('compression','unloading','reversal'):
            errors=[metrics(seen[p,kind,t,1]['calls'][-1]['response']['state'],_end_reference(seen[p,kind,t,1],model)) for t in TOLERANCES]
            for channel in ('pressure_relative','void_ratio_absolute'):
                if not errors[-1][channel]<errors[0][channel]*.2:raise ValueError('refinement did not improve '+channel)
    hashes={r['response']['catalogue_hash'] for g in records for r in g['calls']}
    if len(hashes)!=1:raise ValueError('mixed catalogue identities')
    for kind in ('compression','unloading','reversal'):
        differences=[]
        for tol in (1e-4,1e-8):
            a=seen[10000.,kind,tol,1]['calls'][-1]['response']['state']
            b=seen[10000.,kind,tol,7]['calls'][-1]['response']['state']
            differences.append([abs(a[0]-b[0]),abs(a[6]-b[6])])
        if any(b>=a*.2 for a,b in zip(*differences)):raise ValueError('caller partition discrepancy did not shrink')
    return summary

def _end_reference(group,model):
    p,e=Decimal.from_float(group['pressure']),Decimal.from_float(.8)
    for r in group['calls']:
        z=expected(p,e,r['request']['strain'],model);p,e=z['p'],z['e']
    return z

def run(solver,raw_output=None):
    model=load(MODEL_PATH);records=[]
    combinations=[(p,k,t,1) for p in (10.,10000.,1000000.) for k in ('compression','unloading','reversal') for t in TOLERANCES]
    combinations += [(10000.,k,t,7) for k in ('compression','unloading','reversal') for t in (1e-4,1e-8)]
    for pressure,kind,tol,n in combinations:
        z=[pressure]*3+[0.,0.,0.,.8];calls=[]
        for strain in strains(kind,n):
            r=request(model,z,strain,tol,stress_scale=pressure)
            a=native_call(solver,r)
            if not a.get('ok'):raise ValueError(f'{pressure} {kind} {tol}: '+a.get('message',''))
            calls.append(dict(request=r,response=a));z=a['state']
        records.append(dict(pressure=pressure,kind=kind,tolerance=tol,partitions=n,calls=calls))
    if raw_output is not None:Path(raw_output).write_text(json.dumps(records,indent=2)+"\n")
    summary=assess(records,model)
    return dict(version='clay2013-isotropic-integration-0.1',scope='zero-spin isotropic numerical research; no experimental validation or admission',model_sha256=canonical_hash(model),native_sha256=sha(solver),records=records,summary=summary)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--solver',type=Path,default=ROOT/'build/atlas_clay2013_solver');parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True);report=run(args.solver,args.output.with_suffix(".raw.json"));args.output.write_text(json.dumps(report,indent=2)+'\n');print(f"Verified {len(report['records'])} exact-reference trajectories")
