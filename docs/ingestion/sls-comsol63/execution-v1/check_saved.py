"""Read-only frozen SLS raw evidence/reference/parity verification."""
import importlib.util,json,hashlib
from pathlib import Path
BASE=Path(__file__).resolve().parent;ROOT=BASE.parents[3]
spec=importlib.util.spec_from_file_location('sls_study',BASE/'study.py');study=importlib.util.module_from_spec(spec);spec.loader.exec_module(study)
cases=json.loads((BASE/'cases.json').read_text())['cases']
rows={b:json.loads((BASE/('native-observe-v2-raw.json'if b=='native'else 'wasm-raw.json')).read_text())for b in ['native','wasm']}
for backend,data in rows.items():
    report=study.assess(cases,data)
    if backend=='native':report['original_material_calls_preserved']=True
    assert report==json.loads((BASE/(backend+'-report.json')).read_text())
count=0;largest={'strain':0.,'q':0.,'stress':0.}
def compare(a,b):
    global count
    assert a['ok']==b['ok'] and a.get('message')==b.get('message')
    if 'state'in a:
        assert len(a['state'])==len(b['state'])
        for key,tol,aa,bb in [('strain',2e-7,a['state'][:6],b['state'][:6]),('q',1e-6,a['state'][6:],b['state'][6:])]:
            e=study.error(aa,bb);assert e<=tol,(key,e);largest[key]=max(largest[key],e);count+=len(aa)
    for key in ['initial','parameters','strain_rate','start_time','duration','solver','model','catalogue_hash']:
        if key in a:assert a[key]==b[key],key
    if 'time'in a:assert abs(a['time']-b['time'])<=1e-12*max(1,abs(a['time']))
    if 'points'in a:
        assert len(a['points'])==len(b['points'])
        for x,y in zip(a['points'],b['points']):
            assert x['time']==y['time'] and x['segment']==y['segment']and x['side']==y['side']
            compare(dict(ok=True,state=x['state']),dict(ok=True,state=y['state']))
            for key,tol,label in [('strain',2e-7,'strain'),('observables',1e-6,'stress')]:
                e=study.error(x[key],y[key]);assert e<=tol,(key,e);largest[label]=max(largest[label],e);count+=len(x[key])
for n,w in zip(rows['native'],rows['wasm']):
    assert n['id']==w['id']
    for a,b in zip(n['calls'],w['calls']):
        assert a['returncode']==b['returncode'];compare(json.loads(a['stdout']),json.loads(b['stdout']))
    if 'observation'in n:
        a,b=json.loads(n['observation']),json.loads(w['observation']);assert a['ok']==b['ok']==True
        e=study.error(a['values'],b['values']);assert e<=1e-6;largest['stress']=max(largest['stress'],e);count+=len(a['values'])
print(json.dumps(dict(passed=True,cases_per_backend=len(cases),material_calls_per_backend=2*len(cases),physical_scalars_compared=count,max_parity_error=largest),indent=2))
