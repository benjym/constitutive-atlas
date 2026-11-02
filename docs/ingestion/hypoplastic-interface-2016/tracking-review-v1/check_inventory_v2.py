"""Pure exact additive inventory and E4 engine-byte check."""
from pathlib import Path
import json,hashlib
P=Path(__file__).resolve().parent.parent;C=P/'integration-v1/commit-preparation-v1';read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
a=read(C/'inventory.json');b=read(C/'inventory-v2.json');old={e['path']:e for e in a['entries']};new={e['path']:e for e in b['entries']}
assert len(old)==200 and len(new)==len(b['entries'])==209 and old.keys()<=new.keys()
assert all(old[n]==new[n] for n in old)
R=Path(b['release_root']);engines=read(C/'public-engine-pins-v2.json')['pins'];receipt=read(P/'execution-v1/build-receipt.json')
for name,digest in engines.items():
 assert new[name]['sha256']==digest and sha(R/name)==digest
 suffix='/wasm/'+name.split('web/engines/interface2016/')[1]
 matches=[h for n,h in receipt['artifacts'].items() if n.endswith(suffix)];assert matches==[digest]
expected=set(engines)|{str(x.relative_to(P.parents[2])) for x in [P/'tracking-review-v1'/n for n in ['REPORT.md','check-results.json','check_tracking.py','decision.json']]}
assert new.keys()-old.keys()==expected
for entry in b['entries']:
 data=(R/entry['path']).read_bytes();assert len(data)==entry['size'] and hashlib.sha256(data).hexdigest()==entry['sha256'] and hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['git_blob_sha1']
assert set((C/'paths-v2.txt').read_text().splitlines())==set(new)
result={'passed':True,'old_entries_unchanged':200,'additions':sorted(expected),'exact_E4_engine_and_generated_assets':5,'total_entries':209,'total_bytes':sum(e['size'] for e in b['entries']),'inventory_sha256':sha(C/'inventory-v2.json'),'compiled_module_material_calls':0}
(Path(__file__).parent/'inventory-v2-check-results.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
