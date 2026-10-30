"""Prepare, explicitly capture native CLI responses, or verify saved API evidence."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from atlas.model import load
from tools.verify_update_tangent import RAW as TANGENT_RAW, model_paths

RAW='catalogue/investigations/linearization-api-v1/responses.json.gz'
TIME_MODEL='tests/fixtures/time/maxwell.json'


def reference():return json.loads(gzip.decompress((ROOT/TANGENT_RAW).read_bytes()))
def csv(values):return ','.join(format(v,'.17g') for v in values)


def cases():
    rows=reference()
    result=[(f'matrix-{i}',['--mode','linearize','--model',r['model'],'--initial',csv(r['parent']),'--strain',csv(r['increment'])]) for i,r in enumerate(rows)]
    base=['--mode','linearize','--model','linear-elastic','--strain','0,0,0,0,0,0']
    m=load(ROOT/'models/modified-cam-clay.json')
    invalid=[v for f in m['state'] for v in (f['initial'] if f['shape']=='sym' else [f['initial']])]
    invalid[:3]=[-1e5]*3
    result += [('singular',['--mode','linearize','--model','test-update-tangent-singular','--strain','0,0,0,0,0,0']),
               ('inadmissible-parent',['--mode','linearize','--model','modified-cam-clay','--initial',csv(invalid),'--strain','0,0,0,0,0,0']),
               ('physical-time',['--mode','linearize','--model','test-maxwell','--strain','0,0,0,0,0,0']),
               ('unknown-model',['--mode','linearize','--model','not-a-model','--strain','0,0,0,0,0,0']),
               ('bad-csv',['--mode','linearize','--model','linear-elastic','--strain','0,0,0,0,0,nan']),
               ('bad-parameters',base+['--parameters','100000,-1,0.25']),
               ('unrelated-option',base+['--target','.01']),('time-option',base+['--duration','1']),
               ('unchanged-integrate',['--mode','integrate','--model','linear-elastic','--initial',csv(rows[0]['parent']),'--strain',csv(rows[0]['increment'])]),
               ('describe',['--describe'])]
    return result


def verify(captured):
    specifications=cases();rows=reference()
    if [r['name'] for r in captured]!=[n for n,a in specifications]:raise ValueError('incomplete API matrix')
    for row,(name,args) in zip(captured,specifications):
        if row['argv']!=args or row['stderr']:raise ValueError('capture differs from specified invocation')
        d=row['response']
        expected_exit=0 if name=='describe' or d['ok'] else 1
        if row['returncode']!=expected_exit:raise ValueError('CLI exit/update status mismatch')
        if name.startswith('matrix-'):
            r=rows[int(name.split('-')[1])]
            if not d['ok'] or not d['tangent_ok'] or d['state']!=r['state'] or d['state_tangent']!=r['tangent']:
                raise ValueError('JSON/API differs from verified C++ matrix')
            if d['initial']!=r['parent'] or d['strain']!=r['increment'] or d['reset_guard_at_zero']!=r['reset_guard_at_zero']:
                raise ValueError('input/branch metadata mismatch')
            if d['diagnostics']['increment_fractions']!=r['fractions']:raise ValueError('partition metadata mismatch')
            if d['api_version']!='experimental-update-linearization-0.1' or d['partition_policy']!='accepted_fixed' or d['branch_policy']!='selected_fixed':
                raise ValueError('linearization policy missing')
            if d['tangent_columns']!=['xx','yy','zz','sqrt2_xy','sqrt2_yz','sqrt2_xz']:raise ValueError('Mandel columns mislabelled')
            offset=0
            for f in d['state_fields']:
                if f['offset']!=offset or f['size'] not in (1,6):raise ValueError('invalid state layout')
                offset+=f['size']
            if offset!=len(d['state']):raise ValueError('state layout does not cover matrix rows')
        elif name=='singular':
            if d['ok'] is not True or d['tangent_ok'] is not False or d['state_tangent'] is not None or not d['tangent_message']:
                raise ValueError('singular derivative lost accepted-update distinction')
        elif name in ('inadmissible-parent','physical-time'):
            if d['ok'] is not False or d['tangent_ok'] is not False or d['state_tangent'] is not None or d['state']!=d['initial']:
                raise ValueError('rejected material update did not return rollback state')
        elif name in ('unknown-model','bad-csv','bad-parameters'):
            if d['ok'] is not False or d['tangent_ok'] is not False or d['state_tangent'] is not None or 'state' in d:
                raise ValueError('unparsed request published a material state')
        elif name in ('unrelated-option','time-option'):
            if d['ok'] is not False or 'state' in d:raise ValueError('unsupported option accepted')
        elif name=='unchanged-integrate':
            if d['state']!=rows[0]['state'] or 'tangent_ok' in d:raise ValueError('existing integrate response changed')
    catalogue=captured[-1]['response']
    models={m['id']:m for m in catalogue['models']}
    for row in captured:
        d=row['response']
        if 'api_version' not in d:continue
        if d['catalogue_hash']!=catalogue['sha256']:raise ValueError('wrong catalogue identity')
        model=models[d['model']]
        if d['parameters']!=[p['default'] for p in model['parameters'].values()]:raise ValueError('parameter provenance mismatch')
        if [f['name'] for f in d['state_fields']]!=[f['name'] for f in model['state']]:raise ValueError('state names do not match descriptor')
    return dict(status='passed',cases=len(captured),matrix_parity_cases=11,
                singular_derivative_preserves_update=True,failed_updates_restore_parent=True,
                cli_error_cases=5,existing_integrate_compatible=True,
                scope='Native C ABI through CLI; Emscripten annotation present, Wasm runtime unverified.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('directory',type=Path)
    p=sub.add_parser('capture');p.add_argument('--solver',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    p=sub.add_parser('verify');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='prepare':
        generate(args.directory/'generated',model_paths()+[ROOT/TIME_MODEL]);print('Prepared headers only; compile separately.');return
    if args.command=='capture':
        captured=[]
        for name,argv in cases():
            r=subprocess.run([str(args.solver),*argv],capture_output=True,text=True,timeout=45)
            captured.append(dict(name=name,argv=argv,returncode=r.returncode,stderr=r.stderr,response=json.loads(r.stdout)))
        args.output.write_text(json.dumps(captured,indent=2)+'\n')
        verify(captured);print('Captured and verified',len(captured),'native CLI responses.');return
    raw=args.raw.read_bytes();captured=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw)
    result=verify(captured)
    paths=['cpp/main.cpp','cpp/include/atlas/linearize.hpp','cpp/include/atlas/solver.hpp','atlas/compiler.py',
           'tools/verify_linearization_api.py','tools/verify_update_tangent.py',TANGENT_RAW,TIME_MODEL]
    paths += [str(p.relative_to(ROOT)) for p in model_paths()]
    result.update(kind='update-linearization-api-investigation',sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},raw_sha256=hashlib.sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','cases','matrix_parity_cases')}))


if __name__=='__main__':main()
