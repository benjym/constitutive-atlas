"""Audit saved source/package/browser evidence; never execute compiled artifacts."""
from pathlib import Path
import hashlib,json,sys,subprocess,sqlite3
root=Path(sys.argv[1]).resolve();site=Path(sys.argv[2]).resolve();oldroot=Path(sys.argv[3]).resolve();sys.path.insert(0,str(root))
from atlas.evidence import checked_receipt
pre=Path('docs/ingestion/duncan-chang-1970/release-v2');h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();load=lambda p:json.loads(p.read_text());inventory=load(root/pre/'prospective-source-scope-v2.json');selected={x['path']:x for x in inventory['files']}
assert len(selected)==inventory['count']==4989
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()==inventory['base']=='9cefd1a654f6e0f587edd6aac2c3828bd29e9a16'
size=0
for p,r in selected.items():
 q=root/p;assert q.resolve().is_relative_to(root) and h(q)==r['sha256'] and q.stat().st_size==r['bytes'];size+=r['bytes']
 assert not p.endswith(('.pdf','.dylib','.so','.dll','.exe')) and not any(s in Path(p).parts for s in ['.local','.codex-attachments','paper'])
assert size==inventory['bytes']
changed=subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=root,text=True).splitlines();assert set(changed)<=selected.keys()
assert all(p in ['.github/workflows/verify.yml','catalogue/manifest.json','tests/test_catalogue.py'] or p.endswith('/source-archive-map.json') for p in changed)
# Exact accepted non-map changes.
assert (root/'.github/workflows/verify.yml').read_bytes()==(root/pre/'proposed-verify.yml').read_bytes()
assert (root/'catalogue/manifest.json').read_bytes()==(root/pre/'proposed-manifest-v2.json').read_bytes()
assert (root/'tests/test_catalogue.py').read_bytes()==(root/pre/'proposed-test-catalogue-v2.py').read_bytes()
combined=load(root/pre/'remote-map-union-v1/combined-plan.json')
for o in combined['operations']:assert h(root/o['path'])==o['proposed_sha256']
bindings=[]
for version in ['v1','v2','v3']:
 plan=load(root/pre/f'preservation-{version}/preservation-plan.json');bindings+=plan['bindings']
 for p,d in plan['document_pins'].items():assert h(root/p)==d
for b in bindings:checked_receipt(root,b['document'],b['original_path'],b['sha256'])
freeze=load(root/pre/'package-source-freeze-v1.json')
for p,d in freeze['files'].items():assert h(root/p)==d
package=load(root/pre/'package-manifest-v1.json');assert len(package)==980
for p,r in package.items():assert h(site/p)==r['sha256'] and (site/p).stat().st_size==r['bytes']
process=load(root/pre/'package-process-v1.json');assert process['exit_code']==0 and process['source_postcheck']
assert 'Ran 42 tests' in (root/pre/'unit-v4.log').read_text() and (root/pre/'unit-v4.log').read_text().rstrip().endswith('OK')
# Browser exports have all complete points equal, excluding runtime measurement only.
browser=root/pre/'browser';proof=load(root/pre/'browser-proof-v1.json')
for p,d in proof['files'].items():assert h(browser/p)==d
for a in proof['assets']:assert a['status']==200 and h(site/a['path'])==a['sha256'] and (site/a['path']).stat().st_size==a['bytes']
def run(name):return load(browser/name)
def compare(a,b):
 assert a['specification']==b['specification']
 ra=dict(a['result']);rb=dict(b['result']);ra.pop('elapsed_ms');rb.pop('elapsed_ms');assert ra==rb
pairs=[('dense-run.json',oldroot/'output/playwright/duncan-integration-v2/dense-browser-run.json'),('loose-run.json',oldroot/'output/playwright/duncan-integration-v2/loose-browser-run.json'),('default-run.json',oldroot/'output/playwright/duncan-release-v1/default-run.json')]
for n,p in pairs:compare(run(n),load(p))
for a,b in [('dense-run.json','dense-replay.json'),('dense-run.json','recovered-run.json'),('default-run.json','reset-run.json')]:compare(run(a),run(b))
assert run('edited-run.json')['result']['target']==.0075
assert run('parameter-edited-run.json')['specification']['parameters']!=run('edited-run.json')['specification']['parameters']
s=(browser/'invalid.yml').read_text();assert 'Waiting for a valid input' in s and 'button "↓ Reproducible run" [disabled]' in s and 'button "↓ Results CSV" [disabled]' in s
assert 'Errors: 0, Warnings: 0' in (browser/'console.txt').read_text()
s=(browser/'catalogue-approved.yml').read_text();assert 'Scientific eligibility: undetermined' in s and 'https://doi.org/10.1061/JSFEAQ.0001458' in s
# Package exact admission/model identities and database integrity.
model='duncan-chang-1970-endpoint-average';assert h(site/f'models/{model}.json')=='452b49ef48668c0c5d8aba20dfca398235fa45431e853ee923be05a17c7c88a0'
assert h(site/f'evidence-records/catalogue/agent-reviews/{model}-agent-v1.json')=='189d1da073877eea9278be757548119334814b218d63bee0e97882e5b67151ab'
dbmeta=load(site/'atlas-database.json');assert h(site/'atlas.sqlite')==dbmeta['database']['sha256']
with sqlite3.connect('file:'+str(site/'atlas.sqlite')+'?mode=ro',uri=True) as db:
 assert db.execute('pragma foreign_key_check').fetchall()==[]
 definition=db.execute('select definition_json from models where id=?',(model,)).fetchone()[0];assert json.loads(definition)==load(site/f'models/{model}.json')
print(json.dumps({'status':'PASS','base':inventory['base'],'selected_files':len(selected),'selected_bytes':size,'tracked_changed_files':len(changed),'installed_union_operations':len(combined['operations']),'preserved_bindings':len(bindings),'frozen_package_source_files':len(freeze['files']),'package_files':len(package),'browser_fetched_assets':len(proof['assets']),'browser_export_points':[len(run(n)['result']['points']) for n,_ in pairs],'browser_replay_pairs':3,'focused_saved_tests':42,'limitations':['No builds/compiled calls/browser control performed','No final remote CI/Pages/live E8 proof','Earlier six excluded receipt failures remain explicit','Qualified engine artifacts reused; not a fresh numerical rebuild']},indent=2))
