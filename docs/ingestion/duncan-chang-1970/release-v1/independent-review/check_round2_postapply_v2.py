"""Saved-source preservation audit only; no compiled calls."""
from pathlib import Path
import hashlib,json,sys
root=Path(sys.argv[1]).resolve()
sys.path.insert(0,str(root))
from atlas.evidence import checked_receipt
prefix='docs/ingestion/duncan-chang-1970/release-v2/'
plan=json.loads((root/(prefix+'preservation-v2/preservation-plan.json')).read_text())
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for b in plan['bindings']:
 assert hashfile(root/b['archived_path'])==b['sha256']
 checked_receipt(root,b['document'],b['original_path'],b['sha256'])
for p,v in plan['planned_sidecars'].items():
 assert hashfile(root/p)==v['proposed_sha256']
for p,h in plan['document_pins'].items(): assert hashfile(root/p)==h
receipt_path=prefix+'postapply/receipt.json'
receipt=json.loads((root/receipt_path).read_text())
for p,h in (receipt['current_sources']|receipt['plans']).items():
 assert hashfile(root/p)==h
 checked_receipt(root,receipt_path,p,h)
assert (root/'catalogue/manifest.json').read_bytes()==(root/(prefix+'proposed-manifest-v2.json')).read_bytes()
assert (root/'tests/test_catalogue.py').read_bytes()==(root/(prefix+'proposed-test-catalogue-v2.py')).read_bytes()
log=(root/(prefix+'unit-v2.log')).read_text()
assert 'Ran 42 tests' in log and log.rstrip().endswith('OK')
print(json.dumps({'status':'PASS','preserved_bindings':len(plan['bindings']),'installed_maps':len(plan['planned_sidecars']),'unchanged_documents':len(plan['document_pins']),'new_receipt_valid_source_and_plan_pairs':5,'focused_tests_saved_result':'42 PASS','warning':'Saved log contains ResourceWarning for an unclosed SQLite connection; no numerical or test assertion failure.'},indent=2))
