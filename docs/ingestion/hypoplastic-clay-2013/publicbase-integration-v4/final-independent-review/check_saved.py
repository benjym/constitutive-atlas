"""Independent saved-only v4 review; no material, build, browser or network calls."""
from pathlib import Path
from collections import Counter
import json, hashlib, subprocess, sqlite3, sys, urllib.parse
R=Path('/Users/bmar5496/code/constitutive-atlas')
P=R/'docs/ingestion/hypoplastic-clay-2013/publicbase-integration-v4'
V=P/'package-execution-v2'; B=V/'browser-v2'
C=Path('/private/tmp/atlas-clay2013-release-v4'); S=Path('/private/tmp/atlas-clay2013-release-v4-package-v2')
M=Path('/private/tmp/atlas-clay2013-release-v4-metadata')
def load(p):return json.loads(p.read_text())
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()
def bytesha(b):return hashlib.sha256(b).hexdigest()
def git(*args):return subprocess.check_output(['git',*args],cwd=C)
def maps(root):return {str(f.relative_to(root)):sha(f) for f in root.rglob('*') if f.is_file()}
review_freeze=Path(__file__).with_name('input-freeze.json')
if review_freeze.exists():
 for f,h in load(review_freeze)['files'].items():assert sha(Path(f))==h,('review_input_changed',f)
plan=load(P/'PLAN.json'); checks=load(P/'CHECKS.json'); freeze=load(V/'INPUT_FREEZE.json'); manifest=load(V/'PACKAGE_MANIFEST.json')['files']
assert git('rev-parse','HEAD').decode().strip()==plan['base']==freeze['base']
assert not git('diff','--name-only')
changed=set(filter(None,git('diff','--cached','--name-only','-z').decode().split('\0')))
new=set(filter(None,git('ls-files','--others','--exclude-standard','-z').decode().split('\0')))
assert changed=={x['path'] for x in plan['writes']} and not new; assert len(plan['writes'])==28
for x in plan['writes']:
 assert bytesha(git('show',':'+x['path']))==x['after_sha256']
 assert sha(C/x['path'])==x['after_sha256']; assert (C/x['path']).stat().st_size==x['bytes']
 old=subprocess.run(['git','show','HEAD:'+x['path']],cwd=C,capture_output=True)
 assert (bytesha(old.stdout) if old.returncode==0 else None)==x['before_sha256']
# Exact previously accepted 27 metadata additions, no renewed scientific assertion.
p3=load(P.parent/'release-integration-v3/PLAN.json')
assert {x['path']:x['after_sha256'] for x in plan['writes'] if x['path']!='catalogue/approved-models.json'}=={x['path']:x['after_sha256'] for x in p3['writes'] if x['path']!='catalogue/approved-models.json'}
old=load(P/'registry-before.json');newreg=load(C/'catalogue/approved-models.json')
assert len(old['models'])==18 and len(newreg['models'])==21
assert newreg==dict(old,models=old['models']+newreg['models'][18:])
assert any('orthotropic' in x['id'] for x in old['models'])
sys.path.insert(0,str(C));from atlas.agent_review import approval_entry,validate_review
for f in ['hypoplastic-clay-2013-agent-v1.json','vw96-agent-v1.json','igs97-agent-v1.json']:
 path=C/'catalogue/agent-reviews'/f
 validate_review(path,root=C,for_approval=True)
 assert approval_entry(path,root=C) in newreg['models'][18:]
for name,entries,root in [('source',freeze['candidate_source_files'],C),('external',freeze['external_inputs'],Path('/')),('private',freeze['private_fixture_inputs'],Path('/')),('repair',freeze['repair_receipts'],Path('/'))]:
 for f,h in entries.items(): assert sha(root/f)==h,(name,f)
