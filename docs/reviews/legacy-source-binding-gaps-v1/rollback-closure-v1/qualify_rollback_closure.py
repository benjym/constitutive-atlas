"""Qualify the exact generated sidecar proposal in an isolated filesystem."""
from pathlib import Path
import json,sys,hashlib,shutil,time,collections
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();p=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');plan=json.loads((p/'PLAN.json').read_text());q=p/'qualification-v1';q.mkdir(exist_ok=True);mini=q/'repository';mini.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();targets={r['file'] for r in plan['mutations']};refs=[r for r in plan['references'] if r['target'] in targets and any(s in r['shapes'] for s in ['direct-map','path-object'])];assert len(refs)==735;assert not plan['blockers'];sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
inputs={};escaped=[];absent=[]
def copy(rel,expected=None):
 if rel in inputs:
  if expected:assert inputs[rel]['digest']==expected
  return
 source=root/rel
 if not source.exists():absent.append(rel);return
 if not source.resolve().is_relative_to(root):escaped.append(rel);return
 raw=source.read_bytes();h=sha(raw)
 if expected:assert h==expected,(rel,h,expected)
 dest=mini/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);inputs[rel]={'digest':h,'bytes':len(raw)}
for r in refs:
 copy(r['document'],r['document_digest']);copy(str(Path(r['document']).parent/'source-archive-map.json'));copy(r['target']);copy('catalogue/source-snapshots/'+r['expected_digest']+'/'+r['target'])
source_docs=['catalogue/investigations/solver-rollback-v1/protocol.json','catalogue/investigations/solver-rollback-v1/native/receipt.json','catalogue/investigations/solver-rollback-v1/wasm/receipt.json'];source_h='d241f835c39e4129d1b550e25d5bfad3a70c9b70a3f4dbbc15938d19c7856b60'
for doc in source_docs:copy(doc);copy(str(Path(doc).parent/'source-archive-map.json'))
for r in plan['mutations']:
 current=root/r['file']
 if r['before_digest'] is None:assert not current.exists()
 else:assert sha(current.read_bytes())==r['before_digest'];copy(r['file'],r['before_digest'])
 for rel,key in [('proposed/'+r['file'],'after_digest')]:assert sha((p/rel).read_bytes())==r[key]
freeze={'plan_digest':sha((p/'PLAN.json').read_bytes()),'production_verifier_digest':sha((root/'atlas/evidence.py').read_bytes()),'inputs':inputs,'absent_inputs':sorted(set(absent)),'external_paths_not_copied':sorted(set(escaped)),'acceptance':{'all735_reference_results_retained':True,'no_before_success_lost':True,'all_selected_sources_have_original_expected_hash':True,'three_rollback_bindings_resolved_after':True,'all_plan_map_and_archive_hashes_exact':True,'no_existing_document_source_or_reference_rewritten':True,'existing_unresolved_bindings_not_relabelled':True},'scope':'Isolated candidate only; installation separately requires current-tree drift/new-reference check. No complete-repository, encoded payload, numerical or scientific admission claim.'};(q/'INPUT_FREEZE.json').write_text(json.dumps(freeze,indent=2)+'\n');print(json.dumps({'stage':'frozen','inputs':len(inputs),'refs':len(refs),'escaped':len(escaped)}),flush=True)
def assess(rows,label):
 result=[]
 for i,r in enumerate(rows):
  row={'document':r['document'],'target':r['target'],'expected_digest':r['expected_digest']}
  try:sel=checked_receipt(mini,r['document'],r['target'],r['expected_digest']);assert sha(sel.read_bytes())==r['expected_digest'];row.update(pass_=True,selected=str(sel.relative_to(mini)))
  except ValueError as e:row.update(pass_=False,error=str(e).replace(str(mini),'<fixture>'))
  result.append(row)
  if (i+1)%100==0:print(json.dumps({'stage':label,'checked':i+1}),flush=True)
 (q/(label+'.json')).write_text(json.dumps(result,indent=2)+'\n');return result
before=assess(refs,'before')
for r in plan['archives']:
 src=p/'archives'/r['archive_file'];raw=src.read_bytes();assert sha(raw)==r['digest'];dest=mini/r['archive_file'];dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.exists():assert dest.read_bytes()==raw
 else:dest.write_bytes(raw)
for r in plan['mutations']:
 src=p/'proposed'/r['file'];raw=src.read_bytes();assert sha(raw)==r['after_digest'];dest=mini/r['file'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
after=assess(refs,'after');lost=[{'before':a,'after':b} for a,b in zip(before,after) if a['pass_'] and not b['pass_']];assert not lost,lost[:1]
source_rows=[{'document':d,'target':'atlas/compiler.py','expected_digest':source_h} for d in source_docs];resolved=assess(source_rows,'rollback');assert all(r['pass_'] for r in resolved)
for rel,pin in inputs.items():
 if rel in targets:continue
 assert sha((mini/rel).read_bytes())==pin['digest'],rel
result={'pass':True,'references':len(refs),'before_success':sum(r['pass_'] for r in before),'after_success':sum(r['pass_'] for r in after),'lost_success':len(lost),'before_unresolved':sum(not r['pass_'] for r in before),'after_unresolved':sum(not r['pass_'] for r in after),'rollback_bindings_resolved':len(resolved),'isolated_inputs':len(inputs),'all_unmodified_inputs_preserved':True,'completed_at_unix':time.time(),'scope':'Candidate preservation checks only. Root source maps unchanged; live installation and complete closure/current-tree revalidation remain open.'};(q/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
