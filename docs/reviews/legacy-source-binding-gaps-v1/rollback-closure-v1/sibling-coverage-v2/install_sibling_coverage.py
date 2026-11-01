from pathlib import Path
import json,sys,hashlib,tempfile,os,time
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();base=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');p=base/'sibling-coverage-v2';packet=root/'docs/reviews/legacy-source-binding-gaps-v1/rollback-closure-v1/sibling-coverage-v2';plan=json.loads((p/'PLAN.json').read_text());freeze=json.loads((p/'qualification/INPUT_FREEZE.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();assert json.loads((p/'qualification/RESULT.json').read_text())['pass'];rev=json.loads((p/'REVERSE.json').read_text());assert not rev['installed_v1_primary_references'];assert sha((p/'PLAN.json').read_bytes())==freeze['plan_digest']
for r in rev['input_pins']:assert sha((root/r['file']).read_bytes())==r['digest'],('reverse input drift',r['file'])
for rel,h in freeze['document_pins'].items():assert sha((root/rel).read_bytes())==h
for case in freeze['cases']:assert sha((root/case['source_file']).read_bytes())==case['source_digest']
for r in plan['mutations']:
 assert sha((root/r['file']).read_bytes())==r['before_digest'];assert sha((p/'proposed'/r['file']).read_bytes())==r['after_digest'];target=root/r['archive_file'];assert target.resolve().is_relative_to(root) and not target.is_symlink()
 if target.exists():assert sha(target.read_bytes())==r['before_digest']
sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
before=[]
for c in freeze['cases']:
 try:checked_receipt(root,c['document'],c['source_file'],c['source_digest']);before.append(True)
 except ValueError:before.append(False)
for r in plan['mutations']:
 target=root/r['archive_file'];raw=(root/r['file']).read_bytes();assert sha(raw)==r['before_digest'];target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():
  with target.open('xb') as f:f.write(raw)
 assert sha(target.read_bytes())==r['before_digest']
for r in plan['mutations']:
 target=root/r['file'];assert sha(target.read_bytes())==r['before_digest'];raw=(p/'proposed'/r['file']).read_bytes()
 with tempfile.NamedTemporaryFile(prefix='.atlas-archive-',dir=target.parent,delete=False) as f:f.write(raw);name=f.name
 os.replace(name,target);assert sha(target.read_bytes())==r['after_digest']
for c in freeze['cases']:assert sha(checked_receipt(root,c['document'],c['source_file'],c['source_digest']).read_bytes())==c['source_digest']
prior=json.loads((base/'qualification-v1/after.json').read_text());outcomes=[]
for c in prior:
 try:checked_receipt(root,c['document'],c['target'],c['expected_digest']);ok=True
 except ValueError:ok=False
 assert ok==c['pass_'],('target outcome changed',c);outcomes.append(ok)
sourcepairs=json.loads((root/'docs/reviews/legacy-source-binding-gaps-v1/EXACT_SOURCE_AVAILABILITY.json').read_text())['pairs'];resolved=[]
for c in sourcepairs:
 assert sha((root/c['document']).read_bytes())==c['document_digest']
 try:checked_receipt(root,c['document'],c['original_path'],c['expected_digest']);resolved.append(True)
 except ValueError:resolved.append(False)
assert sum(resolved)==6 and not resolved[-1]
# Complete sibling pin coverage on all21 new maps, even maps needing no amendment.
v1=json.loads((base/'PLAN.json').read_text());maprels=[r['file'] for r in v1['mutations'] if r['before_digest'] is None]+['catalogue/source-replays/dsl-identity-v5/source-archive-map.json'];documents=0
for rel in maprels:
 m=json.loads((root/rel).read_text())
 for doc in (root/rel).parent.glob('*.json'):
  d=str(doc.relative_to(root))
  if d==rel:continue
  assert m['documents'].get(d)==sha(doc.read_bytes()),d;documents+=1
result={'pass':True,'modified_maps':len(plan['mutations']),'preimage_archives_verified':len(plan['mutations']),'exact_document_pins_added':len(plan['added_document_pins']),'sibling_source_cases':len(freeze['cases']),'sibling_cases_before_correction_passed':sum(before),'sibling_cases_after_correction_passed':len(freeze['cases']),'previous735_outcomes_unchanged':True,'working_map_references_preserved':sum(outcomes),'preexisting_unresolved_map_references':sum(not v for v in outcomes),'new_maps_with_complete_sibling_coverage':len(maprels),'sibling_documents_checked':documents,'original_gap_bindings_resolved':sum(resolved),'original_gap_bindings_unresolved':len(resolved)-sum(resolved),'all_original_gap_document_bytes_unchanged':True,'completed_at_unix':time.time(),'scope':'Supersedes v1 sibling-coverage omission, not its preserved target-scope result. No source, science, numerical, model, runtime, build or remote-release changes.'};(packet/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
