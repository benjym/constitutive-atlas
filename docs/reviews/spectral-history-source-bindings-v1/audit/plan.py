"""Read-only minimal live reverse map closure; archived/descriptor edges not mutations."""
from pathlib import Path
import json,hashlib,collections
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 x=json.loads((OUT/'inventory.json').read_text());assignments={};changed=set(x['potential_new_or_extended_sidecars']);initial=set(changed)
 def add(r,reason):
  key=(r['document'],r['original_path'],r['sha256']);assignments[key]={k:r[k]for k in ['document','document_sha256','original_path','sha256','resolution']};assignments[key]['reason']=reason
 for r in x['primary_references']:add(r,'history current source archival')
 while True:
  before=set(changed)
  for r in x['secondary_source_map_references']:
   if r['original_path']in changed and r['resolution']=='live':
    add(r,'live reverse-bound map bytes must remain resolvable');changed.add(str(Path(r['document']).parent/'source-archive-map.json'))
  if changed==before:break
 affected=[r for r in x['secondary_source_map_references']if r['original_path']in changed]
 maps=[]
 for name in sorted(changed):
  p=ROOT/name;maps.append({'original_path':name,'exists':p.exists(),'sha256':sha(p)if p.exists()else None,'initial_history_sibling':name in initial})
 documents={}
 for r in assignments.values():
  name=r['document'];p=ROOT/name;s=p.parent/'source-archive-map.json';mapping=json.loads(s.read_text())if s.exists()else {};pin=mapping.get('documents',{}).get(name)
  d=documents.setdefault(name,{'document':name,'document_sha256':r['document_sha256'],'sibling_sidecar':s.relative_to(ROOT).as_posix(),'document_pin_state':'absent'if pin is None else'matches'if pin==r['document_sha256']else'MISMATCH','bindings':[]})
  target=ROOT/'catalogue/source-snapshots'/r['sha256']/r['original_path'];d['bindings'].append({**r,'canonical_archive':target.relative_to(ROOT).as_posix(),'canonical_archive_valid':target.is_file()and sha(target)==r['sha256']})
 snapshots=[]
 for name,h in sorted({(r['original_path'],r['sha256'])for r in assignments.values()}|{(r['original_path'],r['sha256'])for r in maps if r['exists']}):
  source=ROOT/name;assert sha(source)==h,(name,h);dest=OUT/'source-bytes'/h/name;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(source.read_bytes());snapshots.append({'original_path':name,'sha256':h,'staged_path':dest.relative_to(OUT).as_posix()})
 contextual=[]
 for r in x['secondary_source_map_references']:
  if r['resolution']!='unresolved':continue
  local=(ROOT/r['document']).parent/r['original_path'];canonical=ROOT/'catalogue/source-snapshots'/r['sha256']/r['original_path'];contextual.append({'document':r['document'],'document_sha256':r['document_sha256'],'original_path':r['original_path'],'sha256':r['sha256'],'error':r['error'],'local_candidate_exists':local.is_file(),'local_candidate_matches':local.is_file()and sha(local)==r['sha256'],'canonical_exists':canonical.is_file(),'interpretation':'original packet-local manifest entry or descriptive audit inventory of it; keep outside root-primary source archival'})
 result={'initial_history_source_pairs':len(x['primary_references']),'primary_unresolved':x['summary']['primary_unresolved'],'minimal_total_document_source_pairs':len(assignments),'minimal_total_documents':len(documents),'minimal_maps_to_create_or_extend':maps,'initial_map_count':len(initial),'minimal_map_count':len(changed),'inherited_conservative_map_closure':x['sidecar_reverse_reference_closure'],'minimal_new_map_locations_missing_from_inherited_closure':sorted(changed-set(x['sidecar_reverse_reference_closure'])),'documents':list(documents.values()),'affected_secondary_resolution_counts':dict(collections.Counter(r['resolution']for r in affected)),'affected_secondary_references':affected,'staged_verified_bytes':snapshots,'unresolved_secondary_contexts':contextual,'policy':'Only root-resolving live primary-syntax reverse receipts require sibling map additions. Existing archived edges retain exact old bytes; descriptive original_path entries need canonical bytes, not rewriting the descriptive document. Archive every pre-append existing map byte first.'}
 (OUT/'plan.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps({k:result[k]for k in ['initial_history_source_pairs','minimal_total_document_source_pairs','minimal_total_documents','initial_map_count','minimal_map_count','minimal_new_map_locations_missing_from_inherited_closure','affected_secondary_resolution_counts']},indent=2))
if __name__=='__main__':main()
