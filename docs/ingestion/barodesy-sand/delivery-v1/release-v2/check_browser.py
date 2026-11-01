"""Assess actual downloaded Chrome runs, frozen references and exact native controls replay."""
import json, subprocess, pathlib, sys
ROOT=pathlib.Path('/Users/bmar5496/code/constitutive-atlas')
HERE=pathlib.Path(__file__).resolve().parent.parent
B=ROOT/'output/playwright/barodesy-sand-v2'
refs=json.loads((HERE/'references.json').read_text())
rows=[]
for f in sorted(B.glob('*.json')):
    p=json.loads(f.read_text())
    if not isinstance(p,dict) or p.get('schema_version')!='atlas-laboratory-export-0.2' or f.stem in ['tampered','import-replayed']: continue
    s=p['specification']; r=p['result']; assert r['ok'], f
    controls=B/(f.stem+'-controls.txt'); controls.write_text(','.join(s['loading']['controls_bits']))
    settings=s['integration_settings']; settings_csv=','.join(str(settings[k]) for k in ['residual_tolerance','rate_tolerance','max_iterations','max_depth','max_substeps','max_backtracks'])
    cmd=[str(ROOT/'.local/barodesy-sand-delivery-v1/native/atlas_solver'),'--mode','run-controls','--model',s['model'],'--parameters',','.join(map(str,s['parameters'])),'--initial',','.join(map(str,s['initial'])),'--protocol',str(s['protocol']),'--integration-settings',settings_csv,'--laboratory-controls-file',str(controls),'--response-contract','stress-scope-0.1']
    run=subprocess.run(cmd,capture_output=True,text=True,check=True)
    (B/(f.stem+'-native.txt')).write_text(run.stdout)
    native=json.loads(run.stdout); assert native['ok'], native
    def scaled(a,b):
        if isinstance(a,dict):
            assert a.keys()==b.keys();return max([scaled(a[k],b[k]) for k in a]+[0.])
        if isinstance(a,list):
            assert len(a)==len(b);return max([scaled(x,y) for x,y in zip(a,b)]+[0.])
        if isinstance(a,(float,int)) and not isinstance(a,bool):return abs(a-b)/max(1.,abs(a),abs(b))
        assert a==b;return 0.
    difference=scaled(native['points'],r['points'])
    assert difference<=1e-10,(f,difference)
    if f.stem.startswith('protocol-') or f.stem=='default':assert difference==0.
    row={'id':f.stem,'points':len(r['points']),'exact_native_points':native['points']==r['points'],'native_max_scaled_difference':difference}
    ref=refs.get(f.stem)
    if ref:
        assert len(ref['points'])==len(r['points'])
        errs=[0.,0.,0.]
        for a,b in zip(r['points'],ref['points']):
            vals=[max(abs(a['state'][i]-b[i]) for i in range(3)),abs(a['state'][6]-b[3]),max(abs(a['strain'][i]-b[i+4]) for i in range(3))]
            errs=[max(x,y) for x,y in zip(errs,vals)]
        assert all(x<=v for x,v in zip(errs,[5,2e-7,2e-7])),(f,errs)
        row['independent_reference_max_errors_stress_void_strain']=errs
    rows.append(row)
assert len([r for r in rows if r['id'].startswith('protocol-')])==10
print(json.dumps({'pass':True,'rows':rows,'native_replay':'exact downloaded IEEE754 loading; preexisting frozen 1e-10 scaled parity budget for all point fields, exact equality additionally observed/required for original ten histories and default; elapsed excluded'},indent=2))
