"""Saved-only integrity, independent reference replay and physical parity."""
from pathlib import Path
import hashlib,json,math,sys
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R))
from study import assess,execute
from reference import reference

def parity(native,wasm):
    assert len(native)==len(wasm)
    max_stress=0.;max_strain=0.;scalars=0
    def compare(a,b,budget,kind):
        nonlocal max_stress,max_strain,scalars
        assert len(a)==len(b)
        for x,y in zip(a,b):
            if x is None or y is None:assert x is y;continue
            assert math.isfinite(x) and math.isfinite(y)
            diff=abs(x-y);assert diff<=budget,(kind,diff,budget)
            if kind=='stress':max_stress=max(max_stress,diff)
            else:max_strain=max(max_strain,diff)
            scalars+=1
    for n,w in zip(native,wasm):
        assert n['label']==w['label'] and n['function']==w['function']
        a=n['response'];b=w['response']
        if n['label']=='descriptor':assert a==b;continue
        assert a['ok']==b['ok']
        for key in ['catalogue_hash','time','start_time','duration','solver','segments','model']:
            if key in a:assert a[key]==b[key],key
        if 'state' in a:
            assert len(a['state'])==len(b['state'])==12
            compare(a['state'][:6],b['state'][:6],.01,'stress');compare(a['state'][6:],b['state'][6:],1e-9,'strain')
        if 'points' in a:
            assert len(a['points'])==len(b['points'])
            for x,y in zip(a['points'],b['points']):
                for key in ['time','side','segment']:assert x[key]==y[key]
                assert len(x['state'])==len(y['state'])==12
                for key in ['strain','strain_rate','observables']:assert len(x[key])==len(y[key])==6
                compare(x['state'][:6],y['state'][:6],.01,'stress')
                compare(x['state'][6:],y['state'][6:],1e-9,'strain')
                compare(x['observables'],y['observables'],.01,'stress')
                compare(x['strain'],y['strain'],1e-9,'strain')
                compare(x['strain_rate'],y['strain_rate'],1e-9,'strain')
        if 'values' in a:compare(a['values'],b['values'],.01,'stress')
    return dict(ok=True,physical_scalars=scalars,maximum_stress_difference_Pa=max_stress,maximum_strain_or_rate_difference=max_strain)

def verify(installed=True):
    freeze=json.loads((R/'freeze.json').read_text())
    for name,digest in freeze['inputs'].items():assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
    assert hashlib.sha256((R/'frozen-source.tar.gz').read_bytes()).hexdigest()==freeze['source_archive_sha256']
    manifest=json.loads((R/'manifest.json').read_text()) if (R/'manifest.json').exists() else None
    if manifest:
        for name,digest in manifest['files'].items():
            assert hashlib.sha256((R/name).read_bytes()).hexdigest()==digest,name
    # Reference replay uses equations/closed forms, never compiled artifacts.
    expected=json.loads((R/'references.json').read_text())
    for c in json.loads((R/'requests.json').read_text())['schedules']:
        assert reference(c['spec'],160)==expected[c['id']]
    native=json.loads((R/'native-calls.json').read_text());wasm=json.loads((R/'wasm-calls.json').read_text())
    class Replay:
        def __init__(self,entries):self.entries=entries;self.calls=[]
        def call(self,label,function,args,command):
            entry=self.entries[len(self.calls)]
            assert (label,function,args)==(entry['label'],entry['function'],entry['args']),label
            self.calls.append(entry)
            return entry['response']
    for entries in [native,wasm]:
        replay=Replay(entries);execute(replay);assert len(replay.calls)==len(entries)
    result=dict(native=assess(native),wasm=assess(wasm),parity=parity(native,wasm))
    if installed:
        root=R.parents[3]
        if manifest:
            for name,digest in manifest['installed_files'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
        assert (root/'models/research/burgers/burgers-itasca900-dry-zero-spin-ode.json').read_bytes()==(R/'model.json').read_bytes()
        assert (R/'target.cmake').read_text() in (root/'CMakeLists.txt').read_text()
        for name,digest in freeze['prior_models'].items():assert hashlib.sha256((root/name).read_bytes()).hexdigest()==digest,name
    return result

if __name__=='__main__':print(json.dumps(verify(),indent=2))
