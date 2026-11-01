"""Strict saved release verification; no network or material calls."""
from pathlib import Path,PurePosixPath
import argparse,hashlib,json,math,struct,tarfile,zipfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sha=lambda data:hashlib.sha256(data).hexdigest()
MAX_ZIP=512*1024*1024
MAX_TAR=1024*1024*1024
MAX_FILES=10000
MAX_FILE=128*1024*1024
def stream_sha(stream):
    h=hashlib.sha256()
    for data in iter(lambda:stream.read(1024*1024),b''):h.update(data)
    return h.hexdigest()
def file_sha(path):
    with path.open('rb') as stream:return stream_sha(stream)
def number(token):
    value=float(token)
    if not math.isfinite(value):raise ValueError('Nonfinite JSON number')
    return value
def integer(token):
    number(token)
    return -0.0 if token=='-0' else int(token)
def pairs(items):
    result={}
    for key,value in items:
        if key in result:raise ValueError('Duplicate JSON key')
        result[key]=value
    return result
def invalid(value):raise ValueError('Nonfinite JSON constant: '+value)
def parse(data):return json.loads(data,parse_constant=invalid,parse_int=integer,parse_float=number,object_pairs_hook=pairs)
def read(name):return parse((HERE/name).read_bytes())
def equal(a,b):
    if type(a) is bool or type(b) is bool:return type(a) is type(b) and a is b
    if isinstance(a,(int,float)) and isinstance(b,(int,float)):
        return math.isfinite(a) and math.isfinite(b) and struct.pack('>d',float(a))==struct.pack('>d',float(b))
    if type(a) is not type(b):return False
    if isinstance(a,dict):return a.keys()==b.keys() and all(equal(a[k],b[k]) for k in a)
    if isinstance(a,list):return len(a)==len(b) and all(equal(x,y) for x,y in zip(a,b))
    return a==b

def member_name(name,directory):
    p=PurePosixPath(name)
    assert name and not p.is_absolute() and '..' not in p.parts and '\\' not in name
    n=p.as_posix()
    if n=='.':assert directory;return None
    assert n and not n.endswith('/')
    return n

def private_file(relative):
    p=Path(relative);assert not p.is_absolute() and '..' not in p.parts
    q=(ROOT/p).resolve();assert q.is_relative_to(ROOT.resolve()) and q.is_file()
    return q

def upload_data():
    policy=read('LIVE_POLICY-v4.json');acq=read('upload-acquisition.json');metadata=read('run-artifacts.json')
    matches=[a for a in metadata['artifacts'] if a['id']==acq['artifact_id']];assert len(matches)==1
    artifact=matches[0]
    assert artifact['name']==policy['artifact_name'] and artifact['expired'] is False
    assert artifact['workflow_run']['head_sha']==acq['head_sha']==policy['revision']
    assert artifact['workflow_run']['id']==acq['run']==policy['run']
    archive=private_file(acq['artifact_tar_path']);outer=private_file(acq['artifact_zip_path'])
    assert outer.stat().st_size<=MAX_ZIP and archive.stat().st_size<=MAX_TAR
    outer_hash=file_sha(outer);assert artifact['digest']=='sha256:'+outer_hash==acq['api_digest']
    assert outer_hash==acq['artifact_zip_sha256']
    with zipfile.ZipFile(outer) as z:
        files=[];infos=z.infolist()
        assert len(infos)<=16 and sum(m.file_size for m in infos)<=MAX_TAR
        for m in infos:
            assert m.file_size<=MAX_TAR and not (m.flag_bits&1)
            n=member_name(m.filename,m.is_dir())
            if not m.is_dir():files.append((n,m))
        assert len(files)==1 and files[0][0]=='artifact.tar'
        with z.open(files[0][1]) as stream:zip_tar_hash=stream_sha(stream)
    archive_hash=file_sha(archive);assert zip_tar_hash==archive_hash==acq['artifact_tar_sha256']
    with tarfile.open(archive) as t:
        data={};inventory={};count=0;total=0
        for m in t:
            count+=1;total+=m.size
            assert count<=MAX_FILES and total<=MAX_TAR and 0<=m.size<=MAX_FILE
            assert m.isfile() or m.isdir(),'Special archive member'
            n=member_name(m.name,m.isdir())
            if m.isfile():
                assert n not in inventory,'Duplicate file'
                with t.extractfile(m) as stream:inventory[n]=stream_sha(stream)
                if n in ['engine-implicit-path/package-manifest.json','engine-implicit-path/identity.json']:
                    assert m.size<=1024*1024
                    data[n]=t.extractfile(m).read()
    manifest=parse(data['engine-implicit-path/package-manifest.json']);identity=parse(data['engine-implicit-path/identity.json'])
    assert manifest['kind']=='implicit-path-main-atlas-1'
    for n,h in manifest['files'].items():assert inventory[n]==h,n
    assert identity['release_revision']==policy['revision'] and identity['model']==policy['model']
    assert identity['public_models']==[policy['model']]
    for key in ['model_sha256','review_sha256','module_sha256','wasm_sha256']:assert identity[key]==policy[key]
    assert inventory['app.js']==policy['app_sha256']
    for file,key in [(policy['model']+'.json','model_sha256'),('review.json','review_sha256'),('approval.json','approval_sha256'),('lade-domain.mjs','module_sha256'),('lade-domain.wasm','wasm_sha256'),('models.json','catalogue_file_sha256')]:assert inventory['engine-implicit-path/'+file]==identity[key]
    assert set(policy['required_live_paths'])<=inventory.keys()
    report={'passed':True,'revision':policy['revision'],'run':policy['run'],'artifact_id':artifact['id'],'outer_zip_sha256':outer_hash,'tar_sha256':archive_hash,'files':len(inventory),'policy_sha256':sha((HERE/'LIVE_POLICY-v4.json').read_bytes()),'acquisition_sha256':sha((HERE/'upload-acquisition.json').read_bytes()),'api_metadata_sha256':sha((HERE/'run-artifacts.json').read_bytes()),'identity_sha256':sha(data['engine-implicit-path/identity.json']),'manifest_sha256':sha(data['engine-implicit-path/package-manifest.json'])}
    return inventory,identity,manifest,report,data

