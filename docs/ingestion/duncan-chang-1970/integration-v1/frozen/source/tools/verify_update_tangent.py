"""Prepare/verify fixed-partition update tangent evidence; no native execution."""
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
from atlas.dsl import evaluate,parse
from atlas.model import defaults,load

HARNESS='tests/native/update_tangent.cpp'
RAW='catalogue/investigations/update-tangent-v1/results.json.gz'
FIXTURES=['tests/fixtures/linearization/'+p+'.json' for p in ('reset','implicit','singular')]
RESEARCH='models/research/sanisand-2004-parent-reset-be.json'
RATE='tests/fixtures/time/parent-reset-cutback.json'


def model_paths():return [*sorted((ROOT/'models').glob('*.json')),ROOT/RESEARCH,ROOT/RATE,*[ROOT/p for p in FIXTURES]]


def compare(got,want,atol=1e-10,rtol=1e-10):
    if not math.isfinite(got) or abs(got-want)>atol+rtol*abs(want):raise ValueError('analytical tangent mismatch')


def verify(rows):
    expected=['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96',
              'hypoplastic-sand-igs97','test-update-tangent-reset','test-update-tangent-implicit',
              'test-parent-reset-cutback','test-parent-reset-cutback',
              'research-sanisand-2004-parent-reset-be','research-sanisand-2004-parent-reset-be']
    if [r['model'] for r in rows]!=expected:raise ValueError('incomplete tangent case matrix')
    models={m['id']:m for m in map(load,model_paths())};worst=0.;fd_entries=0;analytical_entries=0
    for row in rows:
        model=models[row['model']];p=defaults(model)
        scales=[evaluate(parse(f['scale']),p) for f in model['state'] for _ in range(6 if f['shape']=='sym' else 1)]
        n=len(scales)
        if len(row['parent'])!=n or len(row['state'])!=n or len(row['tangent'])!=n or len(row['finite_difference'])!=n:
            raise ValueError('invalid result shape')
        if len(row['increment'])!=6 or row['h']!=1e-7:raise ValueError('invalid increment/FD step')
        if any(not math.isfinite(x) for x in row['parent']+row['state']+row['increment']):raise ValueError('nonfinite state/increment')
        if any(len(v)!=6 for v in row['tangent']+row['finite_difference']):raise ValueError('invalid tangent shape')
        if any(not math.isfinite(v) for line in row['tangent']+row['finite_difference'] for v in line):raise ValueError('nonfinite tangent')
        if any(not math.isfinite(v) or v<=0 for v in row['fractions']) or abs(sum(row['fractions'])-1)>1e-12:raise ValueError('invalid accepted partition')
        if row['fd_checked']:
            error=max(abs(a-b)/max(scales[i],abs(b)) for i,(a_row,b_row) in enumerate(zip(row['tangent'],row['finite_difference'])) for a,b in zip(a_row,b_row))
            if error>1e-5:raise ValueError('full-update finite difference mismatch')
            compare(error,row['max_normalized_error'],1e-14,1e-8)
            worst=max(worst,error);fd_entries+=n*6
        elif row['model']!='test-parent-reset-cutback' or not row['reset_guard_at_zero'] or any(row['increment']):
            raise ValueError('unexplained missing finite-difference check')
        analytical=None;de=row['increment'];volume=sum(de[:3])
        if row['model']=='linear-elastic':
            E,nu=p['E'],p['nu'];G=E/(2*(1+nu));lam=E*nu/((1+nu)*(1-2*nu))
            analytical=[[((lam if i<3 and j<3 else 0)+(2*G if i==j else 0)) for j in range(6)] for i in range(6)]
        elif row['model']=='test-update-tangent-reset':
            analytical=[[p['p_ref']*((volume if i==j else 0)+(de[i] if j<3 else 0)) for j in range(6)] for i in range(6)]
            analytical += [[1 if j<3 else 0 for j in range(6)] for _ in range(2)]
            compare(row['state'][7],volume)
        elif row['model'] in ('test-update-tangent-implicit','test-parent-reset-cutback'):
            x=row['parent'][6];derivative=0.
            for fraction in row['fractions']:
                h=fraction*volume
                if row['model']=='test-update-tangent-implicit':
                    nxt=2*x/(1+math.sqrt(1-4*h*x))
                    derivative=(derivative+fraction*nxt*nxt)/(1-2*h*nxt);x=nxt
                else:
                    factor=1+h+h*h/2
                    derivative=derivative*factor+x*fraction*(1+h);x*=factor
            compare(row['state'][6],x,1e-9,1e-9)
            analytical=[[p['p_ref'] if i==j else 0 for j in range(6)] for i in range(6)]
            analytical += [[derivative if j<3 else 0 for j in range(6)],[0]*6]
            if volume and len(row['fractions'])<2:raise ValueError('cutback coverage missing')
        if analytical is not None:
            # The scalar implicit root stops at the common Newton tolerance;
            # root error is amplified by the two implicit derivative solves.
            tolerance=1e-8 if row['model']=='test-update-tangent-implicit' else 1e-10
            for a,b in zip(row['tangent'],analytical):
                for got,want in zip(a,b):compare(got,want,tolerance,tolerance);analytical_entries+=1
    return dict(status='passed',recorded_cases=11,native_status_assertions=2,
                finite_difference_entries=fd_entries,analytical_entries=analytical_entries,
                largest_normalized_fd_error=worst,fd_tolerance=1e-5,
                scope='Converged discrete update, accepted partition and expression/reset branches fixed; no physical-time or mixed-control tangent.')


def main():
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    p=sub.add_parser('prepare');p.add_argument('directory',type=Path)
    p=sub.add_parser('verify');p.add_argument('raw',type=Path);p.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.command=='prepare':
        generate(args.directory/'generated',model_paths());shutil.copyfile(ROOT/HARNESS,args.directory/'probe.cpp')
        print('Prepared C++ only; compile and execute separately.');return
    raw=args.raw.read_bytes();rows=json.loads(gzip.decompress(raw) if args.raw.suffix=='.gz' else raw)
    result=verify(rows)
    paths=[str(p.relative_to(ROOT)) for p in model_paths()]+[HARNESS,'tools/verify_update_tangent.py','atlas/compiler.py',
           'atlas/model.py','atlas/dsl.py','cpp/include/atlas/linearize.hpp','cpp/include/atlas/solver.hpp','cpp/include/atlas/tensor.hpp']
    result.update(kind='accepted-update-tangent-investigation',sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths},raw_sha256=hashlib.sha256(raw).hexdigest())
    args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ('status','finite_difference_entries','analytical_entries','largest_normalized_fd_error')}))


if __name__=='__main__':main()
