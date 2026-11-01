"""Audit actual CLI browser exports and fetched package bytes without rerunning."""
import hashlib
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[4]
OUT=ROOT/'output/playwright/duncan-integration-v2'
SITE=Path('/private/tmp/atlas-duncan-integration-v2/site-v1')
read=lambda p:json.loads(p.read_text())
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for label in ['dense','loose']:
    actual=read(OUT/f'{label}-browser-run.json')
    registered=read(ROOT/f'protocols/duncan-{label}-source-drained-v1.json')
    assert actual['specification']==registered['specification']
    assert actual['result']['ok'] and len(actual['result']['points'])==129
    assert actual['result']['points']==registered['result']['points']
    checks[label+'_129_complete_points_exact_registered_history']=True
dense=read(OUT/'dense-browser-run.json');replay=read(OUT/'dense-browser-replay.json')
assert dense['specification']==replay['specification']
assert dense['result']['points']==replay['result']['points']
checks['actual_import_fresh_replay_exact_points_including_diagnostics']=True
edited=read(OUT/'edited-browser-run.json')
assert edited['result']['ok'] and len(edited['result']['points'])==129
assert edited['specification']['target']==.004
assert edited['specification']['parameters'][2]==1800
assert edited['specification']['initial'][6]==200000
checks['latest_rapid_target_and_parameter_and_initial_history_edits']=True
invalid=(OUT/'invalid-history-result.log').read_text()
assert 'Stopped · last committed state retained' in invalid
assert 'spinbutton "h (kPa)"' in invalid and '"-1"' in invalid
assert 'button "↓ Reproducible run" [disabled]' in invalid
checks['invalid_negative_history_rejected_then_successful_recovery']=True
reset=read(OUT/'reset-browser-run.json');definition=read(ROOT/'models/duncan-chang-1970-endpoint-average.json')
assert reset['result']['ok'] and len(reset['result']['points'])==101
assert reset['specification']['parameters']==[x['default'] for x in definition['parameters'].values()]
assert reset['specification']['initial']==[100000,100000,100000,0,0,0,0]
assert reset['specification']['target']==.01 and reset['specification']['steps']==100
checks['reset_all_parameters_state_and_default_loading']=True
identity=read(OUT/'asset-identity.json')
assert len(identity['assets'])==12
for item in identity['assets']:assert item['sha256']==sha(SITE/item['name'])
checks['twelve_browser_fetched_engine_catalogue_model_review_notice_dossier_assets_match_package']=True
assert 'Total messages: 0 (Errors: 0, Warnings: 0)' in (OUT/'final-console.log').read_text()
network=(OUT/'final-requests.log').read_text()
assert '[404]' not in network and '[500]' not in network
checks['recorded_console_and_visible_network_requests_without_errors']=True
# Copy only snapshots explicitly referenced by this session's retained logs.
for log in OUT.glob('*.log'):
    for name in re.findall(r'\.playwright-cli/(page-[\w.:-]+\.yml)',log.read_text()):
        src=ROOT/'.playwright-cli'/name
        if src.exists():(OUT/name).write_bytes(src.read_bytes())
result=dict(status='passed',scope='Actual main-browser actions and exact saved exports; independent final E6/E7 review and E8 release/live qualification remain separate.',checks=checks,files={str(p.relative_to(ROOT)):sha(p) for p in sorted(OUT.iterdir()) if p.is_file()})
target=Path(__file__).resolve().parent/'browser-audit-results.json'
assert not target.exists(),'Preserve prior observations'
target.write_text(json.dumps(result,indent=2)+'\n')
print(f'{len(checks)} bounded actual-browser checks pass; independent final E6/E7 acceptance and E8 live delivery remain separate.')
