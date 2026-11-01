"""Independent bounded saved browser/package/database audit; reads only."""
from pathlib import Path
import hashlib,json,sqlite3
P=Path(__file__).resolve().parent;B=P.parent;ROOT=B.parents[3];I=B.parent/'integration-v1';O=ROOT/'output/playwright/duncan-integration-v1'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
saved=read(B/'browser-audit-results.json')
for name,h in saved['files'].items():assert sha(ROOT/name)==h,name
manifest=read(I/'package-manifest-v2.json');assert manifest['file_count']==len(manifest['files'])==928
for root in [Path(manifest['source_path']),ROOT/manifest['retained_path']]:
 assert {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}==set(manifest['files'])
 for name,h in manifest['files'].items():assert sha(root/name)==h,name
site=Path(manifest['source_path']);model='duncan-chang-1970-endpoint-average';definition=read(ROOT/'models'/f'{model}.json')
assert sha(site/'models'/f'{model}.json')=='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
for label in ['dense','loose']:
 actual=read(O/f'{label}-browser-run.json');registered=read(ROOT/f'protocols/duncan-{label}-source-drained-v1.json')
 assert actual['catalogue_hash']==registered['catalogue_hash']==manifest['catalogue_hash']
 assert actual['specification']==registered['specification'] and actual['result']['ok'] and len(actual['result']['points'])==129
 assert actual['result']['points']==registered['result']['points']
dense=read(O/'dense-browser-run.json');replay=read(O/'dense-browser-replay.json')
assert dense['specification']==replay['specification'] and dense['result']['points']==replay['result']['points']
edited=read(O/'edited-browser-run.json');spec=edited['specification'];points=edited['result']['points']
assert edited['result']['ok'] and len(points)==129 and spec['target']==points[-1]['control']==.004
assert spec['parameters'][2]==1800 and spec['initial'][6]==points[0]['state'][6]==200000
assert points[0]['state']==spec['initial']
invalid=(O/'invalid-history-result.log').read_text();assert 'Stopped · last committed state retained' in invalid and 'spinbutton "h (kPa)"' in invalid and '"-1"' in invalid and 'button "↓ Reproducible run" [disabled]' in invalid
reset=read(O/'reset-browser-run.json');assert reset['result']['ok'] and len(reset['result']['points'])==101
assert reset['specification']['parameters']==[x['default'] for x in definition['parameters'].values()]
assert reset['specification']['initial']==[100000,100000,100000,0,0,0,0] and reset['specification']['steps']==100 and reset['specification']['target']==.01
identity=read(O/'asset-identity.json');assert len(identity['assets'])==8
for row in identity['assets']:assert row['status']==200 and row['sha256']==sha(site/row['name']) and row['size']==(site/row['name']).stat().st_size
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (O/'final-console.log').read_text()
network=(O/'final-requests.log').read_text();assert '[404]' not in network and '[500]' not in network
snapshot=(O/'page-2026-11-01T10-44-30-625Z.yml').read_text()
for text in ['Approved scope · independent agent review','Pair assessment: not assessed.','not a Duncan discrete-update tangent','No model-specific constitutive-update tangent']:assert text in snapshot,text
dbcheck=read(I/'database-check.json');assert sha(site/'atlas.sqlite')==dbcheck['database_sha256']
db=sqlite3.connect('file:'+str(site/'atlas.sqlite')+'?mode=ro',uri=True)
assert json.loads(db.execute('select definition_json from models where id=?',(model,)).fetchone()[0])==definition
approval=db.execute('select definition_sha256,record_json from model_approvals where model_id=?',(model,)).fetchone();assert approval[0]==sha(ROOT/'models'/f'{model}.json')
review=db.execute('select path,sha256,record_json from agent_reviews where model_id=?',(model,)).fetchone();assert review[1]==sha(ROOT/review[0]) and json.loads(review[2])==read(ROOT/review[0])
entry=read(I/'approval-entry.json');assert json.loads(approval[1])==entry
sources=db.execute('select url,locator,role from sources where model_id=?',(model,)).fetchall();assert [list(x) for x in sources]==dbcheck['sources'] and len(sources)==2
assert not db.execute('pragma foreign_key_check').fetchall();db.close()
supported=read(I/'supported-package.json');assert supported['status']=='passed' and len(supported['ordinary'])==14 and len(supported['named'])==1 and supported['named'][0]['id']=='gis2024-small-drained'
policy=read(ROOT/'catalogue/laboratory-package-policy.json')
for row in supported['ordinary']:
 declared=next((x for x in policy['declared_failures'] if x['model']==row['id']),None)
 assert row['result']['ok']==(declared is None) and len(row['result']['points'])==(101 if declared is None else declared['committed_points'])
assert supported['named'][0]['result']['ok']
print(json.dumps({'identity':'independent-duncan-saved-browser-package-v1','bounded_checks_pass':True,'saved_browser_files_rehashed':len(saved['files']),'manifest_files_checked_each_source_and_durable':928,'exact129point_source_exports':2,'dense_import_replay_including_point_diagnostics':True,'rapid_latest_result_control_and_initial_history_verified':True,'negative_history_rejection_disabled_export_and_recovery':True,'reset10parameters7state_and_default_loading':True,'browser_fetched_asset_hashes':8,'zero_recorded_console_errors_and_warnings':True,'database_exact_definition_approval_review_source_rows_and_foreign_keys':True,'supported_package_ordinary_cases':14,'supported_package_named_cases':1,'all_other_named_cases_claimed':False,'full_e6_e7_accepted':False,'remaining_blocker':'Unchanged browser-wire legacy Duncan protocol1 iteration-count disagreement; full suite aborts before later requests. No waiver.','compiled_calls':0,'browser_control_calls':0},indent=2))
