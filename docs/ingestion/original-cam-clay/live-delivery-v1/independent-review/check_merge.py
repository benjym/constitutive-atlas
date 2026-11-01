"""Independent worktree merge identity checks; no stage/build/binary invocation."""
from pathlib import Path
import hashlib,json,subprocess,sys,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
sys.path.insert(0,str(ROOT))
MAIN='f8252c16a9cac492561a7cd25e58b089a63d7eb2'; RELEASE='82a5961d'
sha=lambda b:hashlib.sha256(b).hexdigest()
bindings={}
def get(rev,name):return subprocess.check_output(['git','show',rev+':'+name],cwd=ROOT)
def bind(name):
    p=ROOT/name;bindings[name]=sha(p.read_bytes());return p
conflicts=['IMPLEMENTATION_PLAN.md','catalogue/approved-models.json','catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json','catalogue/manifest.json','tests/test_catalogue.py','tools/build_web.py','web/app.js']
for name in conflicts:
    raw=bind(name).read_text()
    assert not any(line.startswith(('<<<<<<< ','=======','>>>>>>> ')) for line in raw.splitlines()),name
occ='original-cam-clay-sw-electronic-log-recovery-v1'
for name, key in [('catalogue/approved-models.json','models'),('catalogue/manifest.json','models')]:
    old=json.loads(get(MAIN,name));cur=json.loads((ROOT/name).read_text());release=json.loads(get(RELEASE,name))
    idkey='model_id' if 'approved' in name else 'id'
    a={x[idkey]:x for x in old[key]};b={x[idkey]:x for x in cur[key]};c={x[idkey]:x for x in release[key]}
    assert set(b)==set(a)|{occ}
    if idkey=='model_id':
        assert [x for x in cur[key] if x[idkey]!=occ]==old[key]
    else:assert len(b)==len(cur[key])
    assert all(b[k]==v for k,v in a.items()),name
    assert b[occ]==c[occ]
archive='catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json'
a=json.loads(get(MAIN,archive));c=json.loads(get(RELEASE,archive));b=json.loads((ROOT/archive).read_text())
assert all(e in b['entries'] for e in a['entries']+c['entries'])
for side in (a,c):
    assert all(b['documents'][k]==v for k,v in side['documents'].items())
for e in b['entries']:
    assert sha(bind(e['archived_path']).read_bytes())==e['sha256']
assert (ROOT/'tests/test_catalogue.py').read_bytes()==get(MAIN,'tests/test_catalogue.py')
# Every preexisting board row survives; earlier release waiting-authorization text is historical.
old=get(MAIN,'IMPLEMENTATION_PLAN.md').decode().splitlines();cur=(ROOT/'IMPLEMENTATION_PLAN.md').read_text().splitlines()
it=iter(cur);assert all(any(x==line for x in it) for line in old)
# Preserve dedicated delivery routes/builders/model and scientific evidence byte-for-byte.
names=subprocess.check_output(['git','ls-tree','-r','--name-only',MAIN],cwd=ROOT,text=True).splitlines()
preserve=[n for n in names if n.startswith(('web/','tools/','models/','docs/admission/','docs/models/')) and any(s in n.lower() for s in ('sls','burgers','j2','timed-route','laboratory-controller-router'))]
for name in preserve:assert bind(name).read_bytes()==get(MAIN,name),name
# No production common source changes from release baseline to latestmain or merge.
assert not subprocess.check_output(['git','diff','--name-only','cea9badd',MAIN,'--','atlas','cpp','schemas'],cwd=ROOT).strip()
assert not subprocess.check_output(['git','diff',MAIN,'--name-only','--','atlas','cpp','schemas'],cwd=ROOT).strip()
for name in names:
    if name.startswith(('atlas/','cpp/','schemas/')):bind(name)
for p in (ROOT/'models').glob('*.json'):
    name=str(p.relative_to(ROOT));bind(name)
    assert p.read_bytes()==get(RELEASE,name)
# Installed scientific approval remains exact accepted bytes.
review='catalogue/agent-reviews/original-cam-clay-sw-electronic-log-recovery-agent-v1.json'
assert bind(review).read_bytes()==get(RELEASE,review)
from atlas.agent_review import validate_review
validate_review(ROOT/review,ROOT,for_approval=True)
from atlas.compiler import generate
with tempfile.TemporaryDirectory(prefix='occ-main-merge-review-') as t:
    generate(t)
    generated={}
    for name,expected in [('models.hpp','c23f3a09184a7d8037b2b6da286634aa6e3339bbb3cab109f1209082c248196e'),('models.json','1e5e00c1ecd1739d13ea3f171894e87bd751f767ef75b114bddc906c4414b5d5')]:
        actual=sha((Path(t)/name).read_bytes());assert actual==expected
        generated[name]=actual
out={'status':'pass','reviewer':'/root/occ_e1_e2_closeout_review','latest_main':MAIN,'release':subprocess.check_output(['git','rev-parse',RELEASE],cwd=ROOT,text=True).strip(),'conflict_worktree_files_reviewed':conflicts,'existing_registry_and_manifest_entries_unchanged':True,'dedicated_route_evidence_files_unchanged':len(preserve),'common_production_sources_unchanged':True,'generated':generated,'compiled_calls':0,'builds':0,'bindings':bindings}
(HERE/'merge-check-results.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='bindings'},indent=2))
