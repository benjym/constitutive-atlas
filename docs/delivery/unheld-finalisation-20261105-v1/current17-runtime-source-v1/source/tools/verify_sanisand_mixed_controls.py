"""Prepare/verify SANISAND mixed-control research evidence; no native invocation."""
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
from atlas.model import defaults, interpret, load, prepare_increment
from tools.verify_sanisand_parent_reset import MODEL, flatten
from tools.verify_sanisand_fixed_memory import unpack

HARNESS='tests/native/sanisand_mixed_controls.cpp'
RAW='catalogue/investigations/sanisand-mixed-controls-v1/trajectories.json.gz'


def near(actual,expected,tolerance):
    if not math.isfinite(actual) or abs(actual-expected)>tolerance:
        raise ValueError('analytical/control comparison failed')


def elastic_reference(row,parameters):
    before=row['before'];state=row['state'];de=row['increment'];protocol=row['protocol']
    G0,nu,p_at=(parameters[n] for n in ('G0','nu','p_at'))
    p0=sum(before[:3])/3;e=before[6]
    if protocol==1:
        axial=row['request'];void=(1+e)*math.exp(-(1-2*nu)*axial)-1
        b=2*G0*(1+nu)/3*(2.97-void)**2/(1+void)*axial
        u0=math.sqrt(p0/p_at);u=(b+math.sqrt(b*b+4*u0*u0))/2
        dp=p_at*(u-u0)*(u+u0)
        expected=[before[0]+3*dp,before[1],before[2],0,0,0]
        for a,b in zip(state[:6],expected):near(a,b,.002)
        near(state[6],void,5e-11)
        near(de[1],-nu*axial,1e-11);near(de[2],-nu*axial,1e-11)
    else:
        G=G0*p_at*(2.97-e)**2/(1+e)*math.sqrt(p0/p_at)
        q=row['request'];axial=q/(3*G)
        for a,b in zip(de,[axial,-axial/2,-axial/2,0,0,0]):near(a,b,1e-11)
        expected=[p0+2*q/3,p0-q/3,p0-q/3,0,0,0]
        for a,b in zip(state[:6],expected):near(a,b,.001)
        near(state[6],e,1e-12)
    for a,b in zip(state[7:25],before[7:25]):near(a,b,2e-10)
    near(state[25],0,2e-10)


def verify(rows):
    expected=[(p,n,l,s) for p in (1,3) for n in (0,16,32,64)
              for l in range(4 if n else 1) for s in range(n if n else 1)]
    if [(r['protocol'],r['steps'],r['leg'],r['step']) for r in rows]!=expected:
        raise ValueError('incomplete or reordered mixed-control matrix')
    model=load(ROOT/MODEL);parameters=defaults(model)
    endpoints={};previous=None;worst=0.;resets=0;control_max={1:0.,3:0.};cumulative_max=0.
    for row in rows:
        p,n,l,s=(row[k] for k in ('protocol','steps','leg','step'))
        before=unpack(model,row['before']);current=unpack(model,row['state']);increment=row['increment']
        if len(increment)!=6:raise ValueError('invalid strain increment')
        expected_request=([1,-2,2,-1][l]*(.001 if p==1 else 10000)/n) if n else (1e-6 if p==1 else 100)
        near(row['request'],expected_request,1e-15)
        if l==0 and s==0:
            initial={f['name']:f['initial'] for f in model['state']}
            if row['before']!=flatten(model,initial):raise ValueError('incorrect initial state')
            accumulated_q=0.;count=0
        elif row['before']!=previous:raise ValueError('mixed-control history discontinuity')
        previous=row['state']
        if row['ok'] is not True or row['replay_equal'] is not True or row['substeps']!=1 or row['fractions']!=[1]:
            raise ValueError('control/replay failed or unexpected constitutive partition')
        prepared=prepare_increment(model,before,increment)
        if row['prepared']!=flatten(model,prepared):raise ValueError('outer trial memory preparation differs')
        if current['alpha_in']!=prepared['alpha_in']:raise ValueError('selected memory changed')
        resets+=prepared['alpha_in']!=before['alpha_in']
        residual=interpret(model,current,prepared,increment)
        for name,value in residual.items():
            for v in (value.v if isinstance(value,Sym) else [value]):
                error=abs(v)/(parameters['p_at'] if name=='sigma' else 1)
                if not error<=2e-10:raise ValueError('constitutive residual exceeds solver tolerance')
                worst=max(worst,error)
        near(increment[1],increment[2],0)
        for v in increment[3:]:near(v,0,0)
        near(current['sigma'][1],current['sigma'][2],1e-6)
        if p==1:
            near(increment[0],row['request'],0)
            control=(current['sigma'][1]+current['sigma'][2])/2-1e5
        else:
            near(sum(increment[:3]),0,1e-18)
            q=current['sigma'][0]-(current['sigma'][1]+current['sigma'][2])/2
            q0=before['sigma'][0]-(before['sigma'][1]+before['sigma'][2])/2
            control=q-q0-row['request']
            accumulated_q+=row['request'];count+=1
            near(q,accumulated_q,count*.001+1e-8)
            cumulative_max=max(cumulative_max,abs(q-accumulated_q))
        near(control,row['control_residual'],1e-8);near(control,0,.001)
        control_max[p]=max(control_max[p],abs(control))
        if not n:elastic_reference(row,parameters)
        elif l==3 and s==n-1:endpoints[p,n]=row['state']
    refinement=[]
    for p in (1,3):
        pairs=[(endpoints[p,16],endpoints[p,32]),(endpoints[p,32],endpoints[p,64])]
        changes=[max(abs(a-b)/(1e5 if i<6 else 1) for i,(a,b) in enumerate(zip(x,y)) if i!=25) for x,y in pairs]
        ratio=changes[1]/changes[0]
        if not 0<ratio<.7:raise ValueError('mixed-control endpoint refinement not established')
        refinement.append(dict(protocol=p,scaled_endpoint_changes=changes,ratio=ratio))
    if resets!=18:raise ValueError('reversal reset coverage differs')
    return dict(status='passed',records=len(rows),cyclic_increments=896,elastic_analytical_cases=2,
                cyclic_memory_resets=resets,native_direct_replay_assertions=898,
                largest_scaled_constitutive_residual=worst,largest_control_residual_pa=control_max,
                largest_accumulated_q_error_pa=cumulative_max,refinement=refinement)


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('directory',type=Path)
    p=sub.add_parser('verify');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='prepare':
        generate(args.directory/'generated',[ROOT/MODEL]);shutil.copyfile(ROOT/HARNESS,args.directory/'probe.cpp')
        print('Prepared C++ only; compile and execute separately.');return
    raw=args.raw.read_bytes();rows=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw)
    result=verify(rows)
    paths=[MODEL,HARNESS,'tools/verify_sanisand_mixed_controls.py','tools/verify_sanisand_parent_reset.py',
           'tools/verify_sanisand_fixed_memory.py','atlas/compiler.py','atlas/model.py','atlas/dsl.py',
           'cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp']
    result.update(kind='sanisand-mixed-control-research-investigation',independent_review='pending',
                  scope='Existing drained/stress-controlled axisymmetric protocols on project parent-reset variant; no canonical original-model equivalence.',
                  sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},raw_sha256=hashlib.sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('status','records','elastic_analytical_cases','largest_scaled_constitutive_residual','largest_control_residual_pa')}))


if __name__=='__main__':main()
