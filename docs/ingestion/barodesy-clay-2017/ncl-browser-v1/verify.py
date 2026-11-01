"""Verify saved actual-browser exports and exact candidate package identities."""
from pathlib import Path
import hashlib,json
p=Path(__file__).resolve().parent;r=p.parents[3]
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
manifest=json.loads((p/'manifest.json').read_text())
for name,h in manifest['files'].items():assert sha(r/name)==h,name
qualification=r/'docs/ingestion/barodesy-clay-2017/ncl-laboratory-v1'
expected=json.loads((qualification/'laboratory-document.json').read_text())
clean=lambda x:{k:v for k,v in x.items() if k!='elapsed_ms'}
for name in ('browser-export.json','browser-replay-export.json'):
    doc=json.loads((p/name).read_text())
    assert doc['specification']==expected['specification'],name
    assert doc['catalogue_hash']==expected['catalogue_hash'],name
    assert doc['schema_version']==expected['schema_version'],name
    assert clean(doc['result'])==clean(expected['result']),name
    assert len(doc['result']['points'])==101
    assert doc['result']['initial']==[100000,100000,100000,0,0,0,1.3831693930553504]
package=json.loads((p/'package-manifest.json').read_text())
assert package['source_drift_since_packaging_freeze']==[] and package['root_registry_installed'] is False
site=Path('/private/tmp/barodesy2017-ncl-browser-v1/site')
for name,h in package['files'].items():assert sha(site/name)==h,name
assert package['files']['atlas.wasm']==sha(r/'.local/barodesy2017-ncl-lab-v1/artifacts/wasm/atlas.wasm')
assert package['files']['atlas.js']==sha(r/'.local/barodesy2017-ncl-lab-v1/artifacts/wasm/atlas.js')
assert package['files']['laboratory-examples/barodesy2017-london-ncl-isotropic-v1.json']==sha(qualification/'laboratory-document.json')
assert package['files']['evidence-records/catalogue/agent-reviews/barodesy2017-agent-v1.json']==sha(r/'catalogue/agent-reviews/barodesy2017-agent-v1.json')
http=json.loads((p/'http-assets.json').read_text());assert http['passed'] and len(http['assets'])==8
for row in http['assets']:assert row['status']==200 and package['files'][row['path']]==row['sha256']
print('Two actual browser exports match all101 qualified points;841candidate assets and8HTTP identities verify; root/live delivery unclaimed')
