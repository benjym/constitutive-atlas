"""Independent saved-only E6/E7 audit. No engine imports, browser or compiled calls."""
import hashlib,json,re,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5]
HERE=Path(__file__).resolve().parent
PACK=HERE.parent
OUT=ROOT/'output/playwright/duncan-integration-v2'
SITE=Path('/private/tmp/atlas-duncan-integration-v2/site-v1')
MID='duncan-chang-1970-endpoint-average'
def read(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}; files={}
def bind(p):
 p=Path(p); files[str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p)]=sha(p)
def check_manifest(d,base):
 for name,h in d.items():
  f=base/name;assert f.is_file() and sha(f)==h,(str(f),h);bind(f)
manifest=read(PACK/'package-manifest-v1.json');assert manifest['file_count']==953==len(manifest['files'])
for base in [SITE,ROOT/'.local/private-evidence/duncan-atlas-integration-v2/site-v1']:
 check_manifest(manifest['files'],base)
 assert {str(p.relative_to(base)) for p in base.rglob('*') if p.is_file()}==set(manifest['files'])
 assert not any(p.suffix.lower() in ['.pdf','.f','.for','.f90','.dll'] for p in base.rglob('*') if p.is_file())
checks['two_exact_complete_953_file_package_copies']=True
freeze=read(PACK/'package-source-freeze-v1.json');assert len(freeze['files'])==5578
source_drift=[]
for name,h in freeze['files'].items():
 f=Path(name)
 if not f.is_file() or sha(f)!=h:source_drift.append({'path':name,'frozen_sha256':h,'current_sha256':sha(f) if f.is_file() else None})
 else:bind(f)
checks['current_source_freeze_recheck']={'unchanged':5578-len(source_drift),'drift':source_drift}
assert len(source_drift)==1 and source_drift[0]['path']==str(ROOT/'tools/provision_maxwell_assets.py')
prior=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2/prior-provision_maxwell_assets.py'
assert sha(prior)==source_drift[0]['frozen_sha256'];bind(prior);bind(ROOT/'tools/provision_maxwell_assets.py')
priorreceipt=ROOT/'docs/reviews/common-scalar-functions-v1/dependent-independent-review/post-package-install-bindings-v1.json'
translations={}
for name,h in read(priorreceipt)['files'].items():
 f=ROOT/name
 if sha(f)!=h:
  archive=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v2/prior-sidecars'/name
  assert sha(archive)==h;translations[name]=str(archive.relative_to(ROOT));bind(archive);bind(f)
 else:bind(f)
assert len(translations)==5;bind(priorreceipt)
checks['prior627_receipt_preserved_with5_exact_sidecar_archives']=translations
for item in read(PACK/'current-engine-inputs.json')['files']:
 assert sha(Path(item['path']))==item['sha256']==sha(Path(item['source']));bind(Path(item['source']))
old=read(ROOT/'docs/ingestion/duncan-chang-1970/integration-v1/package-manifest-v2.json')
for item in read(PACK/'retained-engine-inputs.json')['artifacts']:
 rel=str(Path(item['original_path']).relative_to('/private/tmp/atlas-duncan-integration-v1/site-v2'))
 assert old['files'][rel]==item['sha256']==sha(Path(item['retained_input']))==manifest['files'][rel]
checks['14_current_and12_retained_inputs_exact_with_old_version_scope']=True
assert manifest['scalar_functions_notices_sha256']==sha(ROOT/'cpp/scalar-functions/NOTICES.txt')==sha(SITE/'scalar-functions-NOTICES.txt')
model=read(ROOT/'models'/f'{MID}.json');assert sha(ROOT/'models'/f'{MID}.json')=='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
assert read(SITE/'models'/f'{MID}.json')==model
cat=read(SITE/'models.json');assert len(cat['models'])==14
oldcat=read(ROOT/'.local/private-evidence/duncan-atlas-integration-v1/site-v2/models.json')
assert {m['id']:m for m in cat['models']}=={m['id']:m for m in oldcat['models']}
for m in cat['models']:assert m==read(ROOT/'models'/(m['id']+'.json'))
checks['all14_ordinary_definitions_exact_current_JSON']=True
support=read(PACK/'supported-package-v1.json');policy=read(ROOT/'catalogue/laboratory-package-policy.json');strict=read(PACK/'strict-package-v1.json')
assert support['status']=='passed' and support['policy_sha256']==sha(ROOT/'catalogue/laboratory-package-policy.json')
assert {m['id'] for m in support['ordinary']}=={m['id'] for m in cat['models']}
for row in support['ordinary']:
 s=row['specification'];res=row['result'];decl=next((x for x in policy['declared_failures'] if x['model']==row['id']),None)
 assert res['model']==row['id'] and res['catalogue_hash']==cat['sha256']
 if decl:
  assert s==decl['ordinary_specification'] and res['ok'] is False and res['message']==decl['message']
  assert len(res['points'])==decl['committed_points']==1 and res['points'][0]['state']==s['initial']
 else:assert res['ok'] is True and len(res['points'])==s['steps']+1
