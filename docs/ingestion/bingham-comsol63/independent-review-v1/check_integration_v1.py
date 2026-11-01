"""Read-only binding/archival review; never builds or provisions engines."""
from pathlib import Path
import json,hashlib,sys
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3];sys.path.insert(0,str(ROOT));from atlas.evidence import checked_receipt
P=OUT.parent/'release-bindings-v1';plans=[P/'logical-plan.json',P/'additional-routing-test-v1/plan.json'];res=[];pinpaths=set();copied=[]
for p in plans:
 a=json.loads(p.read_text());pinpaths.add(p)
 for edge in a['primary']+a['secondary']:
  doc=ROOT/edge['document'];assert hashlib.sha256(doc.read_bytes()).hexdigest()==edge['document_sha256'];got=checked_receipt(ROOT,edge['document'],edge['original_path'],edge['sha256']);res.append(dict(document=edge['document'],original_path=edge['original_path'],sha256=edge['sha256'],resolved=str(got.relative_to(ROOT))));pinpaths.add(doc);pinpaths.add(got)
 for edge in a.get('copied_context_mentions_retained',[]):
  doc=ROOT/edge['document'];assert hashlib.sha256(doc.read_bytes()).hexdigest()==edge['document_sha256'];copied.append(edge['document']);pinpaths.add(doc)
for p in [P/'prepared-v1/applied.json',P/'additional-routing-test-v1/prepared-v1/applied.json']:
 a=json.loads(p.read_text());pinpaths.add(p)
 for name,h in a['archives'].items():
  archive=ROOT/name;assert hashlib.sha256(archive.read_bytes()).hexdigest()==h;pinpaths.add(archive)
  if name.endswith('source-archive-map.json'):
   old=json.loads(archive.read_text());logical=name.split('/'+h+'/',1)[1];now=json.loads((ROOT/logical).read_text());assert all(now['documents'].get(k)==v for k,v in old['documents'].items());assert all(x in now['entries'] for x in old['entries']);pinpaths.add(ROOT/logical)
for n in ['.github/workflows/verify.yml','web/app.js','tools/build_web.py','tools/provision_bingham_assets.py','tools/test_bingham_native.py','tests/test_j2_main_routing.mjs','docs/ingestion/bingham-comsol63/interface-v1/routing-policy-v2.md','docs/ingestion/bingham-comsol63/interface-v1/routing-checks-attempt1.log','docs/ingestion/bingham-comsol63/interface-v1/routing-checks-attempt2.log','docs/ingestion/bingham-comsol63/release-bindings-v1/archive-checks-attempt2.log']:pinpaths.add(ROOT/n)
r=dict(reviewer='/root/bingham_review',compiled_execution=False,checked_receipt_edges=len(res),resolutions=res,copied_context_edges_unchanged=len(copied),archived_prior_map_entries_preserved=True,files={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(pinpaths)})
(OUT/'input-binding-v5.json').write_text(json.dumps(r,indent=2)+'\n');print('Checked',len(res),'receipt edges;',len(copied),'copied-context exact hashes; all archived prior map entries retained.')