assert len(freeze['candidate_source_files'])==27855 and len(freeze['external_inputs'])==40 and len(freeze['private_fixture_inputs'])==1
assert maps(S)=={f:x['sha256'] for f,x in manifest.items()}; assert len(manifest)==1002
for f,x in manifest.items():assert (S/f).stat().st_size==x['bytes']
assert not any(Path(x['path']).suffix.lower() in ('.pdf','.dll','.wasm','.so','.dylib') for x in plan['writes'])
# Keep failed first attempt exact, including freeze/status pins.
superseed=freeze['supersedes_attempt_only']
assert sha(P/'package-execution-v1/INPUT_FREEZE.json')==superseed['freeze_sha256']
assert sha(P/'package-execution-v1/standard-builder/STATUS.json')==superseed['terminal_status_sha256']
status1=load(P/'package-execution-v1/standard-builder/STATUS.json');status2=load(V/'standard-builder/STATUS.json')
assert status1['exit_code']==1 and status1['status']=='failed'
assert 'dense-0.005-400.json' in (P/'package-execution-v1/standard-builder/stderr.log').read_text()
assert status2['exit_code']==0 and status2['status']=='passed' and status2['argv']==freeze['standard_builder_argv'] and status2['cwd']==str(C)
assert not (V/'standard-builder/stderr.log').read_bytes()
log=(V/'standard-builder/stdout.log').read_text()
assert 'PASS: 106 implicit-path package checks' in log and 'orthotropic-linear-elastic-ogs' in log and 'Packaged '+str(S) in log
repair=load(V/'fixture-repair/RESULT.json');assert repair['total_interface_pins_verified']==24
assert load(V/'fixture-repair/PREFLIGHT.json')['status']=='passed'
for x in repair['files']:
 assert sha(C/x['path'])==sha(Path(x['source']))==x['sha256']
 assert x['path'] not in {x['path'] for x in plan['writes']}
receipt=load(C/repair['receipt']);assert sha(C/repair['receipt'])==repair['receipt_sha256']
# Inspect exact source receipt structure, and require all advertised path/hash pins.
pinrows=[{'path':f,'sha256':h} for f,h in receipt['files'].items()]
assert len(pinrows)==24
def scan(x):
 if isinstance(x,dict):
  if 'path' in x and 'sha256' in x:pinrows.append(x)
  for v in x.values():scan(v)
 elif isinstance(x,list):
  for v in x:scan(v)
scan(receipt)
for x in pinrows:assert sha(C/x['path'])==x['sha256']
# Full nine-table row multisets, preserving duplicates.
def db(path):
 with sqlite3.connect('file:'+str(path)+'?mode=ro',uri=True) as c:
  assert c.execute('pragma integrity_check').fetchall()==[('ok',)]
  assert not c.execute('pragma foreign_key_check').fetchall()
  return {n:Counter(c.execute('select * from '+n).fetchall()) for (n,) in c.execute("select name from sqlite_master where type='table'")}
before=db(M/'before/atlas.sqlite');after=db(M/'after/atlas.sqlite');assert len(before)==9 and before.keys()==after.keys()
tables={}
for n,a in before.items():
 b=after[n];removed=a-b;added=b-a;assert not removed
 assert sum(added.values())==(3 if n in ('agent_reviews','model_approvals') else 0)
 tables[n]={'before':sum(a.values()),'after':sum(b.values()),'added':sum(added.values()),'removed':0}
