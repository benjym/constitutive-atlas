"""Pure source/package reconciliation checks. Never executes compiled artifacts."""
from pathlib import Path
import argparse, hashlib, json, subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DELIVERY=ROOT/'docs/ingestion/burgers-itasca900/delivery-v1'
REC=DELIVERY/'reconcile-v4'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def run(source,package):
    source,package=Path(source),Path(package)
    shared=['web/app.js','web/formulation-view.mjs','tools/build_web.py','catalogue/manifest.json']
    for name in shared: assert sha(source/name)==sha(REC/'source'/name),name
    base=DELIVERY/'reconcile-v3/base.json'
    assert json.loads(base.read_text())['base']=='61b8635a03b4c0405199cd839716116487354f19'
    plan=json.loads((DELIVERY/'reconcile-v3/archive-plan.json').read_text())
    original={}
    checked=source/'docs/ingestion/power-creep-itasca900/delivery-v2/builder-route-v3/review/checked-hashes.json'
    for binding in plan['bindings']:
        side=json.loads((source/binding['sidecar']).read_text())
        assert side['documents'][binding['document']]==sha(source/binding['document'])
        entry=next(x for x in side['entries'] if x['original_path']==binding['original_path'])
        assert entry['sha256']==binding['sha256']==sha(source/entry['archived_path'])
        assert json.loads(checked.read_text())['files'][entry['original_path']]==entry['sha256']
        original[entry['original_path']]=source/entry['archived_path']
    a={x['id']:x for x in json.loads(original['catalogue/manifest.json'].read_text())['models']}
    b={x['id']:x for x in json.loads((source/'catalogue/manifest.json').read_text())['models']}
    assert all(b[k]==v for k,v in a.items())
    assert set(b)-set(a)=={'burgers-itasca900-dry-zero-spin-ode'}
    burg=b['burgers-itasca900-dry-zero-spin-ode'];power=b['power-creep-itasca900-both-active-ode']
    assert burg['timed_laboratory']=='index.html' and not burg.get('public_timed_laboratory',False)
    assert power['timed_laboratory']=='power-creep.html' and power['public_timed_laboratory'] is True
    app=(source/'web/app.js').read_text();builder=(source/'tools/build_web.py').read_text()
    for token in ['import {timedLaboratoryRoute}', '!!timedLaboratoryRoute(entry)', "if(timedRoute){location.href=timedRoute;return;}", "entry.timed_laboratory==='index.html'", "location.hash='laboratory?model='+encodeURIComponent(entry.id)"]:
        assert token in app,token
    for token in ['bundle_power_creep(dest,args.power_creep_wasm_dir or args.wasm_dir)','bundle_burgers(dest,args.burgers_wasm_dir)',"'timed-route.mjs'",'test_power_creep_package.mjs','test_burgers_package.mjs']:
        assert token in builder,token
    for name in ['web/app.js','web/formulation-view.mjs','web/timed-route.mjs','web/timed-contract.mjs','web/timed-laboratory.mjs','web/timed-worker.mjs']:
        assert sha(source/name)==sha(package/Path(name).name),name
    old=json.loads((ROOT/'docs/reviews/burgers-browser-v1/package-inputs.json').read_text())['files']
    allowed={'app.js','catalogue.json','engine-burgers/identity.json','engine-burgers/package.json'}
    changed=[name for name,digest in old.items() if sha(package/name)!=digest]
    assert set(changed)<=allowed,changed
    oldidentity=json.loads((ROOT/'docs/reviews/burgers-browser-v1/saved-results.json').read_text())['package_identity']
    identity=json.loads((package/'engine-burgers/identity.json').read_text())
    assert {k:v for k,v in identity.items() if k!='release_revision'}=={k:v for k,v in oldidentity.items() if k!='release_revision'}
    assert identity['release_revision']=='7454234281e94cea7c2d8bae5121099fed677a5a'
    default=json.loads((REC/'burgers-reconciled-v4-default.json').read_text())
    replay=json.loads((REC/'burgers-reconciled-v4-replay.json').read_text())
    assert default==replay and default['provenance']==identity
    previous=json.loads((DELIVERY/'burgers-release-default.json').read_text())
    assert default['result']==previous['result'] and default['controls']==previous['controls']
    for name,digest in json.loads((REC/'package-assets.json').read_text()).items():assert sha(package/name)==digest,name
    packages={}
    for name in ['power-creep-package.json','engine-burgers/package.json']:
        files=json.loads((package/name).read_text())['files']
        for asset,digest in files.items(): assert sha(package/asset)==digest,asset
        packages[name]=len(files)
    assert (package/'power-creep.html').is_file()
    assert not (package/'sls.html').exists() and not (package/'j2.html').exists()
    return dict(preserved_existing_catalogue_entries=len(a),new_entries=[burg['id']],archive_receipt_edges_verified=len(plan['bindings']),unchanged_v1_package_assets=len(old)-len(changed),changed_v1_assets=changed,package_manifest_assets=packages,exact_browser_full_replay=True,browser_points=len(default['result']['points']),browser_result_identical_to_v1=True,compiled_calls=0,live_verified=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--package',required=True);a=p.parse_args()
    print(json.dumps(run(a.source,a.package),indent=2))
