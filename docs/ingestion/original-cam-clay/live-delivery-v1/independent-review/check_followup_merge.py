"""Read-only merge/receipt identities; never loads a compiled artifact."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
OUT=Path(__file__).resolve().parent
BASE='142b278ad88e68454e3ae96f54b7a284ed6920d2'
REMOTE='52851b3d'
MERGE='b3be0920c311c3e9d52cad9d8a0ae778fd13dfa6'
def git(*a):return subprocess.check_output(['git',*a],cwd=ROOT)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads((ROOT/p).read_text())
incoming=git('diff','--name-only',BASE+'..'+MERGE).decode().splitlines()
equal=[p for p in incoming if (ROOT/p).read_bytes()==git('show',REMOTE+':'+p)]
overlap=sorted(set(incoming)-set(equal))
assert overlap==['.github/workflows/verify.yml','IMPLEMENTATION_PLAN.md','catalogue/manifest.json','tools/build_web.py','web/index.html']
assert len(equal)==178
assert (ROOT/'web/app.js').read_bytes()==git('show',BASE+':web/app.js')
assert git('diff','--name-only',BASE+'..'+MERGE,'--','cpp','schemas','models')==b''
current=load('catalogue/manifest.json')['models']
remote=json.loads(git('show',REMOTE+':catalogue/manifest.json'))['models']
prior=json.loads(git('show',BASE+':catalogue/manifest.json'))['models']
occ='original-cam-clay-sw-electronic-log-recovery-v1'
assert [m for m in current if m['id']!=occ]==remote
assert [m for m in current if m['id']==occ]==[m for m in prior if m['id']==occ]
board=(ROOT/'IMPLEMENTATION_PLAN.md').read_text()
assert all(line in board for line in git('show',BASE+':IMPLEMENTATION_PLAN.md').decode().splitlines() if line.startswith('- [') and 'MODEL-sls-comsol63' not in line)
mapping=load('catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json')
row=next(x for x in mapping['entries'] if x['original_path']=='tests/test_laboratory_view.mjs')
assert row['sha256']=='e2b3d1527edb321012993eeb8778e1399ca27789979e0eacd9561de993809553'
assert sha(ROOT/row['archived_path'])==row['sha256']
receipt=load('docs/ingestion/original-cam-clay/live-delivery-v1/package-local-browser-v2.json')
old=load('docs/ingestion/burgers-itasca900/delivery-v1/release-package-assets.json')
for key,filename in [('module_sha256','burgers.mjs'),('wasm_sha256','burgers.wasm')]:
 assert receipt[key]==old['engine-burgers/'+filename]
 assert sha(Path(receipt['Burgers_artifact'])/filename)==receipt[key]
extra=['web/app.js','catalogue/investigations/tresca-mixed-catalogue-v1/source-archive-map.json',row['archived_path'],'docs/ingestion/burgers-itasca900/delivery-v1/release-package-assets.json']
extra+=['docs/ingestion/original-cam-clay/live-delivery-v1/'+x for x in ['portable-ci-v2.json','package-process-v2.json','package-local-browser-v1.json','package-local-browser-v2.json']]
print(json.dumps(dict(status='accepted_bounded_merge_delta',baseline=BASE,remote=REMOTE,merge=MERGE,incoming_equal=len(equal),overlap=overlap,sha256={p:sha(ROOT/p) for p in sorted(set(incoming+extra))}),indent=2))
