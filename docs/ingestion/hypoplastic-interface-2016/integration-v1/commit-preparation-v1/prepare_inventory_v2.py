"""Read-only additive production engine/tracking-review inventory correction."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');OUT=Path(__file__).resolve().parent
RELEASE=Path('/private/tmp/atlas-interface2016-delivery-v1/release-v2')
d=json.loads((OUT/'inventory.json').read_text());d['version']=2;d['supersedes']='inventory.json'
receipt=json.loads((RELEASE/'docs/ingestion/hypoplastic-interface-2016/execution-v1/build-receipt.json').read_text())
entries={e['path']:e for e in d['entries']};pins={};copy=[]
for p in sorted((RELEASE/'web/engines/interface2016').rglob('*')):
 if not p.is_file():continue
 assert not p.is_symlink()
 name=p.relative_to(RELEASE).as_posix();relative=p.relative_to(RELEASE/'web/engines/interface2016').as_posix()
 matches=[h for q,h in receipt['artifacts'].items() if q.endswith('/'+relative)]
 data=p.read_bytes();digest=hashlib.sha256(data).hexdigest();assert matches==[digest],(name,matches,digest)
 assert relative in ['atlas_path_capability.mjs','atlas_path_capability.wasm','generated/path_catalogue.json','generated/path_models.hpp','generated/path_api.cpp']
 pins[name]=digest
 entries[name]={'path':name,'sha256':digest,'git_blob_sha1':hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),'size':len(data),'mode':'100644','change':'add','source':str(p),'reasons':['exact public engine/generated assets required by ordinary clean-checkout builder; E4 reviewed artifact digest']}
assert len(pins)==5
for filename in ['REPORT.md','check-results.json','check_tracking.py','decision.json']:
 name='docs/ingestion/hypoplastic-interface-2016/tracking-review-v1/'+filename
 p=RELEASE/name
 if not p.is_file():p=ROOT/name;copy.append(name)
 assert p.is_file() and not p.is_symlink()
 data=p.read_bytes();entries[name]={'path':name,'sha256':hashlib.sha256(data).hexdigest(),'git_blob_sha1':hashlib.sha1(f'blob {len(data)}\0'.encode()+data).hexdigest(),'size':len(data),'mode':'100644','change':'add','source':str(p),'reasons':['independent tracking review four-file handoff']}
d['entries']=[entries[n] for n in sorted(entries)]
d['parent_copy_required_before_execution']+=copy
d['checks'].pop('private_originals_or_compiled_artifacts_included',None)
d['checks']['private_originals_or_native_artifacts_included']=False
d['checks']['qualified_public_Wasm_engine_included']=True
d['checks']['public_engine_E4_pins_verified']=pins
d['checks']['v2_reason']='Normal clean-checkout builder requires exact qualified public engine; additive five assets plus independent tracking review four files. Native dylib excluded.'
(OUT/'inventory-v2.json').write_text(json.dumps(d,indent=2)+'\n')
(OUT/'paths-v2.txt').write_text(''.join(e['path']+'\n' for e in d['entries']))
(OUT/'public-engine-pins-v2.json').write_text(json.dumps({'verified_against':'docs/ingestion/hypoplastic-interface-2016/execution-v1/build-receipt.json','pins':pins,'total_files':len(d['entries']),'copy_required':copy,'compiled_calls':0,'git_mutations':0},indent=2)+'\n')
print(json.dumps({'files':len(d['entries']),'public_engine_pins':pins,'copy_required':copy},indent=2))
