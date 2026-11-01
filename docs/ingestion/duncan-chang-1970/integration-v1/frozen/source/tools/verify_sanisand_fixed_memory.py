"""Prepare or inspect the fixed-memory SANISAND research run; never compile/run."""
import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.dsl import Sym
from atlas.model import evaluation_environment, interpret, load

MODEL='models/research/sanisand-2004-fixed-memory-be.json'
HARNESS='tests/native/sanisand_fixed_memory.cpp'
TRANSACTIONS='tests/native/sanisand_transactions.cpp'
PATHS=[[.002,-.001,-.001,0,0,0],[-.002,.001,.001,0,0,0],
       [.001,-.0003,-.0007,.001,-.0004,.0002]]


def unpack(model, values):
    if any(type(v) not in (int,float) or not math.isfinite(v) for v in values):
        raise ValueError('nonfinite or invalid native state')
    result={};offset=0
    for field in model['state']:
        n=6 if field['shape']=='sym' else 1
        result[field['name']]=values[offset:offset+n] if n==6 else values[offset]
        offset+=n
    if offset!=len(values):raise ValueError('native state size mismatch')
    return result


def verify(rows):
    model=load(ROOT/MODEL)
    if len(rows)!=336:raise ValueError('incomplete native matrix')
    worst=0.;max_yield=-float('inf');active=0;refinement=[]
    for path in range(3):
        endpoints=[]
        for steps in (16,32,64):
            selected=[r for r in rows if r['path']==path and r['steps']==steps]
            if len(selected)!=steps:raise ValueError('incomplete native path')
            previous={f['name']:f['initial'] for f in model['state']}
            increment=[v/steps for v in PATHS[path]]
            for step,row in enumerate(selected):
                if row['step']!=step or row['ok'] is not True or row['substeps']!=1:
                    raise ValueError('unexpected partition/failure; cannot compare full-step residual')
                current=unpack(model,row['state'])
                residual=interpret(model,current,previous,increment)
                for name,value in residual.items():
                    components=value.v if isinstance(value,Sym) else [value]
                    error=max(abs(v)/(1e5 if name=='sigma' else 1) for v in components)
                    if not error<=2e-10:raise ValueError('residual exceeds common-solver tolerance')
                    worst=max(worst,error)
                env=evaluation_environment(model,current,previous,increment)
                max_yield=max(max_yield,env['cone_scaled'])
                if current['gamma']<0 or env['plastic_multiplier']<0:
                    raise ValueError('negative multiplier')
                if current['alpha_in']!=previous['alpha_in']:raise ValueError('memory changed')
                for name in ('alpha','fabric','alpha_in'):
                    if abs(sum(current[name][:3]))>1e-9:raise ValueError('history lost deviatoric constraint')
                active+=current['gamma']>1e-8
                previous=current
            endpoints.append(row['state'])
        changes=[max(abs(a-b)/(1e5 if i<6 else 1) for i,(a,b) in enumerate(zip(x,y)) if i!=25)
                 for x,y in zip(endpoints,endpoints[1:])]
        ratio=changes[1]/changes[0]
        if not 0<ratio<.7:raise ValueError('endpoint refinement not established')
        refinement.append(dict(path=path,steps=[16,32,64],scaled_endpoint_changes=changes,ratio=ratio))
    if active<300:raise ValueError('matrix did not exercise plastic response')
    return dict(status='passed',increments=len(rows),active_increments=active,
                largest_scaled_residual=worst,largest_scaled_yield=max_yield,refinement=refinement)


def verify_transactions(rows):
    model=load(ROOT/MODEL)
    names=['alpha','fabric','alpha_in','first-trial','zero-trial','late-failure','repeat-trial']
    if [r['case'] for r in rows]!=names:raise ValueError('incomplete transaction matrix')
    for row in rows:
        before=unpack(model,row['before']);current=unpack(model,row['state'])
        if row['case'] in names[:3]:
            if row['ok'] is not False or row['iterations']!=0 or row['state']!=row['before']:
                raise ValueError('invalid history was not rejected before solving')
            try:evaluation_environment(model,before,before,[0]*6)
            except ValueError:pass
            else:raise ValueError('claimed invalid parent is in domain')
        elif row['case']=='late-failure':
            if (row['ok'] is not False or row['state']!=row['before'] or
                row['substeps']<1 or row['rejected']<1):
                raise ValueError('late failure rollback was not established')
            if before['gamma']<=0 or not any(before['alpha_in']):
                raise ValueError('rollback did not exercise transient and nonzero persistent memory')
        else:
            if row['ok'] is not True or row['substeps']!=1:raise ValueError('unexpected trial partition/failure')
            increment=[0]*6 if row['case']=='zero-trial' else [.000125,-.0000625,-.0000625,0,0,0]
            residual=interpret(model,current,before,increment)
            if any(abs(x)/(1e5 if n=='sigma' else 1)>2e-10 for n,v in residual.items()
                   for x in (v.v if isinstance(v,Sym) else [v])):
                raise ValueError('trial residual exceeds solver tolerance')
    if rows[3]['state']!=rows[6]['state'] or any(rows[i]['before']!=rows[3]['before'] for i in (4,5,6)):
        raise ValueError('repeated trials did not read the same immutable parent')
    return dict(status='passed',cases=7,invalid_histories=3,
                late_failure={k:rows[5][k] for k in ('substeps','rejected','iterations')},
                repeated_trial='exact numeric state equality',scope='Domain rejection and whole-parent rollback; no reversal semantics.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('directory',type=Path)
    p=sub.add_parser('prepare-transactions');p.add_argument('directory',type=Path)
    p=sub.add_parser('verify');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('verify-transactions');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command in ('prepare','prepare-transactions'):
        generate(args.directory/'generated',[ROOT/MODEL])
        shutil.copyfile(ROOT/(TRANSACTIONS if args.command=='prepare-transactions' else HARNESS),args.directory/'probe.cpp')
        print('Prepared C++ only; compile and run separately.');return
    raw=args.raw.read_bytes()
    rows=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw)
    result=verify_transactions(rows) if args.command=='verify-transactions' else verify(rows)
    paths=[MODEL,HARNESS,TRANSACTIONS,'tools/verify_sanisand_fixed_memory.py','atlas/compiler.py',
           'atlas/model.py','atlas/dsl.py','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp']
    result.update(kind='fixed-memory-sanisand-research-investigation',independent_review='pending',
                  scope=result.get('scope','Native common-solver monotonic paths only; no reversals, reference-code or experimental agreement.'),
                  sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                  raw_sha256=hashlib.sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','increments','cases','largest_scaled_residual') if k in result}))


if __name__=='__main__':main()
