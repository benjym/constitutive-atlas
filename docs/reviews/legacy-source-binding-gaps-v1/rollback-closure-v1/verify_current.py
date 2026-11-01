"""Read-only verification of the installed legacy source-binding repair."""
from pathlib import Path
import argparse,gzip,hashlib,json,sys
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();root=a.root.resolve();packet=root/'docs/reviews/legacy-source-binding-gaps-v1';base=packet/'rollback-closure-v1';v2=base/'sibling-coverage-v2';sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
plan=json.loads(gzip.decompress((base/'PLAN.json.gz').read_bytes()));supp=json.loads((v2/'PLAN.json').read_text());maps={r['file']:r['after_digest'] for r in plan['mutations']};maps.update({r['file']:r['after_digest'] for r in supp['mutations']});archives={r['archive_file']:r['digest'] for r in plan['archives']};archives.update({r['archive_file']:r['before_digest'] for r in supp['mutations']})
for rel,h in maps.items():assert sha(root/rel)==h,rel
for rel,h in archives.items():
 path=root/rel;assert path.resolve().is_relative_to(root) and not path.is_symlink(),rel;assert sha(path)==h,rel
refs=json.loads((base/'qualification-v1/after.json').read_text());passing=0;unresolved=0;improved=0
for r in refs:
 try:sel=checked_receipt(root,r['document'],r['target'],r['expected_digest']);assert sha(sel)==r['expected_digest'];ok=True
 except ValueError:ok=False
 assert not r['pass_'] or ok,('regressed',r);passing+=ok;unresolved+=not ok;improved+=ok and not r['pass_']
freeze=json.loads((v2/'qualification/INPUT_FREEZE.json').read_text())
for r in freeze['cases']:assert sha(checked_receipt(root,r['document'],r['source_file'],r['source_digest']))==r['source_digest']
for rel,h in freeze['document_pins'].items():assert sha(root/rel)==h
original=json.loads((packet/'EXACT_SOURCE_AVAILABILITY.json').read_text());pairs=[]
for r in original['pairs']:
 assert sha(root/r['document'])==r['document_digest']
 try:sel=checked_receipt(root,r['document'],r['original_path'],r['expected_digest']);ok=True
 except ValueError:ok=False
 pairs.append({'document':r['document'],'source_file':r['original_path'],'expected_digest':r['expected_digest'],'resolved':ok})
assert all(r['resolved'] for r in pairs[:6]);out={'pass':True,'current_maps_verified':len(maps),'canonical_archive_versions_verified':len(archives),'target_reference_pairs':len(refs),'working_target_references':passing,'unresolved_target_references':unresolved,'improved_since_original_qualification':improved,'sibling_source_pairs':len(freeze['cases']),'original_gap_pairs':pairs,'original_gaps_resolved':sum(r['resolved'] for r in pairs),'original_gaps_unresolved':sum(not r['resolved'] for r in pairs),'scope':'Declared installed repair and source consumers only. No full-repository completeness, scientific/numerical admission, compiled execution, or live-release claim.'};a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='original_gap_pairs'}))
