from pathlib import Path
import json,hashlib,re,sys,collections
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();base=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');p=base/'sibling-coverage-v2';plan=json.loads((p/'PLAN.json').read_text());sha=lambda b:hashlib.sha256(b).hexdigest();HEX=re.compile(r'[0-9a-f]{64}\Z');target_hash={r['file']:r['before_digest'] for r in plan['mutations']};primary=[];candidates=(p/'reverse-candidates.txt').read_text().splitlines();reverse_pins=[]
def pairs(n,secondary=False):
 todo=[n];out=set()
 while todo:
  v=todo.pop()
  if isinstance(v,dict):
   for k,h in v.items():
    if isinstance(h,str) and HEX.fullmatch(h):out.add((k,h,'direct-map'))
   for pk in ['path']+(['original_path'] if secondary else []):
    if isinstance(v.get(pk),str):
     for hk in ['sha256','hash']:
      h=v.get(hk)
      if isinstance(h,str) and HEX.fullmatch(h):out.add((v[pk],h,pk+'-object'))
   todo.extend(x for x in v.values() if isinstance(x,(dict,list)))
  elif isinstance(v,list):todo.extend(x for x in v if isinstance(x,(dict,list)))
 return out
for rel in candidates:
 raw=(root/rel).read_bytes();reverse_pins.append({'file':rel,'digest':sha(raw)});doc=json.loads(raw)
 for path,h,shape in pairs(doc):
  if target_hash.get(path)==h:primary.append({'document':rel,'target':path,'digest':h,'shape':shape})
(p/'REVERSE.json').write_text(json.dumps({'candidate_documents':len(candidates),'input_pins':reverse_pins,'installed_v1_primary_references':primary,'scope':'Targeted literal-path candidate enumeration, exact JSON direct/path hash matching. No embedded encoded payload claim.'},indent=2)+'\n');assert not primary,primary[:3]
mini=p/'qualification/repository';mini.mkdir(parents=True,exist_ok=True);source_hashes={};cases=[];documents={};skipped=collections.Counter()
for pin in plan['added_document_pins']:
 rel=pin['document_file'];raw=(root/rel).read_bytes();assert sha(raw)==pin['document_digest'];doc=json.loads(raw);dest=mini/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);documents[rel]=pin['document_digest']
 for path,h,shape in pairs(doc):
  relpath=Path(path)
  if relpath.is_absolute() or '..' in relpath.parts:skipped['unsafe_path']+=1;continue
  source=root/relpath
  if not source.is_file():skipped['not_a_live_file']+=1;continue
  if not source.resolve().is_relative_to(root):skipped['external_symlink']+=1;continue
  if path not in source_hashes:source_hashes[path]=sha(source.read_bytes())
  if source_hashes[path]!=h:skipped['live_digest_differs']+=1;continue
  dest=mini/path;dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():dest.write_bytes(source.read_bytes())
  cases.append({'document':rel,'source_file':path,'source_digest':h})
# All newly bound sibling documents are exact, including those without valid source pairs.
(p/'qualification/INPUT_FREEZE.json').write_text(json.dumps({'plan_digest':sha((p/'PLAN.json').read_bytes()),'document_pins':documents,'source_pins':source_hashes,'cases':cases,'skipped_pair_shapes':dict(skipped),'acceptance':'Every exact source pair valid with absent sidecars (the original state) must remain valid with the proposed document pins; all current map fields preserved and document pins exact.'},indent=2)+'\n')
sys.path.insert(0,str(root));from atlas.evidence import checked_receipt
for r in cases:assert sha(checked_receipt(mini,r['document'],r['source_file'],r['source_digest']).read_bytes())==r['source_digest']
for m in plan['mutations']:
 old=json.loads((root/m['file']).read_bytes());new=json.loads((p/'proposed'/m['file']).read_bytes());assert old['entries']==new['entries'];assert all(new['documents'].get(k)==v for k,v in old['documents'].items());dest=mini/m['file'];dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes((p/'proposed'/m['file']).read_bytes())
for r in cases:assert sha(checked_receipt(mini,r['document'],r['source_file'],r['source_digest']).read_bytes())==r['source_digest']
result={'pass':True,'maps_modified':len(plan['mutations']),'added_document_pins':len(plan['added_document_pins']),'previously_valid_source_pair_cases':len(cases),'source_documents':len(documents),'reverse_candidates':len(candidates),'unhandled_installed_v1_primary_references':len(primary),'all_original_map_entries_and_document_pins_preserved':True,'scope':'Isolated absent-sidecar to complete-document-pin preservation, no source or numerical changes; root installation pending fresh exact inputs.'};(p/'qualification/RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
