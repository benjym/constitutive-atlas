"""Independent decoded-JSON discovery; does not rely on rg path-string prefilter."""
from pathlib import Path
import ast,gzip,hashlib,json,re
ROOT=Path('/private/tmp/atlas-bingham-release-v3');OUT=Path(__file__).resolve().parent;P=OUT.with_name('final-imported-context-v1')
h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();valid=lambda x:isinstance(x,str) and bool(re.fullmatch('[0-9a-f]{64}',x))
def pairs(v):
 if isinstance(v,dict):
  for k,s in v.items():
   if valid(s) and ('/' in k or '.' in k or (ROOT/k).is_file()):yield k,s
  if isinstance(v.get('path'),str):
   for k in ['sha256','hash']:
    if valid(v.get(k)):yield v['path'],v[k]
  for x in v.values():yield from pairs(x)
 elif isinstance(v,list):
  for x in v:yield from pairs(x)
t=ast.parse((P/'prepare.py').read_text());d=ROOT/'docs/ingestion/bingham-comsol63/current-integration-v3-preparation-v1';t0=ast.parse((d/'audit_preservation.py').read_text());excluded=next(ast.literal_eval(n.value) for n in t0.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id=='excluded' for x in n.targets));excluded|={'final-imported-context-v1','actual-integration-v3-candidates-v1','qualified-engine-candidate-v5','qualified-engine-evidence-v5','package-inputs-v3-preparation-v1'}
def skip(n):return bool(set(Path(n).parts)&excluded or any(re.fullmatch(r'prior-v\d+',x) for x in Path(n).parts))
inv=json.loads(gzip.decompress((P/'imported-input-inventory.json.gz').read_bytes()));comp=json.loads((P/'FINAL-COMPOSITION.json').read_text());selected=comp['selected_source_and_admission_files'];targets={n:h(ROOT/n) for n,v in selected.items() if (ROOT/n).is_file() and h(ROOT/n)!=v}
rows={};parsed=0;malformed=[]
for n in inv:
 if not n.endswith('.json') or n.endswith('/source-archive-map.json') or skip(n):continue
 try:found=set(pairs(json.loads((ROOT/n).read_text())))
 except (UnicodeError,json.JSONDecodeError):malformed.append(n);continue
 parsed+=1
 if found:rows[n]=found
parents={Path(n).parent.as_posix() for n,found in rows.items() if any(targets.get(path)==s for path,s in found)}
parents|={Path(n).parent.as_posix() for n in rows if n.startswith(('docs/ingestion/bingham-comsol63/','docs/investigations/physical-time-v2-'))};parents.add('catalogue/agent-reviews')
for i in range(20):
 maps={p+'/source-archive-map.json':h(ROOT/p/'source-archive-map.json') for p in parents if (ROOT/p/'source-archive-map.json').is_file()}
 new=parents|{Path(n).parent.as_posix() for n,found in rows.items() if any(maps.get(path)==s for path,s in found)}
 if new==parents:break
 parents=new
else:raise AssertionError('No closure')
sibs=json.loads((P/'SIBLINGS.json').read_text());assert parents==set(sibs['parent_contexts']),(parents-set(sibs['parent_contexts']),set(sibs['parent_contexts'])-parents)
effective={n:len(found) for n,found in rows.items() if Path(n).parent.as_posix() in parents};all_siblings={q.relative_to(ROOT).as_posix() for parent in parents for q in (ROOT/parent).glob('*.json') if q.name!='source-archive-map.json'};assert all_siblings==set(sibs['documents'])
proof=json.loads(gzip.decompress((P/'FINAL-REPLAY.json.gz').read_bytes()));edges={(e['document'],e['original_path'],e['sha256']) for e in proof['edges']};expected={(n,path,s) for n in effective for path,s in rows[n]};assert expected==edges
result={'full_decoded_JSON_discovery':True,'parsed_active_owner_JSON':parsed,'affected_parent_contexts':len(parents),'all_immediate_sibling_documents':len(all_siblings),'effective_documents_with_recognized_edges':len(effective),'recognized_edges':len(edges),'zero_pair_valid_siblings':len(all_siblings)-len(effective)-len(set(malformed)&all_siblings),'malformed_siblings':sorted(set(malformed)&all_siblings),'all_original_edges_preserved_in_final_replay':True,'prefilter_omission_detected':False}
(OUT/'DISCOVERY-CHECK.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
