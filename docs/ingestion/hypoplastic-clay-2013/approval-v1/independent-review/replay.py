"""Read-only replay of retained clay2013 scientific evidence; no compiled calls.
Run: python3 -B path/to/replay.py --root /absolute/repository
"""
import argparse, contextlib, hashlib, importlib.util, io, json, runpy, struct, sys
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    root=a.root.resolve();sys.path.insert(0,str(root))
    read=lambda n:json.loads((root/n).read_text())
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    freeze=read('docs/ingestion/hypoplastic-clay-2013/approval-v1/INPUT_FREEZE.json')
    for n,h in freeze['inputs'].items():assert sha(root/n)==h,n
    retention=read('docs/ingestion/hypoplastic-clay-2013/approval-v1/private-retention.json')
    for path in (freeze['private_source']['path'],retention['private_durable_path']):assert sha(Path(path))==freeze['private_source']['sha256'],path
    pins=Path(__file__).with_name('replay-inputs.json')
    if pins.exists():
        for n,h in json.loads(pins.read_text()).items():assert sha(root/n)==h,n
    from atlas.evidence import checked_receipt
    receipts=0
    for doc in ('catalogue/investigations/clay2013-integration-v1/manifest.json','catalogue/investigations/clay-nonisotropic-v1/manifest.json','catalogue/investigations/clay2013-algebra-v1/manifest.json'):
        manifest=read(doc)
        for n,h in manifest['files'].items():
            checked_receipt(root,doc,n,h);receipts+=1
    m=read('models/hypoplastic-clay-2013.json')
    old=read('models/research/clay2013/hypoplastic-clay-2013-research.json')
    assert sha(root/'models/hypoplastic-clay-2013.json')==freeze['model_sha256']
    assert (root/'models/hypoplastic-clay-2013.json').read_bytes()==(root/'catalogue/investigations/clay2013-preview-v2/models/hypoplastic-clay-2013.json').read_bytes()
    for k in ('parameters','derived','equations','domain'):assert m[k]==old[k],k
    assert [(x['name'],x['shape'],x['unit'])for x in m['state']]==[(x['name'],x['shape'],x['unit'])for x in old['state']]
    from tools.clay2013_integration_study import assess as iso
    from tools.clay2013_nonisotropic_study import assess as noniso
    result={'freeze_inputs':len(freeze['inputs']),'historical_receipts':receipts,'source_hash_verified':True,'exact_model_preview_match':True,'unchanged_research_rates_and_domain':True,'backends':{}}
    reference=read('catalogue/investigations/clay-nonisotropic-v1/evidence.json')
    for backend in ('native','wasm'):
        i=read('catalogue/investigations/clay2013-integration-v1/'+backend+'.json')
        n=read('catalogue/investigations/clay-nonisotropic-v1/'+backend+'.json')
        si=iso(i['records'],old);sn=noniso(n['records'],old,reference)
        if 'summary'in i:
            saved=json.loads(json.dumps(i['summary']))
            for row in saved:row['key'][0]=float(row['key'][0])
            assert si==saved
        if 'summary'in n:assert sn==n['summary']
        result['backends'][backend]={'isotropic_trajectories':len(si),'isotropic_calls':sum(len(g['calls'])for g in i['records']),'nonisotropic_trajectories':len(sn),'nonisotropic_calls':sum(len(g['calls'])for g in n['records']),'tight_nonisotropic_max_stress_error_Pa':max(x['stress_max']for x in sn if x['tolerance']==1e-8)}
    wasm=read('catalogue/investigations/clay2013-integration-v1/wasm.json')
    for probe in wasm['failure_probes']:
        response=probe['response']
        if probe['kind']=='zero':assert response['ok']is True
        else:assert response['ok']is False and response['message']
        bits=lambda v:[struct.pack('>d',float(x))for x in v]
        assert bits(response['state'])==bits(probe['request']['initial'])
        assert response['diagnostics']['substeps']>0
    result['retained_partial_progress_rollback_probes']=sum(p['kind']!='zero' for p in wasm['failure_probes'])
    stream=io.StringIO()
    with contextlib.redirect_stdout(stream):runpy.run_path(str(root/'catalogue/investigations/clay2013-preview-v2/verify_study.py'))
    result['historical_actual_driver_browser_replay']=json.loads(stream.getvalue())
    result.update(pass_all=True,new_compiled_or_material_calls=0,current_runtime_delivery_certified=False)
    print(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':main()
