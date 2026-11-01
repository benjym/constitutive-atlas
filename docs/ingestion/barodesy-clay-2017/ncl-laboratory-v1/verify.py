"""Saved-only packet, private retention and scalar-reference verification."""
from pathlib import Path
import hashlib,importlib.util,json
p=Path(__file__).resolve().parent;r=p.parents[3]
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
manifest=json.loads((p/'manifest.json').read_text())
for name,h in manifest['files'].items():assert sha(r/name)==h,name
source=json.loads((p/'source-manifest.json').read_text())
for name,h in source['files'].items():assert sha(r/source['snapshot']/name)==h,name
for name,receipt in json.loads((p/'retained-artifact-receipts.json').read_text()).items():
    assert sha(r/name)==receipt['sha256'],name
    assert (r/name).stat().st_size==receipt['bytes'],name
packaging=json.loads((p/'packaging-inputs.json').read_text())
for name,h in packaging['files'].items():assert sha(r/packaging['root']/name)==h,name
freeze=json.loads((p/'execution-freeze.json').read_text())
# The original temporary artifact paths are identified by exact retained bytes;
# packet paths remain exact current frozen checker/runner/policy/source manifest.
retained={v['sha256'] for v in json.loads((p/'retained-artifact-receipts.json').read_text()).values()}
for name,h in freeze['files'].items():
    if name.startswith(str(p)+'/'):assert sha(Path(name))==h,name
    else:assert h in retained,(name,'unretained execution input')
spec=importlib.util.spec_from_file_location('barodesy_ncl_frozen_check',p/'check.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.assess(p/'results')==json.loads((p/'results/assessment.json').read_text())
entry=json.loads((p/'proposed-example-entry.json').read_text());doc=json.loads((p/'laboratory-document.json').read_text())
assert sha(p/'laboratory-document.json')==entry['document_sha256']
assert sha(r/'models/barodesy-clay-2017.json')==entry['definition_sha256']
index=json.loads((p/'packaged-index.json').read_text())
assert index['catalogue_hash']==doc['catalogue_hash']
assert any(x['id']==entry['id'] and x['document_sha256']==entry['document_sha256'] for x in index['examples'])
print('Exact packet/source/private artifacts, execution freeze, scalar reference and proposed example identity verified; no compiled calls')
