"""Independent saved-only release package and browser metadata-delta audit."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[5];HERE=Path(__file__).resolve().parent;PACK=HERE.parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
old=read(ROOT/'docs/ingestion/duncan-chang-1970/integration-v2/package-manifest-v1.json');new=read(PACK/'package-manifest-v6.json');site=Path(new['source_path']);oldsite=Path(old['source_path']);assert new['count']==len(new['files'])==953
assert set(new['files'])==set(old['files'])=={str(f.relative_to(site)) for f in site.rglob('*') if f.is_file()}
for n,h in new['files'].items():assert sha(site/n)==h
changed={n for n,h in new['files'].items() if old['files'][n]!=h};assert changed=={'catalogue.json','atlas-database.json'}
a=read(oldsite/'catalogue.json');b=read(site/'catalogue.json');row=next(x for x in b['models'] if x['id']=='duncan-chang-1970');gap=row.pop('capability_gap');assert a==b
assert gap=='Family discovery entry has no separate executable law; use reviewed duncan-chang-1970-endpoint-average realization. Other family revisions are not admitted by this record.'
a=read(oldsite/'atlas-database.json');b=read(site/'atlas-database.json')
for section,name in [('source_inputs','catalogue/manifest.json'),('package_inputs','catalogue.json')]:
 assert b[section][name]==new['files']['catalogue.json'];b[section][name]=a[section][name]
assert a==b
freeze=read(PACK/'package-source-freeze-v2.json');base=Path(freeze['source_root'])
for n,h in freeze['files'].items():assert sha(base/n)==h
assert read(PACK/'package-process-v6.json')['source_postcheck'] is True and read(PACK/'package-process-v6.json')['exit_code']==0
browser=read(PACK/'browser-delta-v1.json');assert browser['passed']
for asset in browser['asset_hashes']:assert asset['status']==200 and asset['sha256']==sha(site/asset['path']) and asset['bytes']==(site/asset['path']).stat().st_size
for n,h in browser['browser_files'].items():assert sha(ROOT/n)==h
for m in read(PACK/'browser-public-mirrors-v1.json'):assert sha(ROOT/m['original'])==sha(ROOT/m['public'])==m['sha256']
actual=read(ROOT/'output/playwright/duncan-release-v1/default-run.json');prior=read(ROOT/'output/playwright/duncan-integration-v2/reset-browser-run.json');assert actual['specification']==prior['specification'];assert actual['result']['points']==prior['result']['points'] and len(actual['result']['points'])==101 and actual['result']['ok']
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (ROOT/'output/playwright/duncan-release-v1/console.txt').read_text()
support=read(PACK/'supported-package-v6.json');assert support['status']=='passed' and len(support['ordinary'])==14 and len(support['named'])==1
assert len([x for x in support['ordinary'] if x['result']['ok']])==13
assert 'Ran 34 tests' in (PACK/'atlas-duncan-release-unit-v4.log').read_text() and (PACK/'atlas-duncan-release-unit-v4.log').read_text().rstrip().endswith('OK')
result={'status':'passed','package_files':953,'unchanged_files':951,'changes':['catalogue family discovery capability_gap only','database descriptor source/package catalogue hashes only'],'source_pins':len(freeze['files']),'browser_exact_complete_default_points':101,'browser_fetched_assets':6,'public_browser_mirrors':8,'unit_tests':34,'compiled_execution':False,'browser_control':False,'E6_E7_metadata_delta':'accepted','E8_live_delivery':False}
(HERE/'package-v6-audit-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
