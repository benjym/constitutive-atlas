"""Verify saved actual live Playwright observations against authenticated upload."""
from pathlib import Path
import hashlib
import json
import re

HERE = Path(__file__).resolve().parent
raw = json.loads((HERE / 'ACTUAL-TOOL-RESULTS.json').read_text())

def result(name):
    call = raw[name]
    assert not call.get('isError', False), name
    text = next(x['text'] for x in call['content'] if x['type'] == 'text' and '### Result\n' in x['text'])
    return json.loads(text.split('### Result\n', 1)[1].split('\n### Ran', 1)[0])

upload = json.loads((HERE.parent / 'upload-live-v1/UPLOAD-MANIFEST.json').read_text())['files']
manifest = json.loads((HERE / 'ARTIFACT-MANIFEST.json').read_text())['files']
assert len(manifest) == 10
for name, item in manifest.items():
    data = (HERE / 'artifacts' / name).read_bytes()
    assert hashlib.sha256(data).hexdigest() == item['sha256'] and len(data) == item['bytes']
profile = result('profile')
assert profile['technicalInitiallyClosed'] and len(profile['parameterRows']) == 5
assert profile['related'] == ['#catalogue/bingham-comsol63-mises-perfect-zero-spin-ode', '#catalogue/power-creep-itasca900-both-active-ode']
assert len(profile['sourceLinks']) == 3
assert all(x.startswith('https://doc.comsol.com/6.3/') for x in profile['sourceLinks'])
links = profile['technicalLinks']
assert len(links) == 4 and all(x['status'] == 200 and x['url'].startswith('https://benjym.github.io/constitutive-atlas/') for x in links)
assert result('relaxation')['tableRows'] == 7 and result('relaxation')['measurementUnavailable']
for mode in ('relaxation', 'creep', 'rate'):
    run = result(mode)
    assert run['plots'] == 3 and run['status'].endswith('· ' + mode + '.')
fetched = result('fetched-assets')
assert len(fetched) == 25
for item in fetched:
    expected = upload[item['path']]
    assert item['status'] == 200 and item['bytes'] == expected['bytes'] and item['sha256'] == expected['sha256']
mobile = result('mobile-profile')
assert mobile['viewport'] == mobile['pageWidth'] == 375
assert mobile['profileWidth'] == mobile['profileScrollWidth'] == 301
assert mobile['parameterRows'] == 5 and mobile['technicalClosed']
teardown = result('teardown')
assert teardown['console'] == [] and teardown['requestFailures'] == []
assert teardown['cacheRestored'] and teardown['finalURL'] == 'about:blank'
assert teardown['viewport'] == {'width': 1280, 'height': 900}
console = (HERE / 'artifacts/console.txt').read_text()
assert 'Errors: 0' in console and 'Warnings: 0' in console
network = (HERE / 'artifacts/network.txt').read_text()
assert not re.search(r'=> \[[45]\d\d\]', network)
assert 'net::ERR_' not in network
exports = json.loads((HERE / 'EXPORT-CHECKS.json').read_text())
assert exports['passed'] and exports['comparisons'] == 342
assert all(x['exact_E7_result'] for x in exports['modes'])
report = dict(passed=True, release=exports['release'], modes=3,
              actual_reference_comparisons=342, exact_E7_results=True,
              fetched_upload_asset_matches=25, technical_links_200=4,
              profile_parameter_rows=5, mobile_viewport=375,
              mobile_page_overflow=False, console_warnings_or_errors=0,
              request_failures=0, final_browser_url='about:blank',
              scope='Actual public project-path profile and UI-driven three-mode runs; no experimental validation claim.')
(HERE / 'CHECKS.json').write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps(report, indent=2))
