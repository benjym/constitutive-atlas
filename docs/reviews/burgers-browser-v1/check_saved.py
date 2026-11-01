"""Reassess saved delivery calls, browser downloads and package byte bindings.
Reads binaries only for hashes; never loads/runs compiled/vendor code.
"""
from pathlib import Path
import argparse, hashlib, importlib.util, json, sys, tarfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DELIVERY=ROOT/'docs/ingestion/burgers-itasca900/delivery-v1'
PACKET=ROOT/'docs/ingestion/burgers-itasca900/integration-v1'
sys.path.insert(0,str(PACKET));sys.path.insert(0,str(ROOT))
from study import assess
from verify import parity
from reference import reference

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def run(site,study,source):
    site=Path(site);study=Path(study);source=Path(source)
    calls={b:json.loads((study/b/'calls.json').read_text()) for b in ['native','wasm']}
    assessment={b:assess(rows) for b,rows in calls.items()}
    pairs=parity(calls['native'],calls['wasm'])
    spec=importlib.util.spec_from_file_location('review_native_refinement',ROOT/'tools/test_burgers_native.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    refinement={b:module.refinement(rows) for b,rows in calls.items()}
    for b in calls:
        report=json.loads((study/b/'report.json').read_text())
        assert report['separate_refinement']==refinement[b] and report['Kelvin_corruption_rejected']
    refs=json.loads((PACKET/'references.json').read_text())
    downloaded={}
    for name,refid in [('burgers-release-default.json','relaxation'),('burgers-release-creep.json','creep'),('burgers-custom.json',None)]:
        doc=json.loads((DELIVERY/name).read_text()); actual=doc['result']['points']
        if refid is not None:
            expected=refs[refid]
        else:
            c=doc['controls']
            spec=dict(initial=c['initial'],initial_strain=c['strain'],start_time=c['start'],parameters=c['parameters'],
                      segments=[dict(duration=c['duration'],samples=c['samples'],controls=[dict(quantity='stress' if c['mode']=='creep' else 'strain',kind='hold') for _ in range(6)])])
            expected=reference(spec,160)
        assert len(actual)==len(expected)
        stress=history=strain=0.
        for a,b in zip(actual,expected):
            assert a['time']==float(b['time']) and a['segment']==b['segment'] and a['side']==b['side']
            stress=max(stress,max(abs(x-float(y)) for x,y in zip(a['state'][:6],b['state'][:6])))
            history=max(history,max(abs(x-float(y)) for x,y in zip(a['state'][6:],b['state'][6:])))
            strain=max(strain,max(abs(x-float(y)) for x,y in zip(a['strain'],b['strain'])))
        assert stress<=20 and history<=2e-6 and strain<=2e-6
        downloaded[name]={'stress_Pa':stress,'Kelvin_strain':history,'accumulated_strain':strain}
    assert json.loads((DELIVERY/'burgers-release-default.json').read_text())==json.loads((DELIVERY/'burgers-release-replay.json').read_text())
    inventory=json.loads((study/'source-files.json').read_text());count=0
    with tarfile.open(study/'source.tar.gz') as t:
        members={m.name:m for m in t if m.isfile()}
        for name,digest in inventory.items():
            assert hashlib.sha256(t.extractfile(members[name]).read()).hexdigest()==digest,name
            count+=1
    identity=json.loads((site/'engine-burgers/identity.json').read_text())
    for name in ['burgers-release-default.json','burgers-release-replay.json','burgers-release-creep.json']:
        assert json.loads((DELIVERY/name).read_text())['provenance']==identity,name
    for file,key in [('burgers.mjs','module_sha256'),('burgers.wasm','wasm_sha256'),('models.json','catalogue_file_sha256'),('approval.json','approval_sha256'),('review.json','review_sha256'),(identity['model']+'.json','model_sha256')]:
        assert sha(site/'engine-burgers'/file)==identity[key],file
    package=json.loads((site/'engine-burgers/package.json').read_text())
    for name,digest in package['files'].items():assert sha(site/name)==digest,name
    assets=json.loads((DELIVERY/'release-package-assets.json').read_text())
    for name,digest in assets.items():assert sha(site/name)==digest,name
    artifacts=json.loads((study/'artifacts.json').read_text())
    assert artifacts['wasm/burgers.wasm']['sha256']==identity['wasm_sha256']
    assert artifacts['wasm/burgers.mjs']['sha256']==identity['module_sha256']
    assert identity['model_sha256']=='1452a27d5d3b50989ca66df5beb7f08e22434596800133983339466d3571933c'
    for name in ['timed-contract.mjs','timed-laboratory.mjs','timed-worker.mjs']:
        assert sha(source/'web'/name)==sha(site/name),name
    assert sha(source/'web/app.js')==sha(site/'app.js')
    assert not (site/'sls.html').exists() and not (site/'power-creep.html').exists() and not (site/'j2.html').exists()
    return {'saved_assessment':assessment,'saved_parity':pairs,'separate_refinement':refinement,
            'browser_download_reference_errors':downloaded,'exact_browser_replay':True,
            'frozen_build_source_files':count,'package_identity':identity,'release_asset_hashes_checked':len(assets),
            'retired_standalone_pages_absent':True,'reviewer_compiled_calls':0}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('site');parser.add_argument('--source',required=True)
    parser.add_argument('--study',default=str(DELIVERY/'release-build-v2'))
    args=parser.parse_args()
    print(json.dumps(run(args.site,args.study,args.source),indent=2))
