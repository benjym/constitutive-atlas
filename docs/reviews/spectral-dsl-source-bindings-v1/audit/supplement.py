"""Read-only source availability, precise archival plan and contextual map audit."""
from pathlib import Path
import json,hashlib,collections,ast,subprocess
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');OUT=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inv=json.loads((OUT/'inventory.json').read_text());live=inv['live_source_identities'];current=[r for r in inv['primary_references']if r['expected_equals_current_live']];groups={}
 for r in current:
  d=r['document'];s=ROOT/d;side=s.parent/'source-archive-map.json';mapping=json.loads(side.read_text())if side.exists()else None
  g=groups.setdefault(d,{'document':d,'document_sha256':sha(s),'sidecar':side.relative_to(ROOT).as_posix(),'sidecar_exists':side.exists(),'sidecar_sha256':sha(side)if side.exists()else None,'document_pin_state':('absent'if mapping is None or d not in mapping.get('documents',{})else 'matches'if mapping['documents'][d]==sha(s)else 'MISMATCH'),'bindings':[]})
  canonical=ROOT/'catalogue/source-snapshots'/r['sha256']/r['original_path']
  g['bindings'].append({'original_path':r['original_path'],'sha256':r['sha256'],'current_resolution':r['resolution'],'canonical_archive':canonical.relative_to(ROOT).as_posix(),'canonical_archive_valid':canonical.is_file()and sha(canonical)==r['sha256']})
 candidates={name:[]for name in ('dsl.py','compiler.py','history_compiler.py','model.py')}
 for name in candidates:
  for p in ROOT.rglob(name):
   if p.is_file():candidates[name].append((p,sha(p)))
 needed=sorted({(r['original_path'],r['sha256'])for r in inv['primary_references']if r['resolution']=='unresolved'})
 available=[]
 for name,h in needed:
  matches=[p.relative_to(ROOT).as_posix()for p,pin in candidates[Path(name).name]if pin==h]
  available.append({'original_path':name,'sha256':h,'repository_matches':matches,'canonical_archive_exists':(ROOT/'catalogue/source-snapshots'/h/name).is_file()})
 contextual=[]
 for r in inv['secondary_source_map_references']:
  if r['resolution']!='unresolved':continue
  local=(ROOT/r['document']).parent/r['original_path']
  contextual.append({'document':r['document'],'document_sha256':r['document_sha256'],'literal_source_path':r['original_path'],'sha256':r['sha256'],'repository_root_resolution':r['resolution'],'document_relative_candidate':local.relative_to(ROOT).as_posix(),'document_relative_exists':local.is_file(),'document_relative_sha256':sha(local)if local.is_file()else None,'document_relative_matches':local.is_file()and sha(local)==r['sha256'],'interpretation':'Contextual packet-local path; scanner only asks root-relative checked_receipt. Consumer interpretation must be kept distinct.'})
 imports={}
 for item in live:
  name=item['original_path'];tree=ast.parse((ROOT/name).read_text());imports[name]=[ast.get_source_segment((ROOT/name).read_text(),n)for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom))]
 result={'current_source_bytes_unchanged_since_inventory':all(sha(ROOT/r['original_path'])==r['sha256']for r in live),'live_source_identities':live,'current_pairs':len(current),'current_documents':len(groups),'current_archive_plan':list(groups.values()),'unresolved_distinct_source_identity_availability':available,'candidate_file_counts':{k:len(v)for k,v in candidates.items()},'contextual_secondary_references':contextual,'target_module_direct_imports':imports,'limits':'No source or receipt mutation; repository file availability only, no new git/external search. Import inventory is not dynamic dependency closure.'}
 (OUT/'supplement.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
 print(json.dumps({'current_pairs':len(current),'documents':len(groups),'source_unchanged':result['current_source_bytes_unchanged_since_inventory'],'unresolved_identity_count':len(available),'contextual_secondary':contextual},indent=2))
if __name__=='__main__':main()
