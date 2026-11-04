from pathlib import Path
import json,hashlib,tarfile
Q=Path(__file__).resolve().parent;R=Q.parents[4];P=Q.parent/'direct-profile-compatibility-v1';S=Path('/private/tmp/atlas-md1997-current-main-integration-v1/source')
h=lambda b:hashlib.sha256(b).hexdigest()
read=lambda p:json.loads(p.read_bytes())
receipt=read(Q.parent/'current-qualified-profile-copies-v1/receipt.json');b=read(P/'proposed-bindings.json');r=read(P/'results.json');count=0;old_qual={}
with tarfile.open(R/'.local/private-evidence/md1997-current-package-v7/complete-output.tar.gz') as t:
 for name,folder in [('norsand','engine-path'),('maxwell','engine-maxwell')]:
  raw=t.extractfile('site/'+folder+'/qualification.json').read();q=json.loads(raw);old_qual[name]=h(raw)
  for filename,v in r[name]['generated'].items():assert v['sha256']==receipt['profiles'][name]['original_inventory']['generated/'+filename];count+=1
  bp=b['profiles'][name]['proposed_binding']
  if name=='norsand':
   assert bp['sources']==b['profiles'][name]['complete_source_manifest'];count+=1
   for restored,archivename in [('atlas_path_capability.mjs','engine.mjs'),('atlas_path_capability.wasm','engine.wasm')]:assert h(t.extractfile('site/'+folder+'/'+archivename).read())==bp['artifacts'][restored]==q['binding']['artifacts'][restored];count+=1
  else:
   for filename,key in [('maxwell.mjs','module_sha256'),('maxwell.wasm','wasm_sha256'),('models.json','catalogue_file_sha256')]:assert h(t.extractfile('site/'+folder+'/'+filename).read())==bp[key]==q['binding'][key];count+=1
# Historical Interface receipt and current retained refresh files bind the same bytes.
iq=read(S/'docs/ingestion/hypoplastic-interface-2016/execution-v1/build-receipt.json');engine=S/'docs/ingestion/vibe-2026/controlled-path-refresh-v1/execution-v2/interface2016/engine'
for filename in ['atlas_path_capability.mjs','atlas_path_capability.wasm']:
 want=next(v for n,v in iq['artifacts'].items() if n.endswith('/wasm/'+filename));assert h((engine/filename).read_bytes())==want;count+=1
for filename in ['path_api.cpp','path_models.hpp','path_catalogue.json']:
 want=next(v for n,v in iq['artifacts'].items() if n.endswith('/generated/'+filename));assert h((engine/'generated'/filename).read_bytes())==want;count+=1
m=read(P/'manifest.json');assert all(h((P/n).read_bytes())==v for n,v in m['files'].items());count+=len(m['files'])
print(json.dumps({'passed':True,'checks':count,'original_qualification_raw_hashes':old_qual,'subject_unchanged':True,'gate_claim':'original numerical/scientific observations inherited, not rerun; original qualifications unmodified'},indent=2))
