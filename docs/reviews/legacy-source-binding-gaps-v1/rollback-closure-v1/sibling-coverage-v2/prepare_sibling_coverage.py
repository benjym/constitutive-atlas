from pathlib import Path
import json,hashlib,subprocess,re
root=Path('/Users/bmar5496/code/constitutive-atlas').resolve();base=Path('/private/tmp/atlas-legacy-source-binding-gaps-v1/rollback-plan-v1');plan=json.loads((base/'PLAN.json').read_text());out=base/'sibling-coverage-v2';out.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest();maps=[r['file'] for r in plan['mutations'] if r['before_digest'] is None]+['catalogue/source-replays/dsl-identity-v5/source-archive-map.json'];mutations=[];newpins=[]
for rel in maps:
 raw=(root/rel).read_bytes();m=json.loads(raw)
 for doc in sorted((root/rel).parent.glob('*.json')):
  docrel=str(doc.relative_to(root))
  if docrel==rel:continue
  h=sha(doc.read_bytes());prior=m['documents'].get(docrel)
  if prior is not None:assert prior==h,(rel,docrel)
  else:m['documents'][docrel]=h;newpins.append({'map_file':rel,'document_file':docrel,'document_digest':h})
 proposed=(json.dumps(m,indent=2)+'\n').encode()
 if proposed==raw:continue
 dest=out/'proposed'/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(proposed);arc='catalogue/source-snapshots/'+sha(raw)+'/'+rel;dest=out/'archives'/arc;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw);mutations.append({'file':rel,'before_digest':sha(raw),'after_digest':sha(proposed),'archive_file':arc})
(out/'target-paths.txt').write_text('\n'.join(r['file'] for r in mutations)+'\n')
result={'scope':'Supplement exact sibling document pins for21 newly created maps. Existing documents/entries and all source identities unchanged. Preserve every installed-v1 map before editing. Before installation, reverse-scan current dependencies on these installed-v1 map hashes and require no unhandled primary consumer; all previous735 outcomes and six original positive bindings must remain equal.','maps_checked':len(maps),'mutations':mutations,'added_document_pins':newpins,'acceptance':'All sibling JSON document pins exact; source pairs previously valid without the new sidecars remain valid; original targeted outcomes unchanged. No old failure waiver.'};(out/'PLAN.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'maps_checked':len(maps),'mutations':len(mutations),'pins':len(newpins)}))