assert len(support['named'])==1 and support['named'][0]['result']['ok'] is True
assert strict['status']=='failed' and strict['models'][-1]['id']==policy['declared_failures'][0]['model']
assert strict['models'][-1]['result']['message']==policy['declared_failures'][0]['message']
assert read(PACK/'strict-process-v1.json')['exit_code']==1
checks['supported14_plus_GIS_named_pass_strict_GIS_failure_preserved']=True
for label in ['dense','loose']:
 actual=read(OUT/f'{label}-browser-run.json');registered=read(ROOT/f'protocols/duncan-{label}-source-drained-v1.json')
 assert actual['specification']==registered['specification'] and actual['result']['ok'] and len(actual['result']['points'])==129
 assert actual['result']['points']==registered['result']['points']
dense=read(OUT/'dense-browser-run.json');replay=read(OUT/'dense-browser-replay.json')
assert dense['specification']==replay['specification'] and dense['result']['points']==replay['result']['points']
edited=read(OUT/'edited-browser-run.json');s=edited['specification']
assert edited['result']['ok'] and len(edited['result']['points'])==129 and s['target']==.004 and s['parameters'][2]==1800 and s['initial'][6]==200000
invalid=(OUT/'invalid-history-result.log').read_text();assert 'Stopped · last committed state retained' in invalid and '"-1"' in invalid and 'button "↓ Reproducible run" [disabled]' in invalid
reset=read(OUT/'reset-browser-run.json');s=reset['specification']
assert reset['result']['ok'] and len(reset['result']['points'])==101 and s['parameters']==[x['default'] for x in model['parameters'].values()] and s['initial']==[100000,100000,100000,0,0,0,0] and s['target']==.01 and s['steps']==100
checks['browser_two129_presets_import_replay_invalid_recovery_reset_latest_edits']=True
assets=read(OUT/'asset-identity.json')['assets'];assert len(assets)==12
for item in assets:assert item['status']==200 and item['size']==(SITE/item['name']).stat().st_size and item['sha256']==sha(SITE/item['name'])
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (OUT/'final-console.log').read_text()
statuses=re.findall(r'=> \[(\d+)\]',(OUT/'final-requests.log').read_text());assert statuses and all(x=='200' for x in statuses)
checks['12_browser_fetched_sizes_statuses_hashes_console_and_shown_network']=True
log=(OUT/'open-snapshot.log').read_text();assert '#catalogue/'+MID in log and 'Approved scope · independent agent review' in log and 'Scientific eligibility: undetermined.' in log and 'Pair assessment: not assessed.' in log
checks['browser_catalogue_deeplink_approval_and_applicability_limits']=True
c=sqlite3.connect('file:'+str(SITE/'atlas.sqlite')+'?mode=ro',uri=True)
row=c.execute('SELECT definition_json,executable FROM models WHERE id=?',(MID,)).fetchone();assert json.loads(row[0])==model and row[1]==1
approval=next(a for a in read(ROOT/'catalogue/approved-models.json')['models'] if a['model_id']==MID)
rows=c.execute('SELECT record_json FROM model_approvals WHERE model_id=?',(MID,)).fetchall();assert len(rows)==1 and json.loads(rows[0][0])==approval
rows=c.execute('SELECT path,sha256,record_json FROM agent_reviews WHERE model_id=?',(MID,)).fetchall();assert len(rows)==1
path,h,raw=rows[0];assert h==approval['review']['sha256']==sha(ROOT/path) and path==approval['review']['path'] and json.loads(raw)==read(ROOT/path)
assert any(row[0]=='https://doi.org/10.1061/JSFEAQ.0001458' for row in c.execute('SELECT url FROM sources WHERE model_id=?',(MID,)))
assert not c.execute('PRAGMA foreign_key_check').fetchall();c.close()
checks['readonly_SQLite_exact_definition_approval_review_DOI_FK']=True
for receipt in [ROOT/'docs/reviews/common-scalar-functions-v1/independent-review/final-actual-root-bindings-v1.json']:
 check_manifest(read(receipt)['files'],ROOT);bind(receipt)
checks['final_actual_root_generic_qualification23pins']=True
for base in [PACK,ROOT/'docs/ingestion/duncan-chang-1970/browser-v2',OUT]:
 for f in base.iterdir():
  if f.is_file():bind(f)
bind(ROOT/'catalogue/laboratory-package-policy.json');bind(ROOT/'docs/MODEL_DELIVERY_CHECKLIST.md');bind(ROOT/'catalogue/agent-reviews/duncan-chang-1970-endpoint-average-agent-v1.json')
result={'identity':'duncan-integration-v2-independent-saved-audit-v1','checks':checks,'source_drift_requires_additive_disposition':source_drift,'compiled_execution':False,'browser_control':False,'files':files}
(HERE/'audit-results-v1.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'checks':len(checks),'source_drift':source_drift,'bound_files':len(files)},indent=2))
