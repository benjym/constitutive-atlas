"""Source-only candidate checks in a fresh project copy; no compiler/artifact calls."""
import hashlib,json,pathlib,shutil,subprocess,sys,tempfile
HERE=pathlib.Path(__file__).resolve().parent
ROOT=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else pathlib.Path('/Users/bmar5496/code/constitutive-atlas')
with tempfile.TemporaryDirectory(prefix='atlas-trace-candidate-') as tmp:
    root=pathlib.Path(tmp)
    shutil.copytree(ROOT/'atlas',root/'atlas',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
    shutil.copytree(ROOT/'schemas',root/'schemas')
    shutil.copyfile(HERE/'dsl.py',root/'atlas/dsl.py')
    shutil.copytree(ROOT/'tests/fixtures/log1p',root/'fixtures')
    shutil.copyfile(ROOT/'docs/reviews/tensor-trace-accuracy-v1/corpus.json',root/'corpus.json')
    code=r'''
import json,math,struct,tempfile,pathlib
from atlas.dsl import Sym,trace,dev,evaluate,parse
from atlas.compiler import generate
bits=lambda x:struct.pack('>d',x).hex()
checks=0
for case in json.loads(pathlib.Path('corpus.json').read_text())['records']:
    a=Sym(tuple(float.fromhex(x) for x in case['inputs_hex'])+(0.,0.,0.))
    try:
        result=trace(a)
    except ValueError:
        assert not case['ok'],case['id']
    else:
        assert case['ok'] and bits(result)==case['expected_bits'],case['id']
    checks+=1
for component in range(6):
    for invalid in (float('inf'),-float('inf'),float('nan'),True,None,1j):
        a=[0.]*6;a[component]=invalid
        try:trace(Sym(tuple(a)))
        except ValueError:pass
        else:raise AssertionError(('accepted invalid tensor',component,repr(invalid)))
        checks+=1
for bad in (Sym((0.,)*5),Sym((0.,)*7),[0.]*6,None):
    try:trace(bad)
    except ValueError:pass
    else:raise AssertionError('accepted wrong tensor shape')
    checks+=1
A=Sym((1e308,1e308,1e308,0.,0.,0.))
for expr in ('select(trace(A)>0,1,2)','0*trace(A)','select(trace(dev(A))>0,1,2)'):
    try:evaluate(parse(expr),{'A':A})
    except ValueError:pass
    else:raise AssertionError(('masked invalid trace',expr))
    checks+=1
for expr,expected in [('select(1>0,7,trace(A))',7.),('select(1<0,trace(A),9)',9.)]:
    assert evaluate(parse(expr),{'A':A})==expected
    checks+=1
assert dev(Sym((3.,0.,0.,2.,-1.,4.))).v==(2.,-1.,-1.,2.,-1.,4.)
checks+=1
# Generate actual complete model headers from the candidate compiler path.
for context in ('equation','derived','domain','initial','observable','reset'):
    m=json.loads(pathlib.Path('fixtures/direct.json').read_text())
    m['id']='test-trace-'+context
    m['equations']['sigma']='0*K*I'
    expr='select(trace(A)>0,1,2)'
    if context=='equation':m['equations']['sigma']='K*('+expr+')*I'
    elif context=='derived':m['derived']=[{'name':'q','expr':expr}]
    elif context=='domain':m['domain']=[expr+'>0']
    elif context=='initial':m['initial_checks']=[expr+'>0']
    elif context=='observable':m=json.loads(pathlib.Path('fixtures/time-observable.json').read_text());m['equations']['sigma']='0*K*strain_rate';m['observables']=[{'name':'stress','shape':'sym','unit':'Pa','scale':'K','expr':'K*('+expr+')*I'}]
    else:m['increment_reset']={'scope':'parent_increment','updates':[{'target':'A','guard':expr,'value':'0*I'}]}
    p=pathlib.Path(context+'.json');p.write_text(json.dumps(m))
    with tempfile.TemporaryDirectory() as tmp:
        generate(tmp,[p])
        header=(pathlib.Path(tmp)/'models.hpp').read_text()
        assert 'atlas::trace_or_mark(A, atlas_eval_ok)' in header,context
    checks+=1
print(json.dumps({'version':'trace-context-candidate-source-checks-v1','checks':checks,'pass':True,'compiled_execution':False,'full_generated_context_semantics_verified':False},sort_keys=True))
'''
    bootstrap='import sys,os;sys.path.insert(0,sys.argv[1]);os.chdir(sys.argv[1]);exec(sys.argv[2])'
    proc=subprocess.run([sys.executable,'-I','-S','-B','-c',bootstrap,str(root),code],text=True,capture_output=True)
    print(proc.stdout,end='');print(proc.stderr,end='',file=sys.stderr)
    raise SystemExit(proc.returncode)
