from pathlib import Path
import json,hashlib,importlib.util,math,shutil
r=Path('/Users/bmar5496/code/constitutive-atlas');s=r/'catalogue/investigations/clay2013-preview-v2';source=Path('/Users/bmar5496/Documents/Codex/2026-10-30-let-s-start-a-new-major/.playwright-cli/hypoplastic-clay-2013-run.json');d=s/'browser';d.mkdir();shutil.copy2(source,d/'export.json')
for p in Path('/private/tmp').glob('atlas-clay2013-browser-v2-*.txt'):shutil.copy2(p,d/p.name)
load=lambda p:json.loads(p.read_text());req=next(x for x in load(s/'requests.json')if x['id']=='actual-consumer-default');doc=load(d/'export.json');spec=doc['specification'];result=doc['result'];expected={'model':req['model'],'parameters':list(map(float,req['parameters'].split(','))),'initial':list(map(float,req['initial'].split(','))),'protocol':req['protocol'],'target':req['target'],'steps':req['steps'],'cycles':req['cycles'],'integration_settings':dict(version='incremental-settings-0.1',norm='scaled_component_max',**dict(zip(load(s/'acceptance.json')['settings_order'],map(float,req['integration_settings'].split(',')))))}
assert spec==expected and result['ok']is True and len(result['points'])==101
module_spec=importlib.util.spec_from_file_location('clay2',s/'assess.py');m=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(m)
wasm=m.decode(next(x for x in load(s/'wasm/journal.json')if x['id']==req['id'])['raw']);assert doc['catalogue_hash']==wasm['catalogue_hash']
maxerror=0;volume=0
for point,reference in zip(result['points'],wasm['points']):
 a=m.physical({'points':[point]},'run')[0];b=m.physical({'points':[reference]},'run')[0]
 for x,y in zip(a,b):maxerror=max(maxerror,abs(x-y)/max(1,abs(x),abs(y)))
 volume=max(volume,abs(point['state'][6]-((1+spec['initial'][6])*math.exp(-math.fsum(point['strain'][:3]))-1)))
assert maxerror<=1e-10 and volume<=1e-6
snapshot=(d/'atlas-clay2013-browser-v2-snapshot.txt').read_text();assert '"10"'in snapshot and 'https://doi.org/10.1007/s11440-012-0199-y'in snapshot and './models/hypoplastic-clay-2013.json'in snapshot
assert 'Errors: 0, Warnings: 0'in(d/'atlas-clay2013-browser-v2-console.txt').read_text()
report={'pass':True,'exact_declared_specification':True,'points':101,'maximum_scaled_wasm_difference':maxerror,'maximum_independent_void_error':volume,'candidate_site_only':True,'scientific_admission':False,'deployment':False};(d/'comparison.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
