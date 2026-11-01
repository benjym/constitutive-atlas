"""Verify saved publication/upload/live/browser evidence; no material calls."""
from pathlib import Path
import hashlib,json,tarfile,argparse

HERE=Path(__file__).resolve().parent
sha=lambda data:hashlib.sha256(data).hexdigest()
def read(name):return json.loads((HERE/name).read_text())

def upload(archive):
    policy=read('LIVE_POLICY-v2.json')
    with tarfile.open(archive) as t:
        members=t.getmembers()
        assert all(m.isfile() or m.isdir() for m in members),'Links/special archive members rejected'
        names=[m.name.removeprefix('./') for m in members]
        assert all(n and not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
        files=[m for m in members if m.isfile()]
        assert len(files)==len({m.name.removeprefix('./') for m in files})
        data={m.name.removeprefix('./'):t.extractfile(m).read() for m in files}
    inventory={n:sha(b) for n,b in data.items()}
    manifest=json.loads(data['engine-implicit-path/package-manifest.json'])
    identity=json.loads(data['engine-implicit-path/identity.json'])
    assert manifest['kind']=='implicit-path-main-atlas-1'
    for n,h in manifest['files'].items():assert inventory[n]==h,n
    assert identity['release_revision']==policy['revision']
    assert identity['model']==policy['model'] and identity['public_models']==[policy['model']]
    for k in ['model_sha256','review_sha256','module_sha256','wasm_sha256']:assert identity[k]==policy[k]
    assert inventory['app.js']==policy['app_sha256']
    for file,key in [(policy['model']+'.json','model_sha256'),('review.json','review_sha256'),('approval.json','approval_sha256'),('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256'),('models.json','catalogue_file_sha256')]:assert inventory['engine-implicit-path/'+file]==identity[key]
    assert set(policy['required_live_paths'])<=inventory.keys()
    acquisition=read('upload-acquisition.json');artifacts=read('run-artifacts.json')['artifacts']
    matches=[a for a in artifacts if a['id']==acquisition['artifact_id']]
    assert len(matches)==1
    artifact=matches[0]
    assert artifact['name']==policy['artifact_name'] and not artifact['expired']
    assert artifact['workflow_run']['head_sha']==policy['revision']
    assert artifact['workflow_run']['id']==policy['run']==acquisition['run']
    assert acquisition['artifact_tar_sha256']==sha(Path(archive).read_bytes())
    (HERE/'tested-upload.json').write_text(json.dumps(inventory,indent=2)+'\n')
    (HERE/'uploaded-identity.json').write_bytes(data['engine-implicit-path/identity.json'])
    (HERE/'uploaded-package-manifest.json').write_bytes(data['engine-implicit-path/package-manifest.json'])
    return {'passed':True,'files':len(inventory),'archive_sha256':acquisition['artifact_tar_sha256'],'revision':policy['revision']}

def final():
    policy=read('LIVE_POLICY-v2.json');ci=read('release-run.json')
    assert ci['headSha']==policy['revision'] and ci['status']=='completed' and ci['conclusion']=='success'
    assert {j['name'] for j in ci['jobs']}==set(policy['required_jobs'])
    assert all(j['status']=='completed' and j['conclusion']=='success' for j in ci['jobs'])
    dep=read('deployment.json')
    assert dep['deployment']['sha']==policy['revision'] and dep['statuses'][0]['state']=='success'
    tested=read('tested-upload.json');live=read('live-assets.json')
    assert live['passed'] and live['revision']==policy['revision'] and live['run']==policy['run']
    assert len(live['assets'])==len(policy['required_live_paths'])
    assert {a['path'] for a in live['assets']}==set(policy['required_live_paths'])
    for a in live['assets']:assert a['status']==200 and a['expected']==a['observed']==tested[a['path']]
    identity=read('uploaded-identity.json')
    reference=(HERE/'public-presets-v1.json').read_bytes();assert sha(reference)==policy['reference_report_sha256']
    refs={r['name']:r for r in json.loads(reference)['rows']}
    counts={}
    for name in policy['browser_presets']:
        export=read('browser-'+name+'-export.json');state=read('browser-'+name+'-state.json')
        assert export['provenance']==identity and export['controls']==refs[name]['controls']
        result=dict(export['result']);expected=dict(refs[name]['phases'][0]['result'])
        result.pop('elapsed_ms');expected.pop('elapsed_ms');assert result==expected
        assert len(result['points'])==policy['increments_per_preset']+1
        assert state['url']==policy['base_url']+policy['route'] and state['model']==policy['model']
        assert state['exportDisabled'] is False and state['stateRows']==policy['increments_per_preset']+2
        assert len(state['plots'])==4 and all(p['distinctPoints']>=3 and p['distinctY']>=2 for p in state['plots'])
        required={'engine-implicit-path/review.html','engine-implicit-path/approval.json','engine-implicit-path/review.json','engine-implicit-path/'+policy['model']+'.json'}
        assert required<=set(state['links'])
        counts[name]=len(result['points'])
    assert read('browser-console.json')==[]
    return {'passed':True,'revision':policy['revision'],'run':policy['run'],'required_jobs':len(ci['jobs']),'live_assets':len(live['assets']),'browser_full_response_points':counts,'scope':'Named public small-strain zero-pore-pressure preparations; no experimental validation or broader arbitrary-input claim'}

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--archive',type=Path);args=parser.parse_args()
    print(json.dumps(upload(args.archive) if args.archive else final(),indent=2))