def upload():
    inventory,identity,manifest,report,data=upload_data()
    encoded=(json.dumps(inventory,indent=2)+'\n').encode();report['inventory_sha256']=sha(encoded)
    for name,value in [('tested-upload.json',encoded),('uploaded-identity.json',data['engine-implicit-path/identity.json']),('uploaded-package-manifest.json',data['engine-implicit-path/package-manifest.json'])]:
        p=HERE/name
        if p.exists():assert p.read_bytes()==value,'Preserve prior upload evidence'
        else:p.write_bytes(value)
    p=HERE/'upload-verification.json';value=(json.dumps(report,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==value
    else:p.write_bytes(value)
    return report

def final():
    policy=read('LIVE_POLICY-v4.json');ci=read('release-run.json')
    assert ci['databaseId']==policy['run'] and ci['headSha']==policy['revision'] and ci['status']=='completed' and ci['conclusion']=='success'
    assert len(ci['jobs'])==len(policy['required_jobs']) and {j['name'] for j in ci['jobs']}==set(policy['required_jobs'])
    assert all(j['status']=='completed' and j['conclusion']=='success' for j in ci['jobs'])
    dep=read('deployment.json');deployment=dep['deployment'];status=dep['statuses'][0]
    assert deployment['sha']==policy['revision'] and deployment['ref']=='main' and deployment['environment']=='github-pages'
    assert status['state']=='success' and status['environment']=='github-pages' and status['environment_url']==policy['base_url']
    job=next(j for j in ci['jobs'] if j['name']=='deploy')
    expected_url=f"https://github.com/benjym/constitutive-atlas/actions/runs/{policy['run']}/job/{job['databaseId']}"
    assert status['target_url']==expected_url and status['log_url']==expected_url and status['deployment_url']==deployment['url']
    tested,identity,manifest,verification,data=upload_data()
    verification['inventory_sha256']=sha((json.dumps(tested,indent=2)+'\n').encode())
    assert equal(read('upload-verification.json'),verification)
    assert equal(read('tested-upload.json'),tested)
    assert sha((HERE/'uploaded-identity.json').read_bytes())==verification['identity_sha256']
    assert sha((HERE/'uploaded-package-manifest.json').read_bytes())==verification['manifest_sha256']
    live=read('live-assets.json')
    assert live['passed'] is True and live['revision']==policy['revision'] and live['run']==policy['run']
    assert len(live['assets'])==len(policy['required_live_paths']) and {a['path'] for a in live['assets']}==set(policy['required_live_paths'])
    for a in live['assets']:assert a['status']==200 and a['expected']==a['observed']==tested[a['path']]
    reference=(HERE/'public-presets-v1.json').read_bytes();assert sha(reference)==policy['reference_report_sha256'];refs={r['name']:r for r in parse(reference)['rows']};counts={}
    for name in policy['browser_presets']:
        export=read('browser-'+name+'-export.json');state=read('browser-'+name+'-state.json')
        assert equal(export['provenance'],identity) and equal(export['controls'],refs[name]['controls'])
        result=dict(export['result']);expected=dict(refs[name]['phases'][0]['result']);result.pop('elapsed_ms');expected.pop('elapsed_ms');assert equal(result,expected)
        assert len(result['points'])==policy['increments_per_preset']+1
        assert state['url']==policy['base_url']+policy['route'] and state['model']==policy['model']
        assert state['exportDisabled'] is False and state['stateRows']==policy['increments_per_preset']+2
        assert len(state['plots'])==4 and all(p['distinctPoints']>=3 and p['distinctY']>=2 for p in state['plots'])
        required={'engine-implicit-path/review.html','engine-implicit-path/approval.json','engine-implicit-path/review.json','engine-implicit-path/'+policy['model']+'.json'}
        assert required<=set(state['links']);counts[name]=len(result['points'])
    assert read('browser-console.json')==[]
    return {'passed':True,'revision':policy['revision'],'run':policy['run'],'required_jobs':len(ci['jobs']),'live_assets':len(live['assets']),'browser_full_response_points':counts,'scope':'Named bounded preparations; no experimental or general arbitrary-input claim'}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--upload',action='store_true');args=parser.parse_args();print(json.dumps(upload() if args.upload else final(),indent=2))
