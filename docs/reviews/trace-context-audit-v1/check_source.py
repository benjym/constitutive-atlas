"""Independent source-only operator/context audit; no C++ compilation/execution."""
import copy, hashlib, json, math, pathlib, shutil, struct, subprocess, sys, tempfile

ROOT=pathlib.Path(sys.argv[1]).resolve()
FILES=['atlas/dsl.py','atlas/model.py','atlas/compiler.py','atlas/history.py','atlas/history_compiler.py',
       'cpp/include/atlas/tensor.hpp','cpp/include/atlas/trace_accuracy.hpp','cpp/include/atlas/history_runtime.hpp',
       'cpp/include/atlas/solver.hpp','cpp/include/atlas/time.hpp','cpp/include/atlas/schedule.hpp',
       'docs/reviews/tensor-trace-context-v1/dsl.py','docs/reviews/tensor-trace-context-v1/tensor.hpp']
pins={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}
with tempfile.TemporaryDirectory(prefix='trace-independent-context-') as temp:
    target=pathlib.Path(temp)
    shutil.copytree(ROOT/'atlas',target/'atlas',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(ROOT/'schemas',target/'schemas')
    shutil.copyfile(ROOT/'docs/reviews/tensor-trace-context-v1/dsl.py',target/'atlas/dsl.py')
    shutil.copytree(ROOT/'tests/fixtures/log1p',target/'fixtures')
    shutil.copyfile(ROOT/'tests/fixtures/log1p-history/log1p.json',target/'history.json')
    code=r'''
import copy,json,math,pathlib,struct,tempfile
from fractions import Fraction
from atlas.dsl import Sym,trace,dev,evaluate,parse
from atlas.model import validate
from atlas.compiler import generate
from atlas.history import make_snapshot,advance
records=[]
def record(name,condition):
    assert condition,name
    records.append(name)
maximum=float.fromhex('0x1.fffffffffffffp1023')
for name,values in [('cancellation',[500.,1e-130,-500.]),('intermediate-overflow',[maximum,maximum,-maximum]),('positive-zero',[-0.,0.,-0.])]:
    independent=float(sum((Fraction.from_float(x) for x in values),Fraction()))
    expected=0. if independent==0 else independent
    record(name,struct.pack('>d',trace(Sym(tuple(values)+(0.,0.,0.))))==struct.pack('>d',expected))
A=Sym((maximum,-maximum,-maximum,0.,0.,0.))
record('dev-input-trace-finite',trace(A)==-maximum)
try:dev(A)
except ValueError:record('dev-result-overflow-rejected',True)
else:raise AssertionError('dev overflow accepted')
for name,expr,should_fail in [('masked-predicate','select(trace(A)>0,1,2)',True),('eager-zero','0*trace(A)',True),('lazy-then','select(1>0,7,trace(A))',False),('lazy-else','select(1<0,trace(A),7)',False)]:
    try:value=evaluate(parse(expr),{'A':Sym((maximum,maximum,maximum,0.,0.,0.))})
    except ValueError:record(name,should_fail)
    else:record(name,not should_fail and value==7)
# Scale validation is executable evidence; undefined name inference remains source-only.
for physical in (False,True):
    model=json.loads(pathlib.Path('fixtures/time-observable.json' if physical else 'fixtures/direct.json').read_text())
    model['state'][0]['scale']='trace(sym(K,K,K,0*K,0*K,0*K))/3'
    if physical:model['observables'][0]['scale']='trace(sym(K,K,K,0*K,0*K,0*K))/3'
    validate(model)
    record('trace-scale-accepted-'+str(physical),True)
    with tempfile.TemporaryDirectory() as generated:
        path=pathlib.Path(generated)/'input.json';path.write_text(json.dumps(model));generate(generated,[path])
        record('actual-scale-header-generated-'+str(physical),(pathlib.Path(generated)/'models.hpp').is_file())
template=json.loads(pathlib.Path('history.json').read_text())
for where in ('guard','write','check','lazy'):
    program=copy.deepcopy(template);phase=program['phases'][0]
    phase['writes']={'A':'I'}
    if where=='guard':phase['guard']='select(trace(X)>0,-1,1)'
    elif where=='write':phase['writes']={'A':'select(trace(X)>0,I,0*I)'}
    elif where=='check':phase['writes']={'A':'X'};phase['checks']=['select(trace(A)>0,1,2)>0']
    else:phase['writes']={'A':'select(g>0,I,trace(X)*I)'}
    parent=make_snapshot(program,{'A':[2.,3.,4.,0.,0.,0.]},generation=7,preparation_epoch=4)
    before=copy.deepcopy(parent)
    result=advance(program,parent,{'X':[maximum,maximum,maximum,0.,0.,0.],'gate':1.})
    if where=='lazy':record('history-lazy-arm',result['ok'] and result['snapshot']['generation']==8)
    else:record('history-'+where+'-rollback',not result['ok'] and result['snapshot'] is parent and parent==before and result['events']==[])
# Later failure rolls back an earlier successful write and preparation epoch.
program=copy.deepcopy(template)
phase=program['phases'][0];phase.update(kind='prepare',name='prepared',writes={'A':'I'})
program['phases'].append({'name':'advanced','kind':'advance','base':'prepared','bindings':{'X':{'input':'X'}},'writes':{'A':'select(trace(X)>0,I,0*I)'}})
parent=make_snapshot(program,{'A':[2.,3.,4.,0.,0.,0.]},generation=7,preparation_epoch=4)
result=advance(program,parent,{'X':[maximum,maximum,maximum,0.,0.,0.],'gate':1.})
record('history-late-phase-rollback',not result['ok'] and result['snapshot'] is parent and result['events']==[] and result['diagnostics']=={'attempted_phases':2,'executed_phases':2,'failed_phase':'advanced'} and parent['generation']==7 and parent['preparation_epoch']==4)
print(json.dumps({'checks':len(records),'passed':records,'compiled_execution':False},sort_keys=True))
'''
    bootstrap='import sys,os;sys.path.insert(0,sys.argv[1]);os.chdir(sys.argv[1]);exec(sys.argv[2])'
    result=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,str(target),code],capture_output=True,text=True)
    if result.returncode:
        print(result.stdout,end='');print(result.stderr,end='',file=sys.stderr);raise SystemExit(result.returncode)
    out=json.loads(result.stdout)
    out.update(version='trace-context-independent-source-audit-v1',reviewed_source_hashes=pins,production_modified=False)
    print(json.dumps(out,indent=2,sort_keys=True))
