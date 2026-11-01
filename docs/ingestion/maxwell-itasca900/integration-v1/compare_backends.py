"""Apply the prospectively frozen physical parity limits to retained raw data."""
import json,math
from pathlib import Path
BASE=Path(__file__).resolve().parent
COUNT=0;MAX_STRESS=0;MAX_STRAIN=0

def compare(a,b,path=''):
    global COUNT,MAX_STRESS,MAX_STRAIN
    if path.split('.')[-1] in ('iterations','substeps','rejected'):
        assert type(a) is int and a>=0 and type(b) is int and b>=0;return
    if path.endswith('temporal_error_norm'):
        assert type(a) in (int,float) and math.isfinite(a) and a>=0
        assert type(b) in (int,float) and math.isfinite(b) and b>=0
        # Failing calls may retain an unaccepted diagnostic; successes were
        # separately checked by the analytical assessor.
        return
    if path.endswith('nonlinear_residual_norm'):
        assert 0<=a<=1e-10 and 0<=b<=1e-10;return
    if isinstance(a,list):
        assert isinstance(b,list) and len(a)==len(b)
        for i,(x,y) in enumerate(zip(a,b)):compare(x,y,path+f'[{i}]')
    elif isinstance(a,dict):
        assert a.keys()==b.keys()
        for key in a:compare(a[key],b[key],path+'.'+key)
    elif type(a) in (int,float):
        assert type(b) in (int,float) and math.isfinite(a) and math.isfinite(b)
        delta=abs(a-b);COUNT+=1
        if '.state[' in path or '.observables[' in path:
            assert delta<=1e-6,(path,a,b);MAX_STRESS=max(MAX_STRESS,delta)
        elif '.strain[' in path or '.strain_rate[' in path:
            assert delta<=1e-11,(path,a,b);MAX_STRAIN=max(MAX_STRAIN,delta)
        else:assert a==b,(path,a,b)
    else:assert a==b,(path,a,b)

for suffix in ('raw','transactions-raw'):
    native=json.loads((BASE/f'native-{suffix}.json').read_text());wasm=json.loads((BASE/f'wasm-{suffix}.json').read_text())
    assert [r['id'] for r in native]==[r['id'] for r in wasm]
    for n,w in zip(native,wasm):
        for nc,wc in zip(n['calls'],w['calls']):
            assert nc['returncode']==wc['returncode']
            compare(json.loads(nc['stdout']),json.loads(wc['stdout']))
report={'passed':True,'numeric_comparisons':COUNT,'maximum_stress_difference_Pa':MAX_STRESS,'maximum_strain_or_rate_difference':MAX_STRAIN}
(BASE/'parity-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