assert db(S/'atlas.sqlite')==after
assert maps(M/'before')==checks['before_manifest'];assert maps(M/'after')==checks['after_manifest']
for f,h in checks['after_manifest'].items():assert sha(S/f)==h
b=checks['before_manifest'];a=checks['after_manifest'];delta={'added':sorted(a.keys()-b.keys()),'changed':sorted(f for f in a.keys()&b.keys() if a[f]!=b[f]),'removed':sorted(b.keys()-a.keys())}
assert len(delta['added'])==6 and len(delta['changed'])==4 and not delta['removed']
assert sha(M/'before/models.json')==sha(S/'models.json')=='77e85070a62ada86d47af3890817f57d6ce0194e646a396dbf7ff75c75f9834a'
# Existing policy exactly pinned; do not run its Wasm/material calls.
support=load(V/'SUPPORTED_REPORT.json');policy=load(V/'SUPPORTED_PLAN.json')
assert support['status']=='passed' and len(support['ordinary'])==14 and len(support['named'])==1
assert support['policy_sha256']==policy['policy_sha256']==sha(C/'catalogue/laboratory-package-policy.json')
assert len([x for x in support['ordinary'] if x['result']['ok']])==13
assert [x['id'] for x in support['ordinary'] if not x['result']['ok']]==['research-hp-extracted-asbs-gis-2024-v03']
assert support['named'][0]['result']['ok']
assert sha(C/'tools/test_supported_package.mjs')==policy['checker_sha256']
assert load(V/'SUPPORTED_STATUS.json')['exit_code']==0
# Actual-browser saved exports: compare every scalar and full state, elapsed only excluded.
bp=load(B/'PLAN.json');assert sha(B/'serve.py')==bp['server_sha256']
for f,h in load(B/'EVIDENCE_MANIFEST.json')['files'].items():assert sha(B/f)==h
export=load(B/'public-export.json');replay=load(B/'public-replay-export.json')
entry=next(x for x in support['ordinary'] if x['id']=='hypoplastic-clay-2013')
def physical(x):return {k:v for k,v in x.items() if k!='elapsed_ms'}
assert export['catalogue_hash']==support['catalogue_hash']==replay['catalogue_hash']
assert export['specification']==entry['specification']==replay['specification']
assert physical(export['result'])==physical(entry['result'])==physical(replay['result'])
assert len(export['result']['points'])==101
assert load(B/'console.json')==[]
startup=load(B/'STARTUP.json');url=urllib.parse.urlsplit(startup['url']);assert url.hostname=='127.0.0.1' and url.port==startup['port'] and url.path==bp['url_prefix']
rows=[json.loads(x) for x in (B/'responses.jsonl').read_text().splitlines()];assets={}
for row in rows:
 rel=row['relative_path'];pin=manifest[rel]
 assert row['path'].startswith(bp['url_prefix']) and row['status']==200 and row['method']=='GET'
 assert row['write_completed'] and row['cache_control']=='no-store' and row['request_if_none_match'] is None and row['request_if_modified_since'] is None
 assert row['body_sha256']==pin['sha256'] and row['body_bytes']==row['content_length']==row['write_returned_bytes']==pin['bytes']
 assert 'Chrome/' in row['user_agent']
 if row['referer']:assert row['referer'].startswith('http://127.0.0.1:'+str(url.port)+bp['url_prefix'])
 if rel in bp['required_assets']:assets[rel]=assets.get(rel,0)+1
assert set(assets)==set(bp['required_assets'])
assert 'Response up to date' in (B/'final-ax.txt').read_text()

# Original accepted controls/reset/overlays are inherited, not newly observed.
prior=load(P.parent/'current-delivery-v1/independent-review/decision.json')
assert prior['accepted'] and sha(P.parent/'current-delivery-v1/independent-review/decision.json')=='56c986b0693c0c813ae02ed37973f8a0c9eae1caf0544c714b6d9db79d0868fb'
oldmanifest=load(P.parent/'current-delivery-v1/PACKAGE_MANIFEST.json')['files']
for f in ['atlas.js','atlas.wasm','models.json','laboratory-worker.mjs']:assert manifest[f]==oldmanifest[f]
publicfixture=C/'docs/ingestion/lade-duncan-1975/atlas-integration-v1/live-release-v1/interface-request.json'
assert sha(publicfixture)==next(iter(freeze['private_fixture_inputs'].values()))
assert (C/'.github/workflows/verify.yml').read_text().count('restore_interface_request.py')==2
assert sha(C/'models/hypoplastic-clay-2013.json')==prior['model_sha256']
# Recheck the reviewer-generated ordinary metadata export, no material calls.
metadata_receipt=Path(__file__).with_name('metadata-exports.json')
if metadata_receipt.exists():
 d=load(metadata_receipt);assert all(x['exit_code']==0 for x in d['commands'])
 assert maps(Path(d['output']))==checks['after_manifest']

result={'status':'passed','reviewer_run_id':'/root/contour_lifecycle_review','base':plan['base'],'source_writes':28,'staged_paths':28,'unstaged_tracked_paths':0,'untracked_unignored_paths':0,'unchanged_previously_accepted_additions':27,'preserved_approvals':18,'approvals_after':21,'source_pins':27855,'external_pins':40,'private_pins':1,'repair_pins':len(pinrows),'ordinary_successes':13,'declared_ordinary_failures_retained':1,'downloadable_definitions':23,'inherited_core_engine_and_worker_unchanged':True,'package_files':1002,'database_tables':tables,'public_metadata_delta':delta,'saved_builder_exit':0,'saved_builder_seconds':status2['elapsed_seconds'],'retained_failed_builder_exit':1,'supported_ordinary':14,'supported_named':1,'browser_points':101,'browser_full_physical_result_exact':True,'required_browser_asset_deliveries':assets,'browser_trace_rows':len(rows),'reviewer_material_calls':0,'reviewer_builds':0,'reviewer_browser_calls':0,'remote_actions':0}
if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
