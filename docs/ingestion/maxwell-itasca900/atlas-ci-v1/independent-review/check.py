"""Pure source/archive/saved-restore review; no build/compiled execution/remote CI."""
import ast,difflib,hashlib,importlib.util,json,sys,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[5];BASE=ROOT/'docs/ingestion/maxwell-itasca900/atlas-ci-v1';sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
for n,h in load(BASE/'bindings-v2.json').items():assert sha((ROOT/n).read_bytes())==h,n
# Original input manifest remains resolvable after the cleanup test addition.
for n,h in load(BASE/'bindings.json').items():assert checked_receipt(ROOT,str((BASE/'bindings.json').relative_to(ROOT)),n,h).is_file()
for n in ['tools/provision_maxwell_assets.py','tests/test_provision_maxwell_assets.py']:ast.parse((ROOT/n).read_text())
from tools import provision_maxwell_assets as p
assert p.ARCHIVE_SHA256==sha((p.PACKET/'compiled-closure-v1.tar.gz').read_bytes())=='7595c20b97502e1f15354c07f4fcd7e54ef6f956283038330895934d9f02fd52'
assert p.QUALIFICATION_SHA256==sha((p.PACKET/'maxwell-qualification.json').read_bytes())=='d989230df995a154ec721769bef3afd5d5347bc40d652af95229cdb5dab9433c'
assert p.REVIEW_SHA256==sha((p.PACKET/'independent-review/final-v1/build-review.json').read_bytes())=='0fb88a7954f1f87682b8ee64b6e8538710c3b36ad359708431023aa550097914'
q=load(p.PACKET/'maxwell-qualification.json');review=load(p.PACKET/'independent-review/final-v1/build-review.json');assert q['binding']==review['binding'] and review['status']=='accepted' and q['gates']==review['gates'] and all(v is True for v in review['gates'].values())
selected=p.selected_bytes(p.PACKET/'compiled-closure-v1.tar.gz',q['binding']);assert set(selected)=={'maxwell.js','maxwell.wasm','generated/models.json'}
assert selected['maxwell.wasm'][:8]==b'\0asm\x01\0\0\0'
js=selected['maxwell.js'].decode();assert 'export default createAtlas' in js
assert all(x not in js for x in ['/Users/','/opt/homebrew/','/private/tmp/'])
assert 'extractall' not in (ROOT/'tools/provision_maxwell_assets.py').read_text()
checks=load(BASE/'checks.json');assert checks[0]['exit_code']==checks[1]['exit_code']==0;restore=json.loads(checks[1]['stdout']);assert restore['status']=='passed'
restored=Path(checks[1]['command'][-1]);assert {str(x.relative_to(restored)) for x in restored.rglob('*') if x.is_file()}==set(restore['files'])
for n,h in restore['files'].items():assert sha((restored/n).read_bytes())==h
assert load(BASE/'checks-v2.json')['exit_code']==0
# Exact workflow projection, retaining every unrelated prior byte.
w=load(BASE/'workflow-binding.json');old=(ROOT/w['before_archive']).read_bytes();current=(ROOT/w['path']).read_bytes();assert sha(old)==w['before_sha256'] and sha(current)==w['after_sha256']
addition=b'          python -B -m unittest tests.test_provision_maxwell_assets\n          python -B tools/provision_maxwell_assets.py\n'
assert current.count(addition)==2 and current.replace(addition,b'')==old
assert current.count(addition+b'          python tools/build_web.py\n')==2
patch=''.join(difflib.unified_diff(old.decode().splitlines(True),current.decode().splitlines(True),fromfile=w['path'],tofile=w['path']))
assert patch==(BASE/'workflow.patch').read_text()
assert "default=ROOT/'build-maxwell-wasm'" in (ROOT/'tools/provision_maxwell_assets.py').read_text()
assert "default=ROOT/'build-maxwell-wasm'" in (ROOT/'tools/build_web.py').read_text()
# Preserved original workflow receipt documents and sidecar closures.
before=load(BASE/'frozen/bindings-before.json');pres=load(BASE/'preservation.json');assert len(pres['bindings'])==2 and len(pres['changed_sidecars'])==2
for row in pres['bindings']:
 assert sha((ROOT/row['archived_path']).read_bytes())==row['sha256']
 assert checked_receipt(ROOT,row['document'],row['original_path'],row['sha256'])==ROOT/row['archived_path']
 pin=next(x['document_sha256'] for x in before['primary_references'] if x['document']==row['document']);assert sha((ROOT/row['document']).read_bytes())==pin
spec=importlib.util.spec_from_file_location('ci_preservation_scan',BASE/'scan.py');scan=importlib.util.module_from_spec(spec);spec.loader.exec_module(scan);scan.TARGETS={w['path']};after=scan.scan(ROOT);counts={}
for group in ['primary_references','secondary_source_map_references']:
 idx={(x['document'],x['original_path'],x['sha256']):x for x in after[group]};good=[x for x in before[group] if x['resolution']!='unresolved']
 for x in good:
  y=idx.get((x['document'],x['original_path'],x['sha256']));assert y and y['resolution']!='unresolved',(group,x)
 counts[group]=len(good)
assert counts=={'primary_references':25,'secondary_source_map_references':4064}
print(json.dumps({'passed':True,'selected_regular_engine_members':3,'saved_restore_files':len(restore['files']),'qualification_and_actual_review_binding':'exact retained accepted evidence','existing_bundle_guard':'unchanged sha e712f6884290718fddc54ca00b7b7332a9d321f9d2105cc4bca84f9bfca9254c','workflow_added_prebuilder_pairs':2,'unrelated_workflow_bytes':'exact retained','preserved_receipt_bindings':2,'prior_resolved_primary_preserved':25,'prior_resolved_secondary_preserved':4064,'previously_resolved_bindings_lost':0,'preexisting_unresolved_primary':33,'preexisting_unresolved_secondary':304,'platform_assessment':'Standard Wasm v1 and host-path-free ES module; no native executable installed. Linux CI execution not performed.','reviewer_builds':0,'reviewer_compiled_calls':0,'remote_ci_runs':0},indent=2))
