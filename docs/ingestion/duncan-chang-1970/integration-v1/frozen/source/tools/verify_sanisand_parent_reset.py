"""Prepare/verify the parent-reset research variant; no compiler or native run."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.dsl import Sym
from atlas.model import defaults, evaluation_environment, interpret, load, prepare_increment
from tools.verify_sanisand_fixed_memory import MODEL as FIXED, unpack

MODEL='models/research/sanisand-2004-parent-reset-be.json'
HARNESS='tests/native/sanisand_parent_reset.cpp'
RAW='catalogue/investigations/sanisand-parent-reset-v1/trajectories.json.gz'


def flatten(model,state):
    return [v for f in model['state'] for v in (state[f['name']] if f['shape']=='sym' else [state[f['name']]])]


def verify(rows):
    expected=[(p,n,l,s) for p in (0,1) for n in (16,32,64)
              for l in range(6) for s in range(n if l<4 else 1)]
    if [(r['path'],r['steps'],r['leg'],r['step']) for r in rows]!=expected:
        raise ValueError('incomplete or reordered parent-reset matrix')
    model=load(ROOT/MODEL);fixed=load(ROOT/FIXED)
    for field in ('parameters','state','derived','equations','domain','initial_checks'):
        if model[field]!=fixed[field]:raise ValueError('unexpected change to fixed-memory equations')
    previous=None;peaks={};endpoints={};resets=0;rollbacks=0;worst=0.;monotonic=0
    historical=json.loads(gzip.decompress((ROOT/'catalogue/investigations/sanisand-fixed-memory-be-v1/trajectories.json.gz').read_bytes()))
    fixed_rows={(r['path'],r['steps'],r['step']):r['state'] for r in historical}
    for row in rows:
        p,n,l,s=(row[k] for k in ('path','steps','leg','step'))
        if len(row['increment'])!=6:raise ValueError('invalid increment layout')
        before=unpack(model,row['before']);current=unpack(model,row['state'])
        prepared=prepare_increment(model,before,row['increment'])
        if flatten(model,prepared)!=row['prepared']:raise ValueError('Python/native memory selection mismatch')
        if l<4:
            if l==0 and s==0:
                initial={f['name']:f['initial'] for f in model['state']}
                if row['before']!=flatten(model,initial):raise ValueError('incorrect initial state')
            elif row['before']!=previous:raise ValueError('path history is discontinuous')
            previous=row['state']
            resets+=prepared['alpha_in']!=before['alpha_in']
            if l==0:
                if row['state']!=fixed_rows[(0 if p==0 else 2,n,s)]:
                    raise ValueError('monotonic response differs from retained fixed-memory run')
                monotonic+=1
                if s==n-1:peaks[p,n]=row['state']
            if l==3 and s==n-1:endpoints[p,n]=row['state']
        elif row['before']!=peaks[p,n]:raise ValueError('failure/zero trial did not restart from stored peak')
        if l==4:
            if row['ok'] is not False or row['state']!=row['before'] or row['prepared']==row['before']:
                raise ValueError('reset rollback not established')
            if row['substeps']<1 or row['rejected']<1:raise ValueError('failure lacks accepted internal work')
            rollbacks+=1
            continue
        if row['ok'] is not True or row['substeps']!=1 or row['fractions']!=[1]:
            raise ValueError('unexpected failure/partition in successful case')
        residual=interpret(model,current,prepared,row['increment'])
        for name,value in residual.items():
            for component in (value.v if isinstance(value,Sym) else [value]):
                error=abs(component)/(defaults(model)['p_at'] if name=='sigma' else 1)
                if not error<=2e-10:raise ValueError('residual exceeds solver tolerance')
                worst=max(worst,error)
        if current['alpha_in']!=prepared['alpha_in']:raise ValueError('memory evolved after selection')
        if l==5 and row['prepared']!=row['before']:raise ValueError('zero increment changed memory')
        evaluation_environment(model,current,prepared,row['increment'])
    refinement=[]
    for p in (0,1):
        pairs=[(endpoints[p,16],endpoints[p,32]),(endpoints[p,32],endpoints[p,64])]
        changes=[max(abs(a-b)/(1e5 if i<6 else 1) for i,(a,b) in enumerate(zip(x,y)) if i!=25) for x,y in pairs]
        ratio=changes[1]/changes[0]
        if not 0<ratio<.7:raise ValueError('cyclic endpoint refinement not established')
        refinement.append(dict(path=p,scaled_endpoint_changes=changes,ratio=ratio))
    if resets!=18 or rollbacks!=6 or monotonic!=224:raise ValueError('coverage counts differ')
    return dict(status='passed',records=len(rows),cyclic_increments=896,zero_trials=6,
                cyclic_memory_resets=resets,rollback_after_reset=rollbacks,monotonic_parity_checks=monotonic,
                largest_scaled_residual=worst,refinement=refinement)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('directory',type=Path)
    p=sub.add_parser('verify');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='prepare':
        generate(args.directory/'generated',[ROOT/FIXED,ROOT/MODEL])
        shutil.copyfile(ROOT/HARNESS,args.directory/'probe.cpp')
        print('Prepared C++ only; compile and execute separately.');return
    raw=args.raw.read_bytes();rows=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw)
    result=verify(rows)
    paths=[MODEL,FIXED,HARNESS,'tools/verify_sanisand_parent_reset.py','tools/verify_sanisand_fixed_memory.py',
           'atlas/compiler.py','atlas/model.py','atlas/dsl.py','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp',
           'catalogue/investigations/sanisand-fixed-memory-be-v1/trajectories.json.gz']
    result.update(kind='sanisand-parent-reset-research-investigation',independent_review='pending',
                  scope='Project parent-direction reset variant; no canonical original-model or full OpenSees equivalence.',
                  sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},
                  raw_sha256=hashlib.sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','records','cyclic_memory_resets','rollback_after_reset','largest_scaled_residual')}))


if __name__=='__main__':main()
