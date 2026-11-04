from pathlib import Path
import hashlib,json,sqlite3,sys
sys.dont_write_bytecode=True
N=Path(__file__).resolve().parents[1];O=Path(__file__).resolve().parent;R=Path('/private/tmp/atlas-baseline-delivery-20261105/source');S=Path('/private/tmp/atlas-baseline-delivery-20261105/site-v1')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
inv=json.loads((N/'package-inventory-v1.json').read_text());members={p.relative_to(S).as_posix() for p in S.rglob('*') if p.is_file()};assert members=={x['path'] for x in inv['files']}
for x in inv['files']:assert (S/x['path']).stat().st_size==x['bytes'] and sha(S/x['path'])==x['sha256'],x['path']
assert len(members)==1549 and sum(x['bytes'] for x in inv['files'])==1109907607
catalogue=json.loads((S/'models.json').read_text());models={x['id']:x for x in catalogue['models']};assert len(models)==16
five=['linear-elastic','drucker-prager','modified-cam-clay','hypoplastic-sand-vw96','hypoplastic-sand-igs97'];registry=json.loads((R/'catalogue/approved-models.json').read_text());archive=registry['historical_registries'][0];assert sha(R/archive['path'])==archive['sha256'];old=json.loads((R/archive['path']).read_text())
assert len(old['models'])==len(registry['models'])==30
assert [x for x in old['models'] if x['model_id'] not in five]==[x for x in registry['models'] if x['model_id'] not in five]
reviews=json.loads((S/'evidence.json').read_text())['agent_reviews'];assert len(reviews)==33
for name in five:
 assert models[name]['schema_version']=='0.3';definition=S/'models'/f'{name}.json';assert definition.read_bytes()==(R/'models'/f'{name}.json').read_bytes()
 current=[x for x in reviews if x['catalogue_id']==name and x['definition_current']];historical=[x for x in reviews if x['catalogue_id']==name and not x['definition_current']]
 assert len(current)==1 and current[0]['status']=='accepted' and current[0]['definition_sha256']==sha(definition) and current[0]['registered_approval_id']
 assert len(historical)==1 and historical[0]['status']=='accepted' and historical[0]['registered_approval_id'] is None
 # Both readable technical record and exact JSON are retained in public evidence.
 for x in current+historical:
  assert sha(R/x['record_path'])==x['record_sha256']
  assert (S/'evidence-records'/x['record_path']).exists()
examples=json.loads((S/'laboratory-examples.json').read_text());assert examples['catalogue_hash']==catalogue['sha256'] and len(examples['examples'])==9
for x in examples['examples']:
 f=S/x['document_url'].removeprefix('./');assert sha(f)==x['document_sha256'];d=json.loads(f.read_text());assert d['catalogue_hash']==catalogue['sha256'];assert d['specification']['model']==x['model'] and d['result']['ok']
 assert sha(S/x['definition_url'].removeprefix('./'))==x['definition_sha256']
 assert d['result']['catalogue_hash']==catalogue['sha256']
roles=['engine','engine-kelvin-voigt','engine-sls','engine-burgers','material-point-j2','material-point-orthotropic','material-point-hill','engine-bingham','engine-perzyna','engine-path','material-point-interface2016','engine-maxwell','engine-implicit-path','engine-controlled-time']
assert (S/'atlas.js').is_file() and (S/'atlas.wasm').is_file()
for role in roles:assert (S/role).is_dir() and any((S/role).rglob('*.wasm')),role
profiles,_=json.JSONDecoder().raw_decode((S/'model-profile-data.mjs').read_text().split('export const modelProfiles =',1)[1].lstrip());assert all(name in profiles for name in five)
con=sqlite3.connect('file:'+str(S/'atlas.sqlite')+'?mode=ro',uri=True)
assert con.execute('select count(*) from model_approvals').fetchone()[0]==30 and con.execute('select count(*) from agent_reviews').fetchone()[0]==26
for name in five:
 rows=con.execute('select definition_sha256 from model_approvals where model_id=?',(name,)).fetchall();assert rows==[(sha(S/'models'/f'{name}.json'),)]
db=json.loads((S/'atlas-database.json').read_text());assert sha(S/'atlas.sqlite')==db['database']['sha256']
for dr in ['package-ci-smoke-v1','package-supported-observer-v1','scoped-parity-observer-v1']:
 r=json.loads((N/dr/'receipt.json').read_text());assert r['returncode']==r['reaped_returncode']==0 and r['mandatory_reap'] and r['status']=='passed' and r['cleanup_errors']==[]
 for stream in ['stdout','stderr']:assert sha(Path(r[stream]['path']))==r[stream]['sha256']
supported=json.loads((N/'supported-package-v1.json').read_text());assert supported['status']=='passed' and supported['catalogue_hash']==catalogue['sha256'] and len(supported['ordinary'])==16
assert {x['id'] for x in supported['ordinary']}==set(models)
for x in supported['ordinary']:
 assert x['result']['ok']==(x['expected_outcome']=='success')
scoped=json.loads((N/'scoped-parity-current16-v1.json').read_text());assert scoped['status']=='passed' and scoped['catalogue_hash']==catalogue['sha256'] and len(scoped['cases'])==43 and scoped['compared_physical_scalars']==51982 and scoped['maximum_budget_fraction']<1 and scoped['wrong_scope_rejected_before_compiled_call']
assert 'All 994 built experiments passed' in (N/'package-experiments-v1.stdout.raw').read_text()
assert 'ℹ tests 105' in (N/'package-pure-tests-v1.stdout.raw').read_text() and 'ℹ fail 0' in (N/'package-pure-tests-v1.stdout.raw').read_text()
assert (N/'package-v1.stderr.raw').read_bytes()==b''
(O/'checks.json').write_text(json.dumps({'status':'PASS','package_files':1549,'bytes':1109907607,'ordinary':16,'named_examples':9,'engine_roles':15,'public_review_projections':33,'active_approvals':30,'unchanged_other_approvals':25,'sqlite_agent_reviews':26,'scoped_cases':43,'physical_scalars':51982,'public_experiments':994,'pure_tests':105,'compiled_calls_by_reviewer':0},indent=2)+'\n')
print('PASS')
