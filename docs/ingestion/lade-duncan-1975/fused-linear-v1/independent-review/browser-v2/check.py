from pathlib import Path
import json,hashlib,re
H=Path(__file__).resolve().parent;R=H.parents[5];A=R/'docs/ingestion/lade-duncan-1975/atlas-integration-v1';P=R/'output/playwright/lade-main-v2'
load=lambda p:json.loads(p.read_bytes());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
summary=load(A/'actual-package-v2/BROWSER_RESULTS.json');assert summary['status']=='passed-local-observations'
for name,h in summary['evidence_files'].items():assert sha(R/name)==h
manifest={r['path']:r for r in load(A/'actual-package-v2/PACKAGE_MANIFEST.json')['files']};fetched=load(P/'fetched-assets.json')
assert len(fetched['rows'])==19
for row in fetched['rows']:assert row['status']==200 and row['sha256']==manifest[row['path']]['sha256'] and row['bytes']==manifest[row['path']]['bytes']
assert 'no-store' in (P/'fetch-assets-action.js').read_text()
assert sha(P/'downloaded-model.json')=='120b93f319543518b2b87221ab7457afaca2a1fb5de78af901276e8e89a22e63'
def witness(name):return json.JSONDecoder().raw_decode((P/name).read_text().split('### Result\n')[1])[0]
desktop=witness('desktop-witness.log');assert desktop['selected']=='lade-duncan-1975-midpoint-elastic-eq19-gap-v4' and desktop['family']=='Soil elastoplasticity' and desktop['status']=='Approved bounded numerical scope' and desktop['rows']==402
assert 'small strain' in desktop['description'] and 'zero pore pressure' in desktop['description']
assert len(desktop['sources'])==4 and desktop['sources'][0]['url']=='https://doi.org/10.1061/AJGEB6.0000204'
for row in desktop['sources'][1:]:assert row['url'].removeprefix(summary['server']) in manifest
latest=witness('latest-witness.log');assert latest[0]['event']=='old-worker-started' and latest[0]['run_disabled'] and latest[1]['terminated'] and latest[-1]['event']=='latest-run-completed'
switch=witness('switch-witness.log');assert switch['running_before_switch'] and switch['worker_closed'] and switch['selected']=='linear-elastic' and switch['lade_hidden']
assert not any('implicit-path-worker' in url for url in switch['remaining_workers'])
invalid=witness('invalid-reset-witness.log');assert invalid['invalid']['status'].startswith('Invalid input:') and invalid['invalid']['export_disabled'] and invalid['recovery_status']=='Strain-path response complete.' and invalid['family']=='Soil elastoplasticity'
layout=witness('state-layout-witness.log');assert layout['viewport']==layout['document']==390 and layout['columns']==16 and layout['rows']==402 and layout['table_scroll_width']>layout['table_client_width']
mobile=witness('mobile-witness.log');assert mobile['bounds']['viewport']==mobile['bounds']['document']==mobile['bounds']['body']==390
assert all(0<=c['left']<c['right']<=390 for c in mobile['bounds']['controls'])
for name in ['mobile-header.png','mobile-response.png','mobile-state.png']:assert int.from_bytes((P/name).read_bytes()[16:20],'big')==390
requests=(P/'requests-all-v2.log').read_text();codes=re.findall(r'http://127\.0\.0\.1:56010/[^\n]*?=> \[(\d+)\]',requests);assert len(codes)==174 and all(c=='200' for c in codes)
assert 'Errors: 0, Warnings: 0' in (P/'console-v2.log').read_text()
old=load(A/'actual-package-v1/PACKAGE_MANIFEST.json');old={r['path']:r['sha256'] for r in old['files']}
for name,row in manifest.items():
 if name!='app.js' and not name.startswith('implicit-path-package-checks/'):assert old[name]==row['sha256']
v1=A/'actual-package-v1/browser-data-review/review-receipt.json';assert sha(v1)=='59ff2c9deaefb33561f5434624649ab4f2b1309e0a79a250ad9f3d1e87c943b2'
for name,h in load(v1)['files'].items():assert sha(R/name)==h,name
result=dict(status='passed',fetched_body_hashes=19,download_exact=True,current_origin_HTTP200=174,console_errors=0,console_warnings=0,worker_cancellation_edit=True,worker_cancellation_switch=True,invalid_reset_recovery=True,mobile_width=390,state_columns=16,state_rows=402,scope='Saved actual Chrome observations and exact unchanged-component composition; no reviewer browser call or live delivery')
(H/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
