"""Read-only independent audit; no build or compiled artifact execution."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
LIVE=OUT.parent
SITE=Path('/private/tmp/atlas-occ-main-site-v1')
BASE='0db194b33703c4186ae197a421f98c46c1b96729'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=ROOT)
bound={}
def bind(p):
 p=Path(p);bound[str(p.relative_to(ROOT))]=sha(p)
repair=json.loads((LIVE/'harness-repair.json').read_text())
for row in repair['before']:
 old=git('show',BASE+':'+row['original_path'])
 archive=ROOT/row['archived_path'];current=ROOT/row['original_path']
 assert archive.read_bytes()==old and sha(archive)==row['sha256']
 assert current.read_bytes().replace(b'specialLaboratoryActive:()=>false,',b'',1)==old
 assert current.read_bytes().count(b'specialLaboratoryActive:()=>false,')==1
 bind(current);bind(archive)
maps=['docs/ingestion/barodesy-clay-2017/ncl-laboratory-v1/source-archive-map.json','docs/ingestion/burgers-itasca900/integration-v1/source-archive-map.json','docs/reviews/gis2024-mixed-catalogue-v1/source-archive-map.json','docs/reviews/gis2024-v03-research-freeze-v1/source-archive-map.json','docs/reviews/laboratory-scope-view-v1/source-archive-map.json','docs/reviews/sanisand-v03-research-freeze-v1/source-archive-map.json']
assert len(maps)==6
added=0
for name in maps:
 old=json.loads(git('show',BASE+':'+name));new=json.loads((ROOT/name).read_text())
 assert {k:v for k,v in old.items() if k!='entries'}=={k:v for k,v in new.items() if k!='entries'}
 assert new['entries'][:len(old['entries'])]==old['entries']
 extra=new['entries'][len(old['entries']):]
 assert extra and all(x in repair['before'] for x in extra)
 added+=len(extra);bind(ROOT/name)
manifest=json.loads((LIVE/'package-manifest-v1.json').read_text())
for name,row in manifest['files'].items():
 p=SITE/name;assert sha(p)==row['sha256'] and p.stat().st_size==row['bytes'],name
for name,digest in manifest['web_source_sha256'].items():
 assert sha(ROOT/name)==digest==sha(SITE/Path(name).name),name
assert sha(SITE/'atlas.wasm')==sha(Path('/private/tmp/atlas-occ-integration-v1/build-wasm/atlas.wasm'))
result=json.loads((LIVE/'supported-package-v1.json').read_text())
assert result['status']=='passed' and len(result['ordinary'])==13 and len(result['named'])==1
assert result['policy_sha256']==sha(ROOT/'catalogue/laboratory-package-policy.json')
success=0
for row in result['ordinary']:
 assert row['result']['catalogue_hash']==result['catalogue_hash']
 assert row['result']['ok']==(row['expected_outcome']=='success')
 success+=row['result']['ok']
assert success==12 and result['named'][0]['result']['ok']
for name in ['harness-repair.json','package-process-v1.json','package-manifest-v1.json','supported-package-v1.json','portable-ci-v1.json','generated-equivalence.json']:
 bind(LIVE/name)
bind(ROOT/'catalogue/laboratory-package-policy.json')
for name in ['web/app.js','tools/build_web.py','web/index.html']:bind(ROOT/name)
checks=subprocess.run(['python3','-B','-m','unittest','tests.test_laboratory_view','tests.test_web_effective_scope','-q'],cwd=ROOT,capture_output=True,text=True)
assert checks.returncode==0,checks.stderr
print(json.dumps(dict(status='accepted',head=git('rev-parse','HEAD').decode().strip(),archive_maps=len(maps),additive_archive_entries=added,package_files=len(manifest['files']),web_source_equalities=len(manifest['web_source_sha256']),ordinary_success=success,ordinary_declared_failure=1,named_success=1,targeted_checks=dict(returncode=checks.returncode,stdout=checks.stdout,stderr=checks.stderr),sha256=bound),indent=2))
