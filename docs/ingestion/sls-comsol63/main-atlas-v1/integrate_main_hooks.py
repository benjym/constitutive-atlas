"""Apply additive main-atlas registration to an explicitly supplied isolated tree."""
import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('root',type=Path);args=p.parse_args();root=args.root
app=root/'web/app.js';s=app.read_text()
old="import {setupTimedLaboratory} from './timed-laboratory.mjs';"
new=old+"\nimport {setupSlsLaboratory} from './sls-laboratory.mjs';\nimport {createLaboratoryControllerRouter} from './laboratory-controller-router.mjs';"
assert old in s and "from './sls-laboratory.mjs'" not in s;s=s.replace(old,new,1)
s=s.replace('entry.id===timedView?.modelId','timedView?.supports(entry.id)')
s=s.replace('entry.id!==timedView?.modelId','!timedView?.supports(entry.id)')
s=s.replace('id===timedView?.modelId','timedView?.supports(id)')
old="timedView=setupTimedLaboratory({chart,cancelOrdinary:()=>cancel('')})";assert old in s
s=s.replace(old,"timedView=createLaboratoryControllerRouter([setupTimedLaboratory({chart,cancelOrdinary:()=>cancel('')}),setupSlsLaboratory({chart,cancelOrdinary:()=>cancel('')})])",1)
assert 'timedView?.modelId' not in s;app.write_text(s)
builder=root/'tools/build_web.py';s=builder.read_text();marker="    (dest/'.nojekyll').touch()";assert marker in s
s=s.replace(marker,"    from build_sls_laboratory import bundle as bundle_sls_laboratory\n    bundle_sls_laboratory(dest,args.sls_wasm_dir)\n    subprocess.run(['node',str(ROOT/'tools/test_sls_laboratory_package.mjs'),str(dest)],check=True)\n"+marker,1);builder.write_text(s)
manifest=root/'catalogue/manifest.json';data=json.loads(manifest.read_text());entry=next(x for x in data['models'] if x['id']=='sls-comsol63-deviatoric-zero-spin-ode');entry['timed_laboratory']='index.html';entry['note']='Independently agent-reviewed bounded COMSOL6.3 ordinary deviatoric SLS plus elastic bulk; physical-time relaxation, creep and rate loading in the main atlas laboratory. Dry total stress, infinitesimal strain, fixed frame/zero spin. Exact passivity assumes traceless branch stress. Illustrative parameters; no calibration or experimental validation; broad machine parameter envelope unqualified.'
manifest.write_text(json.dumps(data,indent=2)+'\n')
print('Registered SLS main laboratory alongside existing timed model; no standalone page.')
