from pathlib import Path
import json,hashlib,sys,tarfile
ROOT=Path(__file__).resolve().parents[6];sys.path.insert(0,str(ROOT))
from atlas.agent_review import validate_review,approval_entry
from tools.generate_implicit_path import regenerate
from tools.build_implicit_path_laboratory import runtime_manifest
OUT=Path(__file__).resolve().parent
A=ROOT/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';P=A/'shared-hook-install-v1/revision-v5';I=A/'shared-hook-install-v1/coordinator-install-v2/installed-v1'
pins={}
def sha(p):
 p=Path(p);v=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p.relative_to(ROOT))]=v;return v
def load(p):sha(p);return json.loads(Path(p).read_bytes())
installed=load(I/'INSTALLED.json');post=load(I/'ROOT_POSTCHECK.json');w=load(P/'APPLY_WHITELIST.json');plan=load(P/'PLAN.json')
ops=installed['operations'];assert len(ops)==107 and len({r['original_path'] for r in ops})==107
expected={r['original_path']:r['new_sha256'] for r in w['writes']+w['future_source_installs']}
assert {r['original_path']:r['new_sha256'] for r in ops}==expected
for r in ops:
 assert sha(ROOT/r['original_path'])==sha(ROOT/r['candidate'])==r['new_sha256']
events=[json.loads(s) for s in (I/'operations.jsonl').read_text().splitlines()];sha(I/'operations.jsonl')
assert [r['original_path'] for r in events if r['event']=='operation_started']==[r['original_path'] for r in ops]
assert {r['original_path']:r['new_sha256'] for r in events if r['event']=='operation_verified'}==expected
assert events[0]['event']=='all_preflight_guards_passed' and events[-1]['event']=='installation_and_binding_postcheck_passed'
checks=[json.loads(s) for s in (I/'binding-checks.jsonl').read_text().splitlines()];sha(I/'binding-checks.jsonl')
assert len(checks)==len({(r['document'],r['original_path'],r['old_sha256']) for r in checks})==43791 and all(r['outcome']=='passed' for r in checks)
assert installed['status']==post['status']=='passed' and installed['apply'] is True and sha(ROOT/installed['review'])==installed['review_sha256']
expected_binding=load(A/'EXPECTED_F_BINDING.json');assert runtime_manifest()==post['runtime']==expected_binding['expected_runtime']
for name,h in post['runtime']['files'].items():assert sha(ROOT/'cpp/profiles/implicit-path-v1'/name)==h
gen=regenerate(OUT/'generated');assert gen==post['generation']
review=ROOT/'catalogue/agent-reviews/lade-duncan-1975-midpoint-elastic-eq19-gap-v4-agent-v1.json';sha(review);rec=validate_review(review,ROOT,True)
registry=load(ROOT/'catalogue/approved-models.json');entry=approval_entry(review,ROOT);assert [r for r in registry['models'] if r['model_id']==rec['model']['id']]==[entry]
restored={}
for kind,folder in [('lade','implicit-path'),('maxwell','maxwell')]:
 log=A/f'actual-package-v1/execution/restore-{kind}-assets';status=load(log/'STATUS.json');report=load(log/'stdout.log');sha(log/'stderr.log')
 assert status['status']==report['status']=='passed' and status['exit_code']==0 and status['elapsed_seconds']<status['deadline_seconds']
 dest=ROOT/'.local/lade-main-atlas-v1'/folder
 assert {p.relative_to(dest).as_posix() for p in dest.rglob('*') if p.is_file()}==set(report['files'])
 for name,h in report['files'].items():assert sha(dest/name)==h
 restored[kind]=report['files']
idx=load(A/'asset-provision-v1/INDEX.json');assert idx['files']==restored['lade']
archive=ROOT/idx['archive']['path'];assert sha(archive)==idx['archive']['sha256']
with tarfile.open(archive) as t:
 assert len(t.getmembers())==5 and all(m.isfile() for m in t.getmembers())
 assert {m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t.getmembers()}==idx['files']
arc=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2/compiled-closure-v1.tar.gz';assert sha(arc)=='2ae27721254cabed74b289c9692d0286fda71bd9eab92933d736d74904f4c9dd'
with tarfile.open(arc) as t:
 assert {m.name:hashlib.sha256(t.extractfile(m).read()).hexdigest() for m in t.getmembers()}=={k:v for k,v in restored['maxwell'].items() if k not in ['build-review.json','maxwell-qualification.json']}
for name,original in [('build-review.json',A/'maxwell-rebind-v1/independent-review/build-review.json'),('maxwell-qualification.json',A/'maxwell-rebind-v1/maxwell-qualification.json')]:assert sha(original)==restored['maxwell'][name]
for name in ['qualified-bundle-adversarial','installed-j2-main-routing']:
 d=A/'actual-package-v1/execution'/name;st=load(d/'STATUS.json');assert st['status']=='passed' and st['exit_code']==0
 sha(d/'stdout.log');sha(d/'stderr.log')
result=dict(status='passed',operations=107,preserved_bindings=43791,runtime_files=29,generation=gen,canonical_approval='exact current accepted review and matching registry entry',restored_files={k:len(v) for k,v in restored.items()},scope='Saved installed identity/provision audit; no build, material API, package/browser/live qualification')
(OUT/'saved-results.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/'saved-pins.json').write_text(json.dumps({'files':pins},indent=2)+'\n');print(json.dumps(result,indent=2))
