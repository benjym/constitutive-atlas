from pathlib import Path
import json,hashlib,os,tempfile,sys,time
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();base=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');packet=root/'docs/reviews/legacy-source-binding-gaps-v1/rollback-closure-v1';plan=json.loads((base/'PLAN.json').read_text());brief=json.loads((packet/'INSTALL_PLAN.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();assert sha((base/'PLAN.json').read_bytes())==brief['full_plan_sha256'];freeze=json.loads((base/'qualification-v1/INPUT_FREEZE.json').read_text());assert sha((root/'atlas/evidence.py').read_bytes())==freeze['production_verifier_digest'];assert json.loads((base/'DRIFT.json').read_text())['pass'];assert json.loads((base/'qualification-v1/NEGATIVES.json').read_text())['pass'];assert json.loads((base/'qualification-v1/RESULT.json').read_text())['pass']
for rel,pin in freeze['inputs'].items():assert sha((root/rel).read_bytes())==pin['digest'],('input drift',rel)
for r in plan['mutations']:
 target=root/r['file'];assert target.resolve().is_relative_to(root);assert not target.is_symlink();before=sha(target.read_bytes()) if target.exists() else None;assert before==r['before_digest'],r['file'];assert sha((base/'proposed'/r['file']).read_bytes())==r['after_digest']
for r in plan['archives']:
 source=base/'archives'/r['archive_file'];assert sha(source.read_bytes())==r['digest'];target=root/r['archive_file'];assert not target.is_symlink();assert target.resolve().is_relative_to(root)
 if target.exists():assert target.read_bytes()==source.read_bytes()
# Preserve every existing map before replacing even the first one.
archives=[]
for r in plan['archives']:
 target=root/r['archive_file'];raw=(base/'archives'/r['archive_file']).read_bytes();created=False
 if not target.exists():
  target.parent.mkdir(parents=True,exist_ok=True);assert target.parent.resolve().is_relative_to(root)
  with target.open('xb') as f:f.write(raw)
  created=True
 assert sha(target.read_bytes())==r['digest'];archives.append({'archive_file':r['archive_file'],'digest':r['digest'],'created':created})
(packet/'ARCHIVES_CREATED.json').write_text(json.dumps(archives,indent=2)+'\n')
for r in plan['mutations']:
 target=root/r['file'];current=sha(target.read_bytes()) if target.exists() else None;assert current==r['before_digest'],('concurrent map change',r['file']);raw=(base/'proposed'/r['file']).read_bytes();target.parent.mkdir(parents=True,exist_ok=True)
 with tempfile.NamedTemporaryFile(prefix='.atlas-archive-',dir=target.parent,delete=False) as f:f.write(raw);temporary=f.name
 os.replace(temporary,target);assert sha(target.read_bytes())==r['after_digest']
sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
rows=[];expected=json.loads((base/'qualification-v1/after.json').read_text())
for r in expected:
 row={k:r[k] for k in ['document','target','expected_digest']}
 try:selected=checked_receipt(root,r['document'],r['target'],r['expected_digest']);assert sha(selected.read_bytes())==r['expected_digest'];row.update(pass_=True,selected=str(selected.relative_to(root)))
 except ValueError as e:row.update(pass_=False,error=str(e).replace(str(root),'<root>'))
 assert row['pass_']==r['pass_'],('isolated/production result differs',row,r);rows.append(row)
original=json.loads((root/'docs/reviews/legacy-source-binding-gaps-v1/EXACT_SOURCE_AVAILABILITY.json').read_text());bindings=[]
for r in original['pairs']:
 assert sha((root/r['document']).read_bytes())==r['document_digest'];row={'document':r['document'],'original_path':r['original_path'],'expected_digest':r['expected_digest'],'original_document_unchanged':True}
 try:sel=checked_receipt(root,r['document'],r['original_path'],r['expected_digest']);row.update(resolved=True,selected=str(sel.relative_to(root)))
 except ValueError as e:row.update(resolved=False,error=str(e).replace(str(root),'<root>'))
 bindings.append(row)
assert sum(r['resolved'] for r in bindings)==6;assert not bindings[-1]['resolved']
modified={r['file'] for r in plan['mutations']}
for rel,pin in freeze['inputs'].items():
 if rel not in modified:assert sha((root/rel).read_bytes())==pin['digest'],('non-map input changed',rel)
result={'pass':True,'map_mutations':len(modified),'new_maps':sum(r['before_digest'] is None for r in plan['mutations']),'archives':len(archives),'new_archives':sum(r['created'] for r in archives),'production_reference_pairs':len(rows),'working_references_preserved':sum(r['pass_'] for r in rows),'preexisting_unresolved_references':sum(not r['pass_'] for r in rows),'all_production_outcomes_match_isolated_qualification':True,'original_gap_pairs':bindings,'resolved_gap_pairs':6,'unresolved_gap_pairs':1,'all_original_documents_and_non_map_inputs_unchanged':True,'completed_at_unix':time.time(),'scope':'Exact declared consumer closure and original seven source pairs only. The227 unrelated historical map-reference failures remain failures. No full audit/numerical/source-law/experimental/scientific-admission claim; no builds or remote publication.'};(packet/'PRODUCTION_RESULTS.json').write_text(json.dumps(rows,indent=2)+'\n');(packet/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['pass','map_mutations','new_maps','new_archives','working_references_preserved','preexisting_unresolved_references','resolved_gap_pairs','unresolved_gap_pairs']}))
