"""Read-only final byte preservation and complete immediate-sibling proof."""
from pathlib import Path
import gzip,hashlib,json
H=Path(__file__).resolve().parent;R=H.parents[3];C=Path('/private/tmp/atlas-bingham-final-context-v1');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
i=json.loads(gzip.decompress((H/'imported-input-inventory.json.gz').read_bytes()));c=json.loads((H/'SEALED-COMPOSITION.json').read_text());p=json.loads((H/'SEALED-PRESERVATION.json').read_text());selected=c['selected_source_and_admission_files'];changed=set(selected)|set(p['maps']);archives=0;unchanged=0;mutable={'docs/ingestion/bingham-comsol63/DELIVERY.md'};observations={}
for n,h in i.items():
 if n in changed:continue
 if n in mutable:
  observations[n]={'initial_observation_sha256':h,'current_sha256':sha(C/n),'scientific_pin':False};continue
 assert sha(C/n)==h,('unexpected existing-byte change',n)
 unchanged+=1;archives+=n.startswith('catalogue/source-snapshots/')
for n,h in selected.items():assert sha(C/n)==h
for n,h in p['files'].items():assert sha(C/n)==h
siblings={};oldentries=oldpins=0
for n,v in p['maps'].items():
 new=json.loads((C/n).read_text());old=json.loads((R/n).read_text()) if (R/n).exists() else {'documents':{},'entries':[]}
 assert v['before_sha256']==(sha(R/n) if (R/n).exists() else None)
 for d,h in old['documents'].items():assert new['documents'][d]==h;oldpins+=1
 for e in old['entries']:assert e in new['entries'];oldentries+=1
 ss={}
 for f in (C/n).parent.glob('*.json'):
  if f.name=='source-archive-map.json':continue
  d=f.relative_to(C).as_posix();ss[d]=sha(f)
  assert d in new['documents'],('missing immediate sibling pin',d)
  if d not in old['documents']:assert new['documents'][d]==sha(f)
 siblings[n]=ss
review='catalogue/agent-reviews/bingham-comsol63-agent-v1.json';assert sha(C/review)=='61022026949f2ce9b9a536ab564239edd97ac0b5b3ba66f4ffe3f0066aa6b836';assert json.loads((C/'catalogue/agent-reviews/source-archive-map.json').read_text())['documents'][review]==sha(C/review)
result={'passed':True,'mutable_tracking_observations':observations,'unchanged_existing_files':unchanged,'unchanged_existing_archive_members':archives,'unchanged_old_document_pins':oldpins,'unchanged_old_entries':oldentries,'changed_maps':len(p['maps']),'selected_source_admission_tracking_paths':c['selected_nonpreservation_count'],'full_immediate_sibling_sets':siblings,'no_build_or_material_calls':True}
(H/'INTEGRITY.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='full_immediate_sibling_sets'},indent=2))
