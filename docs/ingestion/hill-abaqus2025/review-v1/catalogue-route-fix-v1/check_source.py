"""Independent source-only review; no compiled execution or shared writes."""
import hashlib,json,subprocess,sys
from pathlib import Path
REPO=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
RELEASE=Path(sys.argv[1] if len(sys.argv)>1 else '/private/tmp/atlas-hill-release-v3')
BASE='f8416d7732100b7502d2b4e6212c82420603bfcd'
MODEL='models/research/hill/hill-abaqus2025-perfect-be.json'
IDENT='hill-abaqus2025-perfect-be'
def blob(p):return subprocess.check_output(['git','show',BASE+':'+p],cwd=REPO)
def sha(b):return hashlib.sha256(b).hexdigest()
bindings={}
def bind(p,b):bindings[p]=sha(b);return b
old=bind('base:catalogue/manifest.json',blob('catalogue/manifest.json'))
new=bind('candidate:catalogue/manifest.json',(RELEASE/'catalogue/manifest.json').read_bytes())
a=json.loads(old);b=json.loads(new)
e=next(x for x in a['models'] if x['id']==IDENT)
assert e.pop('timed_laboratory')=='index.html';assert 'material_laboratory' not in e
e['material_laboratory']='index.html'
assert a==b,'Only the one Hill route-key replacement is permitted'
entry=next(x for x in b['models'] if x['id']==IDENT)
model=json.loads(bind(MODEL,blob(MODEL)))
assert (RELEASE/MODEL).read_bytes()==blob(MODEL)
assert bindings[MODEL]=='1f98a70a68098d95804639e3abeb69da57e7ceeaf302d621e4738db4340e2621'
assert model['formulation']['time_dependence']=='strain_path'
assert entry['laboratory_kind']=='strain_path'
assert 'timed_laboratory' not in entry and entry['material_laboratory']=='index.html'
app=bind('web/app.js',blob('web/app.js'));test=bind('tests/test_catalogue.py',blob('tests/test_catalogue.py'))
assert (RELEASE/'web/app.js').read_bytes()==app
assert (RELEASE/'tests/test_catalogue.py').read_bytes()==test
s=app.decode();t=test.decode()
assert s.count("entry.material_laboratory==='index.html'")>=2
assert 'setupHillLaboratory({cancelOrdinary:' in s
assert "entry.material_laboratory?'Approved bounded scope · strain-increment laboratory'" in s
assert "entry.get('material_laboratory') or entry.get('path_laboratory') or entry.get('implicit_path_laboratory') else 'physical_time'" in t
assert "self.assertEqual(json.loads((ROOT / entry['approval_record']).read_text()), record)" in t
approval=json.loads(bind(entry['approval_record'],blob(entry['approval_record'])))
registry=json.loads(bind('catalogue/approved-models.json',blob('catalogue/approved-models.json')))
assert approval in registry['models'];assert approval['definition']['sha256']==bindings[MODEL]
assert (RELEASE/entry['approval_record']).read_bytes()==blob(entry['approval_record'])
assert (RELEASE/'catalogue/approved-models.json').read_bytes()==blob('catalogue/approved-models.json')
route=bind('web/timed-route.mjs',blob('web/timed-route.mjs')).decode()
assert 'public_timed_laboratory' in route
assert not entry.get('public_timed_laboratory')
archive='catalogue/source-snapshots/'+sha(old)+'/catalogue/manifest.json'
assert (RELEASE/archive).read_bytes()==old
bind(archive,(RELEASE/archive).read_bytes())
for p in ['docs/ingestion/hill-abaqus2025/delivery-v1/catalogue-route-fix-v1/preservation/preservation-result.json','docs/ingestion/hill-abaqus2025/delivery-v1/catalogue-route-fix-v1/focused-tests.log','docs/ingestion/hill-abaqus2025/delivery-v1/catalogue-route-fix-v1/hill-linux-job-readable-v1.log']:
 bind(p,(REPO/p).read_bytes())
result=dict(decision='accepted source correction; package/browser/remote qualification remains separate',base=BASE,reviewer='/root/hill_scientific_review',release=str(RELEASE),minimal_diff=True,unchanged_model_approval_app_test=True,expected_route='index.html#laboratory?model='+IDENT,expected_time_dependence='strain_path',old_manifest_sha256=sha(old),new_manifest_sha256=sha(new),bindings=bindings)
(OUT/'check-results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='bindings'},indent=2))
