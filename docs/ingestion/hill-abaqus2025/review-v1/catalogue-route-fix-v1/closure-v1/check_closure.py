"""Source and retained-evidence review only: never executes a compiled model."""
import hashlib,json,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[5]
BASE='f8416d7732100b7502d2b4e6212c82420603bfcd';MERGE='3873a48b256ed37cbc78378ee6b41d73139676f8'
def blob(rev,p):return subprocess.check_output(['git','show',rev+':'+p],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
bindings={}
def retain(name,p):
 b=p.read_bytes();(OUT/name).write_bytes(b);bindings[name]=dict(source=str(p),sha256=sha(b));return b
old=json.loads(blob(BASE,'catalogue/manifest.json'));new=json.loads(blob(MERGE,'catalogue/manifest.json'))
e=next(x for x in old['models'] if x['id']=='hill-abaqus2025-perfect-be');assert e.pop('timed_laboratory')=='index.html';e['material_laboratory']='index.html';assert old==new
paths=['web','tools','.github','models','catalogue/approved-models.json','catalogue/agent-reviews','docs/admission/hill-abaqus2025-approved-v1','tests']
assert not subprocess.check_output(['git','diff','--name-only',BASE,MERGE,'--',*paths],cwd=ROOT).strip()
v5=Path('/private/tmp/atlas-hill-site-v5');v6=Path('/private/tmp/atlas-hill-site-v6')
assets=[p.relative_to(v5) for p in v5.rglob('*') if p.is_file() and p.suffix in ('.js','.mjs','.wasm')]
assert len(assets)==76
for p in assets:assert (v5/p).read_bytes()==(v6/p).read_bytes(),p
catalogue=json.loads((v6/'catalogue.json').read_text());assert catalogue==new
manifest=json.loads(retain('package-manifest.json',v6/'material-point-hill/package-manifest.json'))
assert len(manifest)==15
for p,h in manifest.items():assert sha((v6/p).read_bytes())==h
identity=json.loads(retain('identity.json',v6/'material-point-hill/identity.json'))
counts={}
for label in ['final','catalogue']:
 raw=retain('browser-'+label+'.txt',Path('/private/tmp/hill-browser-v6-'+label+'.txt')).decode()
 report=json.loads(raw.split('### Result\n',1)[1].split('\n### Ran Playwright code',1)[0])
 assert all(v is True for v in report['checks'].values());assert report['identity']==identity
 assert not report['page_errors'] and not report['console_errors'] and not report['request_failures']
 counts[label]=len(report['checks']);assert report['preset']['ok']
 retain('browser-'+label+'.js',Path('/private/tmp/hill-browser-v6-'+label+'.js'))
 (OUT/('browser-'+label+'-report.json')).write_text(json.dumps(report,indent=2)+'\n')
assert counts==dict(final=26,catalogue=28)
raw=retain('builder-v6.log',Path('/private/tmp/atlas-hill-builder-v6.log')).decode();assert 'Packaged /private/tmp/atlas-hill-site-v6' in raw
result=dict(accepted=True,E6='closed for exact corrected integration metadata',E7='closed for corrected bounded local package/browser scope',E8='open; remote required checks and verified live delivery remain',base=BASE,merged=MERGE,merged_manifest_sha256=sha(blob(MERGE,'catalogue/manifest.json')),only_production_semantic_delta='Hill timed_laboratory to material_laboratory index.html',unchanged_executable_assets=len(assets),strict_package_manifest_files=len(manifest),browser_pass_counts=counts,compiled_calls_by_reviewer=0,bindings=bindings)
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
